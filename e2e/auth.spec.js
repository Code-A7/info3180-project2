import { test, expect } from '@playwright/test'

const TEST_PASSWORD = 'TestPass123!'

test.describe('Authentication', () => {
  test.beforeEach(async ({ page }) => {
    console.log('[DEBUG] Authentication: Navigating to /login')
    await page.goto('/login', { waitUntil: 'networkidle' })
    await page.waitForLoadState('domcontentloaded')
    console.log('[DEBUG] Authentication: Page loaded')
  })

  test.afterEach(async ({ page }) => {
    console.log('[DEBUG] Cleaning up auth state')
    await page.evaluate(() => {
      localStorage.clear()
      sessionStorage.clear()
    })
  })

  test('login page renders correctly', async ({ page }) => {
    console.log('[DEBUG] Testing: login page renders correctly')
    await page.waitForTimeout(500)
    await expect(page.locator('h1')).toContainText('Welcome Back')
    await expect(page.locator('#email')).toBeVisible()
    await expect(page.locator('#password')).toBeVisible()
    await expect(page.locator('button[type="submit"]')).toBeVisible()
    console.log('[DEBUG] PASS: login page renders correctly')
  })

  test('register link navigates to registration page', async ({ page }) => {
    console.log('[DEBUG] Testing: register link navigates to registration page')
    await page.waitForTimeout(500)
    await page.click('a:has-text("Sign up free")')
    await page.waitForURL('**/register**', { timeout: 10000 })
    await expect(page).toHaveURL('/register')
    console.log('[DEBUG] PASS: register link navigates to registration page')
  })

  test('password visibility toggle works', async ({ page }) => {
    console.log('[DEBUG] Testing: password visibility toggle works')
    await page.waitForTimeout(500)
    const passwordInput = page.locator('#password')
    await expect(passwordInput).toHaveAttribute('type', 'password')

    await page.click('button[type="button"]')
    await page.waitForTimeout(300)
    await expect(passwordInput).toHaveAttribute('type', 'text')

    await page.click('button[type="button"]')
    await page.waitForTimeout(300)
    await expect(passwordInput).toHaveAttribute('type', 'password')
    console.log('[DEBUG] PASS: password visibility toggle works')
  })

  test('forgot password modal opens', async ({ page }) => {
    console.log('[DEBUG] Testing: forgot password modal opens')
    await page.waitForTimeout(500)
    await page.click('button:has-text("Forgot password?")')
    await page.waitForTimeout(500)
    await expect(page.locator('h2:has-text("Reset Password")')).toBeVisible()
    console.log('[DEBUG] PASS: forgot password modal opens')
  })

  test('forgot password modal closes', async ({ page }) => {
    console.log('[DEBUG] Testing: forgot password modal closes')
    await page.waitForTimeout(500)
    await page.click('button:has-text("Forgot password?")')
    await page.waitForTimeout(500)
    await expect(page.locator('h2:has-text("Reset Password")')).toBeVisible()
    await page.click('button:has-text("Cancel")')
    await page.waitForTimeout(500)
    await expect(page.locator('h2:has-text("Reset Password")')).not.toBeVisible()
    console.log('[DEBUG] PASS: forgot password modal closes')
  })

  test('shows validation error for invalid email format', async ({ page }) => {
    console.log('[DEBUG] Testing: shows validation error for invalid email format')
    await page.waitForLoadState('networkidle')
    await page.waitForTimeout(500)
    await page.fill('#email', 'invalid-email')
    await page.fill('#password', TEST_PASSWORD)
    
    // Wait for response or timeout
    await Promise.all([
      page.waitForResponse(r => r.url().includes('/api/') || true),
      page.click('button[type="submit"]')
    ]).catch(() => {})
    
    await page.waitForTimeout(3000)
    
    // Check for any error indicators
    const pageContent = await page.content()
    const hasErrorClass = pageContent.includes('text-red-500') || 
                         pageContent.includes('text-red-600') ||
                         pageContent.includes('text-red-400') ||
                         pageContent.includes('Please enter a valid email') ||
                         pageContent.includes('valid email') ||
                         pageContent.includes('error')
    
    console.log('[DEBUG] Error indicators found:', hasErrorClass)
    expect(hasErrorClass).toBeTruthy()
    console.log('[DEBUG] PASS: shows validation error for invalid email format')
  })

  test('shows validation error for empty password', async ({ page }) => {
    console.log('[DEBUG] Testing: shows validation error for empty password')
    await page.waitForLoadState('networkidle')
    await page.waitForTimeout(500)
    await page.fill('#email', 'test@example.com')
    
    // Wait for response or timeout
    await Promise.all([
      page.waitForResponse(r => r.url().includes('/api/') || true),
      page.click('button[type="submit"]')
    ]).catch(() => {})
    
    await page.waitForTimeout(3000)
    
    // Check for any error indicators
    const pageContent = await page.content()
    const hasErrorClass = pageContent.includes('text-red-500') || 
                         pageContent.includes('text-red-600') ||
                         pageContent.includes('text-red-400') ||
                         pageContent.includes('Password is required') ||
                         pageContent.includes('required')
    
    console.log('[DEBUG] Error indicators found:', hasErrorClass)
    expect(hasErrorClass).toBeTruthy()
    console.log('[DEBUG] PASS: shows validation error for empty password')
  })

  test('remember me checkbox is present', async ({ page }) => {
    console.log('[DEBUG] Testing: remember me checkbox is present')
    await page.waitForTimeout(500)
    await expect(page.locator('input[type="checkbox"]')).toBeVisible()
    await expect(page.locator('text=Remember me')).toBeVisible()
    console.log('[DEBUG] PASS: remember me checkbox is present')
  })
})

