export type EntityType =
  | 'PhoneNumber'
  | 'EmailAddress'
  | 'Person'
  | 'Username'
  | 'SocialProfile'
  | 'IPAddress'
  | 'Domain'
  | 'Organization'
  | 'Location'
  | 'LeakRecord'

export interface GraphNode {
  id: string
  entity_type: EntityType
  value: string
  label: string
  properties: Record<string, unknown>
  pos_x?: number
  pos_y?: number
  created_at: string
}

export interface GraphEdge {
  id: string
  case_id: string
  source_id: string
  target_id: string
  label: string
  transform_name: string
  created_at: string
}

export interface Case {
  id: string
  name: string
  description?: string
  tags: string[]
  notes_md?: string
  node_count: number
  created_at: string
  updated_at: string
}

export interface TransformInfo {
  name: string
  description: string
  input_types: string[]
  output_types: string[]
  timeout: number
  rate_limit: number
}

export interface WsEvent {
  type: string
  payload: unknown
}
