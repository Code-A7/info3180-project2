import { beforeAll, afterEach, vi } from 'vitest'
import { setupCentralMocks, resetAllMocks } from './mocks/index.js'

// happy-dom provides working localStorage/sessionStorage
global.fetch = vi.fn()

beforeAll(() => {
  setupCentralMocks(vi)
})

afterEach(() => {
  resetAllMocks()
  vi.clearAllMocks()
  
  // Clear storage using happy-dom's built-in methods
  localStorage.clear()
  sessionStorage.clear()
})
