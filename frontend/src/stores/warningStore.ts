import { create } from 'zustand'
import { Warning, WarningType, WarningPriority, WarningStatus, PaginatedResponse } from '../types'

interface WarningState {
  warnings: Warning[]
  total: number
  page: number
  size: number
  pages: number
  hasNext: boolean
  hasPrevious: boolean
  isLoading: boolean
  error: string | null
  filters: {
    warning_type: WarningType | ''
    priority: WarningPriority | ''
    status: WarningStatus | ''
    is_read: boolean | ''
    search: string
  }
  unreadCount: number
}

interface WarningActions {
  setWarnings: (data: PaginatedResponse<Warning>) => void
  setLoading: (isLoading: boolean) => void
  setError: (error: string | null) => void
  setFilters: (filters: Partial<WarningState['filters']>) => void
  resetFilters: () => void
  addWarning: (warning: Warning) => void
  updateWarning: (warning: Warning) => void
  removeWarning: (id: number) => void
  markAsRead: (id: number) => void
  setUnreadCount: (count: number) => void
}

type WarningStore = WarningState & WarningActions

const initialState: WarningState = {
  warnings: [],
  total: 0,
  page: 1,
  size: 10,
  pages: 0,
  hasNext: false,
  hasPrevious: false,
  isLoading: false,
  error: null,
  filters: {
    warning_type: '',
    priority: '',
    status: '',
    is_read: '',
    search: '',
  },
  unreadCount: 0,
}

export const useWarningStore = create<WarningStore>((set) => ({
  ...initialState,
  
  setWarnings: (data: PaginatedResponse<Warning>) => {
    set({
      warnings: data.items,
      total: data.total,
      page: data.page,
      size: data.size,
      pages: data.pages,
      hasNext: data.has_next,
      hasPrevious: data.has_previous,
    })
  },
  
  setLoading: (isLoading: boolean) => {
    set({ isLoading })
  },
  
  setError: (error: string | null) => {
    set({ error })
  },
  
  setFilters: (filters: Partial<WarningState['filters']>) => {
    set((state) => ({
      filters: { ...state.filters, ...filters },
    }))
  },
  
  resetFilters: () => {
    set({
      filters: initialState.filters,
    })
  },
  
  addWarning: (warning: Warning) => {
    set((state) => ({
      warnings: [warning, ...state.warnings],
      total: state.total + 1,
      unreadCount: warning.is_read ? state.unreadCount : state.unreadCount + 1,
    }))
  },
  
  updateWarning: (updatedWarning: Warning) => {
    set((state) => ({
      warnings: state.warnings.map((warning) =>
        warning.id === updatedWarning.id ? updatedWarning : warning
      ),
      unreadCount: state.warnings.reduce(
        (count, warning) => count + (warning.id === updatedWarning.id ? (updatedWarning.is_read ? 0 : 1) : (warning.is_read ? 0 : 1)),
        0
      ),
    }))
  },
  
  removeWarning: (id: number) => {
    set((state) => ({
      warnings: state.warnings.filter((warning) => warning.id !== id),
      total: state.total - 1,
    }))
  },
  
  markAsRead: (id: number) => {
    set((state) => ({
      warnings: state.warnings.map((warning) =>
        warning.id === id ? { ...warning, is_read: true } : warning
      ),
      unreadCount: Math.max(0, state.unreadCount - 1),
    }))
  },
  
  setUnreadCount: (count: number) => {
    set({ unreadCount: count })
  },
}))

// Selectors
export const selectWarnings = (state: WarningStore) => state.warnings
export const selectWarningLoading = (state: WarningStore) => state.isLoading
export const selectWarningError = (state: WarningStore) => state.error
export const selectWarningFilters = (state: WarningStore) => state.filters
export const selectWarningPagination = (state: WarningStore) => ({
  page: state.page,
  size: state.size,
  total: state.total,
  pages: state.pages,
  hasNext: state.hasNext,
  hasPrevious: state.hasPrevious,
})
export const selectUnreadCount = (state: WarningStore) => state.unreadCount