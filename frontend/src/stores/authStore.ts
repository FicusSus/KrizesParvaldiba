import { create } from 'zustand'
import { persist } from 'zustand/middleware'
import { User, AuthState } from '../types'

interface AuthActions {
  setUser: (user: User) => void
  setToken: (token: string) => void
  clearAuth: () => void
  setLoading: (isLoading: boolean) => void
}

type AuthStore = AuthState & AuthActions

const initialState: AuthState = {
  user: null,
  token: null,
  isAuthenticated: false,
  isLoading: true,
}

export const useAuthStore = create<AuthStore>()(
  persist(
    (set) => ({
      ...initialState,
      
      setUser: (user: User) => {
        set({
          user,
          isAuthenticated: !!user,
        })
      },
      
      setToken: (token: string) => {
        set({
          token,
          isAuthenticated: !!token,
        })
      },
      
      clearAuth: () => {
        set({
          user: null,
          token: null,
          isAuthenticated: false,
        })
      },
      
      setLoading: (isLoading: boolean) => {
        set({ isLoading })
      },
    }),
    {
      name: 'auth-storage',
      partialize: (state) => ({
        user: state.user,
        token: state.token,
        isAuthenticated: state.isAuthenticated,
      }),
    }
  )
)

// Selectors for better performance
export const selectUser = (state: AuthStore) => state.user
export const selectToken = (state: AuthStore) => state.token
export const selectIsAuthenticated = (state: AuthStore) => state.isAuthenticated
export const selectIsLoading = (state: AuthStore) => state.isLoading