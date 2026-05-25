import asyncio
import hashlib
import httpx
from app.transforms.base import BaseTransform, Entity, TransformResult, EntityType


class EmailOSINTTransform(BaseTransform):
    name = "Email OSINT"
    description = "Check email registration across platforms (Holehe-style) + Gravatar profile"
    input_types = [EntityType.EMAIL_ADDRESS]
    output_types = [EntityType.SOCIAL_PROFILE, EntityType.PERSON]
    timeout = 45
    rate_limit = 3

    async def run(self, entity: Entity, api_keys: dict) -> TransformResult:
        result = TransformResult()
        email = entity.value.strip().lower()

        if "@" not in email:
            result.error = "Invalid email address"
            return result

        tasks = [
            self._check_gravatar(email),
            self._check_github(email),
            self._check_spotify(email),
            self._check_adobe(email),
        ]

        gathered = await asyncio.gather(*tasks, return_exceptions=True)
        for p in gathered:
            if isinstance(p, Entity):
                result.entities.append(p)
                result.edges.append({"from": email, "to": p.value, "label": "registered_with"})
            elif isinstance(p, list):
                for e in p:
                    if isinstance(e, Entity):
                        result.entities.append(e)
                        result.edges.append({"from": email, "to": e.value, "label": "registered_with"})

        return result

    async def _check_gravatar(self, email: str) -> Entity | None:
        md5 = hashlib.md5(email.lower().encode()).hexdigest()
        try:
            async with httpx.AsyncClient(timeout=8.0) as client:
                resp = await client.get(f"https://en.gravatar.com/{md5}.json")
                if resp.status_code == 200:
                    data = resp.json()
                    entries = data.get("entry", [])
                    entry = entries[0] if entries else {}
                    name = entry.get("displayName") or entry.get("name", {}).get("formatted", "")
                    avatar = f"https://www.gravatar.com/avatar/{md5}"
                    urls = [u.get("value", "") for u in entry.get("urls", [])]
                    return Entity(
                        type=EntityType.PERSON,
                        value=f"gravatar:{email}",
                        label=name or f"Gravatar: {email}",
                        properties={
                            "source": "gravatar",
                            "email": email,
                            "display_name": name,
                            "avatar_url": avatar,
                            "profile_url": f"https://gravatar.com/{md5}",
                            "urls": urls,
                        },
                    )
        except Exception:
            pass
        return None

    async def _check_github(self, email: str) -> Entity | None:
        try:
            async with httpx.AsyncClient(timeout=8.0) as client:
                resp = await client.get(
                    "https://api.github.com/search/users",
                    params={"q": f"{email} in:email"},
                    headers={"Accept": "application/vnd.github.v3+json"},
                )
                if resp.status_code == 200:
                    data = resp.json()
                    if data.get("total_count", 0) > 0 and data.get("items"):
                        user = data["items"][0]
                        return Entity(
                            type=EntityType.SOCIAL_PROFILE,
                            value=f"github:{user['login']}",
                            label=f"GitHub: {user['login']}",
                            properties={
                                "platform": "GitHub",
                                "username": user["login"],
                                "profile_url": user["html_url"],
                                "avatar_url": user.get("avatar_url", ""),
                            },
                        )
        except Exception:
            pass
        return None

    async def _check_spotify(self, email: str) -> Entity | None:
        try:
            async with httpx.AsyncClient(timeout=8.0) as client:
                resp = await client.get(
                    "https://spclient.wg.spotify.com/signup/public/v1/account",
                    params={"validate": "1", "email": email},
                    headers={"User-Agent": "Spotify/8.6.0 Android/29"},
                )
                if resp.status_code == 200:
                    try:
                        data = resp.json()
                    except Exception:
                        data = {}
                    # status 20 = email already in use
                    if data.get("status") == 20:
                        return Entity(
                            type=EntityType.SOCIAL_PROFILE,
                            value=f"spotify:{email}",
                            label=f"Spotify account for {email}",
                            properties={"platform": "Spotify", "email": email},
                        )
        except Exception:
            pass
        return None

    async def _check_adobe(self, email: str) -> Entity | None:
        try:
            async with httpx.AsyncClient(timeout=8.0) as client:
                resp = await client.post(
                    "https://auth.services.adobe.com/en_US/index.html",
                    data={"username": email},
                    headers={"Content-Type": "application/x-www-form-urlencoded"},
                )
                if resp.status_code == 200 and "password" in resp.text.lower():
                    return Entity(
                        type=EntityType.SOCIAL_PROFILE,
                        value=f"adobe:{email}",
                        label=f"Adobe account: {email}",
                        properties={"platform": "Adobe", "email": email},
                    )
        except Exception:
            pass
        return None
