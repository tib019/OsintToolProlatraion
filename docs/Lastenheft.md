# Lastenheft — PHANTOM OSINT Investigation Platform

**Dokument-Typ:** Lastenheft (Anforderungsspezifikation)
**Version:** 1.0.0
**Datum:** Mai 2026
**Auftraggeber:** Tobias Heiko Buss
**Erstellt von:** Tobias Heiko Buss

---

## 1. Projektüberblick

### 1.1 Projektbezeichnung

**PHANTOM** — Self-hosted OSINT Investigation Platform

### 1.2 Projektanlass

Open-Source-OSINT-Tools existieren zwar (Maltego, SpiderFoot, theHarvester), sind jedoch entweder:
- kostenpflichtig / Cloud-gebunden (Datenschutzproblem),
- auf Einzelfunktionen beschränkt,
- nicht grafisch (CLI-only),
- oder nicht erweiterbar ohne proprietäre Schnittstellen.

Ein Investigator benötigt eine **selbst gehostete, vollständig integrierte Plattform**, die Graphvisualisierung, automatisierte OSINT-Transforms und Fallverwaltung in einer einzigen Oberfläche vereint — ohne Abhängigkeit von externen Diensten.

### 1.3 Projektziel

Entwicklung einer webbasierten OSINT-Plattform, die es Ermittlern, Sicherheitsforschern und OSINT-Analysten ermöglicht, Untersuchungen visuell als Graph zu führen, automatisiert Daten über Entitäten (Personen, Telefonnummern, E-Mail-Adressen, IP-Adressen etc.) zu sammeln und Erkenntnisse strukturiert zu exportieren.

---

## 2. Ist-Zustand / Ausgangssituation

### 2.1 Problemstellung

| Problem | Auswirkung |
|---------|-----------|
| Manuelle Recherche über viele Browser-Tabs | Erkenntnisse gehen verloren, kein roter Faden |
| Keine Verbindung zwischen Entitäten sichtbar | Zusammenhänge werden übersehen |
| OSINT-Tools nicht integriert | Ergebnisse müssen manuell zusammengefügt werden |
| Cloud-Abhängigkeit bestehender Tools | Sensible Daten verlassen die eigene Infrastruktur |
| Keine Dokumentation der Untersuchungsschritte | Nachvollziehbarkeit fehlt (Audit Trail) |

### 2.2 Betroffene Nutzergruppen

| Nutzergruppe | Beschreibung |
|-------------|-------------|
| OSINT-Analysten | Professionelle Open-Source-Nachrichtendienstler |
| IT-Security-Researcher | Penetration Tester, Red Team, Threat Intelligence |
| Journalisten / Investigative Reporter | Recherche zu Personen und Organisationen |
| Private Investigators | Lizenzierte Privatdetektive |
| Strafverfolgungsbehörden (intern) | Vorfeldermittlung mit öffentlichen Quellen |

---

## 3. Anforderungen

### 3.1 Funktionale Anforderungen

#### 3.1.1 Fallverwaltung (Case Management)

| ID | Anforderung | Priorität |
|----|-------------|----------|
| FA-01 | Das System MUSS mehrere unabhängige Untersuchungsfälle verwalten können | MUSS |
| FA-02 | Jeder Fall MUSS einen Namen, eine Beschreibung, Tags und Markdown-Notizen haben | MUSS |
| FA-03 | Fälle MÜSSEN persistent gespeichert werden (PostgreSQL) | MUSS |
| FA-04 | Das System MUSS einen vollständigen Audit-Trail aller Aktionen je Fall führen | MUSS |
| FA-05 | Fälle MÜSSEN löschbar sein (inkl. aller zugehörigen Graphdaten) | MUSS |

#### 3.1.2 Graphvisualisierung

| ID | Anforderung | Priorität |
|----|-------------|----------|
| FA-10 | Das System MUSS Entitäten als Knoten in einem interaktiven Graphen darstellen | MUSS |
| FA-11 | Beziehungen zwischen Entitäten MÜSSEN als gerichtete Kanten dargestellt werden | MUSS |
| FA-12 | Der Graph MUSS mindestens 3 Layout-Algorithmen unterstützen (Force, Tree, Radial) | MUSS |
| FA-13 | Knoten-Positionen MÜSSEN persistent gespeichert werden | MUSS |
| FA-14 | Der Graph MUSS Echtzeit-Updates über WebSocket empfangen | MUSS |
| FA-15 | Knoten MÜSSEN per Rechtsklick-Kontextmenü ansprechbar sein | SOLL |
| FA-16 | Der Graph MUSS nach PNG, SVG und JSON exportierbar sein | MUSS |

#### 3.1.3 Entitätstypen

Das System MUSS folgende 10 Entitätstypen unterstützen:

`PhoneNumber` · `EmailAddress` · `Person` · `Username` · `SocialProfile` · `IPAddress` · `Domain` · `Organization` · `Location` · `LeakRecord`

#### 3.1.4 OSINT-Transforms

| ID | Anforderung | Priorität |
|----|-------------|----------|
| FA-20 | Das System MUSS automatisierte Transforms auf Entitäten ausführen können | MUSS |
| FA-21 | Transforms MÜSSEN asynchron (im Hintergrund) laufen | MUSS |
| FA-22 | Transform-Ergebnisse MÜSSEN automatisch als Knoten+Kanten in den Graphen eingefügt werden | MUSS |
| FA-23 | Das System MUSS Phone-OSINT unterstützen (Carrier, Plattform-Check, CNAM, Leak-Check) | MUSS |
| FA-24 | Das System MUSS E-Mail-OSINT unterstützen (HaveIBeenPwned, Holehe-Äquivalent) | MUSS |
| FA-25 | Das System MUSS IP/Domain-OSINT unterstützen (WHOIS, DNS, Shodan, Geo) | MUSS |
| FA-26 | Das System MUSS Username-Suche auf 300+ Plattformen unterstützen | SOLL |
| FA-27 | Transforms MÜSSEN konfigurierbare API-Keys nutzen | MUSS |

