# Bedienungsanleitung — PHANTOM OSINT Investigation Platform

**Version:** 1.0.0  
**Datum:** Mai 2026

---

## 1. Installation und Start

### 1.1 Voraussetzungen

| Anforderung | Mindestversion |
|-------------|---------------|
| Docker | 24.0+ |
| docker-compose | v2.0+ |
| RAM | 4 GB |
| Festplatte | 10 GB freier Speicher |

### 1.2 Setup (einmalig)

```bash
# 1. Repository klonen
git clone https://github.com/tib019/OsintToolProlatraion.git
cd OsintToolProlatraion

# 2. Umgebungskonfiguration erstellen
cp .env.example .env

# 3. (Optional) API-Keys in .env eintragen
#    Alle Keys sind optional — PHANTOM startet auch ohne sie
nano .env

# 4. Starten
make up
#  oder: docker compose up -d --build

# 5. Browser öffnen
open http://localhost:3000
```

### 1.3 Makefile-Befehle

| Befehl | Beschreibung |
|--------|-------------|
| `make up` | Alle Services starten (mit Build falls nötig) |
| `make down` | Alle Services stoppen |
| `make build` | Images neu bauen |
| `make logs` | Live-Logs aller Services |
| `make shell` | Backend-Shell öffnen |
| `make psql` | PostgreSQL-Shell öffnen |
| `make reset` | Datenbank komplett zurücksetzen und neu starten |

### 1.4 Dienst-Übersicht

| Dienst | URL | Beschreibung |
|--------|-----|-------------|
| Frontend | http://localhost:3000 | Web-Oberfläche |
| Backend API | http://localhost:8000 | REST-API |
| API-Docs | http://localhost:8000/docs | Swagger UI |
| API-Docs | http://localhost:8000/redoc | ReDoc |

---

## 2. Oberfläche im Überblick

```
┌─────────────────────────────────────────────────────────────────┐
│  PHANTOM  │  Fallname  │  42n · 18e  │  Force Tree Radial  │↓⚙ │
├───────────┬─────────────────────────────────────────┬───────────┤
│  PHANTOM  │                                         │  NODE     │
│           │                                         │  DETAILS  │
│  Cases    │                                         │           │
│  ──────   │          GRAPH CANVAS                   │  Transforms│
│  + New    │         (Cytoscape.js)                  │           │
│           │                                         │  Properties│
│  Add Node │                                         │           │
│  ──────   │                                         │           │
│  Entity   │                                         │           │
│  Types    │                                         │           │
└───────────┴─────────────────────────────────────────┴───────────┤
│  TIMELINE ▼  node_added · transform_completed · edge_added ...  │
└─────────────────────────────────────────────────────────────────┘
```

### 2.1 TopBar

| Element | Funktion |
|---------|---------|
| PHANTOM (Puls-Dot) | Branding / Verbindungsstatus |
| Fallname | Aktiver Fall |
| `42n · 18e` | Anzahl Knoten und Kanten |
| Force / Tree / Radial | Graph-Layout wechseln |
| `↓ Export` | Export-Dropdown (JSON, CSV, PDF, SVG, PNG) |
| `⚙` | Settings-Panel öffnen |

### 2.2 LeftSidebar

| Bereich | Funktion |
|---------|---------|
| Cases | Alle vorhandenen Fälle auflisten und wechseln |
| + New | Neuen Fall erstellen |
| Add Node | Knoten manuell zum aktiven Fall hinzufügen |
| Entity Types | Legende der Entitätstypen mit Farbzuordnung |
| ◀ (oben rechts) | Sidebar einklappen |

### 2.3 RightSidebar

Erscheint sobald ein Knoten ausgewählt wird. Zeigt:
- Entitätstyp und Farbe
- Wert und Erstellungszeitpunkt
- Properties (Key-Value aus Transform-Ergebnissen)
- Verfügbare Transforms mit **▶ Run**-Button

### 2.4 Timeline

Kollabierbare Leiste am unteren Rand. Zeigt alle Audit-Ereignisse des aktiven Falls in Echtzeit:

| Ereignis | Symbol | Farbe |
|---------|--------|-------|
| `node_added` | ⊕ | Grün |
| `node_removed` | ⊖ | Rot |
| `edge_added` | → | Lila |
| `transform_queued` | ⏳ | Gelb |
| `transform_completed` | ✓ | Akzent (Gelbgrün) |
| `transform_failed` | ✗ | Rot |

---

## 3. Erster Start — Schritt für Schritt

### Schritt 1: Fall erstellen

1. Klicke auf **+ New** in der linken Sidebar
2. Gib einen Fallnamen ein (z.B. `"Untersuchung Alpha"`)
3. Drücke **Enter** oder klicke ✓
4. Der Fall erscheint in der Liste und wird automatisch aktiviert

### Schritt 2: Startknoten hinzufügen

