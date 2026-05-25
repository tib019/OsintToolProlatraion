#!/usr/bin/env bash
# ============================================================
# PHANTOM — GitHub Project Setup Script
# Creates all labels, milestones, and issues automatically
#
# Usage:
#   export GITHUB_TOKEN=your_personal_access_token
#   export GITHUB_OWNER=tib019
#   export GITHUB_REPO=phantom-osint-platform
#   bash scripts/setup_github_project.sh
# ============================================================

set -euo pipefail

OWNER="${GITHUB_OWNER:?Set GITHUB_OWNER}"
REPO="${GITHUB_REPO:?Set GITHUB_REPO}"
TOKEN="${GITHUB_TOKEN:?Set GITHUB_TOKEN}"
API="https://api.github.com/repos/${OWNER}/${REPO}"
AUTH="Authorization: token ${TOKEN}"
CONTENT="Content-Type: application/json"

gh_post() { curl -s -X POST -H "$AUTH" -H "$CONTENT" "$1" -d "$2"; }
gh_delete() { curl -s -X DELETE -H "$AUTH" "$1"; }
gh_get() { curl -s -H "$AUTH" "$1"; }

echo "🔧 Setting up PHANTOM project management for ${OWNER}/${REPO}"
echo "============================================================"

# ── Step 1: Delete default labels ────────────────────────────
echo ""
echo "📌 Step 1: Cleaning up default labels..."
DEFAULT_LABELS=("bug" "documentation" "duplicate" "enhancement" "good first issue" "help wanted" "invalid" "question" "wontfix")
for label in "${DEFAULT_LABELS[@]}"; do
  ENCODED=$(python3 -c "import urllib.parse; print(urllib.parse.quote('${label}'))")
  gh_delete "${API}/labels/${ENCODED}" > /dev/null 2>&1 && echo "  ✓ Deleted: ${label}" || true
done

# ── Step 2: Create labels ─────────────────────────────────────
echo ""
echo "🏷️  Step 2: Creating labels..."

create_label() {
  local name="$1" color="$2" desc="$3"
  gh_post "${API}/labels" "{\"name\":\"${name}\",\"color\":\"${color}\",\"description\":\"${desc}\"}" > /dev/null
  echo "  ✓ ${name}"
}

# --- Type ---
create_label "type: feature"       "0075ca" "New feature or capability"
create_label "type: bug"           "d73a4a" "Something isn't working"
create_label "type: docs"          "0075ca" "Documentation improvement"
create_label "type: refactor"      "e4e669" "Code refactoring without feature change"
create_label "type: test"          "e4e669" "Tests and quality assurance"
create_label "type: chore"         "cccccc" "Build, CI, maintenance tasks"
create_label "type: security"      "b60205" "Security-related issue or fix"
create_label "type: performance"   "f9d71c" "Performance improvement"

# --- Priority ---
create_label "priority: critical"  "b60205" "Must be fixed immediately — blocks everything"
create_label "priority: high"      "e11d48" "High priority — needed for current milestone"
create_label "priority: medium"    "f97316" "Medium priority — important but not blocking"
create_label "priority: low"       "84cc16" "Nice to have — low urgency"

# --- Component ---
create_label "component: backend"      "7c3aed" "FastAPI backend"
create_label "component: frontend"     "2563eb" "React frontend"
create_label "component: graph"        "0891b2" "Cytoscape.js graph engine"
create_label "component: database"     "059669" "PostgreSQL / SQLAlchemy"
create_label "component: redis"        "dc2626" "Redis caching layer"
create_label "component: docker"       "0369a1" "Docker / docker-compose infrastructure"
create_label "component: transforms"   "7c3aed" "OSINT transform modules"
create_label "component: export"       "6d28d9" "Export functionality"
create_label "component: websocket"    "0891b2" "WebSocket real-time layer"
create_label "component: auth"         "b45309" "Authentication / API key management"

# --- Phase ---
create_label "phase: 1-infrastructure" "1f2937" "Phase 1 — Docker + Project Scaffold"
create_label "phase: 2-backend-core"   "374151" "Phase 2 — Backend DB + Transforms skeleton"
create_label "phase: 3-frontend-core"  "4b5563" "Phase 3 — Graph canvas + node rendering"
create_label "phase: 4-integration"    "6b7280" "Phase 4 — Wire up frontend ↔ backend"
create_label "phase: 5-transforms"     "9ca3af" "Phase 5 — Implement all 10 OSINT transforms"
create_label "phase: 6-case-mgmt"      "d1d5db" "Phase 6 — Case management system"
create_label "phase: 7-timeline"       "e5e7eb" "Phase 7 — Timeline + Export"
create_label "phase: 8-settings"       "f3f4f6" "Phase 8 — Settings + API key management"
create_label "phase: 9-polish"         "f9fafb" "Phase 9 — Testing, docs, polish"

# --- Status ---
create_label "status: blocked"         "b91c1c" "Blocked by dependency or decision"
create_label "status: in-progress"     "d97706" "Currently being worked on"
create_label "status: review-needed"   "7c3aed" "Ready for review"
create_label "status: needs-design"    "ec4899" "Needs design decision before implementation"

echo ""
echo "✅ Labels created."

# ── Step 3: Create milestones ─────────────────────────────────
echo ""
echo "🎯 Step 3: Creating milestones..."

create_milestone() {
  local title="$1" desc="$2" due="$3"
  gh_post "${API}/milestones" "{\"title\":\"${title}\",\"description\":\"${desc}\",\"due_on\":\"${due}T00:00:00Z\"}" > /dev/null
  echo "  ✓ ${title}"
}

create_milestone "v0.1.0 — Infrastructure & Scaffold"  "Docker setup, project structure, CI/CD foundation. All services running with health checks." "2026-06-07"
create_milestone "v0.2.0 — Backend Core"               "Database models, BaseTransform class, FastAPI skeleton, WebSocket layer, REST API endpoints." "2026-06-21"
create_milestone "v0.3.0 — Frontend Core"              "Graph canvas with Cytoscape.js, node rendering, sidebars, context menu scaffold." "2026-07-05"
create_milestone "v0.4.0 — Integration"                "Frontend ↔ Backend fully wired: create node → run transform → result in graph via WebSocket." "2026-07-19"
create_milestone "v0.5.0 — OSINT Transforms"           "All 10 OSINT transform modules implemented with real HTTP calls." "2026-08-16"
create_milestone "v0.6.0 — Case Management"            "Full case CRUD, graph state persistence, notes, tags, audit log." "2026-08-30"
create_milestone "v0.7.0 — Timeline & Export"          "Timeline panel, PNG/SVG/JSON/PDF/CSV export." "2026-09-13"
create_milestone "v0.8.0 — Settings & API Management"  "API key UI, module toggles, rate limit config, proxy/Tor routing." "2026-09-27"
create_milestone "v1.0.0 — Production Ready"           "Full test suite, documentation, security audit, Docker production build." "2026-10-25"

echo ""
echo "✅ Milestones created."

# ── Step 4: Create issues ─────────────────────────────────────
echo ""
echo "📋 Step 4: Creating issues..."

