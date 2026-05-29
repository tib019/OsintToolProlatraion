import { test, expect } from '@playwright/test'

const MOCK_CASE = {
  id: 'case-abc-123',
  name: 'Alpha Investigation',
  description: '',
  tags: [],
  notes_md: null,
  created_at: new Date().toISOString(),
  updated_at: new Date().toISOString(),
  node_count: 1,
}

const MOCK_NODE = {
  id: 'node-001',
  entity_type: 'PhoneNumber',
  value: '+4915123456789',
  label: '+4915123456789',
  properties: {},
  pos_x: 100,
  pos_y: 100,
  created_at: new Date().toISOString(),
}

const MOCK_EDGE = {
  id: 'edge-001',
  case_id: 'case-abc-123',
  source_id: 'node-001',
  target_id: 'node-002',
  label: 'caller_id',
  transform_name: 'CNAM / Reverse Lookup',
  created_at: new Date().toISOString(),
}

const MOCK_AUDIT = [
  {
    id: 'audit-001',
    event_type: 'node_added',
    entity_type: 'PhoneNumber',
    entity_value: '+4915123456789',
    transform_name: null,
    metadata: {},
    created_at: new Date().toISOString(),
  },
  {
    id: 'audit-002',
    event_type: 'transform_completed',
    entity_type: 'PhoneNumber',
    entity_value: '+4915123456789',
    transform_name: 'PhoneInfoga Scanner',
    metadata: {},
    created_at: new Date().toISOString(),
  },
]

const MOCK_TRANSFORMS = [
  {
    name: 'PhoneInfoga Scanner',
    description: 'Carrier detection, country, line type',
    input_types: ['PhoneNumber'],
    output_types: ['PhoneNumber', 'Organization', 'Location'],
    timeout: 15,
    rate_limit: 30,
  },
  {
    name: 'Leak Database Check',
    description: 'Check HaveIBeenPwned',
    input_types: ['PhoneNumber', 'EmailAddress'],
    output_types: ['LeakRecord'],
    timeout: 15,
    rate_limit: 10,
  },
]

test.beforeEach(async ({ page }) => {
  // Cases list + create — matches /api/cases (no trailing slash)
  await page.route(/\/api\/cases\/?$/, (route) => {
    if (route.request().method() === 'GET') return route.fulfill({ json: [MOCK_CASE] })
    if (route.request().method() === 'POST')
      return route.fulfill({ status: 201, json: MOCK_CASE })
    return route.continue()
  })

  // Case detail
  await page.route(/\/api\/cases\/case-abc-123$/, (route) =>
    route.fulfill({ json: MOCK_CASE }),
  )

  // Graph state
  await page.route(/\/api\/cases\/case-abc-123\/graph$/, (route) =>
    route.fulfill({ json: { nodes: [MOCK_NODE], edges: [MOCK_EDGE] } }),
  )

  // Audit log
  await page.route(/\/api\/cases\/case-abc-123\/audit$/, (route) =>
    route.fulfill({ json: MOCK_AUDIT }),
  )

  // Add node
  await page.route(/\/api\/graph\/case-abc-123\/nodes$/, (route) =>
    route.fulfill({
      status: 201,
      json: { ...MOCK_NODE, id: 'node-new', value: 'new@example.com' },
    }),
  )

  // Transforms
  await page.route(/\/api\/transforms\/entity\//, (route) =>
    route.fulfill({ json: MOCK_TRANSFORMS }),
  )
  await page.route(/\/api\/transforms\/?$/, (route) =>
    route.fulfill({ json: MOCK_TRANSFORMS }),
  )
  await page.route(/\/api\/transforms\/run$/, (route) =>
    route.fulfill({ json: { job_id: 'job-001', status: 'queued' } }),
  )

  // Settings
  await page.route(/\/api\/settings\/api-keys$/, (route) => route.fulfill({ json: [] }))
  await page.route(/\/api\/settings\/modules$/, (route) =>
    route.fulfill({
      json: [
        { name: 'phone_lookup', enabled: true },
        { name: 'email_lookup', enabled: true },
      ],
    }),
  )
})

// ---------------------------------------------------------------------------
// Case loading
// ---------------------------------------------------------------------------

test('existing case appears in sidebar', async ({ page }) => {
  await page.goto('/')
  await expect(page.getByText('Alpha Investigation')).toBeVisible()
})

test('case shows node count', async ({ page }) => {
  await page.goto('/')
  await expect(page.getByText('1 nodes')).toBeVisible()
})

