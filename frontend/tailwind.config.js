module.exports = {
  darkMode: 'class',
  content: ['./index.html', './src/**/*.{js,ts,jsx,tsx}'],
  theme: {
    extend: {
      colors: {
        phantom: {
          bg: '#0a0a0a',
          surface: '#111111',
          panel: '#1a1a1a',
          border: '#2a2a2a',
          accent: '#f59e0b',
          'accent-dim': '#b45309',
          success: '#22c55e',
          error: '#ef4444',
          muted: '#6b7280',
        },
        entity: {
          phone: '#22c55e',
          email: '#3b82f6',
          person: '#eab308',
          username: '#f97316',
          social: '#a855f7',
          ip: '#ef4444',
          domain: '#6b7280',
          org: '#06b6d4',
          location: '#14b8a6',
          leak: '#991b1b',
        },
      },
      fontFamily: {
        mono: ['JetBrains Mono', 'Fira Code', 'monospace'],
      },
    },
  },
  plugins: [],
}
