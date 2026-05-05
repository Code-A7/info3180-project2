import { describe, it, expect } from 'vitest'
import { mount } from '@vue/test-utils'
import BaseButton from '@/components/ui/BaseButton.vue'

describe('BaseButton', () => {
  it('renders button with default slot content', () => {
    const wrapper = mount(BaseButton, {
      slots: { default: 'Click Me' }
    })
    expect(wrapper.text()).toContain('Click Me')
    expect(wrapper.find('button').exists()).toBe(true)
  })

  it('renders with primary variant by default', () => {
    const wrapper = mount(BaseButton)
    expect(wrapper.find('.bg-primary-500').exists()).toBe(true)
  })

  it('renders with primary variant', () => {
    const wrapper = mount(BaseButton, {
      props: { variant: 'primary' }
    })
    expect(wrapper.find('.bg-primary-500').exists()).toBe(true)
  })

  it('renders with secondary variant', () => {
    const wrapper = mount(BaseButton, {
      props: { variant: 'secondary' }
    })
    expect(wrapper.find('.bg-gray-100').exists()).toBe(true)
  })

  it('renders with outline variant', () => {
    const wrapper = mount(BaseButton, {
      props: { variant: 'outline' }
    })
    expect(wrapper.find('.border-2').exists()).toBe(true)
    expect(wrapper.find('.border-primary-500').exists()).toBe(true)
  })

  it('renders with ghost variant', () => {
    const wrapper = mount(BaseButton, {
      props: { variant: 'ghost' }
    })
    expect(wrapper.find('.text-gray-600').exists()).toBe(true)
  })

  it('renders with danger variant', () => {
    const wrapper = mount(BaseButton, {
      props: { variant: 'danger' }
    })
    expect(wrapper.find('.bg-red-500').exists()).toBe(true)
  })

  it('renders with small size', () => {
    const wrapper = mount(BaseButton, {
      props: { size: 'sm' }
    })
    expect(wrapper.find('.px-3').exists()).toBe(true)
    expect(wrapper.find('.py-1\\.5').exists()).toBe(true)
    expect(wrapper.find('.text-sm').exists()).toBe(true)
  })

  it('renders with medium size by default', () => {
    const wrapper = mount(BaseButton)
    expect(wrapper.find('.px-4').exists()).toBe(true)
    expect(wrapper.find('.py-2').exists()).toBe(true)
  })

  it('renders with large size', () => {
    const wrapper = mount(BaseButton, {
      props: { size: 'lg' }
    })
    expect(wrapper.find('.px-6').exists()).toBe(true)
    expect(wrapper.find('.py-3').exists()).toBe(true)
    expect(wrapper.find('.text-lg').exists()).toBe(true)
  })

  it('is disabled when disabled prop is true', () => {
    const wrapper = mount(BaseButton, {
      props: { disabled: true }
    })
    expect(wrapper.find('button').attributes('disabled')).toBeDefined()
    expect(wrapper.find('.opacity-50').exists()).toBe(true)
  })

  it('is disabled when loading prop is true', () => {
    const wrapper = mount(BaseButton, {
      props: { loading: true }
    })
    expect(wrapper.find('button').attributes('disabled')).toBeDefined()
    expect(wrapper.find('.opacity-50').exists()).toBe(true)
  })

  it('shows loading spinner when loading', () => {
    const wrapper = mount(BaseButton, {
      props: { loading: true }
    })
    expect(wrapper.find('.animate-spin').exists()).toBe(true)
  })

  it('hides loading spinner when not loading', () => {
    const wrapper = mount(BaseButton)
    expect(wrapper.find('.animate-spin').exists()).toBe(false)
  })

  it('emits click event when clicked', async () => {
    const wrapper = mount(BaseButton)
    await wrapper.find('button').trigger('click')
    expect(wrapper.emitted('click')).toBeTruthy()
  })

  it('does not emit click when disabled', async () => {
    const wrapper = mount(BaseButton, {
      props: { disabled: true }
    })
    await wrapper.find('button').trigger('click')
    expect(wrapper.emitted('click')).toBeFalsy()
  })

  it('does not emit click when loading', async () => {
    const wrapper = mount(BaseButton, {
      props: { loading: true }
    })
    await wrapper.find('button').trigger('click')
    expect(wrapper.emitted('click')).toBeFalsy()
  })
})
