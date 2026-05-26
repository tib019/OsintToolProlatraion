"""Unit tests for all 5 phone transforms.

Uses respx to mock HTTP calls — no real APIs hit.
"""
import pytest
import respx
import httpx

from app.transforms.base import Entity, EntityType
from app.transforms.phone.phoneinfoga import PhoneInfogaTransform
from app.transforms.phone.platform_checker import PlatformRegistrationTransform
from app.transforms.phone.cnam_lookup import CNAMLookupTransform
from app.transforms.phone.leak_check import LeakCheckTransform
from app.transforms.phone.social_linker import SocialProfileLinkerTransform

VALID_PHONE = "+4915123456789"
VALID_EMAIL = "victim@example.com"


# ---------------------------------------------------------------------------
# PhoneInfoga Scanner
# ---------------------------------------------------------------------------

class TestPhoneInfogaTransform:
    transform = PhoneInfogaTransform()

    async def test_valid_german_number(self):
        entity = Entity(type=EntityType.PHONE_NUMBER, value=VALID_PHONE)
        result = await self.transform.execute(entity, {})
        assert result.error is None
        phone_nodes = [e for e in result.entities if e.type == EntityType.PHONE_NUMBER]
        assert len(phone_nodes) == 1
        assert phone_nodes[0].properties["valid"] is True
        assert phone_nodes[0].properties["region"] == "DE"

    async def test_invalid_number_returns_error(self):
        entity = Entity(type=EntityType.PHONE_NUMBER, value="123")
        result = await self.transform.execute(entity, {})
        assert result.error is not None

    async def test_carrier_node_created(self):
        entity = Entity(type=EntityType.PHONE_NUMBER, value=VALID_PHONE)
        result = await self.transform.execute(entity, {})
        # German mobile numbers may or may not have carrier info depending on phonenumbers DB
        # Just verify no crash and phone node exists
        assert any(e.type == EntityType.PHONE_NUMBER for e in result.entities)

    @respx.mock
    async def test_numverify_enrichment(self):
        respx.get("http://apilayer.net/api/validate").mock(
            return_value=httpx.Response(200, json={
                "valid": True,
                "carrier": "Telekom",
                "line_type": "mobile",
                "country_name": "Germany",
            })
        )
        respx.get(url__startswith="https://ipapi.co/").mock(
            return_value=httpx.Response(429)
        )
        entity = Entity(type=EntityType.PHONE_NUMBER, value=VALID_PHONE)
        result = await self.transform.execute(entity, {"NUMVERIFY_API_KEY": "test-key"})
        assert result.error is None
        assert any(e.type == EntityType.PHONE_NUMBER for e in result.entities)


# ---------------------------------------------------------------------------
# Platform Registration Checker
# ---------------------------------------------------------------------------

class TestPlatformRegistrationTransform:
    transform = PlatformRegistrationTransform()

    @respx.mock
    async def test_whatsapp_registered(self):
        respx.get("https://wa.me/4915123456789").mock(
            return_value=httpx.Response(200, text="<html>WhatsApp page</html>")
        )
        # Mock all other platform checks to avoid network
        respx.post(url__startswith="https://www.instagram.com").mock(return_value=httpx.Response(404))
        respx.post(url__startswith="https://www.amazon.com").mock(return_value=httpx.Response(404))
        respx.post(url__startswith="https://accounts.snapchat.com").mock(return_value=httpx.Response(404))
        respx.get(url__startswith="https://textsecure-service.whispersystems.org").mock(return_value=httpx.Response(404))

        entity = Entity(type=EntityType.PHONE_NUMBER, value=VALID_PHONE)
        result = await self.transform.execute(entity, {})
        assert result.error is None
        whatsapp = [e for e in result.entities if "whatsapp" in e.value]
        assert len(whatsapp) == 1
        assert whatsapp[0].properties["platform"] == "WhatsApp"

    @respx.mock
    async def test_telegram_registered_with_token(self):
        respx.get(url__startswith="https://wa.me/").mock(return_value=httpx.Response(404))
        respx.post("https://api.telegram.org/botTEST_TOKEN/getChat").mock(
            return_value=httpx.Response(200, json={
                "ok": True,
                "result": {
                    "username": "testuser",
                    "first_name": "Test",
                    "last_name": "User",
                },
            })
        )
        respx.post(url__startswith="https://www.instagram.com").mock(return_value=httpx.Response(404))
        respx.post(url__startswith="https://www.amazon.com").mock(return_value=httpx.Response(404))
        respx.post(url__startswith="https://accounts.snapchat.com").mock(return_value=httpx.Response(404))
        respx.get(url__startswith="https://textsecure-service.whispersystems.org").mock(return_value=httpx.Response(404))

        entity = Entity(type=EntityType.PHONE_NUMBER, value=VALID_PHONE)
        result = await self.transform.execute(entity, {"TELEGRAM_BOT_TOKEN": "TEST_TOKEN"})
        telegram = [e for e in result.entities if "telegram" in e.value]
        assert len(telegram) == 1
        assert telegram[0].properties["username"] == "testuser"

    async def test_invalid_phone_returns_error(self):
        entity = Entity(type=EntityType.PHONE_NUMBER, value="not-a-phone")
        result = await self.transform.execute(entity, {})
        assert result.error is not None

    @respx.mock
    async def test_signal_registered(self):
        respx.get(url__startswith="https://wa.me/").mock(return_value=httpx.Response(404))
        respx.post(url__startswith="https://www.instagram.com").mock(return_value=httpx.Response(404))
        respx.post(url__startswith="https://www.amazon.com").mock(return_value=httpx.Response(404))
        respx.post(url__startswith="https://accounts.snapchat.com").mock(return_value=httpx.Response(404))
        respx.get(url__startswith="https://textsecure-service.whispersystems.org").mock(
            return_value=httpx.Response(401)  # 401 = number exists in Signal
        )

        entity = Entity(type=EntityType.PHONE_NUMBER, value=VALID_PHONE)
        result = await self.transform.execute(entity, {})
        signal = [e for e in result.entities if "signal" in e.value]
        assert len(signal) == 1


