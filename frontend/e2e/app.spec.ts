import { test, expect } from '@playwright/test'

test.beforeEach(async ({ page }) => {
  // Mock all API calls so tests don't need a running backend
  await page.route('**/api/cases/', (route) => {
    if (route.request().method() === 'GET') {
      return route.fulfill({ json: [] })
    }
    if (route.request().method() === 'POST') {
      return route.fulfill({
        status: 201,
        json: {
          id: 'test-case-id',
          name: 'Test Case',
          description: '',
          tags: [],
          notes_md: null,
          created_at: new Date().toISOString(),
          updated_at: new Date().toISOString(),
          node_count: 0,
        },
      })
    }
    return route.continue()
  })

  await page.route('**/api/graph/**', (route) =>
    route.fulfill({ json: { nodes: [], edges: [] } }),
  )

  await page.route('**/api/transforms/**', (route) => route.fulfill({ json: [] }))
})

test('page loads and shows PHANTOM branding', async ({ page }) => {
  await page.goto('/')
  await expect(page).toHaveTitle(/PHANTOM|Vite/)
  await expect(page.getByText('PHANTOM').first()).toBeVisible()
})

test('left sidebar shows Cases section', async ({ page }) => {
  await page.goto('/')
  await expect(page.getByText('Cases', { exact: true }).first()).toBeVisible()
})

test('left sidebar shows + New button', async ({ page }) => {
  await page.goto('/')
  await expect(page.getByRole('button', { name: '+ New' })).toBeVisible()
})

test('clicking + New shows case name input', async ({ page }) => {
  await page.goto('/')
  await page.getByRole('button', { name: '+ New' }).click()
  await expect(page.getByPlaceholder('Case name...')).toBeVisible()
})

test('entity type legend is visible', async ({ page }) => {
  await page.goto('/')
  await expect(page.getByText('Entity Types', { exact: false })).toBeVisible()
  await expect(page.getByText('PhoneNumber')).toBeVisible()
  await expect(page.getByText('EmailAddress')).toBeVisible()
  await expect(page.getByText('IPAddress')).toBeVisible()
})

test('right sidebar shows select node prompt when nothing selected', async ({ page }) => {
  await page.goto('/')
  await expect(page.getByText('Select a node')).toBeVisible()
})

test('no cases shows empty state message', async ({ page }) => {
  await page.goto('/')
  await expect(page.getByText('No cases yet')).toBeVisible()
})
