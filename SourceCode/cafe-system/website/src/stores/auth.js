import { defineStore } from 'pinia'
import apiClient from '@/services/api'

export const useAuthStore = defineStore('auth', {
  state: () => ({
    user: null,
    accessToken: localStorage.getItem('access_token') || null,
    refreshToken: localStorage.getItem('refresh_token') || null,
    isAuthenticated: !!localStorage.getItem('access_token')
  }),

  getters: {
    currentUser: (state) => state.user,
    isLoggedIn: (state) => state.isAuthenticated
  },

  actions: {
    async login(credentials) {
      try {
        const { data } = await apiClient.post('/token/', credentials)
        this.accessToken = data.access
        this.refreshToken = data.refresh
        this.isAuthenticated = true

        localStorage.setItem('access_token', data.access)
        localStorage.setItem('refresh_token', data.refresh)

        return data
      } catch (error) {
        throw error
      }
    },

    logout() {
      this.user = null
      this.accessToken = null
      this.refreshToken = null
      this.isAuthenticated = false

      localStorage.removeItem('access_token')
      localStorage.removeItem('refresh_token')
    }
  }
})
