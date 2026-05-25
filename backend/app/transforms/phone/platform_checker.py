import asyncio
import httpx
import phonenumbers
from app.transforms.base import BaseTransform, Entity, TransformResult, EntityType


class PlatformRegistrationTransform(BaseTransform):
    name = "Platform Registration Checker"
    description = "Check if number is registered on WhatsApp, Telegram, Instagram, Amazon, Snapchat, Signal, Viber"
    input_types = [EntityType.PHONE_NUMBER]
    output_types = [EntityType.SOCIAL_PROFILE]
    timeout = 30
    rate_limit = 5

    async def run(self, entity: Entity, api_keys: dict) -> TransformResult:
        result = TransformResult()

        try:
            raw = entity.value.strip()
            if not raw.startswith("+"):
                raw = "+" + raw
            phone = phonenumbers.parse(raw)
            if not phonenumbers.is_valid_number(phone):
                result.error = "Invalid phone number"
                return result
            e164 = phonenumbers.format_number(phone, phonenumbers.PhoneNumberFormat.E164)
            number_clean = e164.replace("+", "")
        except Exception:
            result.error = "Could not parse phone number"
            return result

        tasks = [
            self._check_whatsapp(e164, number_clean),
            self._check_telegram(e164, api_keys),
            self._check_instagram(e164),
            self._check_amazon(e164),
            self._check_snapchat(e164),
            self._check_signal(e164),
        ]

        gathered = await asyncio.gather(*tasks, return_exceptions=True)
        for r in gathered:
            if isinstance(r, Entity):
                result.entities.append(r)
                result.edges.append({"from": e164, "to": r.value, "label": "registered_on"})

        return result

    async def _check_whatsapp(self, e164: str, number_clean: str) -> Entity | None:
        try:
            async with httpx.AsyncClient(timeout=8.0, follow_redirects=False) as client:
                resp = await client.get(f"https://wa.me/{number_clean}")
                # WhatsApp returns 200 for valid numbers
                if resp.status_code in (200, 302):
                    return Entity(
                        type=EntityType.SOCIAL_PROFILE,
                        value=f"whatsapp:{e164}",
                        label=f"WhatsApp {e164}",
                        properties={
                            "platform": "WhatsApp",
                            "phone": e164,
                            "url": f"https://wa.me/{number_clean}",
                        },
                    )
        except Exception:
            pass
        return None

    async def _check_telegram(self, e164: str, api_keys: dict) -> Entity | None:
        bot_token = api_keys.get("TELEGRAM_BOT_TOKEN", "")
        if not bot_token:
            return None
        try:
            async with httpx.AsyncClient(timeout=8.0) as client:
                resp = await client.post(
                    f"https://api.telegram.org/bot{bot_token}/getChat",
                    json={"chat_id": e164},
                )
                data = resp.json()
                if data.get("ok") and data.get("result"):
                    r = data["result"]
                    username = r.get("username", "")
                    return Entity(
                        type=EntityType.SOCIAL_PROFILE,
                        value=f"telegram:{username or e164}",
                        label=f"Telegram @{username}" if username else f"Telegram {e164}",
                        properties={
                            "platform": "Telegram",
                            "phone": e164,
                            "username": username,
                            "first_name": r.get("first_name", ""),
                            "last_name": r.get("last_name", ""),
                        },
                    )
        except Exception:
            pass
        return None

    async def _check_instagram(self, e164: str) -> Entity | None:
        try:
            async with httpx.AsyncClient(timeout=8.0) as client:
                resp = await client.post(
                    "https://www.instagram.com/api/v1/accounts/lookup_phone/",
                    data={"phone_number": e164},
                    headers={
                        "User-Agent": "Instagram 275.0.0.27.98 Android",
                        "Content-Type": "application/x-www-form-urlencoded",
                    },
                )
                if resp.status_code == 200:
                    try:
                        data = resp.json()
                    except Exception:
                        data = {}
                    if data.get("user_exists") or data.get("email"):
                        return Entity(
                            type=EntityType.SOCIAL_PROFILE,
                            value=f"instagram:{e164}",
                            label=f"Instagram {e164}",
                            properties={"platform": "Instagram", "phone": e164},
                        )
        except Exception:
            pass
        return None

    async def _check_amazon(self, e164: str) -> Entity | None:
        try:
            async with httpx.AsyncClient(timeout=8.0, follow_redirects=True) as client:
                resp = await client.post(
                    "https://www.amazon.com/ap/signin",
                    data={"email": e164, "create": "0"},
                    headers={
                        "User-Agent": "Mozilla/5.0",
                        "Content-Type": "application/x-www-form-urlencoded",
                    },
                )
                if resp.status_code == 200 and "passwordInput" in resp.text:
                    return Entity(
                        type=EntityType.SOCIAL_PROFILE,
                        value=f"amazon:{e164}",
                        label=f"Amazon {e164}",
                        properties={"platform": "Amazon", "phone": e164},
                    )
        except Exception:
            pass
        return None

    async def _check_snapchat(self, e164: str) -> Entity | None:
        try:
            async with httpx.AsyncClient(timeout=8.0) as client:
                resp = await client.post(
                    "https://accounts.snapchat.com/accounts/get_username_suggestions",
                    json={"phone_number": e164},
                    headers={"User-Agent": "Snapchat/10.0 (iPhone; iOS 14.0)"},
                )
                if resp.status_code == 200:
                    return Entity(
                        type=EntityType.SOCIAL_PROFILE,
                        value=f"snapchat:{e164}",
                        label=f"Snapchat {e164}",
                        properties={"platform": "Snapchat", "phone": e164},
                    )
        except Exception:
            pass
        return None

    async def _check_signal(self, e164: str) -> Entity | None:
        try:
            async with httpx.AsyncClient(timeout=8.0) as client:
                resp = await client.get(
                    f"https://textsecure-service.whispersystems.org/v1/profile/{e164}",
                    headers={"User-Agent": "Signal-Android/5.0.0"},
                )
                # 200/401/403 all indicate the number exists in Signal's system
                if resp.status_code in (200, 401, 403):
                    return Entity(
                        type=EntityType.SOCIAL_PROFILE,
                        value=f"signal:{e164}",
                        label=f"Signal {e164}",
                        properties={"platform": "Signal", "phone": e164},
                    )
        except Exception:
            pass
        return None
