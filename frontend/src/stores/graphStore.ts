import { create } from 'zustand'
import type { GraphNode, GraphEdge, Case } from '../types'

interface GraphStore {
  nodes: GraphNode[]
  edges: GraphEdge[]
  selectedNodeId: string | null
  activeCase: Case | null
  cases: Case[]
  isLoading: boolean
  contextMenu: { x: number; y: number; nodeId: string } | null

  setNodes: (nodes: GraphNode[]) => void
  setEdges: (edges: GraphEdge[]) => void
  addNode: (node: GraphNode) => void
  addEdge: (edge: GraphEdge) => void
  removeNode: (id: string) => void
  selectNode: (id: string | null) => void
  setActiveCase: (c: Case | null) => void
  setCases: (cases: Case[]) => void
  setLoading: (v: boolean) => void
  setContextMenu: (menu: { x: number; y: number; nodeId: string } | null) => void
}

export const useGraphStore = create<GraphStore>((set) => ({
  nodes: [],
  edges: [],
  selectedNodeId: null,
  activeCase: null,
  cases: [],
  isLoading: false,
  contextMenu: null,

  setNodes: (nodes) => set({ nodes }),
  setEdges: (edges) => set({ edges }),
  addNode: (node) =>
    set((s) => ({ nodes: [...s.nodes.filter((n) => n.id !== node.id), node] })),
  addEdge: (edge) =>
    set((s) => ({ edges: [...s.edges.filter((e) => e.id !== edge.id), edge] })),
  removeNode: (id) =>
    set((s) => ({
      nodes: s.nodes.filter((n) => n.id !== id),
      edges: s.edges.filter((e) => e.source_id !== id && e.target_id !== id),
    })),
  selectNode: (id) => set({ selectedNodeId: id }),
  setActiveCase: (c) => set({ activeCase: c }),
  setCases: (cases) => set({ cases }),
  setLoading: (v) => set({ isLoading: v }),
  setContextMenu: (menu) => set({ contextMenu: menu }),
}))
