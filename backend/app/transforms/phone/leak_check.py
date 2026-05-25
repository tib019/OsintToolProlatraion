import httpx
from app.transforms.base import BaseTransform, Entity, TransformResult, EntityType


class LeakCheckTransform(BaseTransform):
    name = "Leak Database Check"
    description = "Check HaveIBeenPwned for breaches involving this email/phone"
    input_types = [EntityType.PHONE_NUMBER, EntityType.EMAIL_ADDRESS]
    output_types = [EntityType.LEAK_RECORD]
    timeout = 15
    rate_limit = 10

    async def run(self, entity: Entity, api_keys: dict) -> TransformResult:
        result = TransformResult()
        api_key = api_keys.get("HIBP_API_KEY", "")

        if not api_key:
            result.metadata["info"] = (
                "HaveIBeenPwned API key not configured. "
                "Get one at haveibeenpwned.com/API/Key"
            )
            return result

        value = entity.value.strip()

        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                resp = await client.get(
                    f"https://haveibeenpwned.com/api/v3/breachedaccount/{value}",
                    headers={
                        "hibp-api-key": api_key,
                        "User-Agent": "PHANTOM-OSINT-Platform",
                    },
                    params={"truncateResponse": "false"},
                )

                if resp.status_code == 200:
                    breaches = resp.json()
                    for breach in breaches:
                        leak_id = f"hibp:{breach['Name']}"
                        result.entities.append(Entity(
                            type=EntityType.LEAK_RECORD,
                            value=leak_id,
                            label=breach["Name"],
                            properties={
                                "breach_name": breach["Name"],
                                "domain": breach.get("Domain", ""),
                                "breach_date": breach.get("BreachDate", ""),
                                "pwn_count": breach.get("PwnCount", 0),
                                "description": breach.get("Description", "")[:200],
                                "data_classes": breach.get("DataClasses", []),
                                "verified": breach.get("IsVerified", False),
                                "sensitive": breach.get("IsSensitive", False),
                            },
                        ))
                        result.edges.append({"from": value, "to": leak_id, "label": "found_in_breach"})

                elif resp.status_code == 404:
                    result.metadata["info"] = "No breaches found — this is good!"
                elif resp.status_code == 401:
                    result.error = "Invalid HIBP API key"
                elif resp.status_code == 429:
                    result.error = "Rate limit exceeded — try again in a few seconds"
                else:
                    result.metadata["status_code"] = resp.status_code

        except Exception as e:
            result.error = str(e)

        return result
