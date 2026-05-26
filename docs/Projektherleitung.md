# Projektherleitung — PHANTOM OSINT Investigation Platform

**Version:** 1.0.0  
**Datum:** Mai 2026  
**Autor:** Tobias Heiko Buss

---

## 1. Ausgangssituation und Problemstellung

### 1.1 Was ist OSINT?

**OSINT** (Open Source Intelligence) bezeichnet die systematische Sammlung und Analyse von Informationen aus öffentlich zugänglichen Quellen. Dazu gehören:

- Soziale Netzwerke (Instagram, Twitter/X, LinkedIn, Telegram)
- Öffentliche Datenbanken (WHOIS, Shodan, HaveIBeenPwned)
- Telefonverzeichnisse und Carrier-Daten
- DNS- und IP-Routing-Informationen
- Datenleck-Datenbanken

OSINT wird eingesetzt von:
- Strafverfolgungsbehörden (Vorfeldermittlung)
- IT-Sicherheitsforschern (Threat Intelligence, Red Teaming)
- Journalisten (investigative Recherche)
- Privatdetektiven
- Unternehmen (Hintergrundprüfungen, Fraud Detection)

### 1.2 Das Problem mit bestehenden Tools

Im Jahr 2024/2025 existieren mehrere OSINT-Tools — jedes hat jedoch signifikante Nachteile:

| Tool | Problem |
|------|---------|
| **Maltego** | Kommerziell (teuer), Cloud-gebunden, Daten verlassen die eigene Infrastruktur |
| **SpiderFoot** | Kein moderner Graph-Editor, veraltete UI, keine aktive Entwicklung |
| **theHarvester** | CLI-only, kein Graph, kein Fall-Management |
| **Recon-ng** | CLI-only, steile Lernkurve, keine Visualisierung |
| **Shodan CLI** | Nur IP-OSINT, kein integriertes Case-Management |
| **IntelTechniques** | Web-basierte Einzeltools, keine Integration, kein Graphen |

**Kernproblem:** Kein bestehendes Tool kombiniert **grafische Graphvisualisierung + automatisierte Transforms + selbst gehostete Infrastruktur + modernes Web-Interface** in einem einzigen Produkt.

### 1.3 Der Investigator-Workflow (Ist-Zustand)

Ein typischer OSINT-Analyst arbeitet heute so:

```
1. Startet mit einer Telefonnummer oder E-Mail-Adresse
2. Öffnet 10+ Browser-Tabs (PhoneInfoga, HIBP, Shodan, WHOIS, ...)
3. Notiert Ergebnisse manuell in einer Textdatei oder Tabelle
4. Verliert den Überblick über Zusammenhänge
5. Kann den Untersuchungsweg nicht dokumentieren/teilen
6. Hat keine zentrale Sicht auf alle gefundenen Verbindungen
```

**Ergebnis:** Erkenntnisse gehen verloren, Zusammenhänge werden übersehen, die Untersuchung ist nicht reproduzierbar.

---

## 2. Projektidee und Lösungsansatz

### 2.1 Kernidee

PHANTOM folgt dem **Maltego-Paradigma** — Entitäten als Knoten, Beziehungen als Kanten, automatisierte Datenabfragen als "Transforms" — aber als:

- **Vollständig Open Source**
- **Self-Hosted** (keine Daten in der Cloud)
- **Modern** (React, FastAPI, Docker)
- **Erweiterbar** (einfaches Transform-Interface)

### 2.2 Namensgebung

**PHANTOM** steht symbolisch für:
- Operieren im Verborgenen (self-hosted, kein Tracking)
- Sichtbarmachen unsichtbarer Verbindungen (Graphvisualisierung)
- Terminal-Ästhetik (Dark Mode, Monospace-Font, Neon-Akzente)

### 2.3 Technische Grundentscheidungen

#### Warum FastAPI (Python)?

Python dominiert das OSINT-Ökosystem. Bibliotheken wie `phonenumbers`, `shodan`, `requests` sind nativ verfügbar. FastAPI ermöglicht echtes async I/O — essenziell für parallele HTTP-Calls zu externen APIs.

#### Warum React + TypeScript?

Komplexe Graph-Interaktionen erfordern reaktives State-Management. TypeScript verhindert Fehler bei der Handhabung von Entitäts-Typen. Vite sorgt für schnelle Entwicklungs-Iteration.

