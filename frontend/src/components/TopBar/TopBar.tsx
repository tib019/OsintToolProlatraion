import { useState } from 'react'
import { useGraphStore } from '../../stores/graphStore'

interface TopBarProps {
  onLayoutChange: (layout: string) => void
  onExport: () => void
}

const LAYOUTS: [string, string][] = [
  ['cose', 'Force'],
  ['breadthfirst', 'Tree'],
  ['circle', 'Radial'],
]

export function TopBar({ onLayoutChange, onExport }: TopBarProps) {
  const { activeCase, nodes, edges } = useGraphStore()
  const [layout, setLayout] = useState('cose')

  function changeLayout(l: string) {
    setLayout(l)
    onLayoutChange(l)
  }

  return (
    <div className="h-12 bg-phantom-surface border-b border-phantom-border flex items-center px-4 gap-4 font-mono text-xs flex-shrink-0">
      {/* Brand */}
      <div className="text-phantom-accent font-bold tracking-widest text-sm flex-shrink-0 flex items-center gap-2">
        <span className="w-1.5 h-1.5 rounded-full bg-phantom-accent animate-pulse" />
        PHANTOM
      </div>

      <div className="text-phantom-border select-none">|</div>

      {/* Active case name */}
      <div className="text-gray-400 truncate max-w-xs">
        {activeCase ? (
          <span className="text-gray-200">{activeCase.name}</span>
        ) : (
          <span className="text-gray-600">No case open</span>
        )}
      </div>

      {/* Graph stats */}
      {activeCase && (
        <div className="text-gray-600 flex-shrink-0">
          {nodes.length}n · {edges.length}e
        </div>
      )}

      <div className="flex-1" />

      {/* Layout switcher */}
      <div className="flex gap-1 flex-shrink-0">
        {LAYOUTS.map(([l, label]) => (
          <button
            key={l}
            onClick={() => changeLayout(l)}
            className={`px-2 py-1 rounded text-xs transition-colors ${
              layout === l
                ? 'bg-phantom-accent text-black font-bold'
                : 'text-gray-400 hover:text-gray-200 border border-phantom-border hover:border-gray-500'
            }`}
          >
            {label}
          </button>
        ))}
      </div>

      <div className="text-phantom-border select-none flex-shrink-0">|</div>

      {/* Export */}
      <button
        onClick={onExport}
        className="text-gray-400 hover:text-phantom-accent transition-colors px-2 py-1 border border-phantom-border rounded flex-shrink-0"
      >
        ↓ Export
      </button>
    </div>
  )
}
