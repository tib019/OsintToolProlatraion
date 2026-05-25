# PHANTOM – Projektdokumentation

**Projekttitel:** PHANTOM OSINT Platform  
**Version:** 1.0.0  
**Autor:** tib019  
**Erstellungsdatum:** Mai 2026  
**Letztes Update:** Mai 2026  

---

## Inhaltsverzeichnis

1. [Projektübersicht](#1-projektübersicht)
2. [Anforderungsanalyse](#2-anforderungsanalyse)
3. [Systemarchitektur](#3-systemarchitektur)
4. [Datenbankdesign](#4-datenbankdesign)
5. [Backend-Implementierung](#5-backend-implementierung)
6. [Frontend-Implementierung](#6-frontend-implementierung)
7. [OSINT-Transformationsmodule](#7-osint-transformationsmodule)
8. [WebSocket-Kommunikation](#8-websocket-kommunikation)
9. [Sicherheitskonzept](#9-sicherheitskonzept)
10. [Deployment & DevOps](#10-deployment--devops)
11. [Testing & Qualitätssicherung](#11-testing--qualitätssicherung)
12. [Bekannte Limitierungen](#12-bekannte-limitierungen)
13. [Glossar](#13-glossar)

---

## 1. Projektübersicht

### 1.1 Projektziel

PHANTOM ist eine selbst gehostete, vollständige OSINT-Investigationsplattform (Open Source Intelligence), die Ermittlern ermöglicht, digitale Spuren strukturiert zu erfassen, zu verknüpfen und zu analysieren. Das System ist nach dem Vorbild kommerzieller Tools wie Maltego aufgebaut, jedoch als quelloffene, lokale Lösung konzipiert.

### 1.2 Motivation

Kommerzielle OSINT-Tools sind oft teuer, setzen Cloud-Abhängigkeiten voraus und erlauben keine vollständige Kontrolle über die gespeicherten Ermittlungsdaten. PHANTOM löst dieses Problem durch:

- **Datensouveränität**: Alle Daten verbleiben auf dem eigenen Server
- **Modularität**: Neue Transforms können einfach hinzugefügt werden
- **Kosten**: Open-Source, keine Lizenzgebühren
- **Flexibilität**: Anpassbar an eigene API-Schlüssel und Workflows

### 1.3 Zielgruppe

- OSINT-Ermittler und Sicherheitsanalysten
- Penetrationstester (für Reconnaissance-Phase)
- Journalisten und Rechercheure
- IT-Forensiker

### 1.4 Projektumfang

| Bereich | Umfang |
|---------|--------|
| Backend | FastAPI, Python 3.11, SQLAlchemy 2.0 async |
| Frontend | React 18, TypeScript, Vite, Cytoscape.js |
| Datenbank | PostgreSQL 16, Redis 7 |
| Transforms | 10 OSINT-Module (Telefon, E-Mail, IP, Domain, Username) |
| Deployment | Docker Compose, 4 Services |
| CI/CD | GitHub Actions (Lint, Tests, Docker Build) |

---

## 2. Anforderungsanalyse

### 2.1 Funktionale Anforderungen

#### Fallverwaltung
- **FA-01**: Das System soll Ermittlungsfälle anlegen, bearbeiten und löschen können
- **FA-02**: Jeder Fall soll einen Namen, eine Beschreibung, Tags und Notizen (Markdown) enthalten
- **FA-03**: Fälle sollen mit Timestamps (erstellt/aktualisiert) versehen sein

#### Graph-Visualisierung
- **FA-04**: Das System soll Entities als Nodes im Graph darstellen
- **FA-05**: Beziehungen zwischen Entities sollen als Edges dargestellt werden
- **FA-06**: Der Graph soll interaktiv bedienbar sein (Drag & Drop, Zoom, Pan)
- **FA-07**: Node-Positionen sollen persistent gespeichert werden

#### OSINT-Transforms
- **FA-08**: Transforms sollen per Rechtsklick auf einen Node ausgeführt werden können
- **FA-09**: Das System soll mindestens 10 verschiedene OSINT-Transforms unterstützen
- **FA-10**: Neue Nodes aus Transform-Ergebnissen sollen automatisch im Graph erscheinen
- **FA-11**: Transform-Ergebnisse sollen in Echtzeit via WebSocket geliefert werden

#### Audit & Export
- **FA-12**: Alle Aktionen sollen in einem Audit-Log protokolliert werden
- **FA-13**: Graphen sollen in JSON, CSV und PNG exportierbar sein

#### API-Schlüssel-Verwaltung
- **FA-14**: API-Schlüssel für externe Dienste sollen verschlüsselt gespeichert werden
- **FA-15**: API-Schlüssel sollen über die Einstellungsseite verwaltet werden können

### 2.2 Nicht-funktionale Anforderungen

| ID | Anforderung | Priorität |
|----|-------------|-----------|
| NFA-01 | Transform-Timeout max. 30 Sekunden | Hoch |
| NFA-02 | API-Antwortzeiten < 500ms (außer Transforms) | Mittel |
| NFA-03 | Verschlüsselung aller gespeicherten API-Schlüssel | Hoch |
| NFA-04 | Vollständige Docker-Containerisierung | Hoch |
| NFA-05 | TypeScript strict mode im Frontend | Mittel |
| NFA-06 | CORS-Konfiguration für lokale Entwicklung | Mittel |

### 2.3 Entity-Typen

Das System unterstützt folgende OSINT-Entity-Typen:

| Entity-Typ | Beschreibung | Beispiel |
|------------|--------------|---------|
| PhoneNumber | Telefonnummer (E.164) | +49 123 456789 |
| EmailAddress | E-Mail-Adresse | user@example.com |
| Person | Person mit Name | Max Mustermann |
| Username | Benutzername auf Plattformen | @username |
| SocialProfile | Profil auf Social Media | github.com/user |
| IPAddress | IPv4 oder IPv6 Adresse | 192.168.1.1 |
| Domain | Domainname | example.com |
| Organization | Organisation/Unternehmen | Acme Corp |
| Location | Geografischer Ort | Berlin, Germany |
| LeakRecord | Datenleck-Eintrag | breach@example.com |

---

## 3. Systemarchitektur

### 3.1 Überblick

PHANTOM folgt einer klassischen 3-Schichten-Architektur, erweitert um eine Echtzeit-Kommunikationsschicht:

```
┌─────────────────────────────────────────────┐
│           Browser (React + Vite)            │
│  ┌───────────┐ ┌──────────┐ ┌───────────┐  │
│  │LeftSidebar│ │  Graph   │ │RightSide  │  │
│  │  (Fälle)  │ │ Canvas   │ │  bar      │  │
│  └───────────┘ │(Cytoscp.)│ │(Transforms│  │
│                └──────────┘ └───────────┘  │
│        REST API   ↕     WebSocket ↕         │
└─────────────────────────────────────────────┘
                   ↕ HTTP / WS
┌─────────────────────────────────────────────┐
│              FastAPI Backend                │
│  ┌─────────┐ ┌──────────┐ ┌─────────────┐  │
│  │ API     │ │Transform │ │  WebSocket  │  │
│  │ Router  │ │ Engine   │ │  Manager    │  │
│  └─────────┘ └──────────┘ └─────────────┘  │
│        ↕ SQLAlchemy      ↕ Redis           │
└─────────────────────────────────────────────┘
                   ↕                ↕
         PostgreSQL 16          Redis 7
```

### 3.2 Komponentendiagramm

Siehe [`Doku/component.puml`](component.puml) und [`Doku/component.png`](component.png).

### 3.3 Technologie-Stack

#### Backend
| Technologie | Version | Zweck |
|-------------|---------|-------|
| Python | 3.11 | Laufzeitumgebung |
| FastAPI | 0.111+ | REST API Framework |
| SQLAlchemy | 2.0 | ORM (async) |
| asyncpg | 0.29+ | PostgreSQL async Treiber |
| Alembic | 1.13+ | Datenbankmigrationen |
| httpx | 0.27+ | Async HTTP Client |
| phonenumbers | 8.13+ | Telefonnummern-Parsing |
| cryptography | 42+ | Fernet-Verschlüsselung |
| redis | 5.0+ | Cache & Session Store |

#### Frontend
| Technologie | Version | Zweck |
|-------------|---------|-------|
| React | 18 | UI Framework |
| TypeScript | 5.x | Typsicherheit |
| Vite | 5.x | Build-Tool |
| Cytoscape.js | 3.x | Graph-Visualisierung |
| Zustand | 4.x | State Management |
| Axios | 1.x | HTTP Client |
| Tailwind CSS | 3.x | Styling |

#### Infrastruktur
| Technologie | Version | Zweck |
|-------------|---------|-------|
| Docker | 24+ | Containerisierung |
| Docker Compose | 2.x | Orchestrierung |
| PostgreSQL | 16 | Hauptdatenbank |
| Redis | 7 | Cache & Jobs |
| Nginx | - | Reverse Proxy (optional) |

---

## 4. Datenbankdesign

### 4.1 Entitäten-Relationsdiagramm

```
cases (1) ──────< (N) graph_nodes
cases (1) ──────< (N) graph_edges
cases (1) ──────< (N) audit_logs
graph_nodes (1) ──< (N) graph_edges [source]
graph_nodes (1) ──< (N) graph_edges [target]
```

### 4.2 Tabellenstruktur

#### Tabelle: `cases`

| Spalte | Typ | Beschreibung |
|--------|-----|--------------|
| id | UUID (PK) | Eindeutige Fall-ID |
| name | VARCHAR(255) | Fallname |
| description | TEXT | Beschreibung |
| tags | ARRAY(VARCHAR) | Tags für Kategorisierung |
| notes_md | TEXT | Markdown-Notizen |
| created_at | TIMESTAMP | Erstellungszeitpunkt |
| updated_at | TIMESTAMP | Letzte Änderung |

#### Tabelle: `graph_nodes`

| Spalte | Typ | Beschreibung |
|--------|-----|--------------|
| id | UUID (PK) | Node-ID |
| case_id | UUID (FK) | Zugehöriger Fall |
| entity_type | VARCHAR(50) | Entity-Typ (Enum) |
| value | VARCHAR(1024) | Entity-Wert |
| label | VARCHAR(255) | Anzeigename |
| properties | JSONB | Zusätzliche Eigenschaften |
| pos_x | FLOAT | X-Position im Canvas |
| pos_y | FLOAT | Y-Position im Canvas |
| created_at | TIMESTAMP | Erstellungszeitpunkt |

#### Tabelle: `graph_edges`

| Spalte | Typ | Beschreibung |
|--------|-----|--------------|
| id | UUID (PK) | Edge-ID |
| case_id | UUID (FK) | Zugehöriger Fall |
| source_id | UUID (FK) | Quell-Node |
| target_id | UUID (FK) | Ziel-Node |
| label | VARCHAR(255) | Beschriftung |
| transform_name | VARCHAR(100) | Ursprungs-Transform |
| created_at | TIMESTAMP | Erstellungszeitpunkt |

#### Tabelle: `audit_logs`

| Spalte | Typ | Beschreibung |
|--------|-----|--------------|
| id | UUID (PK) | Log-ID |
| case_id | UUID (FK) | Zugehöriger Fall |
| event_type | VARCHAR(100) | Ereignistyp |
| entity_type | VARCHAR(50) | Betroffener Entity-Typ |
| entity_value | VARCHAR(1024) | Betroffener Entity-Wert |
| transform_name | VARCHAR(100) | Ausgeführter Transform |
| metadata_ | JSONB | Zusätzliche Metadaten |
| created_at | TIMESTAMP | Zeitpunkt |

#### Tabelle: `api_keys`

| Spalte | Typ | Beschreibung |
|--------|-----|--------------|
| id | UUID (PK) | Schlüssel-ID |
| service_name | VARCHAR(100) | Dienst (z.B. "shodan") |
| encrypted_key | TEXT | Fernet-verschlüsselter Key |
| is_active | BOOLEAN | Aktivierungsstatus |
| created_at | TIMESTAMP | Erstellungszeitpunkt |

---

## 5. Backend-Implementierung

### 5.1 Verzeichnisstruktur

```
backend/
├── app/
│   ├── api/               # FastAPI Router
│   │   ├── cases.py       # CRUD Fälle
│   │   ├── graph.py       # Node/Edge Verwaltung
│   │   ├── transforms.py  # Transform-Ausführung
│   │   ├── settings.py    # API-Key Verwaltung
│   │   ├── export.py      # Export-Endpoints
│   │   └── websocket.py   # WebSocket Handler
│   ├── core/
│   │   ├── config.py      # Pydantic Settings
│   │   ├── database.py    # SQLAlchemy Engine
│   │   ├── encryption.py  # Fernet Encryption
│   │   └── websocket_manager.py
│   ├── models/            # SQLAlchemy ORM Models
│   ├── schemas/           # Pydantic Schemas
│   ├── services/          # Business Logic
│   ├── transforms/        # OSINT Module
│   └── main.py
├── tests/
├── alembic/
└── requirements.txt
```

### 5.2 API-Endpunkte

#### Fälle (`/api/cases`)

| Methode | Endpunkt | Beschreibung |
|---------|----------|--------------|
| GET | `/api/cases/` | Alle Fälle auflisten |
| POST | `/api/cases/` | Neuen Fall erstellen |
| GET | `/api/cases/{id}` | Fall abrufen |
| PATCH | `/api/cases/{id}` | Fall aktualisieren |
| DELETE | `/api/cases/{id}` | Fall löschen |
| GET | `/api/cases/{id}/graph` | Graph-State abrufen |
| GET | `/api/cases/{id}/audit` | Audit-Log abrufen |

#### Graph (`/api/graph`)

| Methode | Endpunkt | Beschreibung |
|---------|----------|--------------|
| POST | `/api/graph/{case_id}/nodes` | Node hinzufügen |
| DELETE | `/api/graph/{case_id}/nodes/{node_id}` | Node entfernen |
| POST | `/api/graph/{case_id}/edges` | Edge hinzufügen |
| PATCH | `/api/graph/{case_id}/nodes/{node_id}/position` | Position speichern |

#### Transforms (`/api/transforms`)

| Methode | Endpunkt | Beschreibung |
|---------|----------|--------------|
| GET | `/api/transforms/` | Alle Transforms auflisten |
| POST | `/api/transforms/run` | Transform ausführen |
| GET | `/api/transforms/job/{id}` | Job-Status abrufen |

#### Einstellungen (`/api/settings`)

| Methode | Endpunkt | Beschreibung |
|---------|----------|--------------|
| GET | `/api/settings/api-keys` | API-Schlüssel auflisten |
| POST | `/api/settings/api-keys` | API-Schlüssel hinzufügen |
| DELETE | `/api/settings/api-keys/{id}` | API-Schlüssel löschen |

#### Export (`/api/export`)

| Methode | Endpunkt | Beschreibung |
|---------|----------|--------------|
| GET | `/api/export/{case_id}/json` | Als JSON exportieren |
| GET | `/api/export/{case_id}/csv` | Als CSV exportieren |
| GET | `/api/export/{case_id}/png` | Als PNG exportieren |

### 5.3 Transform-Architektur

Alle Transforms erben von der abstrakten Basisklasse `BaseTransform`:

```python
class BaseTransform(ABC):
    name: str
    description: str
    input_types: list[EntityType]
    output_types: list[EntityType]
    timeout: int = 10
    rate_limit: int = 10

    @abstractmethod
    async def run(self, entity: Entity, api_keys: dict) -> TransformResult: ...

    async def execute(self, entity: Entity, api_keys: dict) -> TransformResult:
        # Wrapper mit asyncio.wait_for (Timeout) + Error Handling
```

Die `execute()`-Methode übernimmt automatisch:
- Timeout-Management via `asyncio.wait_for`
- Zeitmessung (duration_ms)
- Exception-Handling (gibt `TransformResult` mit error-Feld zurück)

### 5.4 Verschlüsselung

API-Schlüssel werden mit **Fernet** (symmetrische Verschlüsselung) gespeichert:

1. Aus `APP_SECRET_KEY` wird via SHA-256 ein 32-Byte-Schlüssel abgeleitet
2. Dieser wird Base64-kodiert und als Fernet-Schlüssel verwendet
3. `encrypt(value)` → verschlüsselter Token (gespeichert in DB)
4. `decrypt(token)` → Klartext (nur zur Laufzeit, für Transform-Ausführung)

---

## 6. Frontend-Implementierung

### 6.1 Verzeichnisstruktur

```
frontend/src/
├── api/
│   ├── client.ts       # Axios-Instanz
│   ├── cases.ts        # Cases API
│   ├── graph.ts        # Graph API
│   └── transforms.ts   # Transforms API
├── components/
│   ├── Graph/
│   │   ├── GraphCanvas.tsx     # Cytoscape.js Canvas
│   │   └── cytoscapeStyles.ts  # Node/Edge Styling
│   ├── Sidebar/
│   │   ├── LeftSidebar.tsx     # Fallliste
│   │   └── RightSidebar.tsx    # Node-Details
│   ├── ContextMenu/
│   │   └── NodeContextMenu.tsx
│   └── TopBar/
│       └── TopBar.tsx
├── hooks/
│   └── useWebSocket.ts   # WebSocket Hook
├── stores/
│   └── graphStore.ts     # Zustand Store
├── types/
│   └── index.ts          # TypeScript Types
├── App.tsx
└── main.tsx
```

### 6.2 State Management

Der Zustand wird zentral im Zustand-Store (`graphStore.ts`) verwaltet:

```typescript
interface GraphStore {
  nodes: GraphNode[]           // Alle aktuellen Nodes
  edges: GraphEdge[]           // Alle aktuellen Edges
  selectedNodeId: string | null
  activeCase: Case | null
  cases: Case[]
  isLoading: boolean
  contextMenu: { x, y, nodeId } | null
}
```

### 6.3 Graph-Visualisierung

Cytoscape.js wird mit einem benutzerdefinierten Stylesheet konfiguriert, das jeden Entity-Typ farblich kodiert:

| Entity-Typ | Farbe |
|------------|-------|
| PhoneNumber | Grün (#22c55e) |
| EmailAddress | Blau (#3b82f6) |
| Person | Gelb (#eab308) |
| Username | Lila (#a855f7) |
| SocialProfile | Pink (#ec4899) |
| IPAddress | Orange (#f97316) |
| Domain | Cyan (#06b6d4) |
| Organization | Indigo (#6366f1) |
| Location | Smaragd (#10b981) |
| LeakRecord | Rot (#ef4444) |

### 6.4 WebSocket-Hook

`useWebSocket.ts` implementiert eine automatisch reconnectende WebSocket-Verbindung:

- Verbindet mit `ws://backend/ws/{case_id}`
- Exponential Backoff bei Verbindungsfehlern (1s → 2s → 4s → ... → 30s)
- Verarbeitet Events: `nodes_added`, `edges_added`, `transform_error`
- Ruft bei Empfang `store.addNode()` / `store.addEdge()` auf

---

## 7. OSINT-Transformationsmodule

### 7.1 Übersicht

| Transform | Input-Typ | Beschreibung | API-Key benötigt |
|-----------|-----------|--------------|------------------|
| PhoneInfoga | PhoneNumber | Carrier, Geo, Line-Typ | Numverify (optional) |
| PlatformChecker | PhoneNumber | Plattform-Registrierung | Telegram Bot (optional) |
| CNAMLookup | PhoneNumber | CNAM-Rückwärtssuche | OpenCNAM |
| LeakCheck | Phone/Email | HaveIBeenPwned Breaches | HIBP API Key |
| SocialProfileLinker | PhoneNumber | WhatsApp/Telegram Profile | — |
| UsernameSearch | Username | 83 Plattformen | — |
| EmailOSINT | EmailAddress | Gravatar, GitHub, Spotify | — |
| IPDomainIntel | IP/Domain | Geo, DNS, Shodan | Shodan (optional) |
| GoogleDorking | Alle Typen | Dork-Queries generieren | — |
| SocialGraphExpansion | Username | GitHub Follower-Netzwerk | — |

### 7.2 Transform-Details

#### PhoneInfoga
Analysiert Telefonnummern mit der `phonenumbers`-Bibliothek:
- E.164-Format-Normalisierung
- Carrier-Erkennung (Netzbetreiber)
- Geografische Zuordnung (Land/Region)
- Leitungstyp (Mobile/Festnetz/VOIP)
- Optional: OVH-API für erweiterte Informationen
- Optional: Numverify für globale Carrier-Daten

#### UsernameSearch
Sherlock-artiger paralleler Check über 83 Plattformen:
- Semaphore mit 30 gleichzeitigen Anfragen
- Verschiedene Fehlererkennung (Statuscode, Fehlertext, URL-Redirect)
- Gibt `SocialProfile`-Entities für jede gefundene Plattform zurück

#### IPDomainIntel
Multi-Source-Analyse für IPs und Domains:
- `ipapi.co` für Geolokalisierung
- Google DNS-over-HTTPS für A/MX/TXT/NS Records
- Vorwärts- und Rückwärts-DNS-Lookup
- Optional: Shodan für offene Ports und CVEs

### 7.3 Plattform-Datenbank

`general/data/platforms.json` enthält 83 Plattformdefinitionen:

```json
{
  "GitHub": {
    "url": "https://github.com/{}",
    "errorType": "status_code",
    "errorCode": 404
  },
  "Instagram": {
    "url": "https://www.instagram.com/{}",
    "errorType": "message",
    "errorMsg": "Sorry, this page isn't available."
  }
}
```

---

## 8. WebSocket-Kommunikation

### 8.1 Verbindungsaufbau

```
Frontend                            Backend
   |                                   |
   |--- WS Connect: /ws/{case_id} ---> |
   |                                   |
   |<--- Connection: Accepted --------|
   |                                   |
   |         [Transform läuft]         |
   |                                   |
   |<--- {type: "nodes_added",        |
   |      payload: [NodeResponse]}    |
   |                                   |
   |--- PING -----------------------> |
   |<--- PONG ------------------------|
```

### 8.2 Event-Typen

| Event-Typ | Payload | Beschreibung |
|-----------|---------|--------------|
| `nodes_added` | `NodeResponse[]` | Neue Nodes aus Transform |
| `edges_added` | `EdgeResponse[]` | Neue Edges aus Transform |
| `transform_error` | `{message: string}` | Transform fehlgeschlagen |
| `transform_complete` | `{job_id, duration_ms}` | Transform abgeschlossen |

### 8.3 Sequenzdiagramm

Siehe [`Doku/sequence.puml`](sequence.puml) und [`Doku/sequence.png`](sequence.png).

---

## 9. Sicherheitskonzept

### 9.1 API-Schlüssel-Sicherheit

- Alle API-Schlüssel werden vor dem Speichern mit **Fernet**-Verschlüsselung gesichert
- Der Verschlüsselungsschlüssel wird aus `APP_SECRET_KEY` via SHA-256 abgeleitet
- Klartext-Schlüssel sind nur zur Laufzeit im Speicher vorhanden
- In der Datenbank sind ausschließlich verschlüsselte Tokens gespeichert

### 9.2 CORS-Konfiguration

```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,  # Konfigurierbar per .env
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

### 9.3 Input-Validierung

- Alle API-Eingaben werden durch **Pydantic v2** validiert
- UUID-Validierung bei allen ID-Parametern
- Entity-Typ-Validierung gegen vordefinierte Enum-Werte
- SQL-Injection-Schutz durch SQLAlchemy ORM (parameterisierte Queries)

### 9.4 Datenbankzugang

- Datenbankverbindungen nur über Docker-internes Netzwerk (`phantom-net`)
- PostgreSQL-Port nicht nach außen exponiert in Produktionskonfiguration
- Umgebungsvariablen für alle Credentials (nie Hardcoded)

### 9.5 Empfehlungen für Produktionsbetrieb

1. `APP_SECRET_KEY` mit mindestens 64 zufälligen Bytes generieren
2. Nginx als Reverse Proxy mit HTTPS/TLS vorschalten
3. Firewall-Regeln für PostgreSQL-Port (5432) setzen
4. Regelmäßige Datenbankbackups einrichten
5. Docker-Images regelmäßig aktualisieren

---

## 10. Deployment & DevOps

### 10.1 Docker-Compose-Konfiguration

Das System besteht aus 4 Docker-Services:

| Service | Image | Port | Abhängigkeit |
|---------|-------|------|--------------|
| `postgres` | postgres:16-alpine | 5432 | — |
| `redis` | redis:7-alpine | 6379 | — |
| `backend` | ./backend | 8000 | postgres, redis |
| `frontend` | ./frontend | 5173 | backend |

### 10.2 Umgebungsvariablen

Konfiguration über `.env` (aus `.env.example` kopieren):

```env
# Pflichtfelder
DATABASE_URL=postgresql+asyncpg://phantom:phantom@postgres:5432/phantom
REDIS_URL=redis://redis:6379/0
APP_SECRET_KEY=<zufälliger 64-Byte-String>

# Optionale API-Keys
NUMVERIFY_API_KEY=
SHODAN_API_KEY=
OPENCNAM_SID=
OPENCNAM_AUTH_TOKEN=
HIBP_API_KEY=
TELEGRAM_BOT_TOKEN=
```

### 10.3 Schnellstart

```bash
# Repository klonen
git clone https://github.com/tib019/OsintToolProlatraion.git
cd OsintToolProlatraion

# Konfiguration
cp .env.example .env
# .env anpassen (APP_SECRET_KEY setzen!)

# System starten
make up

# Oder direkt:
docker compose up -d

# Datenbankmigrationen
make migrate

# Logs anzeigen
make logs
```

### 10.4 Makefile-Targets

| Target | Beschreibung |
|--------|--------------|
| `make up` | System starten (detached) |
| `make down` | System stoppen |
| `make build` | Docker-Images bauen |
| `make logs` | Alle Logs anzeigen |
| `make logs-backend` | Backend-Logs |
| `make test` | Tests ausführen |
| `make lint` | Linting & Type-Check |
| `make migrate` | Datenbankmigrationen ausführen |
| `make reset` | Volumes löschen (Datenverlust!) |
| `make psql` | PostgreSQL Shell öffnen |

### 10.5 CI/CD Pipeline

GitHub Actions führt bei jedem Push auf `main`, `develop` und `claude/**`-Branches aus:

1. **Backend Lint**: `ruff check` + `mypy` Type-Checking
2. **Backend Tests**: pytest mit PostgreSQL und Redis Services
3. **Frontend Type-Check**: `tsc --noEmit`
4. **Docker Build**: `docker compose build` Smoke-Test

---

## 11. Testing & Qualitätssicherung

### 11.1 Backend Tests

```bash
cd backend
pytest tests/ -v --tb=short
```

**Test-Konfiguration** (`tests/conftest.py`):
- Separate Test-Datenbank (`phantom_test`)
- Fixtures für AsyncSession
- Automatisches Schema-Setup per Test

### 11.2 Frontend Type-Check

```bash
cd frontend
npm run type-check  # tsc --noEmit
```

TypeScript ist im Strict-Modus konfiguriert (`"strict": true`).

### 11.3 Code-Qualität

| Tool | Bereich | Konfiguration |
|------|---------|---------------|
| Ruff | Python Linting | `pyproject.toml` |
| mypy | Python Type-Check | `--ignore-missing-imports` |
| TypeScript | Frontend Types | `tsconfig.json` strict mode |

---

## 12. Bekannte Limitierungen

### 12.1 Rate-Limiting

- Externe OSINT-APIs haben eigene Rate-Limits
- Das System implementiert kein globales Rate-Limiting
- Empfehlung: API-Schlüssel für kommerzielle Dienste verwenden

### 12.2 Skalierbarkeit

- Das System ist für einzelne Benutzer / kleine Teams konzipiert
- Keine Multi-User-Authentifizierung in v1.0
- Bei hoher Last sollte ein Nginx-Reverse-Proxy vorgeschaltet werden

### 12.3 PlantUML-Diagramme

- Diagramme wurden mit PlantUML 1.2020.02 gerendert
- Neuere PlantUML-Versionen unterstützen zusätzliche `!theme`-Direktiven

### 12.4 OSINT-Genauigkeit

- Transform-Ergebnisse hängen von der Qualität externer APIs ab
- Einige Transforms (Platform Checker, Social Graph) können durch Anti-Bot-Maßnahmen blockiert werden
- Google Dorking generiert nur Suchanfrage-Links, keine automatische Ausführung

---

## 13. Glossar

| Begriff | Erklärung |
|---------|-----------|
| **OSINT** | Open Source Intelligence – Geheimdienstliche Erkenntnisse aus öffentlich zugänglichen Quellen |
| **Entity** | Eine untersuchte Einheit (Telefonnummer, E-Mail, IP-Adresse etc.) |
| **Transform** | Ein OSINT-Modul, das eine Entity analysiert und neue Entities liefert |
| **Graph** | Visualisierung der Beziehungen zwischen Entities (Nodes + Edges) |
| **Node** | Ein einzelner Knoten im Graph (entspricht einer Entity) |
| **Edge** | Eine Verbindung zwischen zwei Nodes |
| **Case** | Ein Ermittlungsfall, der mehrere Entities und Verbindungen bündelt |
| **Audit-Log** | Protokoll aller Aktionen innerhalb eines Falls |
| **Fernet** | Symmetrisches Verschlüsselungsverfahren (AES-128-CBC + HMAC-SHA256) |
| **WebSocket** | Bidirektionales Protokoll für Echtzeit-Kommunikation |
| **Cytoscape.js** | JavaScript-Bibliothek für interaktive Graph-Visualisierung |
| **Zustand** | Leichtgewichtige State-Management-Bibliothek für React |
| **FastAPI** | Modernes Python Web-Framework mit automatischer OpenAPI-Dokumentation |
| **SQLAlchemy** | Python ORM für relationale Datenbanken |
| **Alembic** | Datenbankmigrations-Tool für SQLAlchemy |
| **asyncpg** | Async PostgreSQL-Treiber für Python |
| **CNAM** | Caller Name – Anrufername-Datenbankdienst |
| **HIBP** | Have I Been Pwned – Datenleck-Überprüfungsdienst |
| **Shodan** | Suchmaschine für mit dem Internet verbundene Geräte |

---

*Erstellt mit PHANTOM v1.0.0 – https://github.com/tib019/OsintToolProlatraion*
