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
  type: EntityType
  value: string
  label: string
  properties: Record<string, unknown>
  position?: { x: number; y: number }
}

export interface GraphEdge {
  id: string
  source: string
  target: string
  label: string
  transform: string
}

export interface Case {
  id: string
  name: string
  description: string
  tags: string[]
  createdAt: string
  updatedAt: string
}

export interface Transform {
  id: string
  name: string
  description: string
  inputTypes: EntityType[]
  outputTypes: EntityType[]
}

export interface TransformResult {
  entities: GraphNode[]
  edges: GraphEdge[]
  error?: string
  durationMs: number
}
