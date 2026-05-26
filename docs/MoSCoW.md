# MoSCoW-Analyse — PHANTOM OSINT Investigation Platform

**Version:** 1.0.0  
**Datum:** Mai 2026

---

## Methodik

Die MoSCoW-Methode klassifiziert Anforderungen in vier Kategorien:

| Kategorie | Bedeutung |
|-----------|-----------|
| **M — Must Have** | Unbedingt erforderlich. Ohne diese Features ist das Produkt nicht lieferbar. |
| **S — Should Have** | Wichtig und wertschöpfend, aber kein K.O.-Kriterium für v1.0. |
| **C — Could Have** | Nützlich, aber verzichtbar. Wird nur umgesetzt, wenn Zeit/Budget es erlauben. |
| **W — Won't Have** | Explizit ausgeschlossen für v1.0 — evtl. in späteren Versionen. |

---

## Must Have (M) ✅

*Alle umgesetzt in v1.0.0*

### Infrastruktur & Betrieb
- [x] Docker-Compose-Deployment (1-Befehl-Start)
- [x] PostgreSQL als persistente Datenbank
- [x] Redis als Cache
- [x] Vollständig self-hosted, keine Cloud-Pflicht
- [x] Konfiguration über `.env`-Datei
- [x] CI/CD mit automatischen Tests bei jedem Push

### Backend
- [x] FastAPI mit asynchronem I/O
- [x] REST-API für Cases, Graph, Transforms, Export, Settings
- [x] WebSocket für Echtzeit-Updates
- [x] SQLAlchemy ORM mit Alembic Migrations
- [x] Vollständiger Audit-Trail je Fall
- [x] Pydantic-Validierung auf allen Endpunkten
- [x] API-Key-Verschlüsselung

### Frontend
- [x] React + TypeScript Single-Page-Application
- [x] Interaktiver Graph (Cytoscape.js)
- [x] Fallverwaltung (erstellen, wechseln, löschen)
- [x] Manuell Knoten hinzufügen (alle 10 Entitätstypen)
- [x] Rechtsklick-Kontextmenü mit Transform-Ausführung
- [x] Node-Detail-Ansicht (RightSidebar)
- [x] Echtzeit-Updates über WebSocket

### Transforms
- [x] Transform-Registry und BaseTransform-Klasse
- [x] PhoneInfoga Scanner (Carrier, Format, Geo)
- [x] Leak Database Check (HaveIBeenPwned)
- [x] IP/Domain Intelligence (WHOIS, DNS, Geo, Shodan)
- [x] Transforms laufen asynchron im Hintergrund
- [x] Transform-Ergebnisse werden als Knoten+Kanten persistiert

### Export
- [x] JSON-Export (vollständiger Case-Dump)
- [x] CSV-Export (Nodes + Edges als Tabelle)

---

## Should Have (S) ✅

*Alle umgesetzt in v1.0.0*

### Frontend
- [x] Kollabierbare Timeline (Audit-Log-Anzeige)
- [x] Settings-Panel (API-Keys + Module)
- [x] Export-Dropdown im TopBar (alle 5 Formate)
- [x] 3 Graph-Layouts (Force, Tree, Radial) schaltbar
- [x] Kollabierbare LeftSidebar
- [x] Entity-Typ-Legende mit Farbzuordnung

### Transforms
- [x] Platform Registration Checker (WhatsApp, Telegram, Signal, Instagram, Snapchat)
- [x] CNAM / Reverse Lookup (OpenCNAM)
- [x] Social Media Profile Linker
- [x] Email OSINT
- [x] Username Search

### Export
- [x] PDF-Bericht (ReportLab)
- [x] SVG-Graph-Export
- [x] PNG-Graph-Export (Pillow)

### Qualität
- [x] Backend-Unit-Tests mit HTTP-Mocking (respx)
- [x] API-Integrationstests (alle Endpunkte)
- [x] Playwright E2E-Tests (Chromium)
- [x] ESLint + TypeScript strict mode
- [x] ruff + mypy für Backend

---

## Could Have (C) ⏳

*Nicht in v1.0.0 — geplant für v1.1+*

### Sicherheit & Anonymität
- [ ] Tor/SOCKS5-Proxy-Unterstützung pro Transform-Modul
- [ ] Rate-Limiting auf API-Endpunkten (FastAPI Middleware)
- [ ] Authentifizierung (Username + Password für den Web-Zugang)
- [ ] HTTPS-Terminierung im Docker-Setup (Caddy/Nginx)

### Graph
- [ ] Multi-Node-Selektion (Shift+Click / Drag-Select)
- [ ] Kanten-Filter nach Transform-Typ
- [ ] Knoten-Suche / Filter im Graphen
- [ ] Undo/Redo für Graphoperationen
- [ ] PNG-Export direkt aus dem Cytoscape-Canvas (clientseitig)

### Transforms
- [ ] Google Dorking mit tatsächlicher Abfrage (nicht nur URL-Generierung)
- [ ] Sherlock-Integration für Username-Suche (300+ Plattformen)
- [ ] Holehe-Integration für E-Mail-OSINT
- [ ] Truecaller-Reverse-Lookup
- [ ] Viber-Registrierungscheck
- [ ] Social Graph Expansion (vollständige Implementierung)

### Fallverwaltung
- [ ] Markdown-Notizen-Editor in der UI
- [ ] Case-Tagging und Filterung
- [ ] Case-Vorlagen / Templates
- [ ] Case-Import aus JSON

### UX
- [ ] Dark/Light-Mode-Umschalter (derzeit nur Dark)
- [ ] Keyboard-Shortcuts (z.B. Del zum Löschen, Strg+Z Undo)
- [ ] Globale Suche über alle Cases und Entitäten
- [ ] Node-Kommentare / Annotationen

---

## Won't Have (W) 🚫

*Explizit ausgeschlossen für v1.x*

| Feature | Begründung |
|---------|-----------|
| Cloud-Hosting / SaaS | Widerspricht dem Self-Hosted-Prinzip |
| Multi-User mit Rollen | Erhöht Komplexität massiv; PHANTOM ist Single-User/Team |
| Mobile App (iOS/Android) | Kein sinnvoller Anwendungsfall für OSINT-Grapharbeit |
| Automatische Echtzeit-Überwachung | Passive OSINT, kein kontinuierliches Monitoring |
| Offensive Exploit-Integration | Außerhalb des legalen OSINT-Scopes |
| Browser-Extension | Separates Projekt; zu hohe Maintenance-Last |
| Öffentliche API ohne Auth | Sicherheitsrisiko für sensitive Untersuchungsdaten |
| Windows-Native-App (Electron) | Docker reicht; keine Electron-Komplexität gewünscht |

---

## Zusammenfassung v1.0.0

| Kategorie | Gesamt | Umgesetzt | Quote |
|-----------|--------|-----------|-------|
| Must Have | 25 | 25 | 100% |
| Should Have | 20 | 20 | 100% |
| Could Have | 22 | 0 | — (geplant v1.1+) |
| Won't Have | 8 | 0 | — (bewusst) |
