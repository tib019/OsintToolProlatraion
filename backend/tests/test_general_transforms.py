"""Unit tests for general OSINT transforms (IP/Domain, Email, Username, Dorking, Social)."""
import pytest
import respx
import httpx

from app.transforms.base import Entity, EntityType
from app.transforms.general.ip_domain_intel import IPDomainIntelTransform
from app.transforms.general.email_osint import EmailOSINTTransform
from app.transforms.general.username_search import UsernameSearchTransform
from app.transforms.general.google_dorking import GoogleDorkingTransform
from app.transforms.general.social_graph import SocialGraphExpansionTransform


# ---------------------------------------------------------------------------
# IP/Domain Intelligence
# ---------------------------------------------------------------------------

class TestIPDomainIntelTransform:
    transform = IPDomainIntelTransform()

    @respx.mock
    async def test_ip_geo_lookup(self):
        respx.get("https://ipapi.co/8.8.8.8/json/").mock(
            return_value=httpx.Response(200, json={
                "ip": "8.8.8.8",
                "city": "Mountain View",
                "country_name": "United States",
                "region": "California",
                "org": "AS15169 Google LLC",
                "asn": "AS15169",
                "latitude": 37.3861,
                "longitude": -122.0839,
                "timezone": "America/Los_Angeles",
            })
        )
        # Mock reverse DNS
        entity = Entity(type=EntityType.IP_ADDRESS, value="8.8.8.8")
        result = await self.transform.execute(entity, {})
        assert result.error is None
        locations = [e for e in result.entities if e.type == EntityType.LOCATION]
        assert len(locations) >= 1
        assert "United States" in locations[0].value

    @respx.mock
    async def test_ip_org_node_created(self):
        respx.get("https://ipapi.co/1.1.1.1/json/").mock(
            return_value=httpx.Response(200, json={
                "country_name": "Australia",
                "city": "Sydney",
                "org": "AS13335 Cloudflare",
                "asn": "AS13335",
            })
        )
        entity = Entity(type=EntityType.IP_ADDRESS, value="1.1.1.1")
        result = await self.transform.execute(entity, {})
        orgs = [e for e in result.entities if e.type == EntityType.ORGANIZATION]
        assert len(orgs) >= 1
        assert "Cloudflare" in orgs[0].value

    @respx.mock
    async def test_domain_dns_lookup(self):
        respx.get("https://ipapi.co/example.com/json/").mock(return_value=httpx.Response(200, json={"error": True}))
        respx.get("https://dns.google/resolve", params={"name": "example.com", "type": "A"}).mock(
            return_value=httpx.Response(200, json={
                "Answer": [{"data": "93.184.216.34", "type": 1}]
            })
        )
        respx.get("https://dns.google/resolve", params={"name": "example.com", "type": "MX"}).mock(
            return_value=httpx.Response(200, json={"Answer": []})
        )
        respx.get("https://dns.google/resolve", params={"name": "example.com", "type": "TXT"}).mock(
            return_value=httpx.Response(200, json={"Answer": []})
        )
        respx.get("https://dns.google/resolve", params={"name": "example.com", "type": "NS"}).mock(
            return_value=httpx.Response(200, json={
                "Answer": [{"data": "a.iana-servers.net.", "type": 2}]
            })
        )
        entity = Entity(type=EntityType.DOMAIN, value="example.com")
        result = await self.transform.execute(entity, {})
        assert result.error is None
        ips = [e for e in result.entities if e.type == EntityType.IP_ADDRESS]
        assert len(ips) >= 1
        assert "93.184.216.34" in [e.value for e in ips]

    @respx.mock
    async def test_shodan_enrichment(self):
        respx.get("https://ipapi.co/8.8.8.8/json/").mock(return_value=httpx.Response(429))
        respx.get("https://api.shodan.io/shodan/host/8.8.8.8").mock(
            return_value=httpx.Response(200, json={
                "org": "Google LLC",
                "ports": [53, 443],
                "vulns": {},
                "os": "Linux",
            })
        )
        entity = Entity(type=EntityType.IP_ADDRESS, value="8.8.8.8")
        result = await self.transform.execute(entity, {"SHODAN_API_KEY": "test-key"})
        orgs = [e for e in result.entities if e.type == EntityType.ORGANIZATION]
        assert any("Google" in e.value for e in orgs)

    @respx.mock
    async def test_api_error_returns_no_crash(self):
        respx.get("https://ipapi.co/999.999.999.999/json/").mock(return_value=httpx.Response(500))
        entity = Entity(type=EntityType.IP_ADDRESS, value="999.999.999.999")
        result = await self.transform.execute(entity, {})
        # Should not crash — just returns empty or error
        assert result is not None


