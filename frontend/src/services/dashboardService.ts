import { crisisService } from './crisisService'
import { warningService } from './warningService'
import { dataService } from './dataService'
import { DashboardStats, CrisisTrendData, DataProcessingStats } from '../types'

// Dashboard service class
class DashboardService {
  async getDashboardStats(): Promise<DashboardStats> {
    try {
      // Get statistics from different services
      const [crisisStats, warningStats, dataStats] = await Promise.all([
        crisisService.getCrisisStats(),
        warningService.getWarningStats(),
        dataService.getDataStats(),
      ])
      
      return {
        total_datasets: dataStats.total_datasets,
        processed_datasets: dataStats.processed_datasets,
        pending_datasets: dataStats.pending_datasets,
        total_crises: crisisStats.total,
        active_crises: crisisStats.active,
        high_priority_crises: crisisStats.bySeverity["critical"] + crisisStats.bySeverity["high"],
        total_warnings: warningStats.total,
        delivered_warnings: warningStats.delivered,
        pending_warnings: warningStats.pending,
        model_accuracy: null, // Would come from prediction service
        system_health: 'healthy',
      }
    } catch (error) {
      console.error('Failed to get dashboard stats:', error)
      throw error
    }
  }

  async getCrisisTrends(days: number = 30): Promise<CrisisTrendData[]> {
    try {
      // In a real implementation, this would come from a specific endpoint
      // For now, we'll generate mock data
      const trends: CrisisTrendData[] = []
      const today = new Date()
      
      for (let i = days - 1; i >= 0; i--) {
        const date = new Date(today)
        date.setDate(today.getDate() - i)
        
        const dateStr = date.toISOString().split('T')[0]
        const baseCount = Math.floor(Math.random() * 5) + 1
        
        trends.push({
          date: dateStr,
          total: baseCount * (i % 3 === 0 ? 2 : 1),
          byType: {
            financial: baseCount,
            economic: baseCount * (i % 2 === 0 ? 2 : 1),
            political: baseCount * (i % 3 === 0 ? 2 : 1),
            social: baseCount * (i % 4 === 0 ? 2 : 1),
            environmental: baseCount * (i % 5 === 0 ? 2 : 1),
            health: baseCount * (i % 6 === 0 ? 2 : 1),
            security: baseCount * (i % 7 === 0 ? 2 : 1),
            other: baseCount * (i % 8 === 0 ? 2 : 1),
          },
          bySeverity: {
            low: baseCount * 2,
            medium: baseCount * 3,
            high: baseCount * 1,
            critical: baseCount * (i % 10 === 0 ? 1 : 0),
          },
        })
      }
      
      return trends
    } catch (error) {
      console.error('Failed to get crisis trends:', error)
      throw error
    }
  }

  async getDataProcessingStats(): Promise<DataProcessingStats> {
    try {
      const dataStats = await dataService.getDataStats()
      
      return {
        total_size: dataStats.total_size,
        processed_size: dataStats.total_size * 0.7, // Mock
        row_count: Math.floor(dataStats.total_size / 100), // Mock
        column_count: 15, // Mock
        processing_time: 125.5, // Mock
        memory_usage: 65.2, // Mock
      }
    } catch (error) {
      console.error('Failed to get data processing stats:', error)
      throw error
    }
  }

  async getRecentCrises(limit: number = 5): Promise<any[]> {
    try {
      const response = await crisisService.getCrises({
        page: 1,
        size: limit,
        sort_by: 'created_at',
        sort_order: 'desc',
      })
      return response.items
    } catch (error) {
      console.error('Failed to get recent crises:', error)
      return []
    }
  }

  async getRecentWarnings(limit: number = 5): Promise<any[]> {
    try {
      const response = await warningService.getWarnings({
        page: 1,
        size: limit,
        sort_by: 'created_at',
        sort_order: 'desc',
      })
      return response.items
    } catch (error) {
      console.error('Failed to get recent warnings:', error)
      return []
    }
  }
}

// Singleton instance
const dashboardService = new DashboardService()

export { dashboardService, DashboardService }
export default dashboardService