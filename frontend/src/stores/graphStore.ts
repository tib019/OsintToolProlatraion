import { create } from 'zustand'
import type { GraphNode, GraphEdge, Case } from '../types'

interface GraphState {
  nodes: GraphNode[]
  edges: GraphEdge[]
  selectedNodes: string[]
  activeCase: Case | null
  isLoading: boolean

  addNode: (node: GraphNode) => void
  addEdge: (edge: GraphEdge) => void
  selectNode: (id: string) => void
  clearSelection: () => void
  setActiveCase: (c: Case | null) => void
  setLoading: (v: boolean) => void
}

export const useGraphStore = create<GraphState>((set) => ({
  nodes: [],
  edges: [],
  selectedNodes: [],
  activeCase: null,
  isLoading: false,

  addNode: (node) => set((s) => ({ nodes: [...s.nodes, node] })),
  addEdge: (edge) => set((s) => ({ edges: [...s.edges, edge] })),
  selectNode: (id) => set((s) => ({ selectedNodes: [...s.selectedNodes, id] })),
  clearSelection: () => set({ selectedNodes: [] }),
  setActiveCase: (c) => set({ activeCase: c }),
  setLoading: (v) => set({ isLoading: v }),
}))
