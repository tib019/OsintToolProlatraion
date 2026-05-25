import asyncio
import json
import httpx
from pathlib import Path
from app.transforms.base import BaseTransform, Entity, TransformResult, EntityType

PLATFORMS_FILE = Path(__file__).parent / "data" / "platforms.json"


class UsernameSearchTransform(BaseTransform):
    name = "Username Search"
    description = "Search username across 300+ platforms (Sherlock-style)"
    input_types = [EntityType.USERNAME]
    output_types = [EntityType.SOCIAL_PROFILE]
    timeout = 60
    rate_limit = 2

    async def run(self, entity: Entity, api_keys: dict) -> TransformResult:
        result = TransformResult()
        username = entity.value.strip()
        if not username:
            result.error = "Empty username"
            return result

        try:
            platforms: dict = json.loads(PLATFORMS_FILE.read_text())
        except Exception:
            result.error = "Could not load platforms list"
            return result

        semaphore = asyncio.Semaphore(30)
        found: list[Entity] = []

        async def check(name: str, info: dict) -> None:
            url_template = info.get("url", "")
            if not url_template:
                return
            url = url_template.replace("{username}", username)
            error_type = info.get("errorType", "status_code")
            error_code = info.get("errorCode", 404)
            error_msg = info.get("errorMsg", "")

            async with semaphore:
                try:
                    async with httpx.AsyncClient(
                        timeout=8.0,
                        follow_redirects=True,
                    ) as client:
                        resp = await client.get(
                            url,
                            headers={"User-Agent": "Mozilla/5.0 (compatible; PHANTOM OSINT)"},
                        )

                        found_it = False
                        if error_type == "status_code":
                            found_it = resp.status_code == 200 and resp.status_code != error_code
                        elif error_type == "message":
                            found_it = resp.status_code == 200 and error_msg not in resp.text
                        elif error_type == "response_url":
                            found_it = str(resp.url) == url

                        if found_it:
                            found.append(Entity(
                                type=EntityType.SOCIAL_PROFILE,
                                value=f"{name.lower()}:{username}",
                                label=f"{name}: {username}",
                                properties={
                                    "platform": name,
                                    "username": username,
                                    "url": url,
                                    "status": resp.status_code,
                                },
                            ))
                except Exception:
                    pass

        tasks = [check(name, info) for name, info in platforms.items()]
        await asyncio.gather(*tasks)

        result.entities.extend(found)
        for e in found:
            result.edges.append({"from": username, "to": e.value, "label": "profile_found"})
        result.metadata["checked"] = len(platforms)
        result.metadata["found"] = len(found)

        return result