1. Im **Add Node**-Bereich (linke Sidebar):
   - Wähle den Entitätstyp (z.B. `PhoneNumber`)
   - Gib den Wert ein (z.B. `+4915123456789`)
   - Drücke **Enter** oder **+ Add to Graph**
2. Der Knoten erscheint im Graphen

### Schritt 3: Transform ausführen

**Option A — Rechtsklick auf Knoten:**
1. Rechtsklick auf einen Knoten im Graph
2. Kontextmenü zeigt verfügbare Transforms
3. Klicke auf den gewünschten Transform (z.B. `"PhoneInfoga Scanner"`)
4. Ergebnisse erscheinen automatisch als neue Knoten

**Option B — RightSidebar:**
1. Knoten per Linksklick auswählen
2. In der rechten Sidebar erscheint die Transform-Liste
3. Klicke **▶ Run** neben dem gewünschten Transform
4. Spinner zeigt laufende Ausführung an
5. Neue Knoten und Kanten erscheinen live im Graph

### Schritt 4: Ergebnis exportieren

1. Klicke **↓ Export** in der TopBar
2. Wähle das Format:
   - **JSON** — vollständiger Case-Dump (alle Daten)
   - **CSV** — Tabelle aller Knoten und Kanten
   - **PDF** — formatierter Untersuchungsbericht
   - **SVG** — vektorielle Graph-Darstellung
   - **PNG** — Raster-Graph-Darstellung

---

## 4. API-Keys konfigurieren

Viele Transforms funktionieren ohne API-Keys (Best-Effort), liefern aber mit Keys deutlich bessere Ergebnisse.

### 4.1 Keys über das Settings-Panel setzen

1. Klicke **⚙** in der TopBar
2. Tab **API Keys** ist standardmäßig aktiv
3. Gib den Key im entsprechenden Feld ein
4. Klicke **Save**
5. Status wechselt auf **active** (grün)

### 4.2 Verfügbare API-Keys

| Key | Dienst | Verwendet von | Signup |
|-----|--------|--------------|--------|
| `NUMVERIFY_API_KEY` | Numverify | PhoneInfoga Scanner | numverify.com |
| `SHODAN_API_KEY` | Shodan | IP/Domain Intelligence | shodan.io |
| `OPENCNAM_SID` + `OPENCNAM_AUTH_TOKEN` | OpenCNAM | CNAM Lookup | opencnam.com |
| `HIBP_API_KEY` | HaveIBeenPwned | Leak Database Check | haveibeenpwned.com/API/Key |
| `TELEGRAM_BOT_TOKEN` | Telegram Bot API | Platform Checker, Social Linker | t.me/BotFather |

### 4.3 Keys über `.env` setzen (alternativ)

```env
NUMVERIFY_API_KEY=dein-key-hier
SHODAN_API_KEY=dein-key-hier
OPENCNAM_SID=deine-sid
OPENCNAM_AUTH_TOKEN=dein-token
HIBP_API_KEY=dein-key-hier
TELEGRAM_BOT_TOKEN=dein-token
```

Nach Änderungen: `make down && make up`

---

## 5. Module aktivieren/deaktivieren

1. Klicke **⚙** in der TopBar
2. Tab **Modules** wählen
3. Toggle-Switch neben dem gewünschten Modul umlegen
4. Deaktivierte Module erscheinen nicht mehr im Kontextmenü

| Modul | Beschreibung |
|-------|-------------|
| `phone_lookup` | Alle Phone-OSINT-Transforms |
| `email_lookup` | E-Mail-OSINT-Transforms |
| `domain_lookup` | IP/Domain-Transforms |
| `ip_lookup` | IP-spezifische Transforms |
| `social_lookup` | Social-Media-Transforms |
| `leak_check` | HaveIBeenPwned-Integration |

---

## 6. Graph-Bedienung

### 6.1 Navigation

| Aktion | Geste / Shortcut |
|--------|-----------------|
| Zoomen | Mausrad |
| Graph verschieben | Klicken + Ziehen (Hintergrund) |
| Knoten verschieben | Knoten anklicken + ziehen |
| Knoten auswählen | Linksklick auf Knoten |
| Auswahl aufheben | Klick auf leere Fläche |
| Kontextmenü öffnen | Rechtsklick auf Knoten |
| Kontextmenü schließen | ESC oder Klick außerhalb |

### 6.2 Layout wechseln

| Layout | Eignung |
|--------|---------|
| **Force** (Standard) | Allgemein, zeigt Cluster gut |
| **Tree** | Hierarchische Beziehungen (z.B. Domainstruktur) |
| **Radial** | Übersicht bei vielen Verbindungen von einem Knoten |

### 6.3 Entitätstypen und Farben

| Typ | Farbe |
|-----|-------|
| PhoneNumber | Grün |
| EmailAddress | Blau |
| Person | Gelb |
| Username | Orange |
| SocialProfile | Lila |
| IPAddress | Rot |
| Domain | Grau |
| Organization | Cyan |
| Location | Teal |
| LeakRecord | Dunkelrot |

---

