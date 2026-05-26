# Pflichtenheft — PHANTOM OSINT Investigation Platform

**Dokument-Typ:** Pflichtenheft (Technische Spezifikation)
**Version:** 1.0.0
**Datum:** Mai 2026
**Basis:** Lastenheft v1.0.0

---

## 1. Systemarchitektur

### 1.1 Überblick

```
┌─────────────────────────────────────────────────────────────────┐
│                      Browser (Client)                           │
│  React 18 + TypeScript + Vite + Cytoscape.js + Zustand         │
│  Port 3000                                                       │
└───────────────────────────┬─────────────────────────────────────┘
                            │ HTTP/REST + WebSocket
                            │ (Vite Proxy → backend:8000)
┌───────────────────────────▼─────────────────────────────────────┐
│                    FastAPI Backend                               │
│  Python 3.11 · async · uvicorn · Port 8000                      │
│                                                                  │
│  /api/cases/       — Case CRUD                                  │
│  /api/graph/       — Node + Edge CRUD, position update          │
│  /api/transforms/  — Transform registry + async execution        │
│  /api/export/      — JSON / CSV / PDF / SVG / PNG               │
│  /api/settings/    — API key mgmt + module toggles              │
│  /ws/{case_id}     — WebSocket per Case                         │
└──────────────┬───────────────────────┬──────────────────────────┘
               │                       │
┌──────────────▼──────┐   ┌────────────▼───────────────────────┐
│   PostgreSQL 16      │   │           Redis 7                  │
│   Port 5432          │   │           Port 6379               │
│                      │   │                                    │
│  cases               │   │  Rate limiting                     │
│  graph_nodes         │   │  Transform result cache           │
│  graph_edges         │   │  Session data                     │
│  audit_logs          │   └───────────────────────────────────┘
│  api_keys            │
└──────────────────────┘
```

### 1.2 Deployment

```
docker-compose.yml
├── frontend    (nginx + built React app, Port 3000)
├── backend     (uvicorn FastAPI, Port 8000)
├── postgres    (PostgreSQL 16, Port 5432)
└── redis       (Redis 7, Port 6379)
```

---

## 2. Datenbankschema

### 2.1 Tabellen

#### `cases`

| Spalte | Typ | Beschreibung |
|--------|-----|-------------|
| id | UUID (PK) | Eindeutiger Fallbezeichner |
| name | VARCHAR(255) | Fallname |
| description | TEXT | Optionale Beschreibung |
| tags | JSON | Liste von Tags |
| notes_md | TEXT | Markdown-Notizen |
| created_at | TIMESTAMP | Erstellungszeitpunkt |
| updated_at | TIMESTAMP | Letzter Update |

#### `graph_nodes`

| Spalte | Typ | Beschreibung |
|--------|-----|-------------|
| id | UUID (PK) | Eindeutiger Knotenbezeichner |
| case_id | UUID (FK → cases) | Zugehöriger Fall |
| entity_type | VARCHAR(50) | Entitätstyp (PhoneNumber, etc.) |
| value | TEXT | Roher Wert der Entität |
| label | VARCHAR(255) | Anzeigename im Graph |
| properties | JSON | Zusätzliche Metadaten |
| pos_x | FLOAT | X-Position im Canvas |
| pos_y | FLOAT | Y-Position im Canvas |
| created_at | TIMESTAMP | Erstellungszeitpunkt |

#### `graph_edges`

| Spalte | Typ | Beschreibung |
|--------|-----|-------------|
| id | UUID (PK) | Eindeutiger Kantenbezeichner |
| case_id | UUID (FK → cases) | Zugehöriger Fall |
| source_id | UUID (FK → graph_nodes) | Quellknoten |
| target_id | UUID (FK → graph_nodes) | Zielknoten |
| label | VARCHAR(255) | Beziehungsbezeichnung |
| transform_name | VARCHAR(255) | Auslösender Transform |
| created_at | TIMESTAMP | Erstellungszeitpunkt |

#### `audit_logs`

| Spalte | Typ | Beschreibung |
|--------|-----|-------------|
| id | UUID (PK) | Log-Eintrag-ID |
| case_id | UUID (FK → cases) | Zugehöriger Fall |
| event_type | VARCHAR(100) | Ereignistyp (node_added, etc.) |
| entity_type | VARCHAR(50) | Betroffener Entitätstyp |
| entity_value | TEXT | Betroffener Entitätswert |
| transform_name | VARCHAR(255) | Auslösender Transform |
| metadata | JSON | Zusätzliche Event-Daten |
| created_at | TIMESTAMP | Zeitpunkt |

