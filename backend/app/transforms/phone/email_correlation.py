import httpx
import phonenumbers
from app.transforms.base import BaseTransform, Entity, TransformResult, EntityType


class PhoneEmailCorrelationTransform(BaseTransform):
    """Find email addresses that appear alongside a phone number in breach data.

    This transform does NOT scrape live services or enumerate account-recovery
    flows. It queries an authorized breach-data provider (DeHashed) with the
    operator's own API credentials and correlates email addresses that occur in
    the same leaked records as the input phone number. Without credentials it is
    a no-op, consistent with the other key-gated transforms (CNAM, leak check).
    """

    name = "Phone → Email Correlation"
    description = "Find emails linked to a phone number via breach-data correlation (DeHashed)"
    input_types = [EntityType.PHONE_NUMBER]
    output_types = [EntityType.EMAIL_ADDRESS, EntityType.LEAK_RECORD]
    timeout = 20
    rate_limit = 5

    async def run(self, entity: Entity, api_keys: dict) -> TransformResult:
        result = TransformResult()

        dh_email = api_keys.get("DEHASHED_EMAIL", "")
        dh_key = api_keys.get("DEHASHED_API_KEY", "")

        if not dh_email or not dh_key:
            result.metadata["info"] = (
                "No breach-data provider configured. Set DEHASHED_EMAIL and "
                "DEHASHED_API_KEY to correlate emails from breach records. "
                "There is no reliable public phone->email mapping without such a source."
            )
            return result

        # Normalise to E.164 and prepare query variants (with and without +).
        try:
            raw = entity.value.strip()
            if not raw.startswith("+"):
                raw = "+" + raw
            phone = phonenumbers.parse(raw)
            if not phonenumbers.is_valid_number(phone):
                result.error = "Invalid phone number"
                return result
            e164 = phonenumbers.format_number(phone, phonenumbers.PhoneNumberFormat.E164)
        except Exception:
            result.error = "Could not parse phone number"
            return result

        digits = e164.lstrip("+")

        records = await self._query_dehashed(digits, dh_email, dh_key, result)
        if records is None:
            return result

        # Correlate: collect distinct emails and the breaches they came from.
        seen_emails: dict[str, set[str]] = {}
        for rec in records:
            email = (rec.get("email") or "").strip().lower()
            if not email or "@" not in email:
                continue
            source = (rec.get("database_name") or rec.get("obtained_from") or "unknown").strip()
            seen_emails.setdefault(email, set()).add(source)

        if not seen_emails:
            result.metadata["info"] = "No emails correlated to this number in breach data."
            return result

        for email, sources in seen_emails.items():
            source_list = sorted(s for s in sources if s)
            result.entities.append(Entity(
                type=EntityType.EMAIL_ADDRESS,
                value=email,
                label=email,
                properties={
                    "source": "dehashed",
                    "correlated_from_phone": e164,
                    "breach_sources": source_list,
                    "confidence": "breach-correlation",
                },
            ))
            result.edges.append({
                "from": e164,
                "to": email,
                "label": "associated_email",
            })
            for src in source_list:
                leak_id = f"breach:{src}"
                result.entities.append(Entity(
                    type=EntityType.LEAK_RECORD,
                    value=leak_id,
                    label=src,
                    properties={"breach_name": src, "source": "dehashed"},
                ))
                result.edges.append({"from": email, "to": leak_id, "label": "found_in_breach"})

        result.metadata["correlated_email_count"] = len(seen_emails)
        return result

    async def _query_dehashed(self, digits: str, dh_email: str, dh_key: str,
                              result: TransformResult) -> list[dict] | None:
        """Query DeHashed for records containing the phone number.

        Returns a list of record dicts, or ``None`` if the request failed
        (in which case ``result.error``/``metadata`` is populated).
        """
        try:
            async with httpx.AsyncClient(timeout=15.0) as client:
                resp = await client.get(
                    "https://api.dehashed.com/search",
                    params={"query": f"phone:{digits}", "size": 100},
                    auth=(dh_email, dh_key),
                    headers={
                        "Accept": "application/json",
                        "User-Agent": "PHANTOM-OSINT-Platform",
                    },
                )
                if resp.status_code == 200:
                    data = resp.json()
                    return data.get("entries") or []
                if resp.status_code == 401:
                    result.error = "DeHashed authentication failed — check credentials."
                    return None
                if resp.status_code == 429:
                    result.error = "DeHashed rate limit reached — try again later."
                    return None
                result.error = f"DeHashed returned HTTP {resp.status_code}"
                return None
        except Exception as e:
            result.error = f"DeHashed request failed: {e}"
            return None