# Get milestone numbers
MS1=$(gh_get "${API}/milestones" | python3 -c "import sys,json; ms=json.load(sys.stdin); print(next(m['number'] for m in ms if 'v0.1.0' in m['title']))")
MS2=$(gh_get "${API}/milestones" | python3 -c "import sys,json; ms=json.load(sys.stdin); print(next(m['number'] for m in ms if 'v0.2.0' in m['title']))")
MS3=$(gh_get "${API}/milestones" | python3 -c "import sys,json; ms=json.load(sys.stdin); print(next(m['number'] for m in ms if 'v0.3.0' in m['title']))")
MS4=$(gh_get "${API}/milestones" | python3 -c "import sys,json; ms=json.load(sys.stdin); print(next(m['number'] for m in ms if 'v0.4.0' in m['title']))")
MS5=$(gh_get "${API}/milestones" | python3 -c "import sys,json; ms=json.load(sys.stdin); print(next(m['number'] for m in ms if 'v0.5.0' in m['title']))")
MS6=$(gh_get "${API}/milestones" | python3 -c "import sys,json; ms=json.load(sys.stdin); print(next(m['number'] for m in ms if 'v0.6.0' in m['title']))")
MS7=$(gh_get "${API}/milestones" | python3 -c "import sys,json; ms=json.load(sys.stdin); print(next(m['number'] for m in ms if 'v0.7.0' in m['title']))")
MS8=$(gh_get "${API}/milestones" | python3 -c "import sys,json; ms=json.load(sys.stdin); print(next(m['number'] for m in ms if 'v0.8.0' in m['title']))")
MS9=$(gh_get "${API}/milestones" | python3 -c "import sys,json; ms=json.load(sys.stdin); print(next(m['number'] for m in ms if 'v1.0.0' in m['title']))")

create_issue() {
  local title="$1" body="$2" labels="$3" milestone="$4"
  gh_post "${API}/issues" "{\"title\":$(echo "$title" | python3 -c 'import sys,json; print(json.dumps(sys.stdin.read().strip()))'),\"body\":$(echo "$body" | python3 -c 'import sys,json; print(json.dumps(sys.stdin.read().strip()))'),\"labels\":${labels},\"milestone\":${milestone}}" > /dev/null
  echo "  ✓ ${title}"
}

# ════════════════════════════════════════════════════════════
# PHASE 1 — Infrastructure & Scaffold
# ════════════════════════════════════════════════════════════

