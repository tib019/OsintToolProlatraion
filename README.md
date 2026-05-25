# PHANTOM — OSINT Investigation Platform

[![Version](https://img.shields.io/badge/version-0.1.0--alpha-red?style=for-the-badge)](https://github.com/tib019/phantom-osint-platform)
[![Python](https://img.shields.io/badge/Python-3.11-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://python.org)
[![React](https://img.shields.io/badge/React-18-61DAFB?style=for-the-badge&logo=react&logoColor=black)](https://react.dev)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.111-009688?style=for-the-badge&logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com)
[![Docker](https://img.shields.io/badge/Docker-Compose-2496ED?style=for-the-badge&logo=docker&logoColor=white)](https://docker.com)
[![License](https://img.shields.io/badge/License-Private-gray?style=for-the-badge)](LICENSE)

> **PHANTOM** is a self-hosted, full-stack OSINT investigation platform combining Maltego-style graph investigation with specialized phone number OSINT and general entity reconnaissance. Built for investigators, security researchers, and OSINT analysts.

```
██████╗ ██╗  ██╗ █████╗ ███╗   ██╗████████╗ ██████╗ ███╗   ███╗
██╔══██╗██║  ██║██╔══██╗████╗  ██║╚══██╔══╝██╔═══██╗████╗ ████║
██████╔╝███████║███████║██╔██╗ ██║   ██║   ██║   ██║██╔████╔██║
██╔═══╝ ██╔══██║██╔══██║██║╚██╗██║   ██║   ██║   ██║██║╚██╔╝██║
██║     ██║  ██║██║  ██║██║ ╚████║   ██║   ╚██████╔╝██║ ╚═╝ ██║
╚═╝     ╚═╝  ╚═╝╚═╝  ╚═╝╚═╝  ╚═══╝   ╚═╝    ╚═════╝ ╚═╝     ╚═╝
```

---

## Features

| Category | Capabilities |
|----------|-------------|
| **Graph Investigation** | Cytoscape.js canvas, force/hierarchical/radial layouts, multi-node selection |
| **Phone OSINT** | Carrier detection, platform registration check, CNAM lookup, leak DB check |
| **Entity OSINT** | Username search (300+ platforms), Email OSINT, IP/Domain intel, Google Dorking |
| **Case Management** | Multi-case projects, graph state persistence, markdown notes, audit log |
| **Export** | PNG/SVG/JSON graph export, PDF report generation, CSV entity lists |
| **Infrastructure** | Docker Compose, PostgreSQL, Redis caching, WebSocket real-time updates |

---

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Frontend | React 18 + TypeScript + Vite |
| Graph Engine | Cytoscape.js |
| State Management | Zustand |
| Styling | Tailwind CSS (dark / terminal aesthetic) |
| Backend | Python FastAPI (async) |
| Database | PostgreSQL 16 + SQLAlchemy 2.0 |
| Cache | Redis 7 |
| Containerization | Docker + docker-compose |

---

## Architecture Overview

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

## OSINT Transform Modules

| # | Module | Entity Type | External APIs |
|---|--------|-------------|---------------|
| 1 | PhoneInfoga Scanner | PhoneNumber | OVH, Numverify |
| 2 | Platform Registration Checker | PhoneNumber | WhatsApp, Telegram, Instagram, Amazon, Snapchat, Signal, Viber |
| 3 | Social Media Profile Linker | PhoneNumber → SocialProfile | WhatsApp, Telegram, Facebook |
| 4 | CNAM / Reverse Lookup | PhoneNumber → Person | OpenCNAM, Truecaller |
| 5 | Leak Database Check | PhoneNumber/Email → LeakRecord | HaveIBeenPwned |
| 6 | Username Search | Username → SocialProfile | 300+ platforms (Sherlock-style) |
| 7 | Email OSINT | EmailAddress → SocialProfile | Holehe, Epieos |
| 8 | IP/Domain Intel | IPAddress/Domain | Shodan, WHOIS, GeoDB |
| 9 | Google Dorking | Any Entity | Google (via dork generation) |
| 10 | Social Graph Expansion | SocialProfile | Platform APIs |

---

## Quick Start

### Prerequisites

- Docker 24+ and docker-compose v2
- 4 GB RAM minimum
- API keys (optional but recommended — see `.env.example`)

### Setup

```bash
# 1. Clone the repository
git clone https://github.com/tib019/phantom-osint-platform.git
cd phantom-osint-platform

# 2. Configure environment
cp .env.example .env
# Edit .env with your API keys (all optional)

# 3. Start all services
make up

# 4. Open in browser
open http://localhost:3000
```

### Makefile Commands

```bash
make up       # Start all services (build if needed)
make down     # Stop all services
make build    # Force rebuild all images
make logs     # Follow all service logs
make shell    # Open backend shell
make psql     # Open PostgreSQL shell
make reset    # Wipe database and restart
```

---

## Project Structure

```
phantom/
├── backend/
│   ├── app/
│   │   ├── api/              # FastAPI route handlers
│   │   │   ├── cases.py
│   │   │   ├── graph.py
│   │   │   ├── transforms.py
│   │   │   ├── export.py
│   │   │   └── settings.py
│   │   ├── transforms/       # OSINT transform modules
│   │   │   ├── base.py       # BaseTransform class
│   │   │   ├── phone/
│   │   │   │   ├── phoneinfoga.py
│   │   │   │   ├── platform_checker.py
│   │   │   │   ├── social_linker.py
│   │   │   │   ├── cnam_lookup.py
│   │   │   │   └── leak_check.py
│   │   │   └── general/
│   │   │       ├── username_search.py
│   │   │       ├── email_osint.py
│   │   │       ├── ip_domain_intel.py
│   │   │       ├── google_dorking.py
│   │   │       └── social_graph.py
│   │   ├── models/           # SQLAlchemy ORM models
│   │   ├── schemas/          # Pydantic request/response schemas
│   │   ├── services/         # Business logic layer
│   │   └── core/             # Config, DB, Redis, WebSocket
│   ├── tests/
│   ├── Dockerfile
│   └── requirements.txt
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   │   ├── Graph/        # Cytoscape.js canvas wrapper
│   │   │   ├── Sidebar/      # Left (navigator) + Right (details)
│   │   │   ├── Timeline/     # Bottom discovery timeline
│   │   │   ├── ContextMenu/  # Right-click transform menu
│   │   │   └── Settings/     # API key & module config
│   │   ├── stores/           # Zustand state slices
│   │   ├── hooks/            # Custom React hooks
│   │   └── types/            # TypeScript type definitions
│   ├── Dockerfile
│   └── package.json
├── docker-compose.yml
├── .env.example
├── Makefile
└── README.md
```

---

## Entity Types

| Node Type | Color | Description |
|-----------|-------|-------------|
| `PhoneNumber` | 🟢 Green | E.164 formatted phone numbers |
| `EmailAddress` | 🔵 Blue | Email addresses |
| `Person` | 🟡 Yellow | Real persons / identities |
| `Username` | 🟠 Orange | Online handles / usernames |
| `SocialProfile` | 🟣 Purple | Platform-specific profiles |
| `IPAddress` | 🔴 Red | IPv4/IPv6 addresses |
| `Domain` | ⚪ Gray | Domain names / URLs |
| `Organization` | 🩵 Cyan | Companies / organizations |
| `Location` | 🌍 Teal | Geographic locations |
| `LeakRecord` | ⚫ Dark Red | Data breach records |

---

## API Keys (all optional)

| Service | Used By | Signup |
|---------|---------|--------|
| Numverify | Phone validation | numverify.com |
| Shodan | IP/Domain intel | shodan.io |
| OpenCNAM | CNAM lookup | opencnam.com |
| HaveIBeenPwned | Leak check | haveibeenpwned.com |
| Telegram Bot Token | Telegram profile lookup | t.me/BotFather |

---

## Security & Legal

> **PHANTOM is designed for authorized OSINT investigation, security research, and defensive use cases only.**
> All transforms operate on publicly available data or require explicit API authorization.
> Users are responsible for compliance with applicable laws in their jurisdiction.

- All API keys stored encrypted in PostgreSQL
- No data leaves the self-hosted instance
- Tor/SOCKS5 proxy support per-module for anonymization
- Rate limiting enforced per module

---

## Development Status

See [GitHub Issues](https://github.com/tib019/phantom-osint-platform/issues) and [Project Board](https://github.com/tib019/phantom-osint-platform/projects) for current development status.

| Phase | Status | Target |
|-------|--------|--------|
| Phase 1: Infrastructure & Scaffold | 🟡 In Progress | v0.1.0 |
| Phase 2: Backend Core | ⚪ Planned | v0.2.0 |
| Phase 3: Frontend Core | ⚪ Planned | v0.3.0 |
| Phase 4: Integration | ⚪ Planned | v0.4.0 |
| Phase 5: OSINT Transforms | ⚪ Planned | v0.5.0 |
| Phase 6: Case Management | ⚪ Planned | v0.6.0 |
| Phase 7: Timeline & Export | ⚪ Planned | v0.7.0 |
| Phase 8: Settings & API Mgmt | ⚪ Planned | v0.8.0 |
| Phase 9: Testing & Docs | ⚪ Planned | v1.0.0 |

---

## Author

**Tobias Heiko Buss**
- GitHub: [@tib019](https://github.com/tib019)
- Hamburg, Deutschland

---

## License

Private project. All rights reserved.
