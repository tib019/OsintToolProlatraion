import { useEffect, useState } from 'react'
import { useGraphStore } from '../../stores/graphStore'
import { settingsApi } from '../../api/settings'
import type { ApiKeyInfo, ModuleState } from '../../types'

const KNOWN_SERVICES = [
  { id: 'NUMVERIFY_API_KEY', label: 'Numverify', hint: 'Phone validation' },
  { id: 'SHODAN_API_KEY', label: 'Shodan', hint: 'IP/Domain intel' },
  { id: 'OPENCNAM_SID', label: 'OpenCNAM SID', hint: 'CNAM lookup' },
  { id: 'OPENCNAM_AUTH_TOKEN', label: 'OpenCNAM Token', hint: 'CNAM lookup' },
  { id: 'HIBP_API_KEY', label: 'HaveIBeenPwned', hint: 'Leak check' },
  { id: 'TELEGRAM_BOT_TOKEN', label: 'Telegram Bot Token', hint: 'Telegram lookup' },
]

type Tab = 'keys' | 'modules'

function ApiKeysTab() {
  const [keys, setKeys] = useState<ApiKeyInfo[]>([])
  const [keyInputs, setKeyInputs] = useState<Record<string, string>>({})
  const [saving, setSaving] = useState<string | null>(null)

  useEffect(() => {
    settingsApi.listKeys().then(setKeys).catch(() => {})
  }, [])

  function getKey(service: string) {
    return keys.find((k) => k.service_name === service)
  }

  async function handleSave(service: string) {
    const val = keyInputs[service]?.trim()
    if (!val) return
    setSaving(service)
    try {
      const updated = await settingsApi.setKey(service, val)
      setKeys((prev) => {
        const filtered = prev.filter((k) => k.service_name !== service)
        return [...filtered, updated]
      })
      setKeyInputs((prev) => ({ ...prev, [service]: '' }))
    } finally {
      setSaving(null)
    }
  }

  async function handleToggle(service: string, currentlyActive: boolean) {
    const fn = currentlyActive ? settingsApi.deactivateKey : settingsApi.activateKey
    const updated = await fn(service).catch(() => null)
    if (updated) {
      setKeys((prev) => prev.map((k) => (k.service_name === service ? updated : k)))
    }
  }

  async function handleDelete(service: string) {
    await settingsApi.deleteKey(service).catch(() => {})
    setKeys((prev) => prev.filter((k) => k.service_name !== service))
  }

  return (
    <div className="space-y-3">
      {KNOWN_SERVICES.map(({ id, label, hint }) => {
        const existing = getKey(id)
        return (
          <div key={id} className="bg-phantom-panel border border-phantom-border rounded p-3">
            <div className="flex items-center justify-between mb-2">
              <div>
                <span className="text-gray-200 text-xs font-bold">{label}</span>
                <span className="text-gray-600 text-xs ml-2">{hint}</span>
              </div>
              <div className="flex items-center gap-2">
                {existing?.is_set && (
                  <>
                    <span
                      className={`text-xs px-1.5 py-0.5 rounded ${
                        existing.is_active
                          ? 'bg-green-900/40 text-green-400 border border-green-700/40'
                          : 'bg-gray-800 text-gray-500 border border-gray-700'
                      }`}
                    >
                      {existing.is_active ? 'active' : 'inactive'}
                    </span>
                    <button
                      onClick={() => void handleToggle(id, existing.is_active)}
                      className="text-xs text-gray-500 hover:text-gray-300 transition-colors"
                    >
                      {existing.is_active ? 'Deactivate' : 'Activate'}
                    </button>
                    <button
                      onClick={() => void handleDelete(id)}
                      className="text-xs text-red-600 hover:text-red-400 transition-colors"
                    >
                      ✕
                    </button>
                  </>
                )}
              </div>
            </div>
            <div className="flex gap-2">
              <input
                type="password"
                placeholder={existing?.is_set ? '••••••••••••••••' : 'Enter API key…'}
                value={keyInputs[id] ?? ''}
                onChange={(e) => setKeyInputs((prev) => ({ ...prev, [id]: e.target.value }))}
                onKeyDown={(e) => e.key === 'Enter' && void handleSave(id)}
                className="flex-1 bg-phantom-bg border border-phantom-border text-gray-200 text-xs px-2 py-1.5 rounded outline-none focus:border-phantom-accent font-mono"
              />
              <button
                onClick={() => void handleSave(id)}
                disabled={saving === id || !keyInputs[id]?.trim()}
                className="bg-phantom-accent/20 border border-phantom-accent/40 text-phantom-accent text-xs px-3 py-1.5 rounded hover:bg-phantom-accent/30 disabled:opacity-40 transition-colors"
              >
                {saving === id ? '…' : existing?.is_set ? 'Update' : 'Save'}
              </button>
            </div>
          </div>
        )
      })}
    </div>
  )
}

