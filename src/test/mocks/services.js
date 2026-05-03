import { vi } from 'vitest'

export const mockApi = {
  get: vi.fn(),
  post: vi.fn(),
  put: vi.fn(),
  delete: vi.fn(),
  patch: vi.fn(),
  create: vi.fn(() => mockApi),
  interceptors: {
    request: { use: vi.fn() },
    response: { use: vi.fn() }
  },
  defaults: { maxRetries: 2, timeout: 30000 }
}

export const mockAuthService = {
  login: vi.fn(),
  logout: vi.fn(),
  register: vi.fn(),
  getStoredUser: vi.fn(() => null),
  getCurrentUser: vi.fn(),
  verifyEmail: vi.fn(),
  resendVerification: vi.fn(),
  forgotPassword: vi.fn(),
  resetPassword: vi.fn(),
  isAuthenticated: vi.fn(() => false),
  getToken: vi.fn(() => null),
  storeAuthData: vi.fn(),
  clearAuthData: vi.fn(),
  passwordValidation: {
    validate: vi.fn(() => ({ isValid: true, errors: [], strength: 'strong' })),
    calculateStrength: vi.fn(() => 'strong')
  }
}

export const mockValidateEmail = vi.fn((email) => {
  const re = /^[^\s@]+@[^\s@]+\.[^\s@]+$/
  return re.test(email)
})

export const mockProfileService = {
  getProfile: vi.fn(() => Promise.reject(new Error('No profile'))),
  createProfile: vi.fn(),
  updateProfile: vi.fn(),
  uploadPicture: vi.fn(),
  deletePhoto: vi.fn(),
  setPrimaryPhoto: vi.fn()
}

export const mockMatchService = {
  getMatches: vi.fn(() => Promise.resolve([])),
  getPotentialMatches: vi.fn(() => Promise.resolve([])),
  likeUser: vi.fn(),
  dislikeUser: vi.fn(),
  passUser: vi.fn(),
  superLike: vi.fn(),
  unlikeUser: vi.fn(),
  getMatchScore: vi.fn(),
  reportUser: vi.fn()
}

export const mockMessageService = {
  getConversations: vi.fn(() => Promise.resolve([])),
  getMessageHistory: vi.fn(() => Promise.resolve({ 
    messages: [], 
    other_user: null, 
    has_next: false,
    page: 1,
    total_pages: 0
  })),
  sendMessage: vi.fn(),
  sendTypingStatus: vi.fn(),
  markAsRead: vi.fn(),
  getUnreadCount: vi.fn(() => Promise.resolve({ unread_count: 0 })),
  markAllAsRead: vi.fn()
}

export const mockSocketService = {
  connect: vi.fn(),
  disconnect: vi.fn(),
  emit: vi.fn(),
  on: vi.fn(),
  off: vi.fn(),
  isConnected: vi.fn(() => false),
  joinRoom: vi.fn(),
  leaveRoom: vi.fn(),
  getSocket: vi.fn()
}

export const mockNotificationService = {
  getNotifications: vi.fn(() => Promise.resolve([])),
  markAsRead: vi.fn(),
  markAllAsRead: vi.fn(),
  getUnreadCount: vi.fn(() => Promise.resolve({ unread_count: 0 })),
  deleteNotification: vi.fn()
}

export const mockSearchService = {
  searchProfiles: vi.fn(() => Promise.resolve([])),
  addBookmark: vi.fn(),
  removeBookmark: vi.fn(),
  getBookmarks: vi.fn(() => Promise.resolve([]))
}
