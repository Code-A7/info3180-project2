export const API_BASE_URL = 'http://localhost:5000'
export const APP_BASE_URL = 'http://localhost:5173'

export async function createTestUser(api, email = null) {
  const uniqueEmail = email || `test${Date.now()}@example.com`
  
  await api.post(`${API_BASE_URL}/api/auth/register`, {
    data: {
      email: uniqueEmail,
      password: 'TestPass123!',
      confirm_password: 'TestPass123!'
    }
  })
  
  return uniqueEmail
}

export async function verifyUser(api, email) {
  await api.post(`${API_BASE_URL}/api/auth/login`, {
    data: {
      email,
      password: 'TestPass123!'
    }
  })
}

export async function loginUser(page, email = 'test@example.com', password = 'TestPass123!') {
  await page.goto(`${APP_BASE_URL}/login`)
  await page.fill('#email', email)
  await page.fill('#password', password)
  await page.click('button[type="submit"]')
  await page.waitForURL(`${APP_BASE_URL}/`)
}

export async function registerUser(page) {
  const uniqueEmail = `test${Date.now()}@example.com`
  
  await page.goto(`${APP_BASE_URL}/register`)
  await page.fill('#name', 'Test User')
  await page.fill('#email', uniqueEmail)
  await page.fill('#password', 'TestPass123!')
  await page.fill('#confirmPassword', 'TestPass123!')
  await page.click('button[type="submit"]')
  
  return uniqueEmail
}

export async function logoutUser(page) {
  await page.click('button:has-text("Logout"), button:has-text("Sign Out")')
  await page.waitForURL(`${APP_BASE_URL}/login`)
}

export async function clearAuthState(page) {
  await page.evaluate(() => {
    localStorage.clear()
    sessionStorage.clear()
  })
}
