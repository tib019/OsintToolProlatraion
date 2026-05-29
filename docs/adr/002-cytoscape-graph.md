# ADR-002: Cytoscape.js für die Graph-Visualisierung

**Status:** Accepted  
**Datum:** 2025

## Kontext

PHANTOM visualisiert OSINT-Ermittlungen als interaktiven Graphen: Knoten repräsentieren Entitäten (Personen, Telefonnummern, IPs), Kanten repräsentieren Beziehungen zwischen ihnen. Der Graph muss:
- Mehrere hundert Knoten performant rendern
- Layouts automatisch berechnen (Force, Tree, Radial)
- Interaktion ermöglichen: Drag, Zoom, Rechtsklick-Kontextmenü, Selektion
- Graphzustand serialisierbar sein (Persistenz in PostgreSQL)

Kandidaten:
- **Cytoscape.js:** Dedizierte Graph-Library, speziell für Netzwerk-Analyse
- **D3.js (Force Simulation):** Flexibel, aber Graph-Features manuell implementieren
- **React Flow:** React-native, gut für Flussdiagramme, weniger für OSINT-Graphen
- **Vis.js (Network):** Ähnlich Cytoscape, weniger aktiv gewartet

## Entscheidung

Wir verwenden **Cytoscape.js**.

Cytoscape ist die Referenz-Library für biologische Netzwerk- und Graphanalyse und wird in wissenschaftlichen OSINT-Tools verwendet. Es liefert out-of-the-box:
- Compound Nodes (Gruppenknoten)
- `cytoscape-cola`, `cytoscape-dagre`, `cytoscape-cose-bilkent` für Force/Tree/Radial-Layouts
- Export als SVG/PNG/JSON nativ
- Event-System für Rechtsklick-Kontextmenü
- Graphzustand als JSON serialisierbar → direkt in PostgreSQL speicherbar

## Konsequenzen

**Positiv:**
- Graph-Persistenz: `cy.json()` serialisiert den kompletten Zustand
- Layout-Algorithmen ohne Eigenentwicklung
- Performance: WebGL-Renderer für große Graphen (cytoscape-webgl)
- Maltego-ähnliche UX direkt erreichbar

**Negativ:**
- Kein React-nativer State (Cytoscape verwaltet seinen eigenen DOM-unabhängigen Zustand)
- Integration mit React erfordert `useRef` + manuelle Event-Bridge
- Steile Lernkurve bei custom Layouts und Extensions
