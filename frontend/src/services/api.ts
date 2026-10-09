import axios, { AxiosInstance, AxiosRequestConfig, AxiosResponse, AxiosError } from 'axios'
import { toast } from 'sonner'
import { ErrorResponse, PaginatedResponse, QueryParams, FilterParams } from '../types'
import { useAuthStore } from '../stores/authStore'

// Create axios instance
const api: AxiosInstance = axios.create({
  baseURL: import.meta.env.VITE_API_URL || '/api/v1',
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json',
  },
})

// Request interceptor to add auth token
api.interceptors.request.use(
  (config: AxiosRequestConfig) => {
    const token = useAuthStore.getState().token
    if (token && config.headers) {
      config.headers.Authorization = `Bearer ${token}`
    }
    return config
  },
  (error: AxiosError) => {
    return Promise.reject(error)
  }
)

// Response interceptor to handle errors
api.interceptors.response.use(
  (response: AxiosResponse) => response,
  (error: AxiosError<ErrorResponse>) => {
    // Handle specific error cases
    if (error.response) {
      const { status, data } = error.response
      
      switch (status) {
        case 401:
          // Unauthorized - clear auth and redirect to login
          useAuthStore.getState().clearAuth()
          window.location.href = '/login'
          break
          
        case 403:
          toast.error('Access denied', { description: data?.message || 'You do not have permission' })
          break
          
        case 404:
          toast.error('Not found', { description: data?.message || 'Resource not found' })
          break
          
        case 400:
        case 422:
          toast.error('Validation error', { description: data?.message || 'Please check your input' })
          break
          
        case 500:
          toast.error('Server error', { description: data?.message || 'An unexpected error occurred' })
          break
          
        default:
          toast.error('Error', { description: data?.message || 'An error occurred' })
      }
    } else if (error.request) {
      // Network error
      toast.error('Network error', { description: 'Please check your internet connection' })
    } else {
      // Other errors
      toast.error('Error', { description: error.message })
    }
    
    return Promise.reject(error)
  }
)

// Generic API methods
class ApiService {
  get<T>(url: string, config?: AxiosRequestConfig): Promise<AxiosResponse<T>> {
    return api.get<T>(url, config)
  }

  post<T>(url: string, data?: unknown, config?: AxiosRequestConfig): Promise<AxiosResponse<T>> {
    return api.post<T>(url, data, config)
  }

  put<T>(url: string, data?: unknown, config?: AxiosRequestConfig): Promise<AxiosResponse<T>> {
    return api.put<T>(url, data, config)
  }

  patch<T>(url: string, data?: unknown, config?: AxiosRequestConfig): Promise<AxiosResponse<T>> {
    return api.patch<T>(url, data, config)
  }

  delete<T>(url: string, config?: AxiosRequestConfig): Promise<AxiosResponse<T>> {
    return api.delete<T>(url, config)
  }

  // Helper method for paginated requests
  async paginatedGet<T>(
    url: string,
    params: QueryParams & FilterParams = {},
    config?: AxiosRequestConfig
  ): Promise<PaginatedResponse<T>> {
    try {
      const response = await this.get<PaginatedResponse<T>>(url, {
        params,
        ...config,
      })
      return response.data
    } catch (error) {
      throw error
    }
  }
}

// Singleton instance
const apiService = new ApiService()

export { api, apiService, ApiService }
export default api