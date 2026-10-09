import { apiService } from './api'
import type { User, LoginCredentials, RegisterCredentials, ApiResponse } from '../types'
import { useAuthStore } from '../stores/authStore'

// Endpoint paths
const AUTH_ENDPOINTS = {
  LOGIN: '/users/token',
  REGISTER: '/users/register',
  ME: '/users/me',
  LOGOUT: '/users/logout',
  REFRESH: '/users/refresh',
}

// Auth service class
class AuthService {
  async login(credentials: LoginCredentials): Promise<{ user: User; token: string }> {
    try {
      const response = await apiService.post<ApiResponse<{ 
        user: User 
        access_token: string 
        refresh_token: string 
      }>(AUTH_ENDPOINTS.LOGIN, credentials)
      
      const { user, access_token: token } = response.data.data
      
      // Store auth state
      useAuthStore.getState().setUser(user)
      useAuthStore.getState().setToken(token)
      useAuthStore.getState().setLoading(false)
      
      return { user, token }
    } catch (error) {
      useAuthStore.getState().setLoading(false)
      throw error
    }
  }

  async register(credentials: RegisterCredentials): Promise<{ user: User; token: string }> {
    try {
      const response = await apiService.post<ApiResponse<{ 
        user: User 
        access_token: string 
        refresh_token: string 
      }>(AUTH_ENDPOINTS.REGISTER, credentials)
      
      const { user, access_token: token } = response.data.data
      
      // Store auth state
      useAuthStore.getState().setUser(user)
      useAuthStore.getState().setToken(token)
      useAuthStore.getState().setLoading(false)
      
      return { user, token }
    } catch (error) {
      useAuthStore.getState().setLoading(false)
      throw error
    }
  }

  async checkAuth(): Promise<{ user: User | null; token: string | null }> {
    try {
      const response = await apiService.get<ApiResponse<User>>(AUTH_ENDPOINTS.ME)
      const user = response.data.data
      const token = useAuthStore.getState().token
      
      return { user, token }
    } catch (error) {
      return { user: null, token: null }
    }
  }

  async logout(): Promise<void> {
    try {
      // In a real implementation, you might call a logout endpoint
      // For now, we'll just clear the local auth state
      useAuthStore.getState().clearAuth()
    } catch (error) {
      // Ensure auth is cleared even if logout fails
      useAuthStore.getState().clearAuth()
      throw error
    }
  }

  async refreshToken(refreshToken: string): Promise<{ token: string }> {
    try {
      const response = await apiService.post<ApiResponse<{ 
        access_token: string 
        refresh_token: string 
      }>(AUTH_ENDPOINTS.REFRESH, { refresh_token: refreshToken })
      
      const { access_token: token } = response.data.data
      
      // Update token in store
      useAuthStore.getState().setToken(token)
      
      return { token }
    } catch (error) {
      // Clear auth if refresh fails
      useAuthStore.getState().clearAuth()
      throw error
    }
  }
}

// Singleton instance
const authService = new AuthService()

// Convenience function for checking auth
export const checkAuth = async () => {
  return authService.checkAuth()
}

// Convenience function for logout
export const logout = async () => {
  return authService.logout()
}

export { authService, AuthService, AUTH_ENDPOINTS }
export default authService