#### 3.1.5 Einstellungen

| ID | Anforderung | Priorität |
|----|-------------|----------|
| FA-30 | API-Keys MÜSSEN verschlüsselt in der Datenbank gespeichert werden | MUSS |
| FA-31 | Module (Transforms) MÜSSEN einzeln aktiviert/deaktiviert werden können | SOLL |
| FA-32 | API-Keys MÜSSEN über die UI gesetzt, aktualisiert und gelöscht werden können | MUSS |

#### 3.1.6 Export

| ID | Anforderung | Priorität |
|----|-------------|----------|
| FA-40 | Das System MUSS den Graphen als JSON exportieren | MUSS |
| FA-41 | Das System MUSS Entitätslisten als CSV exportieren | MUSS |
| FA-42 | Das System SOLL einen PDF-Bericht erzeugen können | SOLL |
| FA-43 | Das System SOLL den Graphen als SVG/PNG exportieren können | SOLL |

### 3.2 Nicht-funktionale Anforderungen

#### 3.2.1 Performance

| ID | Anforderung |
|----|-------------|
| NFA-01 | Die Web-Oberfläche MUSS innerhalb von 2 Sekunden nach Seitenaufruf vollständig geladen sein |
| NFA-02 | Graph-Rendering MUSS bis zu 500 Knoten flüssig (≥ 30 FPS) darstellen |
| NFA-03 | Transform-Ergebnisse MÜSSEN innerhalb von 30 Sekunden im Graph erscheinen |
| NFA-04 | API-Antwortzeiten MÜSSEN unter 200 ms für CRUD-Operationen liegen |

#### 3.2.2 Sicherheit

| ID | Anforderung |
|----|-------------|
| NFA-10 | Alle API-Keys MÜSSEN AES-256-verschlüsselt gespeichert werden |
| NFA-11 | Das System MUSS vollständig self-hosted betreibbar sein (kein Cloud-Zwang) |
| NFA-12 | Keine Nutzerdaten dürfen die eigene Infrastruktur ohne explizite Nutzerkonfiguration verlassen |
| NFA-13 | Das System SOLL Tor/SOCKS5-Proxy-Unterstützung pro Modul bieten |

#### 3.2.3 Betrieb

| ID | Anforderung |
|----|-------------|
| NFA-20 | Das System MUSS mittels Docker Compose in ≤ 5 Minuten deploybar sein |
| NFA-21 | Das System MUSS auf Linux, macOS und Windows (Docker) lauffähig sein |
| NFA-22 | Alle Konfigurationen MÜSSEN über eine `.env`-Datei steuerbar sein |

#### 3.2.4 Qualität

| ID | Anforderung |
|----|-------------|
| NFA-30 | Der Backend-Code MUSS eine Test-Coverage von ≥ 80% kritischer Pfade haben |
| NFA-31 | Die API MUSS vollständig durch automatische Tests abgedeckt sein |
| NFA-32 | CI/CD MUSS bei jedem Push automatisch Lint, Tests und Docker-Build prüfen |

---

## 4. Abgrenzung

### 4.1 Was PHANTOM NICHT ist

- Kein automatisiertes Hacking-Tool (keine Exploits, kein Scanning ohne Erlaubnis)
- Keine zentrale Cloud-Plattform (kein SaaS-Angebot geplant)
- Kein Echtzeit-Social-Media-Monitor
- Keine juristische Beratung — Nutzer sind für Rechtskonformität selbst verantwortlich

### 4.2 Rechtlicher Hinweis

PHANTOM ist ausschließlich für **autorisierte OSINT-Untersuchungen, Sicherheitsforschung und defensive Anwendungsfälle** konzipiert. Alle Transforms operieren auf öffentlich zugänglichen Daten oder erfordern explizite API-Autorisierung.

---

## 5. Lieferumfang

| Komponente | Beschreibung |
|-----------|-------------|
| Backend | FastAPI (Python 3.11), async, REST + WebSocket |
| Frontend | React 18 + TypeScript + Vite + Cytoscape.js |
| Datenbank | PostgreSQL 16 mit SQLAlchemy 2.0 |
| Cache | Redis 7 |
| Container | Docker + docker-compose |
| CI/CD | GitHub Actions (Lint, Tests, Docker Build, E2E) |
| Dokumentation | Lastenheft, Pflichtenheft, MoSCoW, Bedienungsanleitung |

---

## 6. Abnahmekriterien

Das Projekt gilt als abgenommen, wenn:

1. ✅ Alle 9 Entwicklungsphasen abgeschlossen sind
2. ✅ Alle automatischen Tests (Backend + E2E) grün sind
3. ✅ Docker-Compose-Deployment ohne manuelle Eingriffe startet
4. ✅ Alle 10 OSINT-Transforms registriert und funktionsfähig sind
5. ✅ Export in allen 5 Formaten (JSON, CSV, PDF, SVG, PNG) funktioniert
6. ✅ Settings-Panel API-Keys korrekt speichert und abruft
7. ✅ Timeline Audit-Events in Echtzeit anzeigt