test('clicking case activates it in topbar', async ({ page }) => {
  await page.goto('/')
  await page.getByText('Alpha Investigation').click()
  // TopBar should show the active case name
  await expect(page.getByText('Alpha Investigation').first()).toBeVisible()
})

test('case graph stats appear in topbar after activation', async ({ page }) => {
  await page.goto('/')
  await page.getByText('Alpha Investigation').click()
  // n · e format
  await expect(page.getByText(/\dn\s·\s\de/)).toBeVisible()
})

// ---------------------------------------------------------------------------
// Timeline with active case
// ---------------------------------------------------------------------------

test('timeline shows audit events after case load', async ({ page }) => {
  await page.goto('/')
  await page.getByText('Alpha Investigation').click()
  await expect(page.getByText('node_added')).toBeVisible()
  await expect(page.getByText('transform_completed')).toBeVisible()
})

test('timeline shows entity value in events', async ({ page }) => {
  await page.goto('/')
  await page.getByText('Alpha Investigation').click()
  await expect(page.getByText('+4915123456789').first()).toBeVisible()
})

test('timeline shows transform name', async ({ page }) => {
  await page.goto('/')
  await page.getByText('Alpha Investigation').click()
  await expect(page.getByText('PhoneInfoga Scanner')).toBeVisible()
})

// ---------------------------------------------------------------------------
// Export dropdown (requires active case)
// ---------------------------------------------------------------------------

test('export dropdown opens when case is active', async ({ page }) => {
  await page.goto('/')
  await page.getByText('Alpha Investigation').click()
  const exportBtn = page.getByRole('button', { name: '↓ Export' })
  await expect(exportBtn).toBeEnabled()
  await exportBtn.click()
  await expect(page.getByRole('button', { name: /json/i })).toBeVisible()
  await expect(page.getByRole('button', { name: /csv/i })).toBeVisible()
  await expect(page.getByRole('button', { name: /pdf/i })).toBeVisible()
})

test('export dropdown closes after format selected', async ({ page }) => {
  await page.route(/\/api\/export\//, (route) => route.fulfill({ body: '{}' }))
  await page.goto('/')
  await page.getByText('Alpha Investigation').click()
  await page.getByRole('button', { name: '↓ Export' }).click()
  await page.getByRole('button', { name: /json/i }).click()
  await expect(page.getByRole('button', { name: /csv/i })).not.toBeVisible()
})

// ---------------------------------------------------------------------------
// Add node panel
// ---------------------------------------------------------------------------

test('add node panel visible when case active', async ({ page }) => {
  await page.goto('/')
  await page.getByText('Alpha Investigation').click()
  await expect(page.getByText('Add Node')).toBeVisible()
  await expect(page.getByPlaceholder('Value...')).toBeVisible()
})

test('add node button disabled when value empty', async ({ page }) => {
  await page.goto('/')
  await page.getByText('Alpha Investigation').click()
  const addBtn = page.getByRole('button', { name: '+ Add to Graph' })
  await expect(addBtn).toBeDisabled()
})

test('add node button enables when value typed', async ({ page }) => {
  await page.goto('/')
  await page.getByText('Alpha Investigation').click()
  await page.getByPlaceholder('Value...').fill('+4915123456789')
  const addBtn = page.getByRole('button', { name: '+ Add to Graph' })
  await expect(addBtn).toBeEnabled()
})

// ---------------------------------------------------------------------------
// Settings panel content
// ---------------------------------------------------------------------------

test('settings modules tab shows module list', async ({ page }) => {
  await page.goto('/')
  await page.getByTitle('Settings').click()
  await page.getByRole('button', { name: 'Modules' }).click()
  await expect(page.getByText('phone_lookup')).toBeVisible()
  await expect(page.getByText('email_lookup')).toBeVisible()
})

test('settings api keys tab is default active', async ({ page }) => {
  await page.goto('/')
  await page.getByTitle('Settings').click()
  await expect(page.getByText('Numverify')).toBeVisible()
  await expect(page.getByText('Shodan')).toBeVisible()
  await expect(page.getByText('HaveIBeenPwned')).toBeVisible()
})

test('settings backdrop click closes panel', async ({ page }) => {
  await page.goto('/')
  await page.getByTitle('Settings').click()
  await expect(page.getByText('SETTINGS')).toBeVisible()
  // Click the backdrop (outside the modal box)
  await page.mouse.click(10, 10)
  await expect(page.getByText('SETTINGS')).not.toBeVisible()
})
