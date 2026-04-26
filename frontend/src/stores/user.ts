import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { authAPI } from '@/api/endpoints'
import type { User } from '@/types'

export const useUserStore = defineStore('user', () => {
  const user = ref<User | null>(null)
  const token = ref<string>(localStorage.getItem('ddyl_token') || '')
  const isLoggedIn = computed(() => !!token.value)

  async function login(username: string, password: string) {
    const res = await authAPI.login({ username, password })
    token.value = res.data.access_token
    localStorage.setItem('ddyl_token', token.value)
    await fetchUser()
    return res.data
  }

  async function fetchUser() {
    try {
      const res = await authAPI.me()
      user.value = res.data
    } catch {
      logout()
    }
  }

  function logout() {
    user.value = null
    token.value = ''
    localStorage.removeItem('ddyl_token')
  }

  return { user, token, isLoggedIn, login, fetchUser, logout }
})
