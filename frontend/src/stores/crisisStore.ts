import { create } from 'zustand'
import { Crisis, CrisisType, CrisisSeverity, CrisisStatus, PaginatedResponse, QueryParams } from '../types'

interface CrisisState {
  crises: Crisis[]
  total: number
  page: number
  size: number
  pages: number
  hasNext: boolean
  hasPrevious: boolean
  isLoading: boolean
  error: string | null
  filters: {
    crisis_type: CrisisType | ''
    severity: CrisisSeverity | ''
    status: CrisisStatus | ''
    search: string
  }
}

interface CrisisActions {
  setCrises: (data: PaginatedResponse<Crisis>) => void
  setLoading: (isLoading: boolean) => void
  setError: (error: string | null) => void
  setFilters: (filters: Partial<CrisisState['filters']>) => void
  resetFilters: () => void
  addCrisis: (crisis: Crisis) => void
  updateCrisis: (crisis: Crisis) => void
  removeCrisis: (id: number) => void
}

type CrisisStore = CrisisState & CrisisActions

const initialState: CrisisState = {
  crises: [],
  total: 0,
  page: 1,
  size: 10,
  pages: 0,
  hasNext: false,
  hasPrevious: false,
  isLoading: false,
  error: null,
  filters: {
    crisis_type: '',
    severity: '',
    status: '',
    search: '',
  },
}

export const useCrisisStore = create<CrisisStore>((set) => ({
  ...initialState,
  
  setCrises: (data: PaginatedResponse<Crisis>) => {
    set({
      crises: data.items,
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
  
  setFilters: (filters: Partial<CrisisState['filters']>) => {
    set((state) => ({
      filters: { ...state.filters, ...filters },
    }))
  },
  
  resetFilters: () => {
    set({
      filters: initialState.filters,
    })
  },
  
  addCrisis: (crisis: Crisis) => {
    set((state) => ({
      crises: [crisis, ...state.crises],
      total: state.total + 1,
    }))
  },
  
  updateCrisis: (updatedCrisis: Crisis) => {
    set((state) => ({
      crises: state.crises.map((crisis) =>
        crisis.id === updatedCrisis.id ? updatedCrisis : crisis
      ),
    }))
  },
  
  removeCrisis: (id: number) => {
    set((state) => ({
      crises: state.crises.filter((crisis) => crisis.id !== id),
      total: state.total - 1,
    }))
  },
}))

// Selectors
export const selectCrises = (state: CrisisStore) => state.crises
export const selectCrisisLoading = (state: CrisisStore) => state.isLoading
export const selectCrisisError = (state: CrisisStore) => state.error
export const selectCrisisFilters = (state: CrisisStore) => state.filters
export const selectCrisisPagination = (state: CrisisStore) => ({
  page: state.page,
  size: state.size,
  total: state.total,
  pages: state.pages,
  hasNext: state.hasNext,
  hasPrevious: state.hasPrevious,
})