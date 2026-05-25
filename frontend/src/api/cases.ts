import { api } from './client'
import type { Case, GraphNode, GraphEdge } from '../types'

export const casesApi = {
  list: () => api.get<Case[]>('/api/cases').then(r => r.data),
  get: (id: string) => api.get<Case>(`/api/cases/${id}`).then(r => r.data),
  create: (data: { name: string; description?: string; tags?: string[] }) =>
    api.post<Case>('/api/cases', data).then(r => r.data),
  update: (id: string, data: Partial<Case>) =>
    api.patch<Case>(`/api/cases/${id}`, data).then(r => r.data),
  delete: (id: string) => api.delete(`/api/cases/${id}`),
  getGraph: (id: string) =>
    api.get<{ nodes: GraphNode[]; edges: GraphEdge[] }>(`/api/cases/${id}/graph`).then(r => r.data),
  getAudit: (id: string) => api.get(`/api/cases/${id}/audit`).then(r => r.data),
}
