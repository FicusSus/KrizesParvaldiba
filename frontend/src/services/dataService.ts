import { apiService } from './api'
import { 
  DataSource, 
  DataSourceType,
  Dataset,
  DatasetType,
  DatasetStatus,
  PaginatedResponse,
  QueryParams,
  ApiResponse 
} from '../types'

// Endpoint paths
const DATA_ENDPOINTS = {
  SOURCES_LIST: '/data/sources',
  SOURCES_CREATE: '/data/sources',
  SOURCES_DETAIL: '/data/sources/{id}',
  SOURCES_UPDATE: '/data/sources/{id}',
  SOURCES_DELETE: '/data/sources/{id}',
  DATASETS_LIST: '/data/datasets',
  DATASETS_CREATE: '/data/datasets',
  DATASETS_DETAIL: '/data/datasets/{id}',
  DATASETS_UPLOAD: '/data/upload',
}

// Data service class
class DataService {
  // Data Sources
  async getDataSources(
    params: QueryParams & {
      source_type?: DataSourceType
      is_active?: boolean
      search?: string
    } = {}
  ): Promise<PaginatedResponse<DataSource>> {
    try {
      return await apiService.paginatedGet<DataSource>(DATA_ENDPOINTS.SOURCES_LIST, params)
    } catch (error) {
      throw error
    }
  }

  async getDataSource(id: number): Promise<DataSource> {
    try {
      const response = await apiService.get<ApiResponse<DataSource>>(
        DATA_ENDPOINTS.SOURCES_DETAIL.replace('{id}', id.toString())
      )
      return response.data.data
    } catch (error) {
      throw error
    }
  }

  async createDataSource(dataSourceData: Partial<DataSource>): Promise<DataSource> {
    try {
      const response = await apiService.post<ApiResponse<DataSource>>(
        DATA_ENDPOINTS.SOURCES_CREATE,
        dataSourceData
      )
      return response.data.data
    } catch (error) {
      throw error
    }
  }

  async updateDataSource(
    id: number,
    dataSourceData: Partial<DataSource>
  ): Promise<DataSource> {
    try {
      const response = await apiService.put<ApiResponse<DataSource>>(
        DATA_ENDPOINTS.SOURCES_UPDATE.replace('{id}', id.toString()),
        dataSourceData
      )
      return response.data.data
    } catch (error) {
      throw error
    }
  }

  async deleteDataSource(id: number): Promise<void> {
    try {
      await apiService.delete(
        DATA_ENDPOINTS.SOURCES_DELETE.replace('{id}', id.toString())
      )
    } catch (error) {
      throw error
    }
  }

  // Datasets
  async getDatasets(
    params: QueryParams & {
      dataset_type?: DatasetType
      status?: DatasetStatus
      data_source_id?: number
      search?: string
    } = {}
  ): Promise<PaginatedResponse<Dataset>> {
    try {
      return await apiService.paginatedGet<Dataset>(DATA_ENDPOINTS.DATASETS_LIST, params)
    } catch (error) {
      throw error
    }
  }

  async getDataset(id: number): Promise<Dataset> {
    try {
      const response = await apiService.get<ApiResponse<Dataset>>(
        DATA_ENDPOINTS.DATASETS_DETAIL.replace('{id}', id.toString())
      )
      return response.data.data
    } catch (error) {
      throw error
    }
  }

  async createDataset(datasetData: Partial<Dataset>): Promise<Dataset> {
    try {
      const response = await apiService.post<ApiResponse<Dataset>>(
        DATA_ENDPOINTS.DATASETS_CREATE,
        datasetData
      )
      return response.data.data
    } catch (error) {
      throw error
    }
  }

  async uploadDataset(
    file: File,
    datasetType: DatasetType = DatasetType.RAW,
    dataSourceId?: number
  ): Promise<Dataset> {
    try {
      const formData = new FormData()
      formData.append('file', file)
      formData.append('dataset_type', datasetType)
      if (dataSourceId) {
        formData.append('data_source_id', dataSourceId.toString())
      }
      
      const response = await apiService.post<ApiResponse<Dataset>>(
        DATA_ENDPOINTS.DATASETS_UPLOAD,
        formData,
        {
          headers: {
            'Content-Type': 'multipart/form-data',
          },
        }
      )
      return response.data.data
    } catch (error) {
      throw error
    }
  }

  async getDataStats(): Promise<{
    total_datasets: number
    processed_datasets: number
    pending_datasets: number
    total_size: number
    by_type: Record<DatasetType, number>
    by_status: Record<DatasetStatus, number>
  }> {
    try {
      const response = await this.getDatasets({ size: 1000 })
      const datasets = response.items
      
      const stats = {
        total_datasets: datasets.length,
        processed_datasets: datasets.filter(d => d.is_processed).length,
        pending_datasets: datasets.filter(d => d.is_processing).length,
        total_size: datasets.reduce((sum, d) => sum + (d.file_size || 0), 0),
        by_type: { raw: 0, processed: 0, aggregated: 0, features: 0 } as Record<DatasetType, number>,
        by_status: { pending: 0, processing: 0, completed: 0, failed: 0, archived: 0 } as Record<DatasetStatus, number>,
      }
      
      datasets.forEach(dataset => {
        stats.by_type[dataset.dataset_type] += 1
        stats.by_status[dataset.status] += 1
      })
      
      return stats
    } catch (error) {
      throw error
    }
  }
}

// Singleton instance
const dataService = new DataService()

export { dataService, DataService, DATA_ENDPOINTS }
export default dataService