function ModulesTab() {
  const [modules, setModules] = useState<ModuleState[]>([])

  useEffect(() => {
    settingsApi.listModules().then(setModules).catch(() => {})
  }, [])

  async function handleToggle(name: string, enabled: boolean) {
    const updated = await settingsApi.toggleModule(name, !enabled).catch(() => null)
    if (updated) {
      setModules((prev) => prev.map((m) => (m.name === name ? updated : m)))
    }
  }

  return (
    <div className="space-y-2">
      {modules.map((m) => (
        <div
          key={m.name}
          className="flex items-center justify-between bg-phantom-panel border border-phantom-border rounded px-3 py-2.5"
        >
          <div>
            <span className="text-gray-200 text-xs font-mono">{m.name}</span>
          </div>
          <button
            onClick={() => void handleToggle(m.name, m.enabled)}
            className={`relative w-10 h-5 rounded-full transition-colors ${
              m.enabled ? 'bg-phantom-accent' : 'bg-gray-700'
            }`}
          >
            <span
              className={`absolute top-0.5 w-4 h-4 rounded-full bg-white transition-transform ${
                m.enabled ? 'translate-x-5' : 'translate-x-0.5'
              }`}
            />
          </button>
        </div>
      ))}
    </div>
  )
}

export function SettingsPanel() {
  const { settingsOpen, setSettingsOpen } = useGraphStore()
  const [tab, setTab] = useState<Tab>('keys')

  if (!settingsOpen) return null

  return (
    <div
      className="fixed inset-0 z-50 flex items-center justify-center bg-black/70"
      onMouseDown={(e) => e.target === e.currentTarget && setSettingsOpen(false)}
    >
      <div className="bg-phantom-surface border border-phantom-border rounded-lg w-[600px] max-h-[80vh] flex flex-col font-mono shadow-2xl">
        {/* Header */}
        <div className="flex items-center justify-between px-5 py-3 border-b border-phantom-border">
          <span className="text-phantom-accent font-bold tracking-wider text-sm">SETTINGS</span>
          <button
            onClick={() => setSettingsOpen(false)}
            className="text-gray-500 hover:text-gray-200 transition-colors text-lg leading-none"
          >
            ✕
          </button>
        </div>

        {/* Tabs */}
        <div className="flex border-b border-phantom-border">
          {(['keys', 'modules'] as Tab[]).map((t) => (
            <button
              key={t}
              onClick={() => setTab(t)}
              className={`px-5 py-2.5 text-xs transition-colors ${
                tab === t
                  ? 'text-phantom-accent border-b-2 border-phantom-accent'
                  : 'text-gray-500 hover:text-gray-300'
              }`}
            >
              {t === 'keys' ? 'API Keys' : 'Modules'}
            </button>
          ))}
        </div>

        {/* Content */}
        <div className="flex-1 overflow-y-auto p-5">
          {tab === 'keys' ? <ApiKeysTab /> : <ModulesTab />}
        </div>
      </div>
    </div>
  )
}