## 7. OSINT-Transforms Referenz

### 7.1 Phone-Transforms

#### PhoneInfoga Scanner
- **Input:** PhoneNumber
- **Output:** PhoneNumber (angereichert), Organization (Carrier), Location
- **Ohne Key:** Carrier-Name, Land, Leitungstyp, Zeitzonen (via `phonenumbers`-Library)
- **Mit `NUMVERIFY_API_KEY`:** Zusätzliche Carrier-Verifikation

#### Platform Registration Checker
- **Input:** PhoneNumber
- **Output:** SocialProfile (je Plattform)
- **Prüft:** WhatsApp, Telegram, Instagram, Amazon, Snapchat, Signal
- **Ohne Key:** WhatsApp, Instagram, Amazon, Snapchat, Signal
- **Mit `TELEGRAM_BOT_TOKEN`:** Telegram-Profil mit Username

#### CNAM / Reverse Lookup
- **Input:** PhoneNumber
- **Output:** Person (Anrufername)
- **Benötigt:** `OPENCNAM_SID` + `OPENCNAM_AUTH_TOKEN` (kostenpflichtig)

#### Leak Database Check
- **Input:** PhoneNumber, EmailAddress
- **Output:** LeakRecord (je Datenpanne)
- **Benötigt:** `HIBP_API_KEY`
- **Liefert:** Datenpannen-Name, Datum, Anzahl betroffener Konten, Datenkategorien

#### Social Media Profile Linker
- **Input:** PhoneNumber
- **Output:** SocialProfile (WhatsApp + Telegram)
- **Mit `TELEGRAM_BOT_TOKEN`:** Telegram-Profil mit Display-Name und Username

### 7.2 General-Transforms

#### IP/Domain Intelligence
- **Input:** IPAddress, Domain
- **Output:** Organization, Location, Domain, IPAddress
- **Ohne Key:** Geolokation, Reverse-DNS, DNS-Records (A, MX, NS, TXT)
- **Mit `SHODAN_API_KEY`:** Port-Scan-Ergebnisse, bekannte Schwachstellen

#### Email OSINT
- **Input:** EmailAddress
- **Output:** SocialProfile
- **Prüft Plattform-Registrierung** der E-Mail-Adresse

#### Username Search
- **Input:** Username
- **Output:** SocialProfile
- **Sucht** nach dem Username auf bekannten Plattformen

#### Google Dorking
- **Input:** Alle Entitätstypen
- **Output:** Generiert Such-URLs für Google-Dork-Abfragen

#### Social Graph Expansion
- **Input:** SocialProfile
- **Output:** SocialProfile
- **Erweitert** bekannte Social-Profile

---

## 8. Export-Formate im Detail

### JSON
```json
{
  "case": { "id": "...", "name": "...", "tags": [], ... },
  "nodes": [{ "id": "...", "entity_type": "PhoneNumber", "value": "...", ... }],
  "edges": [{ "source_id": "...", "target_id": "...", "label": "...", ... }]
}
```

### CSV
Zwei Sektionen: `=== NODES ===` und `=== EDGES ===` mit tabellarischen Daten.

### PDF
Strukturierter Bericht mit:
- Case-Metadaten (Name, Beschreibung, Erstellungsdatum)
- Markdown-Notizen (falls vorhanden)
- Tabelle aller Knoten
- Tabelle aller Kanten

### SVG / PNG
Automatisch berechnetes oder gespeichertes Layout aller Knoten und Kanten als Vektorgrafik bzw. Rasterbild.

---

## 9. Fehlerbehebung

### Services starten nicht

```bash
# Logs prüfen
make logs

# Datenbank zurücksetzen (ACHTUNG: löscht alle Daten)
make reset
```

### Backend nicht erreichbar

```bash
# Backend-Status prüfen
docker compose ps

# Logs des Backends
docker compose logs backend
```

### Transform liefert keine Ergebnisse

1. API-Key prüfen (Settings → API Keys → ist `active`?)
2. Netzwerk-Konnektivität vom Container prüfen: `make shell && curl https://api.shodan.io`
3. Timeline prüfen: Zeigt sie `transform_failed`? Error-Details sind im Metadata-Feld

### Graph lädt nicht

1. Browser-Konsole auf JavaScript-Fehler prüfen (F12)
2. Backend-API direkt testen: http://localhost:8000/docs
3. Prüfen ob der Fall Knoten hat: `GET /api/cases/{id}/graph`

---

## 10. Technische Informationen

### Daten-Backup

```bash
# PostgreSQL-Dump erstellen
docker compose exec postgres pg_dump -U phantom phantom_db > backup.sql

# Wiederherstellen
docker compose exec -T postgres psql -U phantom phantom_db < backup.sql
```

### Datenbankzugriff

```bash
make psql
# → psql als phantom-User auf phantom_db
```

### API direkt nutzen (Swagger)

Alle API-Endpunkte sind unter http://localhost:8000/docs interaktiv dokumentiert und testbar.
