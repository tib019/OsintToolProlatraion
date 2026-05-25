import React from 'react'

function App() {
  return (
    <div className="min-h-screen bg-phantom-bg text-gray-200 font-mono flex flex-col">
      {/* Header */}
      <header className="border-b border-phantom-border bg-phantom-surface px-6 py-4 flex items-center gap-3">
        <div className="w-2 h-2 rounded-full bg-phantom-accent animate-pulse" />
        <h1 className="text-phantom-accent font-bold tracking-widest text-lg uppercase">
          PHANTOM
        </h1>
        <span className="text-phantom-muted text-sm">— OSINT Platform</span>
      </header>

      {/* Main content */}
      <main className="flex-1 flex flex-col items-center justify-center gap-8 p-8">
        {/* Graph canvas placeholder */}
        <div className="w-full max-w-4xl aspect-video bg-phantom-panel border border-phantom-border rounded-lg flex flex-col items-center justify-center gap-4 relative overflow-hidden">
          {/* Grid lines decoration */}
          <div
            className="absolute inset-0 opacity-10"
            style={{
              backgroundImage:
                'linear-gradient(#f59e0b 1px, transparent 1px), linear-gradient(90deg, #f59e0b 1px, transparent 1px)',
              backgroundSize: '40px 40px',
            }}
          />

          {/* Placeholder node dots */}
          <div className="absolute top-1/3 left-1/4 w-3 h-3 rounded-full bg-entity-person opacity-60" />
          <div className="absolute top-1/2 left-1/2 w-4 h-4 rounded-full bg-entity-email opacity-60" />
          <div className="absolute top-2/3 left-2/3 w-3 h-3 rounded-full bg-entity-phone opacity-60" />
          <div className="absolute top-1/4 left-3/5 w-3 h-3 rounded-full bg-entity-username opacity-60" />

          <div className="relative z-10 text-center">
            <p className="text-phantom-muted text-sm uppercase tracking-widest mb-2">
              Graph Canvas
            </p>
            <p className="text-phantom-accent font-bold text-xl tracking-wider">
              Coming in Phase 3
            </p>
            <p className="text-phantom-muted text-xs mt-2">
              Entity relationship graph will render here
            </p>
          </div>
        </div>

        {/* Status bar */}
        <div className="flex items-center gap-6 text-xs text-phantom-muted">
          <span className="flex items-center gap-2">
            <span className="w-1.5 h-1.5 rounded-full bg-phantom-success" />
            Backend connected
          </span>
          <span className="flex items-center gap-2">
            <span className="w-1.5 h-1.5 rounded-full bg-phantom-accent" />
            Phase 2 — API layer
          </span>
          <span className="flex items-center gap-2">
            <span className="w-1.5 h-1.5 rounded-full bg-phantom-muted" />
            Graph UI pending
          </span>
        </div>
      </main>

      {/* Footer */}
      <footer className="border-t border-phantom-border bg-phantom-surface px-6 py-3 text-phantom-muted text-xs flex justify-between">
        <span>PHANTOM OSINT Platform</span>
        <span>v0.1.0-alpha</span>
      </footer>
    </div>
  )
}

export default App
