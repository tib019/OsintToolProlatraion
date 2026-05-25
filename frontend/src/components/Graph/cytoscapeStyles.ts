import * as cytoscape from 'cytoscape'

export const ENTITY_COLORS: Record<string, string> = {
  PhoneNumber: '#22c55e',
  EmailAddress: '#3b82f6',
  Person: '#eab308',
  Username: '#f97316',
  SocialProfile: '#a855f7',
  IPAddress: '#ef4444',
  Domain: '#6b7280',
  Organization: '#06b6d4',
  Location: '#14b8a6',
  LeakRecord: '#991b1b',
}

// StylesheetStyle & StylesheetCSS are both assignable to this union
type AnyStylesheet = cytoscape.StylesheetStyle | cytoscape.StylesheetCSS

export const cytoscapeStyles: AnyStylesheet[] = [
  {
    selector: 'node',
    style: {
      'background-color': (ele: cytoscape.NodeSingular) =>
        ENTITY_COLORS[ele.data('entity_type') as string] || '#6b7280',
      label: 'data(label)',
      color: '#e5e7eb',
      'font-size': '11px',
      'font-family': 'JetBrains Mono, monospace',
      'text-valign': 'bottom',
      'text-margin-y': 4,
      width: 40,
      height: 40,
      'border-width': 2,
      'border-color': '#2a2a2a',
      'text-wrap': 'ellipsis',
      'text-max-width': '100px',
    },
  },
  {
    selector: 'node:selected',
    style: {
      'border-color': '#f59e0b',
      'border-width': 3,
      'overlay-color': '#f59e0b',
      'overlay-opacity': 0.1,
    },
  },
  {
    selector: 'edge',
    style: {
      width: 1.5,
      'line-color': '#374151',
      'target-arrow-color': '#374151',
      'target-arrow-shape': 'triangle',
      'curve-style': 'bezier',
      label: 'data(label)',
      'font-size': '9px',
      color: '#9ca3af',
      'font-family': 'JetBrains Mono, monospace',
      'text-rotation': 'autorotate',
    },
  },
  {
    selector: 'edge:selected',
    style: {
      'line-color': '#f59e0b',
      'target-arrow-color': '#f59e0b',
    },
  },
]
