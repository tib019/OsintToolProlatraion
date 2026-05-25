import asyncio
import hashlib
import httpx
import phonenumbers
from app.transforms.base import BaseTransform, Entity, TransformResult, EntityType


class SocialProfileLinkerTransform(BaseTransform):
    name = "Social Media Profile Linker"
    description = "Link phone number to social profiles on WhatsApp, Telegram, Facebook"
    input_types = [EntityType.PHONE_NUMBER]
    output_types = [EntityType.SOCIAL_PROFILE]
    timeout = 20
    rate_limit = 5

    async def run(self, entity: Entity, api_keys: dict) -> TransformResult:
        result = TransformResult()

        try:
            raw = entity.value.strip()
            if not raw.startswith("+"):
                raw = "+" + raw
            phone = phonenumbers.parse(raw)
            e164 = phonenumbers.format_number(phone, phonenumbers.PhoneNumberFormat.E164)
        except Exception:
            result.error = "Could not parse phone number"
            return result

        tasks = [
            self._whatsapp_profile(e164, api_keys),
            self._telegram_profile(e164, api_keys),
        ]
        profiles = await asyncio.gather(*tasks, return_exceptions=True)
        for p in profiles:
            if isinstance(p, Entity):
                result.entities.append(p)
                result.edges.append({"from": e164, "to": p.value, "label": "linked_profile"})

        return result

    async def _whatsapp_profile(self, e164: str, api_keys: dict) -> Entity | None:
        number_clean = e164.replace("+", "")
        try:
            async with httpx.AsyncClient(timeout=10.0, follow_redirects=True) as client:
                resp = await client.get(f"https://wa.me/{number_clean}")
                if resp.status_code == 200 and "wa.me" in str(resp.url):
                    hash_val = hashlib.md5(e164.encode()).hexdigest()
                    return Entity(
                        type=EntityType.SOCIAL_PROFILE,
                        value=f"whatsapp:{e164}",
                        label=f"WhatsApp {e164}",
                        properties={
                            "platform": "WhatsApp",
                            "phone": e164,
                            "profile_url": f"https://wa.me/{number_clean}",
                            "avatar_hash": hash_val,
                        },
                    )
        except Exception:
            pass
        return None

    async def _telegram_profile(self, e164: str, api_keys: dict) -> Entity | None:
        bot_token = api_keys.get("TELEGRAM_BOT_TOKEN", "")
        if not bot_token:
            return None
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                resp = await client.post(
                    f"https://api.telegram.org/bot{bot_token}/getChat",
                    json={"chat_id": e164},
                )
                data = resp.json()
                if data.get("ok") and data.get("result"):
                    r = data["result"]
                    username = r.get("username", "")
                    name = f"{r.get('first_name', '')} {r.get('last_name', '')}".strip()
                    return Entity(
                        type=EntityType.SOCIAL_PROFILE,
                        value=f"telegram:{username or e164}",
                        label=f"Telegram: {name or username or e164}",
                        properties={
                            "platform": "Telegram",
                            "username": username,
                            "display_name": name,
                            "phone": e164,
                            "profile_url": f"https://t.me/{username}" if username else "",
                        },
                    )
        except Exception:
            pass
        return None
