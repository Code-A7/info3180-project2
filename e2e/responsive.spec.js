import { test, expect } from '@playwright/test'

test.describe('Responsive Design', () => {
  test.beforeEach(async ({ page }) => {
    console.log('[DEBUG] Responsive: Setting mobile viewport')
    await page.setViewportSize({ width: 375, height: 667 })
    await page.waitForTimeout(500)
  })

  test('mobile layout at 375px', async ({ page }) => {
    console.log('[DEBUG] Testing: mobile layout at 375px')
    await page.setViewportSize({ width: 375, height: 667 })
    await page.goto('/', { waitUntil: 'networkidle' })
    await page.waitForLoadState('domcontentloaded')
    await page.waitForTimeout(500)
    await expect(page.locator('body')).toBeVisible()
    console.log('[DEBUG] PASS: mobile layout at 375px')
  })

  test('tablet layout at 768px', async ({ page }) => {
    console.log('[DEBUG] Testing: tablet layout at 768px')
    await page.setViewportSize({ width: 768, height: 1024 })
    await page.goto('/', { waitUntil: 'networkidle' })
    await page.waitForLoadState('domcontentloaded')
    await page.waitForTimeout(500)
    await expect(page.locator('body')).toBeVisible()
    console.log('[DEBUG] PASS: tablet layout at 768px')
  })

  test('desktop layout at 1280px', async ({ page }) => {
    console.log('[DEBUG] Testing: desktop layout at 1280px')
    await page.setViewportSize({ width: 1280, height: 800 })
    await page.goto('/', { waitUntil: 'networkidle' })
    await page.waitForLoadState('domcontentloaded')
    await page.waitForTimeout(500)
    await expect(page.locator('body')).toBeVisible()
    console.log('[DEBUG] PASS: desktop layout at 1280px')
  })

  test('login form is usable on mobile', async ({ page }) => {
    console.log('[DEBUG] Testing: login form is usable on mobile')
    await page.setViewportSize({ width: 375, height: 667 })
    await page.goto('/login', { waitUntil: 'networkidle' })
    await page.waitForLoadState('domcontentloaded')
    await page.waitForTimeout(500)
    await expect(page.locator('#email')).toBeVisible()
    await expect(page.locator('#password')).toBeVisible()
    await expect(page.locator('button[type="submit"]')).toBeVisible()
    console.log('[DEBUG] PASS: login form is usable on mobile')
  })

  test('register form is usable on mobile', async ({ page }) => {
    console.log('[DEBUG] Testing: register form is usable on mobile')
    await page.setViewportSize({ width: 375, height: 667 })
    await page.goto('/register', { waitUntil: 'networkidle' })
    await page.waitForLoadState('domcontentloaded')
    await page.waitForTimeout(500)
    await expect(page.locator('#email')).toBeVisible()
    await expect(page.locator('#password')).toBeVisible()
    await expect(page.locator('#confirmPassword')).toBeVisible()
    console.log('[DEBUG] PASS: register form is usable on mobile')
  })

  test('text is readable on mobile', async ({ page }) => {
    console.log('[DEBUG] Testing: text is readable on mobile')
    await page.setViewportSize({ width: 375, height: 667 })
    await page.goto('/login', { waitUntil: 'networkidle' })
    await page.waitForLoadState('domcontentloaded')
    await page.waitForTimeout(500)
    const h1 = page.locator('h1').first()
    await expect(h1).toBeVisible()
    const fontSize = await h1.evaluate(el => parseInt(getComputedStyle(el).fontSize))
    console.log('[DEBUG] Font size:', fontSize)
    expect(fontSize).toBeGreaterThanOrEqual(16)
    console.log('[DEBUG] PASS: text is readable on mobile')
  })
})
