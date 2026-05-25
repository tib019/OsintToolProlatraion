import asyncio
import re
import httpx
from app.transforms.base import BaseTransform, Entity, TransformResult, EntityType


class SocialGraphExpansionTransform(BaseTransform):
    name = "Social Graph Expansion"
    description = "Extract followers/following from a social profile"
    input_types = [EntityType.SOCIAL_PROFILE]
    output_types = [EntityType.USERNAME, EntityType.SOCIAL_PROFILE]
    timeout = 30
    rate_limit = 3

    async def run(self, entity: Entity, api_keys: dict) -> TransformResult:
        result = TransformResult()
        value = entity.value.strip()
        props = entity.properties

        platform = props.get("platform", "").lower()
        # Derive username: prefer explicit property, then last segment after ":"
        username = props.get("username") or value.split(":")[-1]

        if "github" in platform or value.startswith("github:"):
            entities = await self._github_graph(username)
        elif "twitter" in platform or value.startswith("twitter:"):
            entities = await self._twitter_graph(username)
        else:
            result.metadata["info"] = (
                f"Social graph expansion not yet supported for platform: {platform or value}"
            )
            return result

        for e in entities:
            result.entities.append(e)
            result.edges.append({"from": value, "to": e.value, "label": "connected_to"})

        result.metadata["found"] = len(entities)
        return result

    async def _github_graph(self, username: str) -> list[Entity]:
        entities: list[Entity] = []
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                for endpoint, rel in [("followers", "follower"), ("following", "following")]:
                    try:
                        resp = await client.get(
                            f"https://api.github.com/users/{username}/{endpoint}",
                            params={"per_page": 25},
                            headers={"Accept": "application/vnd.github.v3+json"},
                        )
                        if resp.status_code == 200:
                            for user in resp.json():
                                entities.append(Entity(
                                    type=EntityType.SOCIAL_PROFILE,
                                    value=f"github:{user['login']}",
                                    label=f"GitHub: {user['login']}",
                                    properties={
                                        "platform": "GitHub",
                                        "username": user["login"],
                                        "profile_url": user["html_url"],
                                        "avatar_url": user.get("avatar_url", ""),
                                        "relation": rel,
                                    },
                                ))
                    except Exception:
                        continue
        except Exception:
            pass
        return entities[:50]

    async def _twitter_graph(self, username: str) -> list[Entity]:
        entities: list[Entity] = []
        # Use Nitter (public Twitter mirror) for public scraping without API key
        try:
            async with httpx.AsyncClient(timeout=10.0, follow_redirects=True) as client:
                resp = await client.get(
                    f"https://nitter.net/{username}/followers",
                    headers={"User-Agent": "Mozilla/5.0"},
                )
                if resp.status_code == 200:
                    # Extract @username links from the follower page
                    usernames = re.findall(r'href="/([A-Za-z0-9_]{1,15})"', resp.text)
                    excluded = {
                        "search", "about", "login", "settings", "hashtag",
                        "explore", "notifications", "messages", username.lower(),
                    }
                    seen: set[str] = set()
                    for u in usernames:
                        u_lower = u.lower()
                        if u_lower not in excluded and u_lower not in seen and len(u) > 1:
                            seen.add(u_lower)
                            entities.append(Entity(
                                type=EntityType.USERNAME,
                                value=u,
                                label=f"@{u}",
                                properties={
                                    "source": "twitter_followers",
                                    "platform": "Twitter",
                                },
                            ))
                            if len(entities) >= 25:
                                break
        except Exception:
            pass
        return entities
