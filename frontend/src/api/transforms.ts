import { api } from './client'
import type { TransformInfo } from '../types'

export const transformsApi = {
  list: () => api.get<TransformInfo[]>('/api/transforms').then(r => r.data),
  forEntity: (type: string) =>
    api.get<TransformInfo[]>(`/api/transforms/entity/${type}`).then(r => r.data),
  run: (caseId: string, nodeId: string, transformName: string) =>
    api
      .post('/api/transforms/run', {
        case_id: caseId,
        node_id: nodeId,
        transform_name: transformName,
      })
      .then(r => r.data),
  jobStatus: (jobId: string) =>
    api.get(`/api/transforms/job/${jobId}`).then(r => r.data),
}
