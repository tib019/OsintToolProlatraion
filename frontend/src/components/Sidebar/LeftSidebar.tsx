import { useState } from 'react'
import { useGraphStore } from '../../stores/graphStore'
import { casesApi } from '../../api/cases'
import { graphApi } from '../../api/graph'
import type { EntityType } from '../../types'
import { ENTITY_COLORS } from '../Graph/cytoscapeStyles'

const ENTITY_TYPES: EntityType[] = [
  'PhoneNumber',
  'EmailAddress',
  'Person',
  'Username',
  'SocialProfile',
  'IPAddress',
  'Domain',
  'Organization',
  'Location',
  'LeakRecord',
]

export function LeftSidebar({ onCaseSelect }: { onCaseSelect: (id: string) => void }) {
  const { cases, activeCase, setCases } = useGraphStore()
  const [collapsed, setCollapsed] = useState(false)
  const [newCaseName, setNewCaseName] = useState('')
  const [showNewCase, setShowNewCase] = useState(false)
  const [entityType, setEntityType] = useState<EntityType>('PhoneNumber')
  const [entityValue, setEntityValue] = useState('')
  const [adding, setAdding] = useState(false)

  async function handleCreateCase() {
    if (!newCaseName.trim()) return
    const c = await casesApi.create({ name: newCaseName.trim() })
    setCases([...cases, c])
    setNewCaseName('')
    setShowNewCase(false)
    onCaseSelect(c.id)
  }

  async function handleAddNode() {
    if (!entityValue.trim() || !activeCase) return
    setAdding(true)
    try {
      await graphApi.addNode(activeCase.id, {
        entity_type: entityType,
        value: entityValue.trim(),
        label: entityValue.trim(),
      })
      setEntityValue('')
    } finally {
      setAdding(false)
    }
  }

  if (collapsed) {
    return (
      <div className="w-8 h-full bg-phantom-surface border-r border-phantom-border flex flex-col items-center pt-2">
        <button
          onClick={() => setCollapsed(false)}
          className="text-phantom-accent text-xs p-1 hover:text-yellow-300"
          title="Expand sidebar"
        >
          ▶
        </button>
      </div>
    )
  }

  return (
    <div className="w-64 h-full bg-phantom-surface border-r border-phantom-border flex flex-col font-mono text-sm overflow-hidden flex-shrink-0">
      {/* Header */}
      <div className="flex items-center justify-between px-3 py-2 border-b border-phantom-border">
        <span className="text-phantom-accent font-bold text-xs tracking-wider">PHANTOM</span>
        <button
          onClick={() => setCollapsed(true)}
          className="text-gray-500 hover:text-gray-300 text-xs"
          title="Collapse sidebar"
        >
          ◀
        </button>
      </div>

      {/* Cases list */}
      <div className="px-3 py-2 border-b border-phantom-border">
        <div className="flex items-center justify-between mb-2">
          <span className="text-gray-400 text-xs uppercase tracking-wider">Cases</span>
          <button
            onClick={() => setShowNewCase(!showNewCase)}
            className="text-phantom-accent text-xs hover:text-yellow-300"
          >
            + New
          </button>
        </div>

        {showNewCase && (
          <div className="flex gap-1 mb-2">
            <input
              value={newCaseName}
              onChange={(e) => setNewCaseName(e.target.value)}
              onKeyDown={(e) => e.key === 'Enter' && void handleCreateCase()}
              placeholder="Case name..."
              className="flex-1 bg-phantom-panel border border-phantom-border text-gray-200 text-xs px-2 py-1 rounded outline-none focus:border-phantom-accent"
              autoFocus
            />
            <button
              onClick={() => void handleCreateCase()}
              className="bg-phantom-accent text-black text-xs px-2 py-1 rounded font-bold hover:bg-yellow-400"
            >
              ✓
            </button>
          </div>
        )}

        <div className="space-y-1 max-h-40 overflow-y-auto">
          {cases.map((c) => (
            <button
              key={c.id}
              onClick={() => onCaseSelect(c.id)}
              className={`w-full text-left px-2 py-1.5 rounded text-xs transition-colors ${
                activeCase?.id === c.id
                  ? 'bg-phantom-accent/20 text-phantom-accent border border-phantom-accent/30'
                  : 'text-gray-300 hover:bg-phantom-panel'
              }`}
            >
              <div className="font-medium truncate">{c.name}</div>
              <div className="text-gray-500 text-xs">{c.node_count} nodes</div>
            </button>
          ))}
          {cases.length === 0 && (
            <div className="text-gray-600 text-xs py-1">No cases yet</div>
          )}
        </div>
      </div>

      {/* Add Node panel — only shown when a case is active */}
      {activeCase && (
        <div className="px-3 py-2 border-b border-phantom-border">
          <div className="text-gray-400 text-xs uppercase tracking-wider mb-2">Add Node</div>
          <select
            value={entityType}
            onChange={(e) => setEntityType(e.target.value as EntityType)}
            className="w-full bg-phantom-panel border border-phantom-border text-gray-200 text-xs px-2 py-1 rounded mb-2 outline-none focus:border-phantom-accent"
          >
            {ENTITY_TYPES.map((t) => (
              <option key={t} value={t}>
                {t}
              </option>
            ))}
          </select>
          <input
            value={entityValue}
            onChange={(e) => setEntityValue(e.target.value)}
            onKeyDown={(e) => e.key === 'Enter' && void handleAddNode()}
            placeholder="Value..."
            className="w-full bg-phantom-panel border border-phantom-border text-gray-200 text-xs px-2 py-1 rounded mb-2 outline-none focus:border-phantom-accent"
          />
          <button
            onClick={() => void handleAddNode()}
            disabled={adding || !entityValue.trim()}
            className="w-full bg-phantom-accent text-black text-xs py-1.5 rounded font-bold hover:bg-yellow-400 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
          >
            {adding ? 'Adding...' : '+ Add to Graph'}
          </button>
        </div>
      )}

      {/* Entity type legend */}
      <div className="px-3 py-2 flex-1 overflow-y-auto">
        <div className="text-gray-400 text-xs uppercase tracking-wider mb-2">Entity Types</div>
        <div className="space-y-1">
          {ENTITY_TYPES.map((t) => (
            <div
              key={t}
              className="flex items-center gap-2 text-xs text-gray-400 hover:text-gray-200 cursor-default"
            >
              <span
                className="w-2.5 h-2.5 rounded-full flex-shrink-0"
                style={{ backgroundColor: ENTITY_COLORS[t] }}
              />
              <span>{t}</span>
            </div>
          ))}
        </div>
      </div>

      {/* Active case footer */}
      {activeCase && (
        <div className="px-3 py-2 border-t border-phantom-border">
          <div className="text-gray-600 text-xs truncate">
            Active: <span className="text-gray-400">{activeCase.name}</span>
          </div>
        </div>
      )}
    </div>
  )
}
