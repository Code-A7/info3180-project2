import { describe, it, expect, vi, beforeEach } from 'vitest'
import { mount } from '@vue/test-utils'
import { createRouter, createMemoryHistory } from 'vue-router'
import LoginView from '@/views/LoginView.vue'

const mockLoginFn = vi.fn()
const mockLogoutFn = vi.fn()
const mockCheckAuthFn = vi.fn()
const mockRegisterFn = vi.fn()
const mockVerifyEmailFn = vi.fn()
const mockRefreshUserFn = vi.fn()
const mockClearErrorFn = vi.fn()

vi.mock('@/services/authService', () => ({
  authService: {
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
    clearAuthData: vi.fn()
  },
  validateEmail: vi.fn((email) => /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email)),
  default: {
    login: vi.fn(),
    logout: vi.fn(),
    register: vi.fn()
  }
}))

vi.mock('@/composables/useAuth', () => ({
  useAuth: () => ({
    user: { value: null },
    isAuthenticated: { value: false },
    isLoading: { value: false },
    authError: { value: null },
    login: mockLoginFn,
    logout: mockLogoutFn,
    checkAuth: mockCheckAuthFn,
    register: mockRegisterFn,
    verifyEmail: mockVerifyEmailFn,
    refreshUser: mockRefreshUserFn,
    clearError: mockClearErrorFn
  }),
  default: () => ({
    user: { value: null },
    isAuthenticated: { value: false },
    isLoading: { value: false },
    authError: { value: null },
    login: mockLoginFn,
    logout: mockLogoutFn,
    checkAuth: mockCheckAuthFn,
    register: mockRegisterFn,
    verifyEmail: mockVerifyEmailFn,
    refreshUser: mockRefreshUserFn,
    clearError: mockClearErrorFn
  })
}))

const createRouterWithLogin = () => {
  const router = createRouter({
    history: createMemoryHistory(),
    routes: [
      { path: '/', name: 'home', component: { template: '<div>Home</div>' } },
      { path: '/register', name: 'register', component: { template: '<div>Register</div>' } },
      { path: '/login', name: 'login', component: LoginView }
    ]
  })
  router.push('/login')
  return router
}

