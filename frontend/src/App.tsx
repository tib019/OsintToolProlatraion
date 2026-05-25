import { useEffect, useRef } from 'react'
import { GraphCanvas } from './components/Graph/GraphCanvas'
import type { GraphCanvasHandle } from './components/Graph/GraphCanvas'
import { LeftSidebar } from './components/Sidebar/LeftSidebar'
import { RightSidebar } from './components/Sidebar/RightSidebar'
import { NodeContextMenu } from './components/ContextMenu/NodeContextMenu'
import { TopBar } from './components/TopBar/TopBar'
import { DiscoveryTimeline } from './components/Timeline/DiscoveryTimeline'
import { SettingsPanel } from './components/Settings/SettingsPanel'
import { useGraphStore } from './stores/graphStore'
import { useWebSocket } from './hooks/useWebSocket'
import { casesApi } from './api/cases'

function App() {
  const { activeCase, setCases, setActiveCase, setNodes, setEdges, setAuditLogs } = useGraphStore()
  const canvasRef = useRef<GraphCanvasHandle>(null)

  useEffect(() => {
    casesApi.list().then(setCases).catch(() => {})
  }, [setCases])

  useWebSocket(activeCase?.id ?? null)

  async function handleCaseSelect(id: string) {
    try {
      const [caseData, graph, audit] = await Promise.all([
        casesApi.get(id),
        casesApi.getGraph(id),
        casesApi.getAudit(id),
      ])
      setActiveCase(caseData)
      setNodes(graph.nodes)
      setEdges(graph.edges)
      setAuditLogs([...(audit as Parameters<typeof setAuditLogs>[0])].reverse())
    } catch {
      // handle API errors gracefully
    }
  }

  function handleLayoutChange(layout: string) {
    canvasRef.current?.runLayout(layout)
  }

  function handleExport(format: string) {
    if (!activeCase) return
    const url = `/api/export/${activeCase.id}/${format}`
    const a = document.createElement('a')
    a.href = url
    a.download = `phantom_case_${activeCase.id}.${format}`
    a.click()
  }

  return (
    <div className="h-screen w-screen bg-phantom-bg flex flex-col overflow-hidden">
      <TopBar onLayoutChange={handleLayoutChange} onExport={handleExport} />

      <div className="flex flex-1 overflow-hidden min-h-0">
        <LeftSidebar onCaseSelect={(id) => void handleCaseSelect(id)} />

        <main className="flex-1 flex flex-col overflow-hidden min-w-0">
          <div className="flex-1 relative overflow-hidden">
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
            <NodeContextMenu />
          </div>

          <DiscoveryTimeline />
        </main>

        <RightSidebar />
      </div>

      <SettingsPanel />
    </div>
  )
}

export default App
