import { api } from './client'
import type { ApiKeyInfo, ModuleState } from '../types'

export const settingsApi = {
  listKeys: () => api.get<ApiKeyInfo[]>('/api/settings/api-keys').then(r => r.data),
  setKey: (service_name: string, key: string) =>
    api.post<ApiKeyInfo>('/api/settings/api-keys', { service_name, key }).then(r => r.data),
  deleteKey: (service_name: string) =>
    api.delete(`/api/settings/api-keys/${service_name}`),
  activateKey: (service_name: string) =>
    api.patch<ApiKeyInfo>(`/api/settings/api-keys/${service_name}/activate`).then(r => r.data),
  deactivateKey: (service_name: string) =>
    api.patch<ApiKeyInfo>(`/api/settings/api-keys/${service_name}/deactivate`).then(r => r.data),
  listModules: () => api.get<ModuleState[]>('/api/settings/modules').then(r => r.data),
  toggleModule: (name: string, enabled: boolean) =>
    api.patch<ModuleState>(`/api/settings/modules/${name}`, { name, enabled }).then(r => r.data),
}
