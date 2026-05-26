# UML-Dokumentation — PHANTOM OSINT Investigation Platform

**Version:** 1.0.0  
**Datum:** Mai 2026  
**Notation:** Mermaid (GitHub-nativ renderbar)

---

## Inhaltsverzeichnis

1. [Use-Case-Diagramm](#1-use-case-diagramm)
2. [Klassendiagramm — Domain Model](#2-klassendiagramm--domain-model)
3. [Klassendiagramm — Transform-System](#3-klassendiagramm--transform-system)
4. [Entity-Relationship-Diagramm (ERD)](#4-entity-relationship-diagramm)
5. [Komponentendiagramm](#5-komponentendiagramm)
6. [Sequenzdiagramm — Transform ausführen](#6-sequenzdiagramm--transform-ausführen)
7. [Sequenzdiagramm — Case laden](#7-sequenzdiagramm--case-laden)
8. [Sequenzdiagramm — WebSocket-Verbindung](#8-sequenzdiagramm--websocket-verbindung)
9. [Aktivitätsdiagramm — OSINT-Untersuchung](#9-aktivitätsdiagramm--osint-untersuchung)
10. [Aktivitätsdiagramm — Transform-Execution-Flow](#10-aktivitätsdiagramm--transform-execution-flow)
11. [Zustandsdiagramm — Transform-Job](#11-zustandsdiagramm--transform-job)
12. [Zustandsdiagramm — WebSocket-Verbindung](#12-zustandsdiagramm--websocket-verbindung)

---

## 1. Use-Case-Diagramm

```mermaid
graph LR
    subgraph Actors
        A([OSINT Analyst])
        B([IT-Security Researcher])
        C([Journalist])
    end

    subgraph PHANTOM System
        UC1[Fall erstellen / verwalten]
        UC2[Knoten hinzufügen]
        UC3[Graph visualisieren]
        UC4[Transform ausführen]
        UC5[Ergebnisse im Graph sehen]
        UC6[API-Keys konfigurieren]
        UC7[Module aktivieren / deaktivieren]
        UC8[Audit-Timeline anzeigen]
        UC9[Graph exportieren]
        UC10[Fall-Notizen pflegen]

        UC4 -->|include| UC11[API-Key validieren]
        UC4 -->|include| UC12[Job async starten]
        UC12 -->|include| UC13[WebSocket-Broadcast]
        UC13 -->|include| UC5
        UC9 -->|extend| UC14[PDF-Bericht erzeugen]
        UC9 -->|extend| UC15[JSON / CSV exportieren]
    end

    A --> UC1
    A --> UC2
    A --> UC3
    A --> UC4
    A --> UC6
    A --> UC7
    A --> UC8
    A --> UC9
    A --> UC10

    B --> UC1
    B --> UC2
    B --> UC4
    B --> UC6
    B --> UC9

    C --> UC1
    C --> UC2
    C --> UC3
    C --> UC9
    C --> UC10
```

---

## 2. Klassendiagramm — Domain Model

```mermaid
classDiagram
    class Case {
        +UUID id
        +String name
        +String description
        +List~String~ tags
        +String notes_md
        +DateTime created_at
        +DateTime updated_at
        +create()
        +update()
        +delete()
    }

    class GraphNode {
        +UUID id
        +UUID case_id
        +EntityType entity_type
        +String value
        +String label
        +Dict properties
        +Float pos_x
        +Float pos_y
        +DateTime created_at
        +updatePosition(x, y)
    }

    class GraphEdge {
        +UUID id
        +UUID case_id
        +UUID source_id
        +UUID target_id
        +String label
        +String transform_name
        +DateTime created_at
    }

    class AuditLog {
        +UUID id
        +UUID case_id
        +String event_type
        +String entity_type
        +String entity_value
        +String transform_name
        +Dict metadata
        +DateTime created_at
    }

    class ApiKey {
        +UUID id
        +String service_name
        +String encrypted_key
        +Boolean is_active
        +DateTime created_at
        +DateTime updated_at
        +encrypt(raw_key)
        +decrypt() String
        +activate()
        +deactivate()
    }

    class EntityType {
        <<enumeration>>
        PHONE_NUMBER
        EMAIL_ADDRESS
        PERSON
        USERNAME
        SOCIAL_PROFILE
        IP_ADDRESS
        DOMAIN
        ORGANIZATION
        LOCATION
        LEAK_RECORD
    }

    Case "1" --> "0..*" GraphNode : contains
    Case "1" --> "0..*" GraphEdge : contains
    Case "1" --> "0..*" AuditLog : logs
    GraphNode --> EntityType : typed as
    GraphEdge --> GraphNode : source
    GraphEdge --> GraphNode : target
```

---

## 3. Klassendiagramm — Transform-System

```mermaid
classDiagram
    class BaseTransform {
        <<abstract>>
        +String name
        +String description
        +List~EntityType~ input_types
        +List~EntityType~ output_types
        +Int timeout
        +Int rate_limit
        +run(entity, api_keys)* TransformResult
        +execute(entity, api_keys) TransformResult
    }

    class Entity {
        +EntityType type
        +String value
        +Dict properties
        +String label
    }

    class TransformResult {
        +List~Entity~ entities
        +List~Dict~ edges
        +Dict metadata
        +String error
        +Int duration_ms
    }

    class TransformRegistry {
        -Dict~String, BaseTransform~ _transforms
        +register(transform)
        +get_by_name(name) BaseTransform
        +get_for_entity_type(type) List
        +all_transforms() List
    }

    class PhoneInfogaTransform {
        +name = "PhoneInfoga Scanner"
        +run(entity, api_keys) TransformResult
        -_parse_number(raw) PhoneNumber
        -_enrich_numverify(e164, key) Entity
    }

    class PlatformRegistrationTransform {
        +name = "Platform Registration Checker"
        +run(entity, api_keys) TransformResult
        -_check_whatsapp(e164) Entity
        -_check_telegram(e164, token) Entity
        -_check_signal(e164) Entity
        -_check_instagram(e164) Entity
        -_check_snapchat(e164) Entity
        -_check_amazon(e164) Entity
    }

    class CNAMLookupTransform {
        +name = "CNAM / Reverse Lookup"
        +run(entity, api_keys) TransformResult
    }

    class LeakCheckTransform {
        +name = "Leak Database Check"
        +run(entity, api_keys) TransformResult
    }

    class SocialProfileLinkerTransform {
        +name = "Social Media Profile Linker"
        +run(entity, api_keys) TransformResult
        -_whatsapp_profile(e164) Entity
        -_telegram_profile(e164, token) Entity
    }

    class IPDomainIntelTransform {
        +name = "IP/Domain Intelligence"
        +run(entity, api_keys) TransformResult
        -_geo_lookup(value) List~Entity~
        -_rdns(value, is_ip) List~Entity~
        -_dns_records(domain) List~Entity~
        -_shodan(value, is_ip, key) List~Entity~
    }

    class UsernameSearchTransform {
        +name = "Username Search"
        +run(entity, api_keys) TransformResult
    }

    class EmailOSINTTransform {
        +name = "Email OSINT"
        +run(entity, api_keys) TransformResult
    }

    class GoogleDorkingTransform {
        +name = "Google Dorking"
        +run(entity, api_keys) TransformResult
    }

    class SocialGraphExpansionTransform {
        +name = "Social Graph Expansion"
        +run(entity, api_keys) TransformResult
    }

    BaseTransform <|-- PhoneInfogaTransform
    BaseTransform <|-- PlatformRegistrationTransform
    BaseTransform <|-- CNAMLookupTransform
    BaseTransform <|-- LeakCheckTransform
    BaseTransform <|-- SocialProfileLinkerTransform
    BaseTransform <|-- IPDomainIntelTransform
    BaseTransform <|-- UsernameSearchTransform
    BaseTransform <|-- EmailOSINTTransform
    BaseTransform <|-- GoogleDorkingTransform
    BaseTransform <|-- SocialGraphExpansionTransform

    BaseTransform --> Entity : consumes
    BaseTransform --> TransformResult : produces
    TransformRegistry --> BaseTransform : manages
```

---

## 4. Entity-Relationship-Diagramm

```mermaid
erDiagram
    cases {
        uuid id PK
        varchar name
        text description
        json tags
        text notes_md
        timestamp created_at
        timestamp updated_at
    }

    graph_nodes {
        uuid id PK
        uuid case_id FK
        varchar entity_type
        text value
        varchar label
        json properties
        float pos_x
        float pos_y
        timestamp created_at
    }

    graph_edges {
        uuid id PK
        uuid case_id FK
        uuid source_id FK
        uuid target_id FK
        varchar label
        varchar transform_name
        timestamp created_at
    }

    audit_logs {
        uuid id PK
        uuid case_id FK
        varchar event_type
        varchar entity_type
        text entity_value
        varchar transform_name
        json metadata
        timestamp created_at
    }

    api_keys {
        uuid id PK
        varchar service_name
        text encrypted_key
        boolean is_active
        timestamp created_at
        timestamp updated_at
    }

    cases ||--o{ graph_nodes : "contains"
    cases ||--o{ graph_edges : "contains"
    cases ||--o{ audit_logs : "logs"
    graph_nodes ||--o{ graph_edges : "source_id"
    graph_nodes ||--o{ graph_edges : "target_id"
```

---

## 5. Komponentendiagramm

```mermaid
graph TB
    subgraph Browser["Browser (Port 3000)"]
        subgraph Frontend["React Frontend"]
            APP[App.tsx]
            TOPBAR[TopBar]
            LSIDEBAR[LeftSidebar]
            RSIDEBAR[RightSidebar]
            GRAPH[GraphCanvas\nCytoscape.js]
            CTX[NodeContextMenu]
            TIMELINE[DiscoveryTimeline]
            SETTINGS[SettingsPanel]
            STORE[Zustand Store\ngraphStore]
            WS_HOOK[useWebSocket Hook]
            API_CLIENT[Axios API Client]
        end
    end

    subgraph Backend["FastAPI Backend (Port 8000)"]
        CASES_API["/api/cases/"]
        GRAPH_API["/api/graph/"]
        TRANSFORM_API["/api/transforms/"]
        EXPORT_API["/api/export/"]
        SETTINGS_API["/api/settings/"]
        WS_ENDPOINT["/ws/{case_id}"]

        subgraph Services["Service Layer"]
            CASE_SVC[case_service]
            GRAPH_SVC[graph_service]
            SETTINGS_SVC[settings_service]
        end

        subgraph Transforms["Transform Registry"]
            REGISTRY[TransformRegistry]
            PHONE_T["Phone Transforms\n× 5"]
            GENERAL_T["General Transforms\n× 5"]
        end

        WS_MGR[WebSocketManager]
    end

    subgraph Storage["Storage"]
        PG[(PostgreSQL\nPort 5432)]
        REDIS[(Redis\nPort 6379)]
    end

    subgraph ExternalAPIs["Externe APIs (optional)"]
        HIBP[HaveIBeenPwned]
        SHODAN[Shodan]
        OPENCNAM[OpenCNAM]
        NUMVERIFY[Numverify]
        TELEGRAM[Telegram Bot API]
        IPAPI[ipapi.co]
        GOOGLE_DNS[dns.google]
    end

    APP --> STORE
    APP --> WS_HOOK
    LSIDEBAR --> API_CLIENT
    RSIDEBAR --> API_CLIENT
    TIMELINE --> API_CLIENT
    SETTINGS --> API_CLIENT
    GRAPH --> STORE
    CTX --> API_CLIENT
    WS_HOOK -->|WebSocket| WS_ENDPOINT

    API_CLIENT -->|REST| CASES_API
    API_CLIENT -->|REST| GRAPH_API
    API_CLIENT -->|REST| TRANSFORM_API
    API_CLIENT -->|REST| EXPORT_API
    API_CLIENT -->|REST| SETTINGS_API

    CASES_API --> CASE_SVC
    GRAPH_API --> GRAPH_SVC
    SETTINGS_API --> SETTINGS_SVC
    TRANSFORM_API --> REGISTRY

    CASE_SVC --> PG
    GRAPH_SVC --> PG
    SETTINGS_SVC --> PG
    SETTINGS_SVC -->|cache| REDIS

    REGISTRY --> PHONE_T
    REGISTRY --> GENERAL_T
    PHONE_T -->|HTTP| HIBP
    PHONE_T -->|HTTP| OPENCNAM
    PHONE_T -->|HTTP| NUMVERIFY
    PHONE_T -->|HTTP| TELEGRAM
    GENERAL_T -->|HTTP| SHODAN
    GENERAL_T -->|HTTP| IPAPI
    GENERAL_T -->|HTTP| GOOGLE_DNS

    WS_MGR -->|broadcast| WS_ENDPOINT
    TRANSFORM_API --> WS_MGR
```

---

## 6. Sequenzdiagramm — Transform ausführen

```mermaid
sequenceDiagram
    actor User
    participant UI as React Frontend
    participant WS as WebSocket
    participant API as FastAPI
    participant Registry as TransformRegistry
    participant Transform as BaseTransform
    participant DB as PostgreSQL
    participant ExtAPI as Externe API

    User->>UI: Rechtsklick → Transform wählen
    UI->>API: POST /api/transforms/run\n{case_id, node_id, transform_name}
    
    API->>DB: get_case(case_id) — validieren
    DB-->>API: Case-Objekt
    API->>DB: get_node(node_id) — validieren
    DB-->>API: Node-Objekt
    API->>Registry: get_by_name(transform_name)
    Registry-->>API: Transform-Instanz

    API->>DB: add_audit_log("transform_queued")
    API-->>UI: 202 Accepted {job_id}

    Note over API,ExtAPI: Hintergrund-Task startet

    API->>DB: get_decrypted_api_keys()
    DB-->>API: {SHODAN_API_KEY: "...", ...}

    API->>Transform: execute(entity, api_keys)
    Transform->>ExtAPI: HTTP-Request (z.B. HIBP, Shodan)
    ExtAPI-->>Transform: Ergebnis-JSON
    Transform-->>API: TransformResult {entities, edges}

    loop Für jede Result-Entity
        API->>DB: add_node(case_id, node_data)
        DB-->>API: GraphNode
        API->>DB: add_edge(case_id, edge_data)
        DB-->>API: GraphEdge
    end

    API->>DB: add_audit_log("transform_completed")
    API->>WS: broadcast("transform_completed", {job_id, result})
    WS-->>UI: WebSocket-Event
    UI->>UI: addNode() + addEdge()\nin Zustand-Store
    UI->>UI: Graph re-render\nmit neuen Knoten/Kanten
    UI-->>User: Neue Knoten erscheinen live
```

---

## 7. Sequenzdiagramm — Case laden

```mermaid
sequenceDiagram
    actor User
    participant UI as React Frontend
    participant Store as Zustand Store
    participant API as FastAPI
    participant DB as PostgreSQL

    User->>UI: App öffnen
    UI->>API: GET /api/cases/
    API->>DB: SELECT * FROM cases
    DB-->>API: Liste aller Cases
    API-->>UI: Case[]
    UI->>Store: setCases(cases)
    UI-->>User: Case-Liste in LeftSidebar

    User->>UI: Fall anklicken
    
    par Parallel-Requests
        UI->>API: GET /api/cases/{id}
        API->>DB: SELECT case WHERE id=...
        DB-->>API: Case
        API-->>UI: Case-Objekt
    and
        UI->>API: GET /api/cases/{id}/graph
        API->>DB: SELECT nodes + edges
        DB-->>API: {nodes[], edges[]}
        API-->>UI: Graph-State
    and
        UI->>API: GET /api/cases/{id}/audit
        API->>DB: SELECT audit_logs ORDER BY created_at DESC
        DB-->>API: AuditLog[]
        API-->>UI: Audit-Events
    end

    UI->>Store: setActiveCase(case)
    UI->>Store: setNodes(nodes)
    UI->>Store: setEdges(edges)
    UI->>Store: setAuditLogs(logs)
    
    UI->>UI: WebSocket verbinden\n/ws/{case_id}
    
    UI-->>User: Graph rendert,\nTimeline zeigt Events
```

---

## 8. Sequenzdiagramm — WebSocket-Verbindung

```mermaid
sequenceDiagram
    participant Hook as useWebSocket Hook
    participant WS as Browser WebSocket
    participant Server as FastAPI WS Endpoint
    participant Manager as WebSocketManager
    participant Store as Zustand Store

    Hook->>WS: new WebSocket(ws://host/ws/{case_id})
    WS->>Server: Connect
    Server->>Manager: connect(case_id, websocket)
    Manager-->>Server: OK
    Server-->>WS: 101 Switching Protocols
    WS-->>Hook: onopen()
    Hook->>Hook: reconnectDelay = 1000ms

    Note over WS,Manager: Verbindung aktiv

    Manager->>WS: send({"type":"node_added","payload":{...}})
    WS-->>Hook: onmessage(event)
    Hook->>Hook: JSON.parse(event.data)
    
    alt type === "node_added"
        Hook->>Store: addNode(payload)
    else type === "edge_added"
        Hook->>Store: addEdge(payload)
    else type === "node_removed"
        Hook->>Store: removeNode(payload.node_id)
    else type === "transform_completed"
        Hook->>Store: addAuditLog(...)
    else type === "transform_failed"
        Hook->>Store: addAuditLog(...)
    end

    Note over WS,Manager: Verbindung unterbrochen

    WS-->>Hook: onclose()
    Hook->>Hook: setTimeout(connect, reconnectDelay)
    Hook->>Hook: reconnectDelay = min(delay*2, 30000)
    Hook->>WS: new WebSocket(...)
```

---

## 9. Aktivitätsdiagramm — OSINT-Untersuchung

```mermaid
flowchart TD
    START([Neue Untersuchung beginnen]) --> A
    A[Fall erstellen] --> B[Startentität eingeben\nz.B. Telefonnummer]
    B --> C[Knoten im Graph hinzufügen]
    C --> D{Transforms verfügbar?}
    
    D -->|Nein| E[Knoten manuell annotieren]
    D -->|Ja| F[Transform auswählen]
    
    F --> G{API-Key konfiguriert?}
    G -->|Nein| H[Zu Settings navigieren]
    H --> I[API-Key eingeben & speichern]
    I --> F
    G -->|Ja| J[Transform ausführen]
    
    J --> K[Warten auf Ergebnis\n⏳ Timeline zeigt Status]
    
    K --> L{Ergebnis?}
    L -->|Fehler| M[Fehler in Timeline prüfen]
    M --> N{Korrigierbar?}
    N -->|Ja| F
    N -->|Nein| O[Anderen Transform wählen]
    O --> F
    
    L -->|Neue Entitäten| P[Neue Knoten im Graph prüfen]
    P --> Q{Interessante Knoten?}
    
    Q -->|Ja| R[Knoten selektieren\nDetails in RightSidebar]
    R --> F
    
    Q -->|Nein / Sackgasse| S[Layout optimieren\nForce/Tree/Radial]
    S --> T{Untersuchung abgeschlossen?}
    
    E --> T
    T -->|Nein| C
    T -->|Ja| U[Export wählen]
    U --> V{Format?}
    V -->|Bericht| W[PDF exportieren]
    V -->|Daten| X[JSON/CSV exportieren]
    V -->|Visualisierung| Y[SVG/PNG exportieren]
    
    W --> END([Untersuchung dokumentiert])
    X --> END
    Y --> END
```

---

## 10. Aktivitätsdiagramm — Transform-Execution-Flow

```mermaid
flowchart TD
    START([POST /api/transforms/run]) --> A[Case validieren]
    A --> B{Case existiert?}
    B -->|Nein| ERR1[404 Case not found]
    B -->|Ja| C[Node validieren]
    C --> D{Node im Case?}
    D -->|Nein| ERR2[404 Node not found]
    D -->|Ja| E[Transform in Registry suchen]
    E --> F{Transform registriert?}
    F -->|Nein| ERR3[404 Transform not found]
    F -->|Ja| G[Job-ID generieren\njobs = 'running']
    G --> H[Audit-Log: transform_queued]
    H --> I[202 Accepted + job_id]
    I --> J[BackgroundTask starten]
    
    subgraph Background["Hintergrund-Ausführung"]
        J --> K[API-Keys aus DB laden\n+ entschlüsseln]
        K --> L[Entity-Objekt bauen]
        L --> M[transform.execute\nmit Timeout-Wrapper]
        M --> N{Timeout?}
        N -->|Ja| ERR4[TransformResult.error\n= 'timed out']
        N -->|Nein| O{HTTP-Fehler?}
        O -->|Ja| ERR5[TransformResult.error\n= Exception-Message]
        O -->|Nein| P[Ergebnis-Entities iterieren]
        P --> Q[add_node für jede Entity]
        Q --> R[add_edge: Source → NewNode]
        R --> S{Mehr Entities?}
        S -->|Ja| Q
        S -->|Nein| T[jobs = 'completed']
        T --> U[Audit-Log: transform_completed]
        U --> V[WS broadcast:\ntransform_completed]
        ERR4 --> W[jobs = 'error']
        ERR5 --> W
        W --> X[Audit-Log: transform_failed]
        X --> Y[WS broadcast: transform_failed]
    end
    
    V --> END1([Frontend aktualisiert Graph])
    Y --> END2([Frontend zeigt Fehler in Timeline])
```

---

## 11. Zustandsdiagramm — Transform-Job

```mermaid
stateDiagram-v2
    [*] --> queued : POST /transforms/run\njob_id erzeugt

    queued --> running : BackgroundTask startet

    running --> completed : TransformResult ok\nEntities persistiert\nWS broadcast
    running --> error : Exception / Timeout\nWS broadcast failed

    completed --> [*] : Job in Memory gespeichert\n(GET /transforms/job/{id})
    error --> [*] : Fehler abrufbar

    note right of running
        Timeout: transform.timeout Sekunden
        (default: 10–30s je Transform)
    end note

    note right of completed
        Neue Knoten + Kanten
        im Graph sichtbar
    end note
```

---

## 12. Zustandsdiagramm — WebSocket-Verbindung

```mermaid
stateDiagram-v2
    [*] --> disconnected : App startet

    disconnected --> connecting : caseId gesetzt\nnew WebSocket()

    connecting --> connected : onopen()\nreconnectDelay = 1s

    connected --> receiving : onmessage()
    receiving --> connected : Event verarbeitet

    connected --> disconnected : onclose()\nCase gewechselt

    connected --> reconnecting : onclose()\nunerwartete Trennung

    reconnecting --> connecting : setTimeout(connect, delay)\ndelay = min(delay×2, 30s)

    reconnecting --> disconnected : caseId = null

    note right of connected
        Aktive Echtzeit-Verbindung
        für case_id X
    end note

    note right of reconnecting
        Exponentielles Backoff:
        1s → 2s → 4s → ... → 30s
    end note
```

---

## Diagramm-Übersicht

| # | Diagrammtyp | Zeigt |
|---|-------------|-------|
| 1 | Use-Case | Nutzergruppen und ihre Systeminteraktionen |
| 2 | Klassendiagramm | Domain-Modell (Case, Node, Edge, AuditLog, ApiKey) |
| 3 | Klassendiagramm | Transform-Hierarchie (BaseTransform + 10 Implementierungen) |
| 4 | ERD | Datenbankschema mit Beziehungen und Attributen |
| 5 | Komponentendiagramm | System-Architektur und Abhängigkeiten |
| 6 | Sequenzdiagramm | Transform ausführen (vollständiger Flow) |
| 7 | Sequenzdiagramm | Case laden (parallele API-Calls) |
| 8 | Sequenzdiagramm | WebSocket-Verbindung und Event-Handling |
| 9 | Aktivitätsdiagramm | OSINT-Untersuchungsworkflow |
| 10 | Aktivitätsdiagramm | Transform-Execution-Flow inkl. Fehlerbehandlung |
| 11 | Zustandsdiagramm | Transform-Job-Lifecycle |
| 12 | Zustandsdiagramm | WebSocket-Verbindungszustände |
