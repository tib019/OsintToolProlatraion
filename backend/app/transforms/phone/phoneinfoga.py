import httpx
import phonenumbers
from phonenumbers import carrier, geocoder, timezone, PhoneNumberType, number_type
from app.transforms.base import BaseTransform, Entity, TransformResult, EntityType


class PhoneInfogaTransform(BaseTransform):
    name = "PhoneInfoga Scanner"
    description = "Carrier detection, country, line type, format validation (E164)"
    input_types = [EntityType.PHONE_NUMBER]
    output_types = [EntityType.PHONE_NUMBER, EntityType.ORGANIZATION, EntityType.LOCATION]
    timeout = 15
    rate_limit = 30

    async def run(self, entity: Entity, api_keys: dict) -> TransformResult:
        result = TransformResult()
        raw = entity.value.strip()

        try:
            # Try with + prefix first, then fallback to regional parsing
            if not raw.startswith("+"):
                raw_e164 = "+" + raw
            else:
                raw_e164 = raw

            try:
                phone = phonenumbers.parse(raw_e164, None)
            except phonenumbers.NumberParseException:
                phone = None

            if phone is None or not phonenumbers.is_valid_number(phone):
                # Try common country regions as fallback
                phone = None
                for region in ["DE", "US", "GB", "FR", "IT", "ES"]:
                    try:
                        p = phonenumbers.parse(raw, region)
                        if phonenumbers.is_valid_number(p):
                            phone = p
                            break
                    except phonenumbers.NumberParseException:
                        continue

            if phone is None or not phonenumbers.is_valid_number(phone):
                result.error = f"Invalid phone number: {raw}"
                return result

            e164 = phonenumbers.format_number(phone, phonenumbers.PhoneNumberFormat.E164)
            national = phonenumbers.format_number(phone, phonenumbers.PhoneNumberFormat.NATIONAL)
            intl_format = phonenumbers.format_number(phone, phonenumbers.PhoneNumberFormat.INTERNATIONAL)
            country_code = phone.country_code
            region_code = phonenumbers.region_code_for_number(phone)
            country_name = geocoder.description_for_number(phone, "en")
            carrier_name = carrier.name_for_number(phone, "en")
            timezones = list(timezone.time_zones_for_number(phone))

            num_type = number_type(phone)
            type_map = {
                PhoneNumberType.MOBILE: "MOBILE",
                PhoneNumberType.FIXED_LINE: "FIXED_LINE",
                PhoneNumberType.FIXED_LINE_OR_MOBILE: "FIXED_LINE_OR_MOBILE",
                PhoneNumberType.VOIP: "VOIP",
                PhoneNumberType.PREMIUM_RATE: "PREMIUM_RATE",
                PhoneNumberType.TOLL_FREE: "TOLL_FREE",
            }
            line_type = type_map.get(num_type, "UNKNOWN")

            # Enriched phone node
            result.entities.append(Entity(
                type=EntityType.PHONE_NUMBER,
                value=e164,
                label=intl_format,
                properties={
                    "e164": e164,
                    "national_format": national,
                    "international_format": intl_format,
                    "country_code": f"+{country_code}",
                    "region": region_code,
                    "country": country_name,
                    "line_type": line_type,
                    "timezones": timezones,
                    "valid": True,
                },
            ))

            # Carrier org node
            if carrier_name:
                result.entities.append(Entity(
                    type=EntityType.ORGANIZATION,
                    value=carrier_name,
                    label=carrier_name,
                    properties={"type": "carrier", "phone_number": e164},
                ))
                result.edges.append({"from": e164, "to": carrier_name, "label": "carrier"})

            # Location node
            if country_name:
                result.entities.append(Entity(
                    type=EntityType.LOCATION,
                    value=country_name,
                    label=country_name,
                    properties={"country": country_name, "region_code": region_code},
                ))
                result.edges.append({"from": e164, "to": country_name, "label": "located_in"})

            # Try OVH API for additional carrier info (best-effort, no key needed)
            try:
                async with httpx.AsyncClient(timeout=5.0) as client:
                    region_lower = (region_code or "").lower()
                    number_digits = e164.replace("+", "")
                    ovh_url = (
                        f"https://api.ovh.com/1.0/telephony/number/detailedZone"
                        f"?country={region_lower}&number={number_digits}"
                    )
                    resp = await client.get(ovh_url)
                    if resp.status_code == 200:
                        ovh_data = resp.json()
                        if isinstance(ovh_data, list) and ovh_data:
                            result.metadata["ovh"] = ovh_data[0]
            except Exception:
                pass

            # Optional Numverify API
            numverify_key = api_keys.get("NUMVERIFY_API_KEY", "")
            if numverify_key:
                try:
                    async with httpx.AsyncClient(timeout=8.0) as client:
                        resp = await client.get(
                            "http://apilayer.net/api/validate",
                            params={"access_key": numverify_key, "number": e164, "format": 1},
                        )
                        if resp.status_code == 200:
                            nv = resp.json()
                            if nv.get("valid"):
                                result.metadata["numverify"] = nv
                                if nv.get("carrier") and not carrier_name:
                                    result.entities.append(Entity(
                                        type=EntityType.ORGANIZATION,
                                        value=nv["carrier"],
                                        label=nv["carrier"],
                                        properties={"type": "carrier", "source": "numverify"},
                                    ))
                except Exception:
                    pass

        except phonenumbers.NumberParseException as e:
            result.error = f"Cannot parse number: {e}"

        return result
