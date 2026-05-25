import { api } from './client'
import type { GraphNode, GraphEdge } from '../types'

export const graphApi = {
  addNode: (
    caseId: string,
    data: {
      entity_type: string
      value: string
      label: string
      properties?: Record<string, unknown>
    }
  ) => api.post<GraphNode>(`/api/graph/${caseId}/nodes`, data).then(r => r.data),

  removeNode: (caseId: string, nodeId: string) =>
    api.delete(`/api/graph/${caseId}/nodes/${nodeId}`),

  addEdge: (
    caseId: string,
    data: {
      source_id: string
      target_id: string
      label: string
      transform_name: string
    }
  ) => api.post<GraphEdge>(`/api/graph/${caseId}/edges`, data).then(r => r.data),

  updatePosition: (caseId: string, nodeId: string, x: number, y: number) =>
    api.patch(`/api/graph/${caseId}/nodes/${nodeId}/position`, { x, y }),
}
