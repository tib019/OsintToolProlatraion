# PHANTOM — OSINT Investigation Platform

[![Version](https://img.shields.io/badge/version-1.0.0-brightgreen?style=for-the-badge)](https://github.com/tib019/OsintToolProlatraion)
[![Python](https://img.shields.io/badge/Python-3.11-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://python.org)
[![React](https://img.shields.io/badge/React-18-61DAFB?style=for-the-badge&logo=react&logoColor=black)](https://react.dev)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.111-009688?style=for-the-badge&logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com)
[![Docker](https://img.shields.io/badge/Docker-Compose-2496ED?style=for-the-badge&logo=docker&logoColor=white)](https://docker.com)
[![Tests](https://img.shields.io/badge/Tests-126%20passing-brightgreen?style=for-the-badge)](#)
[![License](https://img.shields.io/badge/License-Private-gray?style=for-the-badge)](LICENSE)

> **PHANTOM** is a self-hosted, full-stack OSINT investigation platform combining Maltego-style graph investigation with automated phone, email, IP/domain and username OSINT. Built for investigators, security researchers, and OSINT analysts.

```
██████╗ ██╗  ██╗ █████╗ ███╗   ██╗████████╗ ██████╗ ███╗   ███╗
██╔══██╗██║  ██║██╔══██╗████╗  ██║╚══██╔══╝██╔═══██╗████╗ ████║
██████╔╝███████║███████║██╔██╗ ██║   ██║   ██║   ██║██╔████╔██║
██╔═══╝ ██╔══██║██╔══██║██║╚██╗██║   ██║   ██║   ██║██║╚██╔╝██║
██║     ██║  ██║██║  ██║██║ ╚████║   ██║   ╚██████╔╝██║ ╚═╝ ██║
╚═╝     ╚═╝  ╚═╝╚═╝  ╚═╝╚═╝  ╚═══╝   ╚═╝    ╚═════╝ ╚═╝     ╚═╝
```

---

## Dokumentation

| Dokument | Beschreibung |
|---------|-------------|
| [Bedienungsanleitung](docs/Bedienungsanleitung.md) | Installation, UI-Überblick, Schritt-für-Schritt-Guide, Transform-Referenz |
| [Lastenheft](docs/Lastenheft.md) | Anforderungsspezifikation, Nutzergruppen, Abnahmekriterien |
| [Pflichtenheft](docs/Pflichtenheft.md) | Technische Spezifikation, Datenbankschema, API-Spec, Architektur |
| [MoSCoW-Analyse](docs/MoSCoW.md) | Must/Should/Could/Won't Have — Prioritätsbewertung |
| [Projektherleitung](docs/Projektherleitung.md) | Problemstellung, Lösungsansatz, Technische Entscheidungen |
| [UML-Dokumentation](docs/UML.md) | 12 Diagramme: Use-Case, Klassen, ERD, Komponenten, Sequenz, Aktivität, Zustand |

---

## Features

| Kategorie | Funktionen |
|----------|------------|
| **Graph Investigation** | Cytoscape.js Canvas, Force/Tree/Radial-Layouts, Rechtsklick-Kontextmenü |
| **Phone OSINT** | Carrier-Erkennung, Plattform-Check (WhatsApp/Telegram/Signal/Instagram/Snapchat), CNAM-Lookup, Leak-Check |
| **Entity OSINT** | Username-Suche, Email-OSINT, IP/Domain-Intel (Shodan, WHOIS, DNS, Geo), Google Dorking |
| **Case Management** | Mehrere Fälle, Graph-Persistenz, Markdown-Notizen, Audit-Trail |
| **Discovery Timeline** | Live-Audit-Log, kollabierbar, Event-Farbkodierung |
| **Settings** | Verschlüsselte API-Keys, Modul-Toggles |
| **Export** | JSON / CSV / PDF / SVG / PNG |
| **Infrastructure** | Docker Compose, PostgreSQL, Redis, WebSocket Echtzeit-Updates |

---

## Tech Stack

| Layer | Technologie |
|-------|------------|
| Frontend | React 18 + TypeScript + Vite |
| Graph Engine | Cytoscape.js |
| State Management | Zustand |
| Styling | Tailwind CSS (Dark Terminal Aesthetic) |
| Backend | Python FastAPI (async) |
| Database | PostgreSQL 16 + SQLAlchemy 2.0 |
| Cache | Redis 7 |
| Containerization | Docker + docker-compose |
| Testing | pytest + respx + Playwright |
| CI/CD | GitHub Actions |

---

## Architektur

```
┌─────────────────────────────────────────────────────┐
│                   PHANTOM Frontend                   │
│  ┌──────────┐ ┌──────────────┐ ┌─────────────────┐  │
│  │  Graph   │ │   Sidebars   │ │    Timeline     │  │
│  │ Canvas   │ │ Left / Right │ │  Bottom Panel   │  │
│  └──────────┘ └──────────────┘ └─────────────────┘  │
└────────────────────────┬────────────────────────────┘
                         │ REST + WebSocket
┌────────────────────────▼────────────────────────────┐
│                   FastAPI Backend                    │
│  ┌─────────────┐ ┌──────────────┐ ┌──────────────┐  │
│  │  Transform  │ │    Case &    │ │   Export     │  │
│  │  Registry   │ │    Graph     │ │   Service    │  │
│  └─────────────┘ └──────────────┘ └──────────────┘  │
└────────────────────────┬────────────────────────────┘
              ┌──────────┴──────────┐
              ▼                     ▼
        PostgreSQL               Redis
        (Graph State,           (Rate Limits,
         Cases, Audit)           Transform Cache)
```

---

## Quick Start

### Voraussetzungen

- Docker 24+ und docker-compose v2
- 4 GB RAM minimum
- API-Keys optional (siehe [Bedienungsanleitung](docs/Bedienungsanleitung.md))

### Setup

```bash
# 1. Repository klonen
git clone https://github.com/tib019/OsintToolProlatraion.git
cd OsintToolProlatraion

# 2. Konfiguration
cp .env.example .env
# .env optional mit API-Keys befüllen

# 3. Starten
make up

# 4. Browser öffnen
open http://localhost:3000
```

### Makefile

```bash
make up       # Alle Services starten
make down     # Alle Services stoppen
make build    # Images neu bauen
make logs     # Live-Logs
make shell    # Backend-Shell
make psql     # PostgreSQL-Shell
make reset    # Datenbank zurücksetzen
```

---

## OSINT-Transforms (10 gesamt)

| # | Transform | Input | Externe APIs |
|---|-----------|-------|-------------|
| 1 | PhoneInfoga Scanner | PhoneNumber | OVH, Numverify |
| 2 | Platform Registration Checker | PhoneNumber | Telegram Bot (opt.) |
| 3 | Social Media Profile Linker | PhoneNumber | WhatsApp, Telegram |
| 4 | CNAM / Reverse Lookup | PhoneNumber | OpenCNAM |
| 5 | Leak Database Check | PhoneNumber / EmailAddress | HaveIBeenPwned |
| 6 | Username Search | Username | Plattform-Checks |
| 7 | Email OSINT | EmailAddress | Plattform-Checks |
| 8 | IP/Domain Intelligence | IPAddress / Domain | Shodan, WHOIS, GeoDB |
| 9 | Google Dorking | Alle Typen | Google (URL-Generierung) |
| 10 | Social Graph Expansion | SocialProfile | Plattform-APIs |

---

## Entitätstypen

| Typ | Farbe | Beschreibung |
|-----|-------|-------------|
| `PhoneNumber` | Grün | E.164-formatierte Telefonnummern |
| `EmailAddress` | Blau | E-Mail-Adressen |
| `Person` | Gelb | Personen / Identitäten |
| `Username` | Orange | Online-Handles |
| `SocialProfile` | Lila | Plattform-spezifische Profile |
| `IPAddress` | Rot | IPv4/IPv6-Adressen |
| `Domain` | Grau | Domainnamen / URLs |
| `Organization` | Cyan | Unternehmen / Organisationen |
| `Location` | Teal | Geografische Orte |
| `LeakRecord` | Dunkelrot | Datenpannen-Einträge |

---

## API-Keys

| Dienst | Verwendet von | Signup |
|--------|-------------|--------|
| Numverify | Phone validation | numverify.com |
| Shodan | IP/Domain intel | shodan.io |
| OpenCNAM | CNAM lookup | opencnam.com |
| HaveIBeenPwned | Leak check | haveibeenpwned.com/API/Key |
| Telegram Bot Token | Telegram lookup | t.me/BotFather |

---

## Tests

```
Backend:   99 Tests (API-Integration + Transform-Unit-Tests mit HTTP-Mocking)
Frontend:  27 Playwright E2E-Tests (Chromium, API-gemockt)
──────────────────────────────────────────────────────
Gesamt:   126 Tests
```

```bash
# Backend-Tests
cd backend && pytest tests/ -v

# Frontend E2E
cd frontend && npx playwright test
```

---

## Sicherheit & Legal

> **PHANTOM ist ausschließlich für autorisierte OSINT-Untersuchungen, Sicherheitsforschung und defensive Anwendungsfälle konzipiert.**
> Nutzer sind für die Rechtskonformität in ihrer Jurisdiktion selbst verantwortlich.

- API-Keys AES-256-verschlüsselt in PostgreSQL
- Keine Daten verlassen die self-hosted Instanz
- Alle Transforms operieren auf öffentlich zugänglichen Daten

---

## Development Status

| Phase | Status | Version |
|-------|--------|---------|
| Phase 1: Infrastructure & Scaffold | ✅ Komplett | v0.1.0 |
| Phase 2: Backend Core | ✅ Komplett | v0.2.0 |
| Phase 3: Frontend Core | ✅ Komplett | v0.3.0 |
| Phase 4: Integration | ✅ Komplett | v0.4.0 |
| Phase 5: OSINT Transforms | ✅ Komplett | v0.5.0 |
| Phase 6: Case Management | ✅ Komplett | v0.6.0 |
| Phase 7: Timeline & Export | ✅ Komplett | v0.7.0 |
| Phase 8: Settings & API Mgmt | ✅ Komplett | v0.8.0 |
| Phase 9: Testing & Docs | ✅ Komplett | v1.0.0 |

---

## Autor

**Tobias Heiko Buss**
- GitHub: [@tib019](https://github.com/tib019)
- Hamburg, Deutschland

---

## Lizenz

Privates Projekt. Alle Rechte vorbehalten.
