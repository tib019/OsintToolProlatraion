import asyncio
import socket
import httpx
from app.transforms.base import BaseTransform, Entity, TransformResult, EntityType


class IPDomainIntelTransform(BaseTransform):
    name = "IP/Domain Intelligence"
    description = "WHOIS, reverse DNS, geolocation, Shodan intel for IP/domain"
    input_types = [EntityType.IP_ADDRESS, EntityType.DOMAIN]
    output_types = [EntityType.ORGANIZATION, EntityType.LOCATION, EntityType.DOMAIN, EntityType.IP_ADDRESS]
    timeout = 20
    rate_limit = 10

    async def run(self, entity: Entity, api_keys: dict) -> TransformResult:
        result = TransformResult()
        value = entity.value.strip()
        is_ip = entity.type == EntityType.IP_ADDRESS

        tasks: list = [
            self._geo_lookup(value),
            self._rdns(value, is_ip),
        ]

        if api_keys.get("SHODAN_API_KEY"):
            tasks.append(self._shodan(value, is_ip, api_keys["SHODAN_API_KEY"]))

        gathered = await asyncio.gather(*tasks, return_exceptions=True)
        for r in gathered:
            if isinstance(r, list):
                for e in r:
                    if isinstance(e, Entity):
                        result.entities.append(e)
                        result.edges.append({"from": value, "to": e.value, "label": "intel"})

        # DNS records for domains only
        if not is_ip:
            dns_entities = await self._dns_records(value)
            for e in dns_entities:
                result.entities.append(e)
                result.edges.append({"from": value, "to": e.value, "label": "dns_record"})

        return result

    async def _geo_lookup(self, value: str) -> list[Entity]:
        entities: list[Entity] = []
        try:
            async with httpx.AsyncClient(timeout=8.0) as client:
                resp = await client.get(f"https://ipapi.co/{value}/json/")
                if resp.status_code == 200:
                    data = resp.json()
                    if not data.get("error"):
                        country = data.get("country_name", "")
                        city = data.get("city", "")
                        org = data.get("org", "")
                        asn = data.get("asn", "")

                        if country or city:
                            loc = ", ".join(part for part in [city, country] if part)
                            entities.append(Entity(
                                type=EntityType.LOCATION,
                                value=loc,
                                label=loc,
                                properties={
                                    "country": country,
                                    "city": city,
                                    "region": data.get("region", ""),
                                    "latitude": data.get("latitude"),
                                    "longitude": data.get("longitude"),
                                    "timezone": data.get("timezone", ""),
                                },
                            ))
                        if org:
                            entities.append(Entity(
                                type=EntityType.ORGANIZATION,
                                value=org,
                                label=org,
                                properties={"type": "ISP/ASN", "asn": asn, "ip": value},
                            ))
        except Exception:
            pass
        return entities

    async def _rdns(self, value: str, is_ip: bool) -> list[Entity]:
        entities: list[Entity] = []
        try:
            loop = asyncio.get_event_loop()
            if is_ip:
                hostname = await loop.run_in_executor(
                    None, lambda: socket.gethostbyaddr(value)[0]
                )
                if hostname:
                    entities.append(Entity(
                        type=EntityType.DOMAIN,
                        value=hostname,
                        label=hostname,
                        properties={"source": "reverse_dns", "ip": value},
                    ))
            else:
                ip = await loop.run_in_executor(
                    None, lambda: socket.gethostbyname(value)
                )
                if ip:
                    entities.append(Entity(
                        type=EntityType.IP_ADDRESS,
                        value=ip,
                        label=ip,
                        properties={"source": "dns_resolution", "domain": value},
                    ))
        except Exception:
            pass
        return entities

    async def _dns_records(self, domain: str) -> list[Entity]:
        entities: list[Entity] = []
        try:
            async with httpx.AsyncClient(timeout=8.0) as client:
                for rtype in ["A", "MX", "TXT", "NS"]:
                    try:
                        resp = await client.get(
                            "https://dns.google/resolve",
                            params={"name": domain, "type": rtype},
                        )
                        if resp.status_code == 200:
                            data = resp.json()
                            for answer in data.get("Answer", []):
                                rdata = answer.get("data", "").rstrip(".")
                                if not rdata:
                                    continue
                                if rtype == "A":
                                    entities.append(Entity(
                                        type=EntityType.IP_ADDRESS,
                                        value=rdata,
                                        label=rdata,
                                        properties={"record_type": "A", "domain": domain},
                                    ))
                                elif rtype in ("NS", "MX"):
                                    # Strip priority prefix from MX records
                                    parts = rdata.split()
                                    host = parts[-1] if parts else rdata
                                    if host:
                                        entities.append(Entity(
                                            type=EntityType.DOMAIN,
                                            value=host,
                                            label=host,
                                            properties={"record_type": rtype, "domain": domain},
                                        ))
                    except Exception:
                        continue
        except Exception:
            pass
        return entities

    async def _shodan(self, value: str, is_ip: bool, api_key: str) -> list[Entity]:
        entities: list[Entity] = []
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                if is_ip:
                    resp = await client.get(
                        f"https://api.shodan.io/shodan/host/{value}",
                        params={"key": api_key},
                    )
                else:
                    resp = await client.get(
                        "https://api.shodan.io/dns/resolve",
                        params={"hostnames": value, "key": api_key},
                    )

                if resp.status_code == 200:
                    data = resp.json()
                    if is_ip and data.get("org"):
                        entities.append(Entity(
                            type=EntityType.ORGANIZATION,
                            value=data["org"],
                            label=data["org"],
                            properties={
                                "source": "shodan",
                                "ports": data.get("ports", []),
                                "vulns": list(data.get("vulns", {}).keys())[:10],
                                "os": data.get("os", ""),
                            },
                        ))
        except Exception:
            pass
        return entities