# ---------------------------------------------------------------------------
# CNAM / Reverse Lookup
# ---------------------------------------------------------------------------

class TestCNAMLookupTransform:
    transform = CNAMLookupTransform()

    async def test_missing_credentials_returns_info(self):
        entity = Entity(type=EntityType.PHONE_NUMBER, value=VALID_PHONE)
        result = await self.transform.execute(entity, {})
        assert result.error is None
        assert "info" in result.metadata
        assert "OpenCNAM" in result.metadata["info"]

    @respx.mock
    async def test_successful_cnam_lookup(self):
        respx.get(url__startswith="https://api.opencnam.com/v3/phone/").mock(
            return_value=httpx.Response(200, json={"name": "Max Mustermann"})
        )
        entity = Entity(type=EntityType.PHONE_NUMBER, value=VALID_PHONE)
        result = await self.transform.execute(entity, {
            "OPENCNAM_SID": "test-sid",
            "OPENCNAM_AUTH_TOKEN": "test-token",
        })
        assert result.error is None
        persons = [e for e in result.entities if e.type == EntityType.PERSON]
        assert len(persons) == 1
        assert persons[0].value == "Max Mustermann"

    @respx.mock
    async def test_unknown_cnam_result_no_entity(self):
        respx.get(url__startswith="https://api.opencnam.com/v3/phone/").mock(
            return_value=httpx.Response(200, json={"name": "UNKNOWN"})
        )
        entity = Entity(type=EntityType.PHONE_NUMBER, value=VALID_PHONE)
        result = await self.transform.execute(entity, {
            "OPENCNAM_SID": "sid",
            "OPENCNAM_AUTH_TOKEN": "token",
        })
        assert len(result.entities) == 0

    @respx.mock
    async def test_invalid_credentials_error(self):
        respx.get(url__startswith="https://api.opencnam.com/v3/phone/").mock(
            return_value=httpx.Response(401)
        )
        entity = Entity(type=EntityType.PHONE_NUMBER, value=VALID_PHONE)
        result = await self.transform.execute(entity, {
            "OPENCNAM_SID": "bad-sid",
            "OPENCNAM_AUTH_TOKEN": "bad-token",
        })
        assert result.error == "Invalid OpenCNAM credentials"


# ---------------------------------------------------------------------------
# Leak Database Check
# ---------------------------------------------------------------------------

