import { defineStore } from 'pinia'
import { ref } from 'vue'

export const useAuthStore = defineStore('auth', () => {
  const isAuthenticated = ref(false)
  const username = ref('')
  
  // Admin credentials
  const ADMIN_USERNAME = 'admin'
  const ADMIN_PASSWORD = 'admin'

  const login = (user, pass) => {
    if (user === ADMIN_USERNAME && pass === ADMIN_PASSWORD) {
      isAuthenticated.value = true
      username.value = user
      return { success: true }
    }
    return { success: false, error: 'Invalid username or password' }
  }

  const logout = () => {
    isAuthenticated.value = false
    username.value = ''
  }

  return { isAuthenticated, username, login, logout }
})