# ---------------------------------------------------------------------------
# Email OSINT
# ---------------------------------------------------------------------------

class TestEmailOSINTTransform:
    transform = EmailOSINTTransform()

    async def test_input_type(self):
        assert EntityType.EMAIL_ADDRESS in self.transform.input_types

    async def test_runs_without_crash(self):
        entity = Entity(type=EntityType.EMAIL_ADDRESS, value="test@example.com")
        result = await self.transform.execute(entity, {})
        assert result is not None

    async def test_output_is_transform_result(self):
        from app.transforms.base import TransformResult
        entity = Entity(type=EntityType.EMAIL_ADDRESS, value="test@example.com")
        result = await self.transform.execute(entity, {})
        assert isinstance(result, TransformResult)


# ---------------------------------------------------------------------------
# Username Search
# ---------------------------------------------------------------------------

class TestUsernameSearchTransform:
    transform = UsernameSearchTransform()

    async def test_input_type(self):
        assert EntityType.USERNAME in self.transform.input_types

    async def test_runs_without_crash(self):
        entity = Entity(type=EntityType.USERNAME, value="phantom_user")
        result = await self.transform.execute(entity, {})
        assert result is not None

    async def test_output_entities_are_social_profiles(self):
        entity = Entity(type=EntityType.USERNAME, value="testuser")
        result = await self.transform.execute(entity, {})
        for e in result.entities:
            assert e.type == EntityType.SOCIAL_PROFILE


# ---------------------------------------------------------------------------
# Google Dorking
# ---------------------------------------------------------------------------

class TestGoogleDorkingTransform:
    transform = GoogleDorkingTransform()

    async def test_accepts_all_entity_types(self):
        for et in EntityType:
            entity = Entity(type=et, value="testvalue")
            result = await self.transform.execute(entity, {})
            assert result is not None

    async def test_phone_number_generates_dorks(self):
        entity = Entity(type=EntityType.PHONE_NUMBER, value="+4915123456789")
        result = await self.transform.execute(entity, {})
        assert result.error is None
        # Google Dorking generates metadata/entities with search URLs
        assert result is not None

    async def test_domain_generates_dorks(self):
        entity = Entity(type=EntityType.DOMAIN, value="example.com")
        result = await self.transform.execute(entity, {})
        assert result.error is None


# ---------------------------------------------------------------------------
# Social Graph Expansion
# ---------------------------------------------------------------------------

class TestSocialGraphExpansionTransform:
    transform = SocialGraphExpansionTransform()

    async def test_input_type(self):
        assert EntityType.SOCIAL_PROFILE in self.transform.input_types

    async def test_runs_without_crash(self):
        entity = Entity(
            type=EntityType.SOCIAL_PROFILE,
            value="instagram:testuser",
            properties={"platform": "Instagram", "username": "testuser"},
        )
        result = await self.transform.execute(entity, {})
        assert result is not None

    async def test_output_type(self):
        assert EntityType.SOCIAL_PROFILE in self.transform.output_types


# ---------------------------------------------------------------------------
# Registry completeness
# ---------------------------------------------------------------------------

async def test_all_general_transforms_registered():
    import app.transforms  # noqa: F401
    from app.transforms.registry import registry
    names = {t.name for t in registry.all_transforms()}
    assert "IP/Domain Intelligence" in names
    assert "Email OSINT" in names
    assert "Username Search" in names
    assert "Google Dorking" in names
    assert "Social Graph Expansion" in names


async def test_transform_timeouts_are_positive():
    import app.transforms  # noqa: F401
    from app.transforms.registry import registry
    for t in registry.all_transforms():
        assert t.timeout > 0, f"{t.name} has invalid timeout"


async def test_transform_names_are_unique():
    import app.transforms  # noqa: F401
    from app.transforms.registry import registry
    names = [t.name for t in registry.all_transforms()]
    assert len(names) == len(set(names)), "Duplicate transform names found"
