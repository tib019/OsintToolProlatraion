# Projektscope: PHANTOM OSINT Platform

## Problemstellung

OSINT-Ermittler (Security Researcher, Investigative Journalisten, IT-Forensiker) arbeiten mit zahlreichen isolierten Tools: Maltego (teuer, cloud-gebunden), einzelne Online-Lookup-Services, manuelle API-Calls. Die Korrelation von Ergebnissen zwischen diesen Tools ist zeitaufwändig und fehleranfällig. Kommerzielle Alternativen kosten mehrere hundert Euro pro Monat.

## Lösung

**PHANTOM** ist eine self-hosted, kostenlose Alternative: Ein interaktives Graph-Interface kombiniert mit automatisierten Transforms für die häufigsten OSINT-Use-Cases. Alle Daten bleiben auf der eigenen Infrastruktur.

## In Scope (v1.0)

- 10 OSINT-Transforms: Phone, Email, IP/Domain, Username, Leak-Check, Google Dorking
- Graph-Visualisierung mit Cytoscape.js (Force, Tree, Radial Layouts)
- Case Management (mehrere Fälle, Graphzustand persistent)
- Discovery Timeline (Audit-Trail aller Aktionen)
- Export: JSON, CSV, PDF, SVG, PNG
- Verschlüsselte API-Key-Verwaltung
- Self-Hosted via Docker Compose (PostgreSQL + Redis)
- 60 Tests (48 Backend + 12 E2E Playwright)

## Out of Scope (bewusst ausgeschlossen)

- Realtime-Monitoring / Alerts bei neuen OSINT-Treffern
- ML-basierte Mustererkennung im Graphen
- Multi-User / Team-Collaboration
- Mobile App
- Cloud-Hosting / SaaS-Betrieb
- Scraping-basierte Transforms (ToS-Konformität)
- Paid-only APIs ohne kostenlosen Tier

## Nicht-funktionale Anforderungen

| Anforderung | Zielwert |
|-------------|----------|
| Transform-Response (gecacht) | < 100ms |
| Transform-Response (extern) | < 2s (abhängig von externer API) |
| Graph-Rendering (< 500 Knoten) | < 500ms |
| Gleichzeitige Transforms | 5 concurrent (Rate-Limit-gesteuert) |
| Test-Coverage | ≥ 80% kritische Paths |

## Ethik & Legal

PHANTOM ist ausschließlich für **autorisierte Untersuchungen, Sicherheitsforschung und defensive Anwendungsfälle** konzipiert. Alle Transforms operieren auf öffentlich zugänglichen Daten. Nutzer sind für die Rechtskonformität in ihrer Jurisdiktion selbst verantwortlich.