create_issue \
"[INFRA] Set up docker-compose with all four services" \
"## 📋 Overview
Configure the complete \`docker-compose.yml\` with all four PHANTOM services running locally with proper health checks, networking, and persistent volumes.

## 🎯 Acceptance Criteria
- [ ] \`docker compose up\` starts all 4 services: \`backend\`, \`frontend\`, \`postgres\`, \`redis\`
- [ ] All services have working \`healthcheck\` directives
- [ ] PostgreSQL data persists across \`docker compose down\` / \`up\` cycles via named volume
- [ ] Redis data persists via named volume
- [ ] All services communicate via internal \`phantom-net\` bridge network
- [ ] Backend is accessible at \`http://localhost:8000\`
- [ ] Frontend is accessible at \`http://localhost:3000\`
- [ ] \`GET /health\` returns \`{\"status\": \"ok\"}\` from backend

## 🔧 Technical Details

### Services required:
\`\`\`yaml
postgres:16-alpine   → persistent volume, healthcheck via pg_isready
redis:7-alpine       → persistent volume, healthcheck via redis-cli ping
backend (FastAPI)    → depends_on postgres+redis healthy, hot-reload
frontend (Vite)      → depends_on backend, hot-reload with volume mount
\`\`\`

### Network:
- Internal bridge: \`phantom-net\`
- Exposed ports: 3000 (frontend), 8000 (backend)
- Postgres & Redis: internal only (no port exposure in production)

## 📁 Files to create/modify
- \`docker-compose.yml\`
- \`backend/Dockerfile\`
- \`frontend/Dockerfile\` (multi-stage: dev + prod)
- \`.env.example\`

## 🔗 Dependencies
None — this is the first task.

## ⏱️ Estimated effort: 2–4 hours" \
'["type: feature","priority: critical","component: docker","phase: 1-infrastructure"]' \
$MS1

create_issue \
"[INFRA] Create Makefile with developer commands" \
"## 📋 Overview
Create a comprehensive \`Makefile\` that wraps common Docker and development commands so developers can work with single, memorable commands.

## 🎯 Acceptance Criteria
- [ ] \`make up\` builds and starts all services, prints access URLs
- [ ] \`make down\` stops all services cleanly
- [ ] \`make build\` force-rebuilds without cache
- [ ] \`make logs\` follows all logs; \`make logs-backend\` / \`make logs-frontend\` for individual
- [ ] \`make shell\` opens bash in backend container
- [ ] \`make psql\` opens psql in postgres container
- [ ] \`make reset\` wipes volumes and restarts (with warning message)
- [ ] \`make migrate\` runs Alembic migrations
- [ ] \`make test\` runs pytest suite
- [ ] \`make lint\` runs ruff + mypy
- [ ] \`make help\` prints all targets with descriptions
- [ ] \`make status\` shows container health status

## 🔧 Technical Details
- Use \`docker compose\` (v2 syntax) not \`docker-compose\`
- \`.PHONY\` declaration for all non-file targets
- Color-coded output where possible
- Commands should be idempotent

## 📁 Files to create
- \`Makefile\`

## 🔗 Dependencies
- Issue: [INFRA] Set up docker-compose

## ⏱️ Estimated effort: 1–2 hours" \
'["type: feature","priority: high","component: docker","phase: 1-infrastructure"]' \
$MS1

create_issue \
"[INFRA] Configure project scaffold and directory structure" \
"## 📋 Overview
Create the complete project directory scaffold with all required files, configuration, and empty module placeholders so the project builds cleanly before any logic is implemented.

## 🎯 Acceptance Criteria
- [ ] Full directory tree matches spec:
  \`\`\`
  phantom/
  ├── backend/app/{api,transforms/{phone,general},models,schemas,services,core}/
  ├── frontend/src/{components/{Graph,Sidebar,Timeline,ContextMenu,Settings},stores,hooks,types}/
  ├── .github/{ISSUE_TEMPLATE,workflows}/
  └── scripts/
  \`\`\`
- [ ] All Python packages have \`__init__.py\`
- [ ] \`backend/requirements.txt\` with all dependencies pinned
- [ ] \`frontend/package.json\` with React 18, Vite, Cytoscape.js, Zustand, Tailwind
- [ ] \`frontend/tsconfig.json\` with strict TypeScript config
- [ ] \`frontend/tailwind.config.js\` with dark theme token setup
- [ ] \`.gitignore\` covers Python, Node, Docker, IDE files
- [ ] \`.env.example\` documents all environment variables
- [ ] Project builds without errors: \`make build\` exits 0

## 📁 Files to create
- All scaffold files listed above
- \`frontend/vite.config.ts\`
- \`frontend/tailwind.config.js\`
- \`frontend/postcss.config.js\`
- \`frontend/tsconfig.json\`

## 🔗 Dependencies
- Issue: [INFRA] Set up docker-compose

## ⏱️ Estimated effort: 2–3 hours" \
'["type: feature","priority: critical","component: backend","component: frontend","phase: 1-infrastructure"]' \
$MS1

create_issue \
"[INFRA] Set up GitHub Actions CI pipeline" \
"## 📋 Overview
Configure GitHub Actions to automatically lint and test the project on every push and pull request.

## 🎯 Acceptance Criteria
- [ ] CI runs on push to \`main\` and all PRs
- [ ] Backend job: install deps → ruff lint → mypy type-check → pytest
- [ ] Frontend job: npm ci → tsc --noEmit → (optional) vitest
- [ ] Docker build job: verify \`docker compose build\` succeeds
- [ ] Jobs run in parallel where possible
- [ ] Badge in README shows CI status

## 📁 Files to create
- \`.github/workflows/ci.yml\`

## ⏱️ Estimated effort: 1–2 hours" \
'["type: chore","priority: medium","component: docker","phase: 1-infrastructure"]' \
$MS1

# ════════════════════════════════════════════════════════════
# PHASE 2 — Backend Core
# ════════════════════════════════════════════════════════════

create_issue \
"[BACKEND] Implement SQLAlchemy database models" \
"## 📋 Overview
Define all SQLAlchemy ORM models that represent the database schema for PHANTOM. This forms the data layer foundation for all features.

## 🎯 Acceptance Criteria
- [ ] All models defined with proper types, constraints, and relationships
- [ ] Alembic migrations generated and applied successfully
- [ ] Models follow SQLAlchemy 2.0 async patterns
- [ ] All tables created in PostgreSQL after \`make migrate\`

## 📐 Models Required

### \`Case\`
\`\`\`python
id: UUID (PK)
name: str (not null, max 255)
description: str (nullable, text)
tags: list[str] (ARRAY type)
notes_md: str (nullable, text)
created_at: datetime
updated_at: datetime
\`\`\`

### \`GraphState\`
\`\`\`python
id: UUID (PK)
case_id: UUID (FK → Case, cascade delete)
nodes_json: JSON  # list of node objects
edges_json: JSON  # list of edge objects
layout_name: str (default: 'force-directed')
viewport: JSON    # {x, y, zoom}
updated_at: datetime
\`\`\`

### \`GraphNode\` (persisted individually for querying)
\`\`\`python
id: UUID (PK)
case_id: UUID (FK → Case)
entity_type: str (enum)
value: str
label: str
properties: JSON
pos_x: float (nullable)
pos_y: float (nullable)
created_at: datetime
\`\`\`

### \`GraphEdge\`
\`\`\`python
id: UUID (PK)
case_id: UUID (FK → Case)
source_id: UUID (FK → GraphNode)
target_id: UUID (FK → GraphNode)
label: str
transform_name: str
created_at: datetime
\`\`\`

### \`AuditLog\`
\`\`\`python
id: UUID (PK)
case_id: UUID (FK → Case)
event_type: str  # NODE_ADDED, EDGE_ADDED, TRANSFORM_RUN, etc.
entity_type: str (nullable)
entity_value: str (nullable)
transform_name: str (nullable)
metadata: JSON
created_at: datetime
\`\`\`

### \`ApiKey\`
\`\`\`python
id: UUID (PK)
service_name: str (unique)
encrypted_key: str
is_active: bool (default True)
created_at: datetime
updated_at: datetime
\`\`\`

## 📁 Files to create
- \`backend/app/models/case.py\`
- \`backend/app/models/graph.py\`
- \`backend/app/models/audit.py\`
- \`backend/app/models/api_key.py\`
- \`backend/app/models/__init__.py\`
- \`backend/alembic.ini\`
- \`backend/alembic/env.py\`
- \`backend/alembic/versions/001_initial_schema.py\`

## 🔗 Dependencies
- Phase 1 completed

## ⏱️ Estimated effort: 4–6 hours" \
'["type: feature","priority: critical","component: backend","component: database","phase: 2-backend-core"]' \
$MS2

create_issue \
"[BACKEND] Implement Pydantic schemas for all API endpoints" \
"## 📋 Overview
Define Pydantic v2 request/response schemas for all API endpoints. These schemas serve as the API contract between frontend and backend.

## 🎯 Acceptance Criteria
- [ ] Request and response schemas for all entity types
- [ ] All schemas use Pydantic v2 (model_config, field_validator)
- [ ] Schemas match DB models but with proper serialization
- [ ] Auto-generated OpenAPI docs at /docs show all schemas
- [ ] UUID and datetime fields properly serialized

## 📐 Schemas Required

### Entity Schemas
\`\`\`python
class EntityTypeEnum(str, Enum): ...
class NodeCreate(BaseModel): type, value, label, properties, pos_x, pos_y
class NodeResponse(BaseModel): id, type, value, label, properties, position
class EdgeCreate(BaseModel): source_id, target_id, label, transform_name
class EdgeResponse(BaseModel): id, source, target, label, transform
\`\`\`

### Case Schemas
\`\`\`python
class CaseCreate(BaseModel): name, description, tags
class CaseUpdate(BaseModel): name?, description?, tags?, notes_md?
class CaseResponse(BaseModel): id, name, description, tags, created_at, updated_at
\`\`\`

### Transform Schemas
\`\`\`python
class TransformRunRequest(BaseModel): entity_id, transform_name
class TransformRunResponse(BaseModel): job_id, status
class TransformResult(BaseModel): nodes, edges, error, duration_ms
\`\`\`

### Graph Schemas
\`\`\`python
class GraphStateResponse(BaseModel): nodes, edges, layout, viewport
class GraphUpdateEvent(BaseModel): type, payload  # WebSocket event
\`\`\`

## 📁 Files to create
- \`backend/app/schemas/entities.py\`
- \`backend/app/schemas/cases.py\`
- \`backend/app/schemas/transforms.py\`
- \`backend/app/schemas/graph.py\`

## 🔗 Dependencies
- Issue: [BACKEND] Implement SQLAlchemy database models

## ⏱️ Estimated effort: 3–4 hours" \
'["type: feature","priority: high","component: backend","phase: 2-backend-core"]' \
$MS2

create_issue \
"[BACKEND] Implement BaseTransform class and Transform Registry" \
"## 📋 Overview
Implement the core transform architecture: the \`BaseTransform\` abstract base class, the \`TransformRegistry\` for module discovery, and the async execution engine with timeout + rate limiting.

## 🎯 Acceptance Criteria
- [ ] \`BaseTransform\` ABC with \`run(entity, api_keys) -> TransformResult\`
- [ ] \`execute()\` wrapper adds: timeout (default 10s), error catching, duration measurement
- [ ] \`TransformRegistry\` auto-discovers all transform classes via module scanning
- [ ] Registry returns available transforms for a given \`EntityType\`
- [ ] Rate limiter implemented via Redis (token bucket or sliding window)
- [ ] Each transform enforces its \`rate_limit\` (requests/minute) via Redis
- [ ] Transform execution is fully async (no blocking I/O)
- [ ] Results include: \`entities\`, \`edges\`, \`error\`, \`duration_ms\`

## 📐 Architecture

\`\`\`python
class BaseTransform(ABC):
    name: str
    description: str
    input_types: list[EntityType]
    output_types: list[EntityType]
    timeout: int = 10          # seconds
    rate_limit: int = 10       # requests/minute

    @abstractmethod
    async def run(self, entity: Entity, api_keys: dict) -> TransformResult: ...

    async def execute(self, entity: Entity, api_keys: dict) -> TransformResult:
        # Timeout wrapper
        # Error handling
        # Duration measurement
        ...

class TransformRegistry:
    _transforms: dict[str, type[BaseTransform]]

    def register(self, transform_class): ...
    def get_for_entity(self, entity_type: EntityType) -> list[BaseTransform]: ...
    def get_by_name(self, name: str) -> BaseTransform: ...
\`\`\`

## 📁 Files to create/modify
- \`backend/app/transforms/base.py\`
- \`backend/app/transforms/registry.py\`
- \`backend/app/core/rate_limiter.py\`
- \`backend/tests/test_base_transform.py\`

## 🔗 Dependencies
- Issue: [BACKEND] Implement Pydantic schemas

## ⏱️ Estimated effort: 4–6 hours" \
'["type: feature","priority: critical","component: backend","component: transforms","phase: 2-backend-core"]' \
$MS2

create_issue \
"[BACKEND] Implement FastAPI REST API endpoints" \
"## 📋 Overview
Implement all REST API route handlers for cases, graph operations, transform execution, export, and settings.

## 🎯 Acceptance Criteria
All endpoints return proper HTTP status codes and schema-validated responses.

### Cases API (\`/api/cases\`)
- [ ] \`GET /api/cases\` — list all cases
- [ ] \`POST /api/cases\` — create case
- [ ] \`GET /api/cases/{id}\` — get case detail
- [ ] \`PATCH /api/cases/{id}\` — update case (name, description, tags, notes)
- [ ] \`DELETE /api/cases/{id}\` — delete case (cascade graph)
- [ ] \`GET /api/cases/{id}/graph\` — get full graph state
- [ ] \`GET /api/cases/{id}/audit\` — get audit log

### Graph API (\`/api/graph\`)
- [ ] \`POST /api/graph/{case_id}/nodes\` — add node
- [ ] \`DELETE /api/graph/{case_id}/nodes/{node_id}\` — remove node + connected edges
- [ ] \`POST /api/graph/{case_id}/edges\` — add edge
- [ ] \`PATCH /api/graph/{case_id}/nodes/{node_id}/position\` — update node position
- [ ] \`POST /api/graph/{case_id}/layout\` — set layout algorithm

### Transforms API (\`/api/transforms\`)
- [ ] \`GET /api/transforms\` — list all transforms
- [ ] \`GET /api/transforms/{entity_type}\` — get transforms for entity type
- [ ] \`POST /api/transforms/run\` — run transform (async, returns job_id)
- [ ] \`GET /api/transforms/job/{job_id}\` — get job status

### Settings API (\`/api/settings\`)
- [ ] \`GET /api/settings/keys\` — list API key services (masked values)
- [ ] \`POST /api/settings/keys\` — store/update API key (encrypted)
- [ ] \`DELETE /api/settings/keys/{service}\` — remove API key
- [ ] \`GET /api/settings/modules\` — get module enable/disable state
- [ ] \`PATCH /api/settings/modules/{name}\` — toggle module

## 📁 Files to create/modify
- \`backend/app/api/cases.py\`
- \`backend/app/api/graph.py\`
- \`backend/app/api/transforms.py\`
- \`backend/app/api/settings.py\`
- \`backend/app/services/case_service.py\`
- \`backend/app/services/graph_service.py\`

## 🔗 Dependencies
- Issue: [BACKEND] Implement SQLAlchemy database models
- Issue: [BACKEND] Implement Pydantic schemas

## ⏱️ Estimated effort: 8–10 hours" \
'["type: feature","priority: critical","component: backend","phase: 2-backend-core"]' \
$MS2

create_issue \
"[BACKEND] Implement WebSocket server for real-time graph updates" \
"## 📋 Overview
Implement the WebSocket endpoint that pushes real-time graph updates to connected frontend clients when transforms complete and new nodes/edges are added.

## 🎯 Acceptance Criteria
- [ ] \`GET /ws/{case_id}\` WebSocket endpoint accepts connections
- [ ] Each case has its own channel (clients subscribe per case)
- [ ] Events broadcast to all clients in a case on: node added, edge added, transform started, transform completed, transform error
- [ ] WebSocket manager handles: connect, disconnect, broadcast
- [ ] Reconnection handled gracefully (frontend auto-reconnects)
- [ ] Background transform jobs push results via WebSocket on completion

## 📐 Event Protocol
\`\`\`json
// Server → Client events:
{ \"type\": \"NODE_ADDED\",      \"payload\": { ...node } }
{ \"type\": \"EDGE_ADDED\",      \"payload\": { ...edge } }
{ \"type\": \"TRANSFORM_START\", \"payload\": { \"job_id\": \"...\", \"transform\": \"...\", \"entity\": \"...\" } }
{ \"type\": \"TRANSFORM_DONE\",  \"payload\": { \"job_id\": \"...\", \"nodes\": [...], \"edges\": [...] } }
{ \"type\": \"TRANSFORM_ERROR\", \"payload\": { \"job_id\": \"...\", \"error\": \"...\" } }

// Client → Server:
{ \"type\": \"PING\" }
\`\`\`

## 📁 Files to create
- \`backend/app/core/websocket_manager.py\`
- \`backend/app/api/websocket.py\`

## 🔗 Dependencies
- Issue: [BACKEND] Implement FastAPI REST API endpoints

## ⏱️ Estimated effort: 4–6 hours" \
'["type: feature","priority: critical","component: backend","component: websocket","phase: 2-backend-core"]' \
$MS2

# ════════════════════════════════════════════════════════════
# PHASE 3 — Frontend Core
# ════════════════════════════════════════════════════════════

create_issue \
"[FRONTEND] Implement Cytoscape.js graph canvas component" \
"## 📋 Overview
Implement the core graph canvas using Cytoscape.js — the main workspace where all OSINT investigation happens. This is the most critical frontend component.

## 🎯 Acceptance Criteria
- [ ] Cytoscape.js instance initialized in React component (useRef pattern)
- [ ] Nodes rendered with: correct color per entity type, icon, label
- [ ] Edges rendered with transform name as label
- [ ] Force-directed layout active by default
- [ ] Hierarchical layout switchable via toolbar
- [ ] Radial layout switchable via toolbar
- [ ] Zoom/pan works (mouse wheel + drag)
- [ ] Single-click selects node → highlights it, opens details in right sidebar
- [ ] Double-click opens node detail panel
- [ ] Right-click opens context menu with available transforms
- [ ] Multi-select via shift+click or drag-select
- [ ] Drag node to reposition
- [ ] Graph syncs to Zustand store on every change
- [ ] Viewport (zoom + pan position) preserved on re-render

## 📐 Node Color Scheme (dark theme / amber accent)
\`\`\`
PhoneNumber   → #22c55e (green)
EmailAddress  → #3b82f6 (blue)
Person        → #eab308 (yellow)
Username      → #f97316 (orange)
SocialProfile → #a855f7 (purple)
IPAddress     → #ef4444 (red)
Domain        → #6b7280 (gray)
Organization  → #06b6d4 (cyan)
Location      → #14b8a6 (teal)
LeakRecord    → #991b1b (dark red)
\`\`\`

## 📁 Files to create
- \`frontend/src/components/Graph/GraphCanvas.tsx\`
- \`frontend/src/components/Graph/useGraphLayout.ts\`
- \`frontend/src/components/Graph/cytoscapeStyles.ts\`
- \`frontend/src/components/Graph/nodeIcons.ts\`

## 🔗 Dependencies
- Phase 1 + 2 scaffold complete

## ⏱️ Estimated effort: 8–12 hours" \
'["type: feature","priority: critical","component: frontend","component: graph","phase: 3-frontend-core"]' \
$MS3

create_issue \
"[FRONTEND] Implement left sidebar — Case Navigator & Entity Types" \
"## 📋 Overview
Implement the left sidebar with two panels: Case Navigator (list/switch cases, add nodes) and Entity Type palette.

## 🎯 Acceptance Criteria
- [ ] Left sidebar is collapsible (toggle button)
- [ ] **Case Navigator panel:**
  - [ ] List all cases from API
  - [ ] Click to switch active case (loads that case's graph)
  - [ ] \"New Case\" button opens modal
  - [ ] Case shows: name, node count, last modified
  - [ ] Active case highlighted
- [ ] **Add Node panel:**
  - [ ] Dropdown: select entity type
  - [ ] Text input: entity value
  - [ ] \"Add to Graph\" button creates node
  - [ ] Validation: non-empty value required
- [ ] **Entity Type legend:**
  - [ ] Lists all 10 entity types with color dot
  - [ ] Click type filters graph to show only that type

## 📁 Files to create
- \`frontend/src/components/Sidebar/LeftSidebar.tsx\`
- \`frontend/src/components/Sidebar/CaseNavigator.tsx\`
- \`frontend/src/components/Sidebar/AddNodePanel.tsx\`
- \`frontend/src/components/Sidebar/EntityTypeLegend.tsx\`

## ⏱️ Estimated effort: 6–8 hours" \
'["type: feature","priority: high","component: frontend","phase: 3-frontend-core"]' \
$MS3

create_issue \
"[FRONTEND] Implement right sidebar — Node Details & Transform Results" \
"## 📋 Overview
Implement the right sidebar that shows detailed information about the selected node and lists transform results.

## 🎯 Acceptance Criteria
- [ ] Right sidebar shows when a node is selected
- [ ] **Node Detail panel:**
  - [ ] Entity type badge (colored)
  - [ ] Entity value (copyable)
  - [ ] All properties as key/value table
  - [ ] Created timestamp
  - [ ] List of connected nodes
  - [ ] \"Delete Node\" button (with confirmation)
- [ ] **Available Transforms panel:**
  - [ ] Lists all transforms applicable to selected node type
  - [ ] Each transform shows: name, description, estimated duration
  - [ ] \"Run\" button per transform
  - [ ] Running state indicator (spinner)
  - [ ] Result count badge after completion
- [ ] **Transform History panel:**
  - [ ] Previous transform runs on this node
  - [ ] Status (success/error), duration, result count

## 📁 Files to create
- \`frontend/src/components/Sidebar/RightSidebar.tsx\`
- \`frontend/src/components/Sidebar/NodeDetailPanel.tsx\`
- \`frontend/src/components/Sidebar/TransformPanel.tsx\`

## ⏱️ Estimated effort: 6–8 hours" \
'["type: feature","priority: high","component: frontend","phase: 3-frontend-core"]' \
$MS3

create_issue \
"[FRONTEND] Implement right-click context menu for graph nodes" \
"## 📋 Overview
Implement the right-click context menu that appears on graph nodes and offers transform actions.

## 🎯 Acceptance Criteria
- [ ] Right-click on any node opens context menu at cursor position
- [ ] Menu shows all transforms applicable to that node's entity type
- [ ] Menu shows: transform name + brief description
- [ ] Click transform → triggers transform execution
- [ ] Menu closes on: transform click, click outside, Escape key
- [ ] Menu never overflows viewport (repositions if near edge)
- [ ] Visual styling: dark background, amber accent on hover, monospace font
- [ ] \"Copy Value\" option always present
- [ ] \"Delete Node\" option always present (bottom, red)
- [ ] Loading state if transforms list is fetching

## 📁 Files to create
- \`frontend/src/components/ContextMenu/NodeContextMenu.tsx\`
- \`frontend/src/hooks/useContextMenu.ts\`

## ⏱️ Estimated effort: 3–5 hours" \
'["type: feature","priority: high","component: frontend","component: graph","phase: 3-frontend-core"]' \
$MS3

create_issue \
"[FRONTEND] Implement top navigation bar" \
"## 📋 Overview
Implement the top navigation bar with search, layout controls, zoom controls, and settings link.

## 🎯 Acceptance Criteria
- [ ] PHANTOM logo / name on the left
- [ ] **Search bar:** global entity search across current case
- [ ] **Layout switcher:** force-directed | hierarchical | radial (button group)
- [ ] **Zoom controls:** zoom in (+), zoom out (−), fit to screen, reset zoom
- [ ] **Export button:** opens export modal
- [ ] **Settings button:** opens settings panel
- [ ] Active case name displayed
- [ ] Node + edge count in current case

## 📁 Files to create
- \`frontend/src/components/TopBar/TopBar.tsx\`
- \`frontend/src/components/TopBar/SearchBar.tsx\`

## ⏱️ Estimated effort: 2–4 hours" \
'["type: feature","priority: medium","component: frontend","phase: 3-frontend-core"]' \
$MS3

# ════════════════════════════════════════════════════════════
# PHASE 4 — Integration
# ════════════════════════════════════════════════════════════

create_issue \
"[INTEGRATION] Wire WebSocket client to graph store" \
"## 📋 Overview
Connect the frontend WebSocket client to the backend WebSocket server so that transform results automatically appear in the graph in real-time.

## 🎯 Acceptance Criteria
- [ ] \`useWebSocket\` hook connects to \`ws://localhost:8000/ws/{case_id}\` on case load
- [ ] On \`NODE_ADDED\` event → node appears in graph immediately
- [ ] On \`EDGE_ADDED\` event → edge appears in graph immediately
- [ ] On \`TRANSFORM_START\` → spinner appears in right sidebar
- [ ] On \`TRANSFORM_DONE\` → results rendered, spinner removed, node count updates
- [ ] On \`TRANSFORM_ERROR\` → error toast shown
- [ ] Auto-reconnect on disconnect (exponential backoff: 1s, 2s, 4s, 8s, max 30s)
- [ ] Connection status indicator in top bar (green dot = connected, red = disconnected)

## 📁 Files to create
- \`frontend/src/hooks/useWebSocket.ts\`
- \`frontend/src/hooks/useGraphSync.ts\`

## 🔗 Dependencies
- Issue: [BACKEND] Implement WebSocket server
- Issue: [FRONTEND] Implement Cytoscape.js graph canvas

## ⏱️ Estimated effort: 4–6 hours" \
'["type: feature","priority: critical","component: frontend","component: websocket","phase: 4-integration"]' \
$MS4

create_issue \
"[INTEGRATION] Implement API client layer (Axios + React Query)" \
"## 📋 Overview
Create a typed API client that wraps all backend REST endpoints and provides React hooks for data fetching with caching and loading states.

## 🎯 Acceptance Criteria
- [ ] Axios instance with base URL from env, timeout 30s
- [ ] API client functions typed with Pydantic-equivalent TypeScript interfaces
- [ ] React Query hooks for all main resources:
  - [ ] \`useCases()\` — list all cases
  - [ ] \`useCase(id)\` — get single case
  - [ ] \`useGraphState(caseId)\` — get graph state
  - [ ] \`useTransforms(entityType)\` — get available transforms
  - [ ] \`useRunTransform()\` — mutation to trigger transform
  - [ ] \`useSettings()\` — get API settings
- [ ] Error handling: API errors shown as toast notifications
- [ ] Loading states propagated to components

## 📁 Files to create
- \`frontend/src/api/client.ts\`
- \`frontend/src/api/cases.ts\`
- \`frontend/src/api/graph.ts\`
- \`frontend/src/api/transforms.ts\`
- \`frontend/src/api/settings.ts\`
- \`frontend/src/hooks/useCases.ts\`
- \`frontend/src/hooks/useTransforms.ts\`

## ⏱️ Estimated effort: 4–6 hours" \
'["type: feature","priority: critical","component: frontend","component: backend","phase: 4-integration"]' \
$MS4

create_issue \
"[INTEGRATION] End-to-end flow: Add node → Run transform → Graph updates" \
"## 📋 Overview
Verify and polish the complete end-to-end flow. This is the core user journey of PHANTOM and must work flawlessly before moving to transform implementation.

## 🎯 Acceptance Criteria
- [ ] User opens PHANTOM at localhost:3000
- [ ] User creates a new Case
- [ ] User adds a PhoneNumber node via left sidebar
- [ ] Phone node appears in graph canvas
- [ ] User right-clicks node → context menu shows applicable transforms
- [ ] User clicks a transform → backend receives request, job created
- [ ] Spinner appears in sidebar during execution
- [ ] On completion: result nodes appear in graph via WebSocket
- [ ] Edges connect result nodes to source node, labeled with transform name
- [ ] Graph state persisted to PostgreSQL
- [ ] Page reload restores graph from DB
- [ ] Audit log entry created for transform run

## 🧪 Test Scenarios
1. PhoneNumber → PhoneInfoga Scanner → carrier/region nodes
2. Username → Username Search → SocialProfile nodes
3. Transform timeout → error shown, no crash

## ⏱️ Estimated effort: 4–6 hours (integration testing + bug fixes)" \
'["type: feature","priority: critical","component: frontend","component: backend","phase: 4-integration"]' \
$MS4

# ════════════════════════════════════════════════════════════
# PHASE 5 — OSINT Transforms
# ════════════════════════════════════════════════════════════

create_issue \
"[TRANSFORM] Implement PhoneInfoga Scanner (Transform #1)" \
"## 📋 Overview
Implement the PhoneInfoga-style phone number scanner that returns carrier, country, line type, and format information.

## 🎯 Acceptance Criteria
- [ ] Input: \`PhoneNumber\` entity (E.164 or local format)
- [ ] Phone number parsed and validated via \`phonenumbers\` library (no API key needed)
- [ ] Returns: carrier name, country code, country name, number type (MOBILE/FIXED_LINE/VOIP), E.164 format, local format
- [ ] OVH carrier lookup via HTTP (no API key, best-effort)
- [ ] Optional: Numverify API for enhanced data if key configured
- [ ] Output nodes: enriched \`PhoneNumber\` node + \`Organization\` node (carrier) + \`Location\` node (country)
- [ ] Handles: invalid numbers gracefully (returns error, not exception)
- [ ] Rate limit: 30/minute (mostly local parsing)

## 📁 Files to create
- \`backend/app/transforms/phone/phoneinfoga.py\`
- \`backend/tests/transforms/test_phoneinfoga.py\`

## 🔗 Dependencies
- Issue: [BACKEND] Implement BaseTransform class

## ⏱️ Estimated effort: 3–4 hours" \
'["type: feature","priority: high","component: transforms","component: backend","phase: 5-transforms"]' \
$MS5

create_issue \
"[TRANSFORM] Implement Platform Registration Checker (Transform #2)" \
"## 📋 Overview
Check if a phone number is registered on major messaging platforms (WhatsApp, Telegram, Instagram, Amazon, Snapchat, Signal, Viber) using HTTP-based checks without official APIs.

## 🎯 Acceptance Criteria
- [ ] Input: \`PhoneNumber\` entity (E.164 format)
- [ ] Checks all 7 platforms concurrently (asyncio.gather)
- [ ] Each check has individual 8s timeout
- [ ] Returns: \`SocialProfile\` node per registered platform
- [ ] Each result node contains: platform, registered (bool), profile_url (if discoverable)
- [ ] Handles: network errors, rate limits (per-platform backoff)
- [ ] Respects per-platform rate limits to avoid blocks

### Platform Check Methods:
- **WhatsApp**: OTP endpoint existence check
- **Telegram**: phone number → username lookup via Bot API (\`getChat\`)
- **Instagram**: registration heuristic endpoint
- **Amazon**: account existence check
- **Snapchat**: phone number lookup endpoint
- **Signal**: registration check endpoint
- **Viber**: number check endpoint

## 📁 Files to create
- \`backend/app/transforms/phone/platform_checker.py\`
- \`backend/tests/transforms/test_platform_checker.py\`

## ⚠️ Note
Some platform endpoints may require reverse engineering or change without notice. Implement with graceful fallbacks.

## ⏱️ Estimated effort: 6–8 hours" \
'["type: feature","priority: high","component: transforms","phase: 5-transforms"]' \
$MS5

create_issue \
"[TRANSFORM] Implement Social Media Profile Linker (Transform #3)" \
"## 📋 Overview
Given a phone number, attempt to retrieve linked social media profile information including profile pictures, display names, and about text.

## 🎯 Acceptance Criteria
- [ ] Input: \`PhoneNumber\` entity
- [ ] **WhatsApp:** profile picture URL (via WA check endpoint), about text if public
- [ ] **Telegram:** username resolution via bot API if number is in contacts-visible mode
- [ ] **Facebook:** limited graph search for phone number (public data only)
- [ ] Returns: \`SocialProfile\` nodes with platform, username, display_name, avatar_url, about
- [ ] Profile picture hash computed for cross-platform identity correlation
- [ ] Hash stored as node property for future deduplication

## 📁 Files to create
- \`backend/app/transforms/phone/social_linker.py\`
- \`backend/tests/transforms/test_social_linker.py\`

## ⏱️ Estimated effort: 4–6 hours" \
'["type: feature","priority: medium","component: transforms","phase: 5-transforms"]' \
$MS5

create_issue \
"[TRANSFORM] Implement CNAM / Reverse Lookup (Transform #4)" \
"## 📋 Overview
Perform caller ID / CNAM lookup to resolve a phone number to a person's name and check spam scores.

## 🎯 Acceptance Criteria
- [ ] Input: \`PhoneNumber\` entity
- [ ] Query OpenCNAM API (requires SID + Auth Token in settings)
- [ ] Returns: \`Person\` node with full name if found
- [ ] Spam score from community data (if available)
- [ ] Graceful degradation if no API key configured (return empty result, not error)
- [ ] Cache results in Redis (TTL: 24h) to avoid redundant API calls

## 📁 Files to create
- \`backend/app/transforms/phone/cnam_lookup.py\`

## ⏱️ Estimated effort: 2–3 hours" \
'["type: feature","priority: medium","component: transforms","phase: 5-transforms"]' \
$MS5

create_issue \
"[TRANSFORM] Implement Leak Database Check (Transform #5)" \
"## 📋 Overview
Check if a phone number or email address appears in known data breach databases using HaveIBeenPwned.

## 🎯 Acceptance Criteria
- [ ] Input: \`PhoneNumber\` or \`EmailAddress\` entity
- [ ] HIBP API v3 integration (requires API key in settings)
- [ ] Returns: one \`LeakRecord\` node per breach found
- [ ] Each LeakRecord contains: breach name, date, data types exposed, verified status
- [ ] Cache results in Redis (TTL: 1h)
- [ ] Without API key: returns informative message (not error)

## 📁 Files to create
- \`backend/app/transforms/phone/leak_check.py\`

## ⏱️ Estimated effort: 2–3 hours" \
'["type: feature","priority: medium","component: transforms","phase: 5-transforms"]' \
$MS5

create_issue \
"[TRANSFORM] Implement Username Search — Sherlock-style (Transform #6)" \
"## 📋 Overview
Search for a username across 300+ social platforms and return found profiles.

## 🎯 Acceptance Criteria
- [ ] Input: \`Username\` entity
- [ ] Check 300+ platforms concurrently (asyncio + semaphore limiting concurrency to 50)
- [ ] Platform list loaded from embedded JSON config file
- [ ] Each check: HTTP GET, validate response (status code + content checks, not just 200)
- [ ] Returns: \`SocialProfile\` node per found profile with: platform, url, username
- [ ] Progress events sent via WebSocket (e.g. \"checked 50/300\")
- [ ] Total timeout: 60s
- [ ] Results stream in as they arrive (not wait for all)
- [ ] Respects \`PROXY_URL\` setting if configured

## 📁 Files to create
- \`backend/app/transforms/general/username_search.py\`
- \`backend/app/transforms/general/data/platforms.json\` (300+ platform definitions)

## ⏱️ Estimated effort: 6–10 hours" \
'["type: feature","priority: high","component: transforms","phase: 5-transforms"]' \
$MS5

create_issue \
"[TRANSFORM] Implement Email OSINT — Holehe-style (Transform #7)" \
"## 📋 Overview
Check email address registration across online services using password recovery endpoint analysis.

## 🎯 Acceptance Criteria
- [ ] Input: \`EmailAddress\` entity
- [ ] Holehe-style checks: use password reset flows to detect account existence without logging in
- [ ] Check 50+ major platforms concurrently
- [ ] Epieos integration: Google account profile data (name, photo URL) via Epieos API
- [ ] Returns: \`SocialProfile\` node per registered platform
- [ ] Google profile returns \`Person\` node with name + avatar

## 📁 Files to create
- \`backend/app/transforms/general/email_osint.py\`

## ⏱️ Estimated effort: 5–7 hours" \
'["type: feature","priority: high","component: transforms","phase: 5-transforms"]' \
$MS5

create_issue \
"[TRANSFORM] Implement IP/Domain Intelligence (Transform #8)" \
"## 📋 Overview
Gather intelligence on IP addresses and domain names using Shodan, WHOIS, reverse DNS, and geolocation.

## 🎯 Acceptance Criteria
- [ ] Input: \`IPAddress\` or \`Domain\` entity
- [ ] **Shodan** (with API key): open ports, services, CVEs, banners, ASN, org
- [ ] **WHOIS**: registrar, dates, nameservers, registrant (if public)
- [ ] **Reverse DNS**: PTR records → \`Domain\` nodes
- [ ] **Geolocation**: country, city, lat/lon → \`Location\` node
- [ ] **DNS Records** (for domains): A, AAAA, MX, TXT, NS → respective entity nodes
- [ ] Without Shodan key: WHOIS + DNS only
- [ ] Returns: \`Organization\` (ASN owner), \`Location\`, additional \`IPAddress\`/\`Domain\` nodes

## 📁 Files to create
- \`backend/app/transforms/general/ip_domain_intel.py\`

## ⏱️ Estimated effort: 4–6 hours" \
'["type: feature","priority: medium","component: transforms","phase: 5-transforms"]' \
$MS5

create_issue \
"[TRANSFORM] Implement Google Dorking Engine (Transform #9)" \
"## 📋 Overview
Auto-generate and execute targeted Google search queries (dorks) for any entity type, returning discovered URLs and mentions.

## 🎯 Acceptance Criteria
- [ ] Input: any entity type
- [ ] Dork templates per entity type:
  - PhoneNumber: \`\"+49... site:truecaller.com OR site:tellows.de\"\`
  - Email: \`\"email@domain.com\" filetype:pdf OR filetype:xls\"`
  - Username: \`\"username\" site:github.com OR site:reddit.com\`
  - etc.
- [ ] Execute dorks via HTTP (SerpAPI or direct Google, with rate limit)
- [ ] Parse result URLs and titles
- [ ] Returns: \`Domain\` nodes for discovered URLs
- [ ] User can view raw dork strings in result (for manual execution)
- [ ] Respects proxy setting

## 📁 Files to create
- \`backend/app/transforms/general/google_dorking.py\`
- \`backend/app/transforms/general/data/dork_templates.json\`

## ⏱️ Estimated effort: 4–5 hours" \
'["type: feature","priority: medium","component: transforms","phase: 5-transforms"]' \
$MS5

create_issue \
"[TRANSFORM] Implement Social Graph Expansion (Transform #10)" \
"## 📋 Overview
Given a social profile, extract a sample of the connected social graph (followers, following, mutual connections).

## 🎯 Acceptance Criteria
- [ ] Input: \`SocialProfile\` entity
- [ ] **Twitter/X**: public followers/following via scraping or official API
- [ ] **Instagram**: public follower list sample
- [ ] **GitHub**: followers, following, organizations
- [ ] Returns: \`Username\` or \`SocialProfile\` nodes for connections
- [ ] Limits: max 50 connections per run (configurable)
- [ ] Includes relation type as edge label (follows, followed_by, member_of)

## 📁 Files to create
- \`backend/app/transforms/general/social_graph.py\`

## ⏱️ Estimated effort: 5–7 hours" \
'["type: feature","priority: low","component: transforms","phase: 5-transforms"]' \
$MS5

# ════════════════════════════════════════════════════════════
# PHASE 6 — Case Management
# ════════════════════════════════════════════════════════════

create_issue \
"[CASE] Implement full Case Management system" \
"## 📋 Overview
Implement the complete case management system: CRUD operations, graph state persistence, markdown notes, tag system, and audit log display.

## 🎯 Acceptance Criteria
- [ ] **Create Case:** name, description, optional tags
- [ ] **Open Case:** loads graph from DB into canvas, restores viewport
- [ ] **Rename / Edit Case:** inline editing in left sidebar
- [ ] **Delete Case:** confirmation dialog, cascade deletes graph + audit
- [ ] **Case Notes:** right-click case → markdown editor opens in modal
  - [ ] Rendered preview toggle (markdown → HTML)
  - [ ] Auto-save on blur
- [ ] **Tag system:** add/remove tags, filter cases by tag
- [ ] **Case list sorting:** by name, by date modified, by node count
- [ ] **Audit Log panel:** timeline of all events in a case
  - [ ] Filterable by event type
  - [ ] Timestamp + event description
  - [ ] Click event → highlight relevant node

## 📁 Files to create/modify
- \`frontend/src/components/Case/CaseModal.tsx\`
- \`frontend/src/components/Case/CaseNotes.tsx\`
- \`frontend/src/components/Case/AuditLogPanel.tsx\`
- \`backend/app/services/case_service.py\` (full implementation)

## ⏱️ Estimated effort: 8–12 hours" \
'["type: feature","priority: high","component: frontend","component: backend","phase: 6-case-mgmt"]' \
$MS6

# ════════════════════════════════════════════════════════════
# PHASE 7 — Timeline & Export
# ════════════════════════════════════════════════════════════

create_issue \
"[TIMELINE] Implement bottom Timeline panel" \
"## 📋 Overview
Implement the chronological timeline panel at the bottom of the screen showing the order of discoveries in the current case.

## 🎯 Acceptance Criteria
- [ ] Bottom panel (collapsible) shows all graph events chronologically
- [ ] Each event shows: timestamp, entity type icon, entity value, transform used
- [ ] Filter by: entity type, transform name, date range
- [ ] Click event → highlights corresponding node in graph, centers viewport
- [ ] Horizontal scroll for long timelines
- [ ] Timeline plays back in order (animated)

## 📁 Files to create
- \`frontend/src/components/Timeline/TimelinePanel.tsx\`
- \`frontend/src/components/Timeline/TimelineEvent.tsx\`

## ⏱️ Estimated effort: 5–7 hours" \
'["type: feature","priority: medium","component: frontend","phase: 7-timeline"]' \
$MS7

create_issue \
"[EXPORT] Implement graph and report export" \
"## 📋 Overview
Implement all export formats: PNG/SVG (graph image), JSON (full graph state), PDF (investigation report), CSV (entity list).

## 🎯 Acceptance Criteria
- [ ] **PNG export:** Cytoscape.js canvas → PNG file, full resolution
- [ ] **SVG export:** Cytoscape.js canvas → SVG file, scalable
- [ ] **JSON export:** full graph state (nodes, edges, case metadata) → downloadable JSON
- [ ] **CSV export:** all entities as rows (type, value, properties, timestamp) → CSV
- [ ] **PDF report:** generated by backend (ReportLab)
  - [ ] Header: PHANTOM logo, case name, date
  - [ ] Executive summary section
  - [ ] Graph screenshot (embedded)
  - [ ] Entity list table
  - [ ] Key findings (audit log summary)
  - [ ] Footer with page numbers

## 📁 Files to create
- \`frontend/src/components/Export/ExportModal.tsx\`
- \`backend/app/services/export_service.py\`
- \`backend/app/api/export.py\` (full implementation)

## ⏱️ Estimated effort: 6–8 hours" \
'["type: feature","priority: medium","component: frontend","component: backend","component: export","phase: 7-timeline"]' \
$MS7

# ════════════════════════════════════════════════════════════
# PHASE 8 — Settings & API Management
# ════════════════════════════════════════════════════════════

create_issue \
"[SETTINGS] Implement Settings panel — API keys & module configuration" \
"## 📋 Overview
Implement the full Settings panel for managing API keys, module enable/disable, rate limits, and proxy configuration.

## 🎯 Acceptance Criteria
- [ ] Settings accessible via top bar button → slides in from right
- [ ] **API Keys section:**
  - [ ] List: Numverify, Shodan, OpenCNAM, HaveIBeenPwned, Telegram
  - [ ] Input field per key (masked after save, click to reveal)
  - [ ] \"Test\" button to verify key works
  - [ ] Status indicator: ✓ valid | ✗ invalid | ? not set
  - [ ] Keys stored encrypted in PostgreSQL
- [ ] **Module Toggles:**
  - [ ] Enable/disable any transform
  - [ ] Disabled transforms don't appear in context menu
- [ ] **Rate Limits:**
  - [ ] Configurable per-module (requests/minute)
  - [ ] Current usage indicator
- [ ] **Proxy / Tor:**
  - [ ] SOCKS5 proxy URL input
  - [ ] Per-module proxy enable toggle
  - [ ] \"Test Proxy\" button (fetches ifconfig.me)

## 📁 Files to create
- \`frontend/src/components/Settings/SettingsPanel.tsx\`
- \`frontend/src/components/Settings/ApiKeyManager.tsx\`
- \`frontend/src/components/Settings/ModuleToggleList.tsx\`
- \`backend/app/core/encryption.py\` (Fernet symmetric encryption for keys)

## ⏱️ Estimated effort: 6–8 hours" \
'["type: feature","priority: high","component: frontend","component: backend","component: auth","phase: 8-settings"]' \
$MS8

# ════════════════════════════════════════════════════════════
# PHASE 9 — Testing, Docs, Polish
# ════════════════════════════════════════════════════════════

create_issue \
"[TEST] Implement backend test suite" \
"## 📋 Overview
Write comprehensive tests for the backend: transform unit tests, API integration tests, WebSocket tests.

## 🎯 Acceptance Criteria
- [ ] pytest + pytest-asyncio setup
- [ ] Unit tests for every transform (mocked HTTP calls)
- [ ] Integration tests for all REST API endpoints
- [ ] WebSocket tests (connect, receive event)
- [ ] Database tests (create/read/update/delete for all models)
- [ ] Test coverage ≥ 70%
- [ ] All tests pass in CI

## 📁 Files to create
- \`backend/tests/test_transforms/test_*.py\` (one per transform)
- \`backend/tests/test_api/test_cases.py\`
- \`backend/tests/test_api/test_graph.py\`
- \`backend/tests/test_api/test_transforms.py\`
- \`backend/tests/conftest.py\` (async fixtures, test DB)

## ⏱️ Estimated effort: 8–12 hours" \
'["type: test","priority: high","component: backend","phase: 9-polish"]' \
$MS9

create_issue \
"[DOCS] Write complete README and setup documentation" \
"## 📋 Overview
Write production-quality documentation: README, API docs, deployment guide, and contributor guide.

## 🎯 Acceptance Criteria
- [ ] README covers: feature overview, quick start, all make commands, API key setup, architecture diagram, screenshot
- [ ] \`SETUP.md\` for first-time setup with prerequisites, step-by-step instructions
- [ ] \`DEPLOYMENT.md\` for production deployment (HTTPS, secrets, reverse proxy)
- [ ] \`TRANSFORMS.md\` documentation for each transform module
- [ ] OpenAPI docs auto-generated at \`/docs\` and \`/redoc\`
- [ ] All environment variables documented in \`.env.example\`

## ⏱️ Estimated effort: 4–6 hours" \
'["type: docs","priority: medium","phase: 9-polish"]' \
$MS9

create_issue \
"[SECURITY] Security hardening and review" \
"## 📋 Overview
Perform a security review and implement all necessary hardening before v1.0 release.

## 🎯 Acceptance Criteria
- [ ] All API keys encrypted at rest (Fernet)
- [ ] No secrets in logs or error messages
- [ ] Input validation on all API endpoints (Pydantic v2 strict mode)
- [ ] Rate limiting on all endpoints (slowapi)
- [ ] CORS restricted to configured origins only
- [ ] SQL injection: all queries use parameterized statements (SQLAlchemy ORM)
- [ ] XSS: React default escaping + CSP headers
- [ ] Docker: backend runs as non-root user
- [ ] Docker: no secrets in image layers
- [ ] \`.env\` not committed, \`.gitignore\` verified
- [ ] OWASP Top 10 checklist reviewed

## ⏱️ Estimated effort: 4–6 hours" \
'["type: security","priority: critical","component: backend","component: docker","phase: 9-polish"]' \
$MS9

create_issue \
"[POLISH] Dark theme UI consistency pass" \
"## 📋 Overview
Review and polish the entire UI for visual consistency: dark theme, amber accents, terminal aesthetic, spacing, typography.

## 🎯 Acceptance Criteria
- [ ] All components use consistent color tokens (Tailwind config)
- [ ] Dark background: #0a0a0a (canvas), #111111 (sidebar), #1a1a1a (panels)
- [ ] Accent color: amber (#f59e0b) for highlights, buttons, active states
- [ ] Monospace font (JetBrains Mono or Fira Code) for entity values, code-like elements
- [ ] Scrollbars styled (dark theme)
- [ ] Loading skeletons / shimmer for async content
- [ ] Toast notifications styled consistently
- [ ] All modals have proper focus trap + keyboard navigation (Escape closes)
- [ ] No layout shifts when sidebars toggle
- [ ] Pixel-perfect at 1920×1080 (primary target resolution)

## ⏱️ Estimated effort: 4–6 hours" \
'["type: feature","priority: medium","component: frontend","phase: 9-polish"]' \
$MS9

echo ""
echo "============================================================"
echo "✅ PHANTOM GitHub Project Setup Complete!"
echo ""
echo "Summary:"
echo "  Labels created:     35+"
echo "  Milestones created: 9"
echo "  Issues created:     25+"
echo ""
echo "Next steps:"
echo "  1. Go to https://github.com/${OWNER}/${REPO}/projects"
echo "     and create a Kanban board (link milestones as columns)"
echo "  2. Assign issues to yourself"
echo "  3. Start with Phase 1 issues"
echo "============================================================"
