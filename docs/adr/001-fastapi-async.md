# ADR-001: FastAPI (async) statt Flask (sync)

**Status:** Accepted  
**Datum:** 2025

## Kontext

PHANTOM führt OSINT-Transforms aus: HTTP-Requests gegen externe APIs (Shodan, HaveIBeenPwned, Numverify, Telegram, WHOIS). Jeder Transform wartet auf externe Antworten. Das Backend muss mehrere Transforms eines Clients parallel verarbeiten können.

Die zwei dominanten Python-Web-Frameworks:
- **Flask:** WSGI (synchron). Jeder Request blockiert einen Worker-Thread.
- **FastAPI:** ASGI (async). Concurrent I/O-Operationen auf demselben Thread.

## Entscheidung

Wir verwenden **FastAPI mit async/await**.

Der Kernunterschied zeigt sich beim gleichzeitigen Ausführen mehrerer Transforms:

```python
# FastAPI: Transforms laufen concurrent, nicht sequenziell
async def run_phone_transforms(phone: str):
    results = await asyncio.gather(
        carrier_lookup(phone),      # ~200ms
        platform_check(phone),      # ~800ms
        leak_check(phone),          # ~400ms
    )
    return results
# Gesamtdauer: ~800ms (max) statt ~1400ms (sum)
```

Zusätzlich liefert FastAPI automatische **OpenAPI/Swagger-Dokumentation** aus den Pydantic-Schemas — relevant für die Transform-API, die auch als öffentliche Schnittstelle für Frontend-Entwicklung genutzt wird.

## Abgewogene Alternativen

**Flask + Celery:** Würde async Tasks ermöglichen, aber erfordert einen Message Broker (Redis, RabbitMQ) und separate Worker-Prozesse. Für diese Anwendung Overkill und erhöhter Infra-Aufwand.

**FastAPI synchron:** Möglich, aber verschenkt den Hauptvorteil.

## Konsequenzen

**Positiv:**
- I/O-bound Transforms (externe API-Calls) laufen concurrent
- Automatische API-Dokumentation via Swagger UI (`/docs`)
- Pydantic-Validierung für alle Request/Response-Modelle
- Moderne Python-Patterns (type hints, dataclasses)

**Negativ:**
- Async-Code erfordert konsequentes `async/await` durch alle Layer
- Synchrone Libraries (z.B. einige OSINT-Tools) müssen in `asyncio.to_thread()` gewrapped werden
- Steilere Lernkurve als Flask für Entwickler ohne async-Erfahrung