#### `api_keys`

| Spalte | Typ | Beschreibung |
|--------|-----|-------------|
| id | UUID (PK) | Schlüssel-ID |
| service_name | VARCHAR(100) | Dienstname (SHODAN_API_KEY, etc.) |
| encrypted_key | TEXT | AES-256-verschlüsselter Wert |
| is_active | BOOLEAN | Aktivierungsstatus |
| created_at | TIMESTAMP | Erstellungszeitpunkt |
| updated_at | TIMESTAMP | Letzter Update |

---

## 3. API-Spezifikation

### 3.1 Cases API

| Method | Endpoint | Beschreibung |
|--------|----------|-------------|
| GET | `/api/cases/` | Alle Fälle abrufen |
| POST | `/api/cases/` | Neuen Fall erstellen |
| GET | `/api/cases/{id}` | Fall abrufen |
| PATCH | `/api/cases/{id}` | Fall aktualisieren |
| DELETE | `/api/cases/{id}` | Fall löschen |
| GET | `/api/cases/{id}/graph` | Graph-State abrufen |
| GET | `/api/cases/{id}/audit` | Audit-Log abrufen |

### 3.2 Graph API

| Method | Endpoint | Beschreibung |
|--------|----------|-------------|
| POST | `/api/graph/{case_id}/nodes` | Knoten hinzufügen |
| DELETE | `/api/graph/{case_id}/nodes/{node_id}` | Knoten löschen |
| PATCH | `/api/graph/{case_id}/nodes/{node_id}/position` | Position aktualisieren |
| POST | `/api/graph/{case_id}/edges` | Kante hinzufügen |

### 3.3 Transforms API

| Method | Endpoint | Beschreibung |
|--------|----------|-------------|
| GET | `/api/transforms/` | Alle Transforms auflisten |
| GET | `/api/transforms/entity/{type}` | Transforms für Entitätstyp |
| POST | `/api/transforms/run` | Transform starten |
| GET | `/api/transforms/job/{job_id}` | Job-Status abfragen |

### 3.4 Export API

| Method | Endpoint | Beschreibung |
|--------|----------|-------------|
| GET | `/api/export/{case_id}/json` | JSON-Export |
| GET | `/api/export/{case_id}/csv` | CSV-Export |
| GET | `/api/export/{case_id}/pdf` | PDF-Bericht |
| GET | `/api/export/{case_id}/svg` | SVG-Graph |
| GET | `/api/export/{case_id}/png` | PNG-Graph |

### 3.5 Settings API

| Method | Endpoint | Beschreibung |
|--------|----------|-------------|
| GET | `/api/settings/api-keys` | API-Keys auflisten |
| POST | `/api/settings/api-keys` | API-Key setzen |
| DELETE | `/api/settings/api-keys/{service}` | API-Key löschen |
| PATCH | `/api/settings/api-keys/{service}/activate` | Aktivieren |
| PATCH | `/api/settings/api-keys/{service}/deactivate` | Deaktivieren |
| GET | `/api/settings/modules` | Module auflisten |
| PATCH | `/api/settings/modules/{name}` | Modul togglen |

### 3.6 WebSocket

```
ws://host/ws/{case_id}
```

**Events (Server → Client):**

| Event | Payload | Beschreibung |
|-------|---------|-------------|
| `node_added` | NodeResponse | Knoten wurde hinzugefügt |
| `node_removed` | `{node_id}` | Knoten wurde gelöscht |
| `node_moved` | `{node_id, x, y}` | Knotenposition geändert |
| `edge_added` | EdgeResponse | Kante wurde hinzugefügt |
| `transform_completed` | `{job_id, result}` | Transform abgeschlossen |
| `transform_failed` | `{job_id, error}` | Transform fehlgeschlagen |

---

## 4. Transform-System

### 4.1 Architektur

```python
class BaseTransform(ABC):
    name: str
    description: str
    input_types: list[EntityType]
    output_types: list[EntityType]
    timeout: int          # Sekunden
    rate_limit: int       # Requests/Minute

    async def run(entity: Entity, api_keys: dict) -> TransformResult: ...
    async def execute(entity, api_keys) -> TransformResult: ...  # + Timeout-Wrapper
```

