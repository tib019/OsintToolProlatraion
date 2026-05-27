# ADR-003: PostgreSQL + Redis (Dual-Storage-Strategie)

**Status:** Accepted  
**Datum:** 2025

## Kontext

PHANTOM speichert zwei fundamental unterschiedliche Datenarten:

1. **Persistente Daten:** Graph-Zustände, Fälle, Audit-Trail, verschlüsselte API-Keys. Müssen dauerhaft erhalten bleiben, ACID-Garantien erforderlich.

2. **Ephemere Daten:** Transform-Ergebnisse (Cache), Rate-Limit-Counter. Kurzlebig (Minuten bis Stunden), hohe Lese-/Schreibfrequenz, kein Datenverlust-Risiko bei Neustart.

## Entscheidung

Wir verwenden **PostgreSQL 16** für persistente Daten und **Redis 7** für ephemere Daten.

```
Transform-Request
    │
    ├─→ Redis: Rate-Limit-Check (< 1ms)
    │       └─ Abbruch wenn Limit erreicht
    │
    ├─→ Redis: Cache-Check (< 1ms)
    │       └─ Cache-Hit: sofort zurückgeben
    │
    └─→ Externe API (~200-800ms)
            └─→ Redis: Ergebnis cachen (TTL: 1h)
            └─→ PostgreSQL: Audit-Trail schreiben
```

**Warum nicht nur PostgreSQL?**  
Rate-Limit-Counter erfordern atomare Increment-Operationen mit TTL — das ist genau Redis' Kernkompetenz (`INCR` + `EXPIRE`). In PostgreSQL würde das Row-Level-Locking und regelmäßige Cleanup-Jobs erfordern.

**Warum nicht nur Redis?**  
Redis hält Daten im RAM; ein Neustart ohne Persistence-Konfiguration löscht alle Graph-Zustände. Für Case Management und Audit-Trail ist das nicht akzeptabel.

## Konsequenzen

**Positiv:**
- Redis-Operationen < 1ms — Rate-Limiting hat keinen messbaren Latenz-Overhead
- Transform-Caching reduziert externe API-Calls bei wiederholten Anfragen
- PostgreSQL JSONB-Spalten speichern Cytoscape-Graphzustand direkt ohne ORM-Friction

**Negativ:**
- Zwei Storage-Systeme = zwei Failure-Points im Docker Compose
- Redis-Daten bei Ausfall ohne AOF/RDB-Persistence verloren (für Cache akzeptabel)
- Lokale Entwicklung benötigt beide Services aktiv