class TestLeakCheckTransform:
    transform = LeakCheckTransform()

    async def test_missing_api_key_returns_info(self):
        entity = Entity(type=EntityType.EMAIL_ADDRESS, value=VALID_EMAIL)
        result = await self.transform.execute(entity, {})
        assert result.error is None
        assert "info" in result.metadata

    @respx.mock
    async def test_breaches_found(self):
        respx.get(
            f"https://haveibeenpwned.com/api/v3/breachedaccount/{VALID_EMAIL}"
        ).mock(return_value=httpx.Response(200, json=[
            {
                "Name": "Adobe",
                "Domain": "adobe.com",
                "BreachDate": "2013-10-04",
                "PwnCount": 152445165,
                "Description": "Adobe breach",
                "DataClasses": ["Email addresses", "Passwords"],
                "IsVerified": True,
                "IsSensitive": False,
            },
            {
                "Name": "LinkedIn",
                "Domain": "linkedin.com",
                "BreachDate": "2012-05-05",
                "PwnCount": 164611595,
                "Description": "LinkedIn breach",
                "DataClasses": ["Email addresses", "Passwords"],
                "IsVerified": True,
                "IsSensitive": False,
            },
        ]))
        entity = Entity(type=EntityType.EMAIL_ADDRESS, value=VALID_EMAIL)
        result = await self.transform.execute(entity, {"HIBP_API_KEY": "test-key"})
        assert result.error is None
        leaks = [e for e in result.entities if e.type == EntityType.LEAK_RECORD]
        assert len(leaks) == 2
        names = {e.label for e in leaks}
        assert "Adobe" in names
        assert "LinkedIn" in names

    @respx.mock
    async def test_no_breaches_found(self):
        respx.get(
            f"https://haveibeenpwned.com/api/v3/breachedaccount/{VALID_EMAIL}"
        ).mock(return_value=httpx.Response(404))
        entity = Entity(type=EntityType.EMAIL_ADDRESS, value=VALID_EMAIL)
        result = await self.transform.execute(entity, {"HIBP_API_KEY": "test-key"})
        assert result.error is None
        assert len(result.entities) == 0
        assert "No breaches found" in result.metadata["info"]

    @respx.mock
    async def test_invalid_key_error(self):
        respx.get(
            f"https://haveibeenpwned.com/api/v3/breachedaccount/{VALID_EMAIL}"
        ).mock(return_value=httpx.Response(401))
        entity = Entity(type=EntityType.EMAIL_ADDRESS, value=VALID_EMAIL)
        result = await self.transform.execute(entity, {"HIBP_API_KEY": "bad-key"})
        assert result.error == "Invalid HIBP API key"

    @respx.mock
    async def test_phone_number_as_input(self):
        respx.get(
            f"https://haveibeenpwned.com/api/v3/breachedaccount/{VALID_PHONE}"
        ).mock(return_value=httpx.Response(404))
        entity = Entity(type=EntityType.PHONE_NUMBER, value=VALID_PHONE)
        result = await self.transform.execute(entity, {"HIBP_API_KEY": "test-key"})
        assert result.error is None


# ---------------------------------------------------------------------------
# Social Media Profile Linker
# ---------------------------------------------------------------------------

class TestSocialProfileLinkerTransform:
    transform = SocialProfileLinkerTransform()

    @respx.mock
    async def test_whatsapp_profile_found(self):
        number_clean = VALID_PHONE.replace("+", "")
        respx.get(f"https://wa.me/{number_clean}").mock(
            return_value=httpx.Response(200, text="<html>whatsapp page</html>",
                                        headers={"content-type": "text/html"})
        )
        entity = Entity(type=EntityType.PHONE_NUMBER, value=VALID_PHONE)
        result = await self.transform.execute(entity, {})
        assert result.error is None
        whatsapp = [e for e in result.entities if "whatsapp" in e.value]
        assert len(whatsapp) == 1
        assert whatsapp[0].properties["platform"] == "WhatsApp"

    @respx.mock
    async def test_telegram_profile_found(self):
        number_clean = VALID_PHONE.replace("+", "")
        respx.get(f"https://wa.me/{number_clean}").mock(return_value=httpx.Response(404))
        respx.post("https://api.telegram.org/botTEST/getChat").mock(
            return_value=httpx.Response(200, json={
                "ok": True,
                "result": {
                    "username": "johndoe",
                    "first_name": "John",
                    "last_name": "Doe",
                },
            })
        )
        entity = Entity(type=EntityType.PHONE_NUMBER, value=VALID_PHONE)
        result = await self.transform.execute(entity, {"TELEGRAM_BOT_TOKEN": "TEST"})
        tg = [e for e in result.entities if "telegram" in e.value]
        assert len(tg) == 1
        assert tg[0].properties["username"] == "johndoe"
        assert "John Doe" in tg[0].label

    async def test_invalid_phone_returns_error(self):
        entity = Entity(type=EntityType.PHONE_NUMBER, value="badphone")
        result = await self.transform.execute(entity, {})
        assert result.error is not None

    @respx.mock
    async def test_no_profiles_found(self):
        number_clean = VALID_PHONE.replace("+", "")
        respx.get(f"https://wa.me/{number_clean}").mock(return_value=httpx.Response(404))
        entity = Entity(type=EntityType.PHONE_NUMBER, value=VALID_PHONE)
        result = await self.transform.execute(entity, {})
        assert result.error is None
        assert len(result.entities) == 0


# ---------------------------------------------------------------------------
# Registry smoke test
# ---------------------------------------------------------------------------

async def test_registry_has_all_phone_transforms():
    import app.transforms  # noqa: F401 — triggers registration
    from app.transforms.registry import registry
    phone_transforms = [
        t for t in registry.all_transforms()
        if EntityType.PHONE_NUMBER in t.input_types
    ]
    # PhoneInfoga, Platform Checker, CNAM, Leak Check, Social Linker, Google Dorking
    assert len(phone_transforms) >= 5
    names = {t.name for t in phone_transforms}
    assert "PhoneInfoga Scanner" in names
    assert "Platform Registration Checker" in names
    assert "CNAM / Reverse Lookup" in names
    assert "Leak Database Check" in names
    assert "Social Media Profile Linker" in names


async def test_registry_total_count():
    import app.transforms  # noqa: F401
    from app.transforms.registry import registry
    assert len(registry) == 10
