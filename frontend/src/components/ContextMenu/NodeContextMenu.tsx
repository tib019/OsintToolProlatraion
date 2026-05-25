import { useEffect, useRef, useState } from 'react'
import { useGraphStore } from '../../stores/graphStore'
import { transformsApi } from '../../api/transforms'
import type { TransformInfo } from '../../types'

export function NodeContextMenu() {
  const { contextMenu, setContextMenu, nodes, activeCase } = useGraphStore()
  const [transforms, setTransforms] = useState<TransformInfo[]>([])
  const menuRef = useRef<HTMLDivElement>(null)

  const node = contextMenu ? nodes.find((n) => n.id === contextMenu.nodeId) : null

  useEffect(() => {
    if (!node) return
    transformsApi
      .forEntity(node.entity_type)
      .then(setTransforms)
      .catch(() => setTransforms([]))
  }, [node?.entity_type, node?.id])

  useEffect(() => {
    function handleClick(e: MouseEvent) {
      if (menuRef.current && !menuRef.current.contains(e.target as Node)) {
        setContextMenu(null)
      }
    }
    function handleKey(e: KeyboardEvent) {
      if (e.key === 'Escape') setContextMenu(null)
    }
    document.addEventListener('mousedown', handleClick)
    document.addEventListener('keydown', handleKey)
    return () => {
      document.removeEventListener('mousedown', handleClick)
      document.removeEventListener('keydown', handleKey)
    }
  }, [setContextMenu])

  if (!contextMenu || !node) return null

  async function runTransform(name: string) {
    if (!activeCase || !node) return
    setContextMenu(null)
    try {
      await transformsApi.run(activeCase.id, node.id, name)
    } catch {
      // errors are silently swallowed; the WS will push results anyway
    }
  }

  function copyValue() {
    navigator.clipboard.writeText(node!.value).catch(() => {})
    setContextMenu(null)
  }

  const style: React.CSSProperties = {
    position: 'fixed',
    zIndex: 9999,
    left: Math.min(contextMenu.x, window.innerWidth - 220),
    top: Math.min(contextMenu.y, window.innerHeight - 300),
  }

  return (
    <div
      ref={menuRef}
      style={style}
      className="w-52 bg-phantom-panel border border-phantom-border rounded shadow-2xl shadow-black/60 font-mono text-xs overflow-hidden"
    >
      {/* Node header */}
      <div className="px-3 py-2 border-b border-phantom-border">
        <div className="text-phantom-accent font-bold truncate">{node.value}</div>
        <div className="text-gray-500">{node.entity_type}</div>
      </div>

      {/* Transform actions */}
      {transforms.map((t) => (
        <button
          key={t.name}
          onClick={() => void runTransform(t.name)}
          className="w-full text-left px-3 py-1.5 text-gray-300 hover:bg-phantom-accent/10 hover:text-phantom-accent transition-colors flex items-center gap-2"
        >
          <span className="text-phantom-accent">▶</span>
          {t.name}
        </button>
      ))}

      {/* Utility actions */}
      <div className="border-t border-phantom-border">
        <button
          onClick={copyValue}
          className="w-full text-left px-3 py-1.5 text-gray-400 hover:bg-phantom-panel hover:text-gray-200 transition-colors"
        >
          ⧉ Copy value
        </button>
      </div>
    </div>
  )
}
