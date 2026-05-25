import { useEffect } from 'react'
import { useGraphStore } from '../../stores/graphStore'
import { casesApi } from '../../api/cases'
import type { AuditLog } from '../../types'

const EVENT_COLORS: Record<string, string> = {
  case_created: 'text-blue-400',
  case_updated: 'text-blue-300',
  node_added: 'text-green-400',
  node_removed: 'text-red-400',
  edge_added: 'text-purple-400',
  transform_queued: 'text-yellow-500',
  transform_completed: 'text-phantom-accent',
  transform_failed: 'text-red-500',
}

const EVENT_ICONS: Record<string, string> = {
  case_created: '📁',
  case_updated: '✏️',
  node_added: '⊕',
  node_removed: '⊖',
  edge_added: '→',
  transform_queued: '⏳',
  transform_completed: '✓',
  transform_failed: '✗',
}

function formatTime(iso: string) {
  const d = new Date(iso)
  return d.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit', second: '2-digit' })
}

function EventRow({ log }: { log: AuditLog }) {
  const color = EVENT_COLORS[log.event_type] ?? 'text-gray-400'
  const icon = EVENT_ICONS[log.event_type] ?? '·'

  return (
    <div className="flex items-start gap-2 px-3 py-1 hover:bg-phantom-panel/50 border-b border-phantom-border/30 last:border-0 transition-colors">
      <span className="text-gray-600 text-xs tabular-nums flex-shrink-0 pt-0.5 w-20">
        {formatTime(log.created_at)}
      </span>
      <span className={`text-xs flex-shrink-0 w-4 text-center ${color}`}>{icon}</span>
      <span className={`text-xs font-mono flex-shrink-0 w-36 ${color}`}>
        {log.event_type}
      </span>
      {log.entity_value && (
        <span className="text-gray-300 text-xs truncate max-w-xs">
          {log.entity_type && <span className="text-gray-500 mr-1">[{log.entity_type}]</span>}
          {log.entity_value}
        </span>
      )}
      {log.transform_name && (
        <span className="text-gray-500 text-xs ml-auto flex-shrink-0">via {log.transform_name}</span>
      )}
    </div>
  )
}

export function DiscoveryTimeline() {
  const { activeCase, auditLogs, setAuditLogs, timelineOpen, setTimelineOpen } = useGraphStore()

  useEffect(() => {
    if (!activeCase) {
      setAuditLogs([])
      return
    }
    casesApi.getAudit(activeCase.id)
      .then((logs) => setAuditLogs((logs as AuditLog[]).reverse()))
      .catch(() => {})
  }, [activeCase, setAuditLogs])

  return (
    <div
      className="bg-phantom-surface border-t border-phantom-border flex flex-col flex-shrink-0 font-mono"
      style={{ height: timelineOpen ? 180 : 32 }}
    >
      {/* Header */}
      <div
        className="flex items-center justify-between px-3 h-8 border-b border-phantom-border cursor-pointer select-none flex-shrink-0 hover:bg-phantom-panel/40 transition-colors"
        onClick={() => setTimelineOpen(!timelineOpen)}
      >
        <div className="flex items-center gap-2">
          <span className="text-phantom-accent text-xs font-bold tracking-wider">TIMELINE</span>
          {activeCase && (
            <span className="text-gray-600 text-xs">{auditLogs.length} events</span>
          )}
        </div>
        <span className="text-gray-500 text-xs">{timelineOpen ? '▼' : '▲'}</span>
      </div>

      {/* Log list */}
      {timelineOpen && (
        <div className="flex-1 overflow-y-auto">
          {!activeCase ? (
            <div className="flex items-center justify-center h-full text-gray-600 text-xs">
              Open a case to see discovery timeline
            </div>
          ) : auditLogs.length === 0 ? (
            <div className="flex items-center justify-center h-full text-gray-600 text-xs">
              No events yet — start investigating
            </div>
          ) : (
            auditLogs.map((log) => <EventRow key={log.id} log={log} />)
          )}
        </div>
      )}
    </div>
  )
}
