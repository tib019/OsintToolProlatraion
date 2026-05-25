import httpx
import phonenumbers
from app.transforms.base import BaseTransform, Entity, TransformResult, EntityType


class CNAMLookupTransform(BaseTransform):
    name = "CNAM / Reverse Lookup"
    description = "Resolve phone number to caller name via OpenCNAM"
    input_types = [EntityType.PHONE_NUMBER]
    output_types = [EntityType.PERSON]
    timeout = 10
    rate_limit = 10

    async def run(self, entity: Entity, api_keys: dict) -> TransformResult:
        result = TransformResult()
        sid = api_keys.get("OPENCNAM_SID", "")
        auth = api_keys.get("OPENCNAM_AUTH_TOKEN", "")

        if not sid or not auth:
            result.metadata["info"] = (
                "OpenCNAM API credentials not configured. "
                "Set OPENCNAM_SID and OPENCNAM_AUTH_TOKEN in Settings."
            )
            return result

        try:
            raw = entity.value.strip()
            if not raw.startswith("+"):
                raw = "+" + raw
            phone = phonenumbers.parse(raw)
            e164 = phonenumbers.format_number(phone, phonenumbers.PhoneNumberFormat.E164)
        except Exception:
            result.error = "Could not parse phone number"
            return result

        try:
            async with httpx.AsyncClient(timeout=8.0) as client:
                resp = await client.get(
                    f"https://api.opencnam.com/v3/phone/{e164}",
                    params={"format": "json"},
                    auth=(sid, auth),
                )
                if resp.status_code == 200:
                    data = resp.json()
                    name = data.get("name", "").strip()
                    if name and name not in ("", "UNKNOWN", "NOT FOUND"):
                        result.entities.append(Entity(
                            type=EntityType.PERSON,
                            value=name,
                            label=name,
                            properties={"source": "opencnam", "phone": e164, "cnam": name},
                        ))
                        result.edges.append({"from": e164, "to": name, "label": "caller_id"})
                elif resp.status_code == 402:
                    result.metadata["info"] = "OpenCNAM account balance depleted"
                elif resp.status_code == 401:
                    result.error = "Invalid OpenCNAM credentials"
                else:
                    result.metadata["status_code"] = resp.status_code
        except Exception as e:
            result.error = str(e)

        return result
