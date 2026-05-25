import { useEffect, useRef } from 'react'
import { GraphCanvas } from './components/Graph/GraphCanvas'
import type { GraphCanvasHandle } from './components/Graph/GraphCanvas'
import { LeftSidebar } from './components/Sidebar/LeftSidebar'
import { RightSidebar } from './components/Sidebar/RightSidebar'
import { NodeContextMenu } from './components/ContextMenu/NodeContextMenu'
import { TopBar } from './components/TopBar/TopBar'
import { useGraphStore } from './stores/graphStore'
import { useWebSocket } from './hooks/useWebSocket'
import { casesApi } from './api/cases'

function App() {
  const { activeCase, setCases, setActiveCase, setNodes, setEdges } = useGraphStore()
  const canvasRef = useRef<GraphCanvasHandle>(null)

  // Load cases on mount
  useEffect(() => {
    casesApi.list().then(setCases).catch(() => {})
  }, [setCases])

  // WebSocket connection for the active case
  useWebSocket(activeCase?.id ?? null)

  async function handleCaseSelect(id: string) {
    try {
      const [caseData, graph] = await Promise.all([
        casesApi.get(id),
        casesApi.getGraph(id),
      ])
      setActiveCase(caseData)
      setNodes(graph.nodes)
      setEdges(graph.edges)
    } catch {
      // handle API errors gracefully — case may still load partially
    }
  }

  function handleLayoutChange(layout: string) {
    canvasRef.current?.runLayout(layout)
  }

  function handleExport() {
    // Export graph as PNG via Cytoscape's built-in PNG export
    // Stubbed — full implementation would call cy.png() from the canvas
    console.info('Export triggered')
  }

  return (
    <div className="h-screen w-screen bg-phantom-bg flex flex-col overflow-hidden">
      <TopBar onLayoutChange={handleLayoutChange} onExport={handleExport} />

      <div className="flex flex-1 overflow-hidden">
        <LeftSidebar onCaseSelect={(id) => void handleCaseSelect(id)} />

        <main className="flex-1 relative overflow-hidden">
          {activeCase ? (
            <GraphCanvas ref={canvasRef} caseId={activeCase.id} />
          ) : (
            <div className="w-full h-full flex items-center justify-center font-mono">
              <div className="text-center select-none">
                <div className="text-phantom-accent text-4xl font-bold tracking-widest mb-4">
                  PHANTOM
                </div>
                <div className="text-gray-500 text-sm mb-2">
                  Open-source OSINT investigation platform
                </div>
                <div className="text-gray-600 text-xs">
                  Select or create a case in the left panel to begin
                </div>
              </div>
            </div>
          )}

          {/* Context menu rendered on top of the graph canvas */}
          <NodeContextMenu />
        </main>

        <RightSidebar />
      </div>
    </div>
  )
}

export default App