describe('LoginView', () => {
  let router

  beforeEach(async () => {
    router = createRouterWithLogin()
    await router.isReady()
    vi.clearAllMocks()
  })

  it('renders login form with all required elements', () => {
    const wrapper = mount(LoginView, {
      global: {
        plugins: [router],
        stubs: {
          'router-link': {
            template: '<a :href="to"><slot /></a>',
            props: ['to']
          }
        }
      }
    })

    expect(wrapper.find('h1').text()).toBe('Welcome Back')
    expect(wrapper.find('#email').exists()).toBe(true)
    expect(wrapper.find('#password').exists()).toBe(true)
    expect(wrapper.find('button[type="submit"]').text()).toContain('Sign In')
    expect(wrapper.find('a[href="/register"]').exists()).toBe(true)
  })

  it('shows validation error for invalid email', async () => {
    const wrapper = mount(LoginView, {
      global: {
        plugins: [router],
        stubs: {
          'router-link': {
            template: '<a :href="to"><slot /></a>',
            props: ['to']
          }
        }
      }
    })

    const emailInput = wrapper.find('#email')
    await emailInput.setValue('invalid-email')
    await wrapper.find('form').trigger('submit.prevent')

    expect(wrapper.find('.text-red-500').exists()).toBe(true)
  })

  it('toggles password visibility when eye icon is clicked', async () => {
    const wrapper = mount(LoginView, {
      global: {
        plugins: [router],
        stubs: {
          'router-link': {
            template: '<a :href="to"><slot /></a>',
            props: ['to']
          }
        }
      }
    })

    const passwordInput = wrapper.find('#password')
    expect(passwordInput.attributes('type')).toBe('password')

    const toggleButton = wrapper.find('button[type="button"]')
    await toggleButton.trigger('click')

    expect(passwordInput.attributes('type')).toBe('text')
  })

  it('shows loading state during form submission', async () => {
    mockLoginFn.mockImplementation(() => new Promise(() => {}))

    const wrapper = mount(LoginView, {
      global: {
        plugins: [router],
        stubs: {
          'router-link': {
            template: '<a :href="to"><slot /></a>',
            props: ['to']
          }
        }
      }
    })

    const emailInput = wrapper.find('#email')
    const passwordInput = wrapper.find('#password')
    await emailInput.setValue('test@example.com')
    await passwordInput.setValue('password123')
    await wrapper.find('form').trigger('submit.prevent')

    await wrapper.vm.$nextTick()
    expect(wrapper.find('button[type="submit"]').text()).toContain('Signing in...')
  })

  it('displays branding', () => {
    const wrapper = mount(LoginView, {
      global: {
        plugins: [router],
        stubs: {
          'router-link': {
            template: '<a :href="to"><slot /></a>',
            props: ['to']
          }
        }
      }
    })

    expect(wrapper.text()).toContain('DriftDater')
  })

  it('has remember me checkbox', () => {
    const wrapper = mount(LoginView, {
      global: {
        plugins: [router],
        stubs: {
          'router-link': {
            template: '<a :href="to"><slot /></a>',
            props: ['to']
          }
        }
      }
    })

    expect(wrapper.find('input[type="checkbox"]').exists()).toBe(true)
    expect(wrapper.text()).toContain('Remember me')
  })

  it('navigates to register page when sign up link is clicked', async () => {
    const pushSpy = vi.spyOn(router, 'push')

    const wrapper = mount(LoginView, {
      global: {
        plugins: [router],
        stubs: {
          'router-link': {
            template: '<a :href="to" @click.prevent="navigate"><slot /></a>',
            props: ['to'],
            methods: { navigate() { router.push(this.to) } }
          }
        }
      }
    })

    const registerLink = wrapper.find('a[href="/register"]')
    await registerLink.trigger('click')

    expect(pushSpy).toHaveBeenCalledWith('/register')
  })

  it('shows success message when redirected from registration', async () => {
    const route = createRouter({
      history: createMemoryHistory(),
      routes: [
        { path: '/login', name: 'login', component: LoginView }
      ]
    })
    route.push('/login?registered=true')
    await route.isReady()

    const wrapper = mount(LoginView, {
      global: {
        plugins: [route],
        stubs: {
          'router-link': {
            template: '<a :href="to"><slot /></a>',
            props: ['to']
          }
        }
      }
    })

    await wrapper.vm.$nextTick()
    await new Promise(resolve => setTimeout(resolve, 0))

    expect(wrapper.find('.bg-green-50').exists()).toBe(true)
  })

  describe('Forgot Password Modal', () => {
    it('opens forgot password modal when link is clicked', async () => {
      const wrapper = mount(LoginView, {
        global: {
          plugins: [router],
          stubs: {
            'router-link': {
              template: '<a :href="to"><slot /></a>',
              props: ['to']
            }
          }
        }
      })

      // Find the "Forgot password?" button by looking for button with type="button"
      const buttons = wrapper.findAll('button')
      const forgotBtn = buttons.find(btn => btn.text().includes('Forgot password?'))
      
      expect(forgotBtn.exists()).toBe(true)
      
      // Click the button
      await forgotBtn.trigger('click')
      
      await wrapper.vm.$nextTick()
      
      // Modal should be visible (check for modal content)
      const modal = wrapper.find('.fixed.inset-0')
      expect(modal.exists()).toBe(true)
    })

    it('closes modal when backdrop is clicked', async () => {
      const wrapper = mount(LoginView, {
        global: {
          plugins: [router],
          stubs: {
            'router-link': {
              template: '<a :href="to"><slot /></a>',
              props: ['to']
            }
          }
        }
      })

      // Open modal first
      const buttons = wrapper.findAll('button')
      const forgotBtn = buttons.find(btn => btn.text().includes('Forgot password?'))
      await forgotBtn.trigger('click')
      
      await wrapper.vm.$nextTick()

      // Find and click the backdrop
      const modal = wrapper.find('.fixed.inset-0')
      expect(modal.exists()).toBe(true)
      
      await modal.trigger('click.self')
      
      await wrapper.vm.$nextTick()
      
      // Modal should be closed
      expect(wrapper.find('.fixed.inset-0').exists()).toBe(false)
    })
  })

  describe('Login with verification error', () => {
    it('shows verification error message', async () => {
      mockLoginFn.mockRejectedValue(new Error('verify your email first'))

      const wrapper = mount(LoginView, {
        global: {
          plugins: [router],
          stubs: {
            'router-link': {
              template: '<a :href="to"><slot /></a>',
              props: ['to']
            }
          }
        }
      })

      const emailInput = wrapper.find('#email')
      const passwordInput = wrapper.find('#password')
      await emailInput.setValue('test@example.com')
      await passwordInput.setValue('password123')

      await wrapper.find('form').trigger('submit.prevent')

      await wrapper.vm.$nextTick()
      expect(wrapper.text()).toContain('email is not verified')
    })
  })
})
