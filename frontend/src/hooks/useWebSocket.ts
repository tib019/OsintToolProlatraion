import { useEffect, useRef, useCallback } from 'react'
import { useGraphStore } from '../stores/graphStore'
import type { GraphNode, GraphEdge, WsEvent } from '../types'

const WS_URL = import.meta.env.VITE_WS_URL || 'ws://localhost:8000'

export function useWebSocket(caseId: string | null) {
  const wsRef = useRef<WebSocket | null>(null)
  const reconnectTimeout = useRef<number>()
  const reconnectDelay = useRef(1000)
  const { addNode, addEdge } = useGraphStore()

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
        if (event.type === 'NODE_ADDED') addNode(event.payload as GraphNode)
        if (event.type === 'EDGE_ADDED') addEdge(event.payload as GraphEdge)
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
  }, [caseId, addNode, addEdge])

  useEffect(() => {
    connect()
    return () => {
      clearTimeout(reconnectTimeout.current)
      wsRef.current?.close()
    }
  }, [connect])
}
