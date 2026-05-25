import { useEffect, useRef, forwardRef, useImperativeHandle } from 'react'
import cytoscape from 'cytoscape'
import { useGraphStore } from '../../stores/graphStore'
import { cytoscapeStyles } from './cytoscapeStyles'
import { graphApi } from '../../api/graph'

export interface GraphCanvasHandle {
  runLayout: (name: string) => void
}

interface GraphCanvasProps {
  caseId: string
}

export const GraphCanvas = forwardRef<GraphCanvasHandle, GraphCanvasProps>(
  ({ caseId }, ref) => {
    const containerRef = useRef<HTMLDivElement>(null)
    const cyRef = useRef<cytoscape.Core | null>(null)
    const { nodes, edges, selectNode, setContextMenu } = useGraphStore()

    // Expose layout runner to parent via ref
    useImperativeHandle(ref, () => ({
      runLayout(name: string) {
        if (cyRef.current) {
          cyRef.current
            .layout({ name, animate: true } as cytoscape.LayoutOptions)
            .run()
        }
      },
    }))

    // Initialize Cytoscape once
    useEffect(() => {
      if (!containerRef.current) return
      const cy = cytoscape({
        container: containerRef.current,
        style: cytoscapeStyles,
        layout: { name: 'cose', animate: true, randomize: false } as cytoscape.LayoutOptions,
        userZoomingEnabled: true,
        userPanningEnabled: true,
        boxSelectionEnabled: true,
      })
      cyRef.current = cy

      cy.on('tap', 'node', (e) => {
        selectNode(e.target.id() as string)
      })

      cy.on('tap', (e) => {
        if (e.target === cy) {
          selectNode(null)
          setContextMenu(null)
        }
      })

      cy.on('cxttap', 'node', (e) => {
        const pos = e.renderedPosition as { x: number; y: number }
        setContextMenu({ x: pos.x, y: pos.y, nodeId: e.target.id() as string })
        e.preventDefault()
      })

      cy.on('dragfree', 'node', (e) => {
        const node = e.target
        const pos = node.position() as { x: number; y: number }
        graphApi.updatePosition(caseId, node.id() as string, pos.x, pos.y).catch(() => {})
      })

      return () => cy.destroy()
      // eslint-disable-next-line react-hooks/exhaustive-deps
    }, [])

    // Sync nodes
    useEffect(() => {
      const cy = cyRef.current
      if (!cy) return

      const existingIds = new Set(cy.nodes().map((n) => n.id()))
      const incomingIds = new Set(nodes.map((n) => n.id))

      for (const node of nodes) {
        if (!existingIds.has(node.id)) {
          cy.add({
            group: 'nodes',
            data: {
              id: node.id,
              label: node.label || node.value,
              entity_type: node.entity_type,
              value: node.value,
            },
            position:
              node.pos_x != null && node.pos_y != null
                ? { x: node.pos_x, y: node.pos_y }
                : undefined,
          })
        }
      }

      for (const id of existingIds) {
        if (!incomingIds.has(id)) cy.getElementById(id).remove()
      }

      if (nodes.length > 0) {
        cy.layout({ name: 'cose', animate: true, randomize: false } as cytoscape.LayoutOptions).run()
      }
    }, [nodes])

    // Sync edges
    useEffect(() => {
      const cy = cyRef.current
      if (!cy) return

      const existingIds = new Set(cy.edges().map((e) => e.id()))
      const incomingIds = new Set(edges.map((e) => e.id))

      for (const edge of edges) {
        if (!existingIds.has(edge.id)) {
          try {
            cy.add({
              group: 'edges',
              data: {
                id: edge.id,
                source: edge.source_id,
                target: edge.target_id,
                label: edge.transform_name,
              },
            })
          } catch {
            // source/target may not exist yet; will retry on next render
          }
        }
      }

      for (const id of existingIds) {
        if (!incomingIds.has(id)) cy.getElementById(id).remove()
      }
    }, [edges])

    return <div ref={containerRef} className="w-full h-full bg-phantom-bg" />
  }
)

GraphCanvas.displayName = 'GraphCanvas'
