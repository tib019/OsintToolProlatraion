import asyncio
import re
import httpx
from app.transforms.base import BaseTransform, Entity, TransformResult, EntityType

DORK_TEMPLATES: dict[str, list[str]] = {
    "PhoneNumber": [
        '"{value}" site:truecaller.com',
        '"{value}" site:tellows.de OR site:tellows.com',
        '"{value}" filetype:pdf OR filetype:xlsx',
        '"{value}"',
    ],
    "EmailAddress": [
        '"{value}" filetype:pdf OR filetype:xls OR filetype:csv',
        '"{value}" site:pastebin.com',
        '"{value}"',
    ],
    "Username": [
        '"{value}" site:github.com OR site:gitlab.com',
        '"{value}" site:reddit.com OR site:twitter.com',
        '"{value}"',
    ],
    "Person": [
        '"{value}" site:linkedin.com',
        '"{value}" site:xing.com',
        '"{value}"',
    ],
    "Domain": [
        "site:{value}",
        "inurl:{value} admin OR login OR panel",
        '"{value}" site:pastebin.com',
    ],
    "IPAddress": [
        '"{value}"',
        '"{value}" site:shodan.io',
    ],
    "Organization": [
        '"{value}" site:linkedin.com',
        '"{value}" employees OR careers OR jobs',
        '"{value}"',
    ],
    "SocialProfile": [
        '"{value}"',
        '"{value}" site:linkedin.com OR site:twitter.com',
    ],
}

# Fallback template used for any entity type not listed above
_DEFAULT_TEMPLATES = ['"{value}"']


class GoogleDorkingTransform(BaseTransform):
    name = "Google Dorking"
    description = "Auto-generate and display targeted Google dorks for any entity"
    input_types = list(EntityType)
    output_types = [EntityType.DOMAIN]
    timeout = 20
    rate_limit = 5

    async def run(self, entity: Entity, api_keys: dict) -> TransformResult:
        result = TransformResult()
        value = entity.value.strip()

        # Resolve entity type string
        entity_type_str = entity.type.value if hasattr(entity.type, "value") else str(entity.type)

        templates = DORK_TEMPLATES.get(entity_type_str, _DEFAULT_TEMPLATES)
        dorks = [t.replace("{value}", value) for t in templates]

        # Build direct Google search links (for use in the UI)
        google_links: list[str] = []
        for d in dorks:
            encoded = httpx.QueryParams({"q": d})
            google_links.append(f"https://www.google.com/search?{encoded}")

        result.metadata["dorks"] = dorks
        result.metadata["google_links"] = google_links

        # Try DuckDuckGo as a free search engine (rate-limited; first 2 dorks only)
        found_urls: set[str] = set()
        async with httpx.AsyncClient(timeout=10.0, follow_redirects=True) as client:
            for dork in dorks[:2]:
                try:
                    resp = await client.get(
                        "https://html.duckduckgo.com/html/",
                        params={"q": dork},
                        headers={"User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36"},
                    )
                    if resp.status_code == 200:
                        urls = re.findall(r'href="(https?://[^"]+)"', resp.text)
                        for url in urls[:5]:
                            if "duckduckgo.com" not in url and url not in found_urls:
                                found_urls.add(url)
                                domain_match = re.match(r"https?://([^/]+)", url)
                                if domain_match:
                                    domain = domain_match.group(1)
                                    result.entities.append(Entity(
                                        type=EntityType.DOMAIN,
                                        value=domain,
                                        label=domain,
                                        properties={
                                            "source": "dork_result",
                                            "full_url": url,
                                            "dork": dork,
                                        },
                                    ))
                                    result.edges.append({
                                        "from": value,
                                        "to": domain,
                                        "label": "found_via_dork",
                                    })
                    await asyncio.sleep(1)
                except Exception:
                    pass

        return result