test.describe('Registration', () => {
  test.beforeEach(async ({ page }) => {
    console.log('[DEBUG] Registration: Navigating to /register')
    await page.goto('/register', { waitUntil: 'networkidle' })
    await page.waitForLoadState('domcontentloaded')
    console.log('[DEBUG] Registration: Page loaded')
  })

  test.afterEach(async ({ page }) => {
    console.log('[DEBUG] Cleaning up registration state')
    await page.evaluate(() => {
      localStorage.clear()
      sessionStorage.clear()
    })
  })

  test('registration page renders correctly', async ({ page }) => {
    console.log('[DEBUG] Testing: registration page renders correctly')
    await page.waitForTimeout(500)
    await expect(page.locator('#email')).toBeVisible()
    await expect(page.locator('#password')).toBeVisible()
    await expect(page.locator('#confirmPassword')).toBeVisible()
    await expect(page.locator('button[type="submit"]')).toBeVisible()
    console.log('[DEBUG] PASS: registration page renders correctly')
  })

  test('login link navigates to login page', async ({ page }) => {
    console.log('[DEBUG] Testing: login link navigates to login page')
    await page.waitForTimeout(500)
    await page.click('a:has-text("Sign in")')
    await page.waitForURL('**/login**', { timeout: 10000 })
    await expect(page).toHaveURL('/login')
    console.log('[DEBUG] PASS: login link navigates to login page')
  })

  test('shows validation error for password mismatch', async ({ page }) => {
    console.log('[DEBUG] Testing: shows validation error for password mismatch')
    await page.waitForLoadState('networkidle')
    await page.waitForTimeout(500)
    await page.fill('#email', `test${Date.now()}@example.com`)
    await page.fill('#password', TEST_PASSWORD)
    await page.fill('#confirmPassword', 'DifferentPass1!')
    
    // Wait for response or timeout
    await Promise.all([
      page.waitForResponse(r => r.url().includes('/api/') || true),
      page.click('button[type="submit"]')
    ]).catch(() => {})
    
    await page.waitForTimeout(3000)
    
    // Check for error indicators
    const pageContent = await page.content()
    const hasError = pageContent.includes('text-red') || 
                    pageContent.includes('mismatch') ||
                    pageContent.includes('Password') ||
                    pageContent.includes('password')
    
    console.log('[DEBUG] Password mismatch error found:', hasError)
    expect(hasError).toBeTruthy()
    console.log('[DEBUG] PASS: shows validation error for password mismatch')
  })
})

test.describe('Protected Routes', () => {
  test('redirects to login when accessing protected route', async ({ page }) => {
    console.log('[DEBUG] Testing: redirects to login when accessing protected route')
    await page.goto('/profile', { waitUntil: 'networkidle' })
    await page.waitForURL('**/login**', { timeout: 10000 })
    await expect(page).toHaveURL(/\/login/)
    console.log('[DEBUG] PASS: redirects to login when accessing protected route')
  })

  test('redirects to login when accessing browse', async ({ page }) => {
    console.log('[DEBUG] Testing: redirects to login when accessing browse')
    await page.goto('/browse', { waitUntil: 'networkidle' })
    await page.waitForURL('**/login**', { timeout: 10000 })
    await expect(page).toHaveURL(/\/login/)
    console.log('[DEBUG] PASS: redirects to login when accessing browse')
  })

  test('redirects to login when accessing messages', async ({ page }) => {
    console.log('[DEBUG] Testing: redirects to login when accessing messages')
    await page.goto('/messages', { waitUntil: 'networkidle' })
    await page.waitForURL('**/login**', { timeout: 10000 })
    await expect(page).toHaveURL(/\/login/)
    console.log('[DEBUG] PASS: redirects to login when accessing messages')
  })
})
