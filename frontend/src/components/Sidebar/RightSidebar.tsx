import { useState, useEffect } from 'react'
import { useGraphStore } from '../../stores/graphStore'
import { transformsApi } from '../../api/transforms'
import type { TransformInfo } from '../../types'
import { ENTITY_COLORS } from '../Graph/cytoscapeStyles'

export function RightSidebar() {
  const { nodes, selectedNodeId, activeCase } = useGraphStore()
  const [transforms, setTransforms] = useState<TransformInfo[]>([])
  const [running, setRunning] = useState<string | null>(null)

  const selectedNode = nodes.find((n) => n.id === selectedNodeId)

  useEffect(() => {
    if (!selectedNode) {
      setTransforms([])
      return
    }
    transformsApi
      .forEntity(selectedNode.entity_type)
      .then(setTransforms)
      .catch(() => setTransforms([]))
  }, [selectedNode])

  async function runTransform(name: string) {
    if (!activeCase || !selectedNodeId) return
    setRunning(name)
    try {
      await transformsApi.run(activeCase.id, selectedNodeId, name)
    } finally {
      setRunning(null)
    }
  }

  if (!selectedNode) {
    return (
      <div className="w-72 h-full bg-phantom-surface border-l border-phantom-border flex items-center justify-center font-mono flex-shrink-0">
        <div className="text-center text-gray-600 text-xs">
          <div className="text-2xl mb-2 opacity-40">◎</div>
          <div>Select a node</div>
        </div>
      </div>
    )
  }

  const color = ENTITY_COLORS[selectedNode.entity_type] || '#6b7280'

  return (
    <div className="w-72 h-full bg-phantom-surface border-l border-phantom-border flex flex-col font-mono text-sm overflow-hidden flex-shrink-0">
      {/* Node identity */}
      <div className="px-3 py-3 border-b border-phantom-border">
        <div className="flex items-center gap-2 mb-2">
          <span
            className="w-3 h-3 rounded-full flex-shrink-0"
            style={{ backgroundColor: color }}
          />
          <span className="text-xs text-gray-400 uppercase tracking-wider">
            {selectedNode.entity_type}
          </span>
        </div>
        <div className="text-gray-100 font-bold text-sm break-all mb-1">{selectedNode.value}</div>
        <div className="text-gray-500 text-xs">
          {new Date(selectedNode.created_at).toLocaleString()}
        </div>
      </div>

      {/* Properties */}
      {Object.keys(selectedNode.properties).length > 0 && (
        <div className="px-3 py-2 border-b border-phantom-border">
          <div className="text-gray-400 text-xs uppercase tracking-wider mb-2">Properties</div>
          <div className="space-y-1 max-h-40 overflow-y-auto">
            {Object.entries(selectedNode.properties).map(([k, v]) => (
              <div key={k} className="flex gap-2 text-xs">
                <span className="text-gray-500 flex-shrink-0">{k}:</span>
                <span className="text-gray-200 break-all">{String(v)}</span>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Transforms */}
      <div className="px-3 py-2 flex-1 overflow-y-auto">
        <div className="text-gray-400 text-xs uppercase tracking-wider mb-2">Transforms</div>
        {transforms.length === 0 && (
          <div className="text-gray-600 text-xs">No transforms available</div>
        )}
        <div className="space-y-1.5">
          {transforms.map((t) => (
            <div
              key={t.name}
              className="bg-phantom-panel border border-phantom-border rounded p-2"
            >
              <div className="flex items-center justify-between mb-1">
                <span className="text-gray-200 text-xs font-medium truncate mr-2">{t.name}</span>
                <button
                  onClick={() => void runTransform(t.name)}
                  disabled={running === t.name}
                  className="bg-phantom-accent/20 text-phantom-accent text-xs px-2 py-0.5 rounded hover:bg-phantom-accent/30 disabled:opacity-50 border border-phantom-accent/30 font-mono flex-shrink-0 transition-colors"
                >
                  {running === t.name ? '...' : '▶ Run'}
                </button>
              </div>
              <div className="text-gray-500 text-xs">{t.description}</div>
              {t.output_types.length > 0 && (
                <div className="text-gray-600 text-xs mt-1">
                  → {t.output_types.join(', ')}
                </div>
              )}
            </div>
          ))}
        </div>
      </div>
    </div>
  )
}
