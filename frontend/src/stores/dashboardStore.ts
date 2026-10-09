import { create } from 'zustand'
import { DashboardStats, DataProcessingStats, CrisisTrendData } from '../types'

interface DashboardState {
  stats: DashboardStats | null
  crisisTrends: CrisisTrendData[]
  dataProcessingStats: DataProcessingStats | null
  recentCrises: any[]
  recentWarnings: any[]
  isLoading: boolean
  error: string | null
  lastUpdated: string | null
}

interface DashboardActions {
  setStats: (stats: DashboardStats) => void
  setCrisisTrends: (trends: CrisisTrendData[]) => void
  setDataProcessingStats: (stats: DataProcessingStats) => void
  setRecentCrises: (crises: any[]) => void
  setRecentWarnings: (warnings: any[]) => void
  setLoading: (isLoading: boolean) => void
  setError: (error: string | null) => void
  setLastUpdated: (date: string) => void
  refresh: () => void
}

type DashboardStore = DashboardState & DashboardActions

const initialState: DashboardState = {
  stats: null,
  crisisTrends: [],
  dataProcessingStats: null,
  recentCrises: [],
  recentWarnings: [],
  isLoading: false,
  error: null,
  lastUpdated: null,
}

export const useDashboardStore = create<DashboardStore>((set) => ({
  ...initialState,
  
  setStats: (stats: DashboardStats) => {
    set({ stats })
  },
  
  setCrisisTrends: (trends: CrisisTrendData[]) => {
    set({ crisisTrends: trends })
  },
  
  setDataProcessingStats: (stats: DataProcessingStats) => {
    set({ dataProcessingStats: stats })
  },
  
  setRecentCrises: (crises: any[]) => {
    set({ recentCrises: crises })
  },
  
  setRecentWarnings: (warnings: any[]) => {
    set({ recentWarnings: warnings })
  },
  
  setLoading: (isLoading: boolean) => {
    set({ isLoading })
  },
  
  setError: (error: string | null) => {
    set({ error })
  },
  
  setLastUpdated: (date: string) => {
    set({ lastUpdated: date })
  },
  
  refresh: () => {
    set({
      isLoading: true,
      error: null,
    })
  },
}))

// Selectors
export const selectDashboardStats = (state: DashboardStore) => state.stats
export const selectCrisisTrends = (state: DashboardStore) => state.crisisTrends
export const selectDataProcessingStats = (state: DashboardStore) => state.dataProcessingStats
export const selectRecentCrises = (state: DashboardStore) => state.recentCrises
export const selectRecentWarnings = (state: DashboardStore) => state.recentWarnings
export const selectDashboardLoading = (state: DashboardStore) => state.isLoading
export const selectDashboardError = (state: DashboardStore) => state.error
export const selectDashboardLastUpdated = (state: DashboardStore) => state.lastUpdated