import { useEffect, useRef, useCallback } from 'react'
import { useGraphStore } from '../stores/graphStore'
import type { GraphNode, GraphEdge, AuditLog, WsEvent } from '../types'

const WS_URL = import.meta.env.VITE_WS_URL || 'ws://localhost:8000'

export function useWebSocket(caseId: string | null) {
  const wsRef = useRef<WebSocket | null>(null)
  const reconnectTimeout = useRef<number>()
  const reconnectDelay = useRef(1000)
  const { addNode, addEdge, removeNode, addAuditLog } = useGraphStore()

  const connect = useCallback(() => {
    if (!caseId) return
    const ws = new WebSocket(`${WS_URL}/ws/${caseId}`)
    wsRef.current = ws

    ws.onopen = () => {
      reconnectDelay.current = 1000
    }

    ws.onmessage = (e) => {
      try {
        const event: WsEvent = JSON.parse(e.data as string)
        switch (event.type) {
          case 'node_added':
            addNode(event.payload as GraphNode)
            break
          case 'edge_added':
            addEdge(event.payload as GraphEdge)
            break
          case 'node_removed': {
            const p = event.payload as { node_id: string }
            removeNode(p.node_id)
            break
          }
          case 'node_moved': {
            const p = event.payload as { node_id: string; x: number; y: number }
            addNode({ ...useGraphStore.getState().nodes.find(n => n.id === p.node_id)!, pos_x: p.x, pos_y: p.y })
            break
          }
          case 'transform_completed':
          case 'transform_failed': {
            const p = event.payload as Record<string, unknown>
            addAuditLog({
              id: crypto.randomUUID(),
              event_type: event.type,
              metadata: p,
              created_at: new Date().toISOString(),
            } as AuditLog)
            break
          }
        }
      } catch {
        // ignore parse errors
      }
    }

    ws.onclose = () => {
      reconnectTimeout.current = window.setTimeout(() => {
        reconnectDelay.current = Math.min(reconnectDelay.current * 2, 30000)
        connect()
      }, reconnectDelay.current)
    }
  }, [caseId, addNode, addEdge, removeNode, addAuditLog])

  useEffect(() => {
    connect()
    return () => {
      clearTimeout(reconnectTimeout.current)
      wsRef.current?.close()
    }
  }, [connect])
}
