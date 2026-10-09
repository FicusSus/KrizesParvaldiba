import { apiService } from './api'
import { 
  Warning, 
  WarningType, 
  WarningPriority, 
  WarningStatus,
  PaginatedResponse,
  QueryParams,
  ApiResponse 
} from '../types'

// Endpoint paths
const WARNING_ENDPOINTS = {
  LIST: '/warnings',
  CREATE: '/warnings',
  DETAIL: '/warnings/{id}',
  UPDATE: '/warnings/{id}',
  DELETE: '/warnings/{id}',
  READ: '/warnings/{id}/read',
  RETRY: '/warnings/{id}/retry',
}

// Warning service class
class WarningService {
  async getWarnings(
    params: QueryParams & {
      warning_type?: WarningType
      priority?: WarningPriority
      status?: WarningStatus
      user_id?: number
      crisis_id?: number
      is_read?: boolean
      search?: string
    } = {}
  ): Promise<PaginatedResponse<Warning>> {
    try {
      return await apiService.paginatedGet<Warning>(WARNING_ENDPOINTS.LIST, params)
    } catch (error) {
      throw error
    }
  }

  async getWarning(id: number): Promise<Warning> {
    try {
      const response = await apiService.get<ApiResponse<Warning>>(
        WARNING_ENDPOINTS.DETAIL.replace('{id}', id.toString())
      )
      return response.data.data
    } catch (error) {
      throw error
    }
  }

  async createWarning(warningData: Partial<Warning>): Promise<Warning> {
    try {
      const response = await apiService.post<ApiResponse<Warning>>(
        WARNING_ENDPOINTS.CREATE,
        warningData
      )
      return response.data.data
    } catch (error) {
      throw error
    }
  }

  async updateWarning(
    id: number,
    warningData: Partial<Warning>
  ): Promise<Warning> {
    try {
      const response = await apiService.put<ApiResponse<Warning>>(
        WARNING_ENDPOINTS.UPDATE.replace('{id}', id.toString()),
        warningData
      )
      return response.data.data
    } catch (error) {
      throw error
    }
  }

  async deleteWarning(id: number): Promise<void> {
    try {
      await apiService.delete(
        WARNING_ENDPOINTS.DELETE.replace('{id}', id.toString())
      )
    } catch (error) {
      throw error
    }
  }

  async markAsRead(id: number): Promise<Warning> {
    try {
      const response = await apiService.post<ApiResponse<Warning>>(
        WARNING_ENDPOINTS.READ.replace('{id}', id.toString())
      )
      return response.data.data
    } catch (error) {
      throw error
    }
  }

  async retryWarning(id: number): Promise<Warning> {
    try {
      const response = await apiService.post<ApiResponse<Warning>>(
        WARNING_ENDPOINTS.RETRY.replace('{id}', id.toString())
      )
      return response.data.data
    } catch (error) {
      throw error
    }
  }

  async getUnreadWarningsCount(): Promise<number> {
    try {
      const response = await this.getWarnings({
        is_read: false,
        size: 1,
      })
      return response.total
    } catch (error) {
      return 0
    }
  }

  async getWarningStats(): Promise<{
    total: number
    delivered: number
    pending: number
    failed: number
    byType: Record<WarningType, number>
    byPriority: Record<WarningPriority, number>
    byStatus: Record<WarningStatus, number>
  }> {
    try {
      const response = await this.getWarnings({ size: 1000 })
      const warnings = response.items
      
      const stats = {
        total: warnings.length,
        delivered: warnings.filter(w => w.is_delivered).length,
        pending: warnings.filter(w => w.status === WarningStatus.PENDING).length,
        failed: warnings.filter(w => w.status === WarningStatus.FAILED).length,
        byType: { email: 0, sms: 0, push: 0, webhook: 0, in_app: 0 } as Record<WarningType, number>,
        byPriority: { low: 0, medium: 0, high: 0, urgent: 0 } as Record<WarningPriority, number>,
        byStatus: { pending: 0, sent: 0, delivered: 0, failed: 0, read: 0 } as Record<WarningStatus, number>,
      }
      
      warnings.forEach(warning => {
        stats.byType[warning.warning_type] += 1
        stats.byPriority[warning.priority] += 1
        stats.byStatus[warning.status] += 1
      })
      
      return stats
    } catch (error) {
      throw error
    }
  }
}

// Singleton instance
const warningService = new WarningService()

export { warningService, WarningService, WARNING_ENDPOINTS }
export default warningService