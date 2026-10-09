import { apiService } from './api'
import { 
  Crisis, 
  CrisisType, 
  CrisisSeverity, 
  CrisisStatus,
  PaginatedResponse,
  QueryParams,
  ApiResponse 
} from '../types'

// Endpoint paths
const CRISIS_ENDPOINTS = {
  LIST: '/crisis',
  CREATE: '/crisis/predict',
  DETAIL: '/crisis/{id}',
  UPDATE: '/crisis/{id}',
  DELETE: '/crisis/{id}',
  CONFIRM: '/crisis/{id}/confirm',
  RESOLVE: '/crisis/{id}/resolve',
  FALSE_ALARM: '/crisis/{id}/false-alarm',
}

// Crisis service class
class CrisisService {
  async getCrises(
    params: QueryParams & {
      crisis_type?: CrisisType
      severity?: CrisisSeverity
      status?: CrisisStatus
      dataset_id?: number
      is_active?: boolean
      search?: string
    } = {}
  ): Promise<PaginatedResponse<Crisis>> {
    try {
      return await apiService.paginatedGet<Crisis>(CRISIS_ENDPOINTS.LIST, params)
    } catch (error) {
      throw error
    }
  }

  async getCrisis(id: number): Promise<Crisis> {
    try {
      const response = await apiService.get<ApiResponse<Crisis>>(
        CRISIS_ENDPOINTS.DETAIL.replace('{id}', id.toString())
      )
      return response.data.data
    } catch (error) {
      throw error
    }
  }

  async createCrisis(crisisData: Partial<Crisis>): Promise<Crisis> {
    try {
      const response = await apiService.post<ApiResponse<Crisis>>(
        CRISIS_ENDPOINTS.CREATE,
        crisisData
      )
      return response.data.data
    } catch (error) {
      throw error
    }
  }

  async updateCrisis(
    id: number,
    crisisData: Partial<Crisis>
  ): Promise<Crisis> {
    try {
      const response = await apiService.put<ApiResponse<Crisis>>(
        CRISIS_ENDPOINTS.UPDATE.replace('{id}', id.toString()),
        crisisData
      )
      return response.data.data
    } catch (error) {
      throw error
    }
  }

  async deleteCrisis(id: number): Promise<void> {
    try {
      await apiService.delete(
        CRISIS_ENDPOINTS.DELETE.replace('{id}', id.toString())
      )
    } catch (error) {
      throw error
    }
  }

  async confirmCrisis(id: number): Promise<Crisis> {
    try {
      const response = await apiService.post<ApiResponse<Crisis>>(
        CRISIS_ENDPOINTS.CONFIRM.replace('{id}', id.toString())
      )
      return response.data.data
    } catch (error) {
      throw error
    }
  }

  async resolveCrisis(id: number): Promise<Crisis> {
    try {
      const response = await apiService.post<ApiResponse<Crisis>>(
        CRISIS_ENDPOINTS.RESOLVE.replace('{id}', id.toString())
      )
      return response.data.data
    } catch (error) {
      throw error
    }
  }

  async markAsFalseAlarm(id: number): Promise<Crisis> {
    try {
      const response = await apiService.post<ApiResponse<Crisis>>(
        CRISIS_ENDPOINTS.FALSE_ALARM.replace('{id}', id.toString())
      )
      return response.data.data
    } catch (error) {
      throw error
    }
  }

  async getCrisisStats(): Promise<{
    total: number
    active: number
    byType: Record<CrisisType, number>
    bySeverity: Record<CrisisSeverity, number>
    byStatus: Record<CrisisStatus, number>
  }> {
    try {
      // This would be a specific endpoint for crisis statistics
      // For now, we'll get all crises and compute stats client-side
      const response = await this.getCrises({ size: 1000 })
      const crises = response.items
      
      const stats = {
        total: crises.length,
        active: crises.filter(c => c.is_active).length,
        byType: { low: 0, medium: 0, high: 0, critical: 0 } as Record<CrisisSeverity, number>,
        bySeverity: { financial: 0, economic: 0, political: 0, social: 0, environmental: 0, health: 0, security: 0, other: 0 } as Record<CrisisType, number>,
        byStatus: { predicted: 0, confirmed: 0, ongoing: 0, resolved: 0, false_alarm: 0 } as Record<CrisisStatus, number>,
      }
      
      crises.forEach(crisis => {
        stats.byType[crisis.severity] += 1
        stats.bySeverity[crisis.crisis_type] += 1
        stats.byStatus[crisis.status] += 1
      })
      
      return stats
    } catch (error) {
      throw error
    }
  }
}

// Singleton instance
const crisisService = new CrisisService()

export { crisisService, CrisisService, CRISIS_ENDPOINTS }
export default crisisService