#### Warum Cytoscape.js?

Cytoscape.js ist der De-facto-Standard für Graphvisualisierung im Web. Es unterstützt hunderte Knoten mit flüssiger Performance, hat ausgereifte Layout-Algorithmen und ist vollständig lizenzfrei.

#### Warum PostgreSQL statt SQLite?

OSINT-Fälle können hunderte Knoten und tausende Kanten haben. PostgreSQL bietet bessere Performance bei komplexen JOIN-Abfragen und JSON-Spalten. Außerdem ist es das einzige DBMS, das sowohl async (asyncpg) als auch volle ACID-Compliance bietet.

#### Warum Redis?

Transform-Ausführungen können mehrere Sekunden dauern. Redis ermöglicht Ergebnis-Caching und Rate-Limiting ohne Datenbankbelastung. In Zukunft können Job-Queues (Celery, ARQ) auf Redis aufgebaut werden.

---

## 3. Entwicklungsprozess

### 3.1 Phasenmodell

Das Projekt wurde in 9 aufeinander aufbauende Phasen entwickelt:

```
Phase 1: Infrastructure & Scaffold
  → Docker-Compose-Setup, CI/CD, Grundstruktur
  
Phase 2: Backend Core
  → Alle Datenbankmodelle, API-Endpunkte, Services
  
Phase 3: Frontend Core
  → Graph-Canvas, Sidebars, Timeline, Settings, Export
  
Phase 4: Integration
  → WebSocket-Echtzeit, API-Proxy, End-to-End-Verbindung
  
Phase 5: OSINT Transforms
  → 10 Transforms: 5 Phone + 5 General OSINT
  
Phase 6: Case Management
  → Fallverwaltung, Audit-Trail, Graph-Persistenz
  
Phase 7: Timeline & Export
  → Discovery-Timeline, JSON/CSV/PDF/SVG/PNG-Export
  
Phase 8: Settings & API Mgmt
  → Verschlüsselte API-Keys, Modul-Toggles
  
Phase 9: Testing & Docs
  → 60 automatische Tests, Playwright E2E, vollständige Dokumentation
```

### 3.2 Technische Entscheidungen im Verlauf

| Entscheidung | Begründung |
|-------------|-----------|
| `aiosqlite` für Tests statt PostgreSQL | Schnellere Test-Ausführung, kein DB-Service nötig |
| `respx` für HTTP-Mocking | Verhindert echte API-Calls in Tests |
| `zustand` statt Redux | Weniger Boilerplate, gleiche Leistung für diesen Use-Case |
| ESLint + `react-hooks/exhaustive-deps` | Verhindert subtile React-Hook-Bugs (wurde im QA-Pass gefunden) |
| WebSocket-Ereignisnamen lowercase | Konsistenz mit Backend (`node_added` statt `NODE_ADDED`) |

---

## 4. Abgrenzung und Verantwortung

### 4.1 Legale Nutzung

PHANTOM ist ein **Werkzeug für autorisierte Untersuchungen**. Die Plattform selbst macht keine illegalen Anfragen — sie orchestriert öffentlich zugängliche APIs und Dienste.

**Verantwortung des Nutzers:**
- Einholung aller notwendigen Genehmigungen vor einer Untersuchung
- Einhaltung der Nutzungsbedingungen aller genutzten APIs
- Compliance mit DSGVO, BDSG und anderen anwendbaren Datenschutzgesetzen
- Keine Verwendung für Stalking, Harassment oder andere illegale Aktivitäten

### 4.2 Datenschutz

Da PHANTOM vollständig self-hosted ist, liegen alle Untersuchungsdaten auf der eigenen Infrastruktur. Die Plattform selbst sammelt keine Nutzerdaten und sendet keine Telemetrie.

---

## 5. Zukunftsperspektive

### v1.1 — Geplante Erweiterungen

- Tor/SOCKS5-Proxy-Unterstützung pro Transform
- Sherlock-Integration (Username-Suche auf 300+ Plattformen)
- Authentifizierung (Single-User Login)
- Multi-Node-Selektion im Graph

### v2.0 — Langfristige Vision

- Plugin-System für Community-Transforms
- API-Server-Modus (PHANTOM als Backend für andere Tools)
- Kollaborativer Mehrbenutzer-Modus (optional, lokal)
- Import/Export von Maltego-MTGX-Dateien