### 4.2 Registrierte Transforms

| Transform | Input | Output | API-Key |
|-----------|-------|--------|---------|
| PhoneInfoga Scanner | PhoneNumber | PhoneNumber, Organization, Location | Numverify (opt.) |
| Platform Registration Checker | PhoneNumber | SocialProfile | Telegram Bot (opt.) |
| CNAM / Reverse Lookup | PhoneNumber | Person | OpenCNAM (req.) |
| Leak Database Check | PhoneNumber, EmailAddress | LeakRecord | HIBP (req.) |
| Social Media Profile Linker | PhoneNumber | SocialProfile | Telegram Bot (opt.) |
| Username Search | Username | SocialProfile | — |
| Email OSINT | EmailAddress | SocialProfile | — |
| IP/Domain Intelligence | IPAddress, Domain | Organization, Location, Domain, IPAddress | Shodan (opt.) |
| Google Dorking | All types | — | — |
| Social Graph Expansion | SocialProfile | SocialProfile | — |

### 4.3 Execution-Flow

```
POST /api/transforms/run
  → Validate case + node + transform
  → Create job_id
  → BackgroundTask: execute_transform()
     → retrieve API keys from DB
     → build Entity object
     → transform.execute() [with timeout]
     → persist result nodes + edges
     → broadcast via WebSocket
     → update audit log
  → Return job_id immediately (202)
```

---

## 5. Frontend-Architektur

### 5.1 Komponentenstruktur

```
App
├── TopBar          (Layout-Switcher, Export-Dropdown, Settings-Button)
├── LeftSidebar     (Case-Auswahl, Add-Node-Panel, Entity-Legende)
├── main
│   ├── GraphCanvas (Cytoscape.js, Event-Handler, Layout-API)
│   ├── NodeContextMenu (Transforms, Copy-Value)
│   └── DiscoveryTimeline (Collapsible, Audit-Log, Echtzeit)
├── RightSidebar    (Node-Details, Properties, Transform-Runner)
└── SettingsPanel   (Modal: API-Keys + Module-Toggles)
```

### 5.2 State Management (Zustand)

```typescript
GraphStore {
  nodes, edges, cases, activeCase
  selectedNodeId, contextMenu
  auditLogs, settingsOpen, timelineOpen
  isLoading

  // Actions
  addNode, addEdge, removeNode, selectNode
  setActiveCase, setCases
  setAuditLogs, addAuditLog
  setSettingsOpen, setTimelineOpen
}
```

### 5.3 WebSocket-Integration

Der `useWebSocket`-Hook verbindet sich automatisch auf `/ws/{case_id}` wenn ein Fall aktiviert wird und verarbeitet alle 6 Event-Typen direkt in den Zustand-Store.

---

## 6. Sicherheitsmaßnahmen

| Maßnahme | Implementierung |
|---------|----------------|
| API-Key-Verschlüsselung | `cryptography`-Library, Fernet (AES-128-CBC + HMAC) |
| Keine Key-Exposition | API gibt nur `is_set: bool` zurück, nie den Klartext |
| Input-Validierung | Pydantic v2 auf allen API-Endpunkten |
| SQL-Injection-Schutz | SQLAlchemy ORM + parametrisierte Queries |
| CORS | Nur konfigurierte Origins (`.env`) |

---

## 7. Test-Strategie

| Ebene | Framework | Coverage |
|-------|-----------|---------|
| Unit (Transforms) | pytest + respx (HTTP-Mock) | 23 Tests |
| Integration (API) | pytest + httpx + AsyncClient | 25 Tests |
| E2E (Frontend) | Playwright + Chromium | 12 Tests |
| CI | GitHub Actions | Bei jedem Push auf main/develop |

**Gesamt: 60 Tests**

---

## 8. CI/CD-Pipeline

```yaml
Jobs:
  backend-lint:     ruff check + mypy --ignore-missing-imports
  backend-test:     pytest (PostgreSQL + Redis via Services)
  frontend-check:   eslint + tsc --noEmit
  frontend-e2e:     playwright test (Chromium, API-gemockt)
  docker-build:     docker compose build
```
