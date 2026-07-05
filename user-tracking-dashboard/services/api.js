// API service - centralized axios wrapper for all backend calls
import axios from 'axios'

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000/api'

const apiClient = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
})

// Add auth token to requests
apiClient.interceptors.request.use((config) => {
  const token = localStorage.getItem('auth_token')
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

// Handle errors globally
apiClient.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      localStorage.removeItem('auth_token')
      window.location.href = '/login'
    }
    return Promise.reject(error)
  }
)

// Users API endpoints
export const usersApi = {
  getUsers: async (page = 1, limit = 20, filters = {}) => {
    const params = new URLSearchParams({ page, limit, ...filters })
    return apiClient.get(`/users?${params}`)
  },

  getUser: async (userId) => {
    return apiClient.get(`/users/${userId}`)
  },

  updateUser: async (userId, payload) => {
    return apiClient.put(`/users/${userId}`, payload)
  },

  deleteUser: async (userId) => {
    return apiClient.delete(`/users/${userId}`)
  },

  setGlobalTokenLimit: async (tokenLimit) => {
    return apiClient.put('/users/bulk-limit', { token_limit: tokenLimit })
  },

  searchUsers: async (query, field = 'name') => {
    return apiClient.get('/users/search', {
      params: { q: query, field },
    })
  },

  exportUsers: async (filters = {}) => {
    return apiClient.get('/users/export', {
      params: filters,
      responseType: 'blob',
    })
  },
}

// Dashboard stats API
export const statsApi = {
  getDashboardStats: async () => {
    return apiClient.get('/stats/dashboard')
  },

  getTokenTrends: async (days = 30) => {
    return apiClient.get('/stats/token-trends', {
      params: { days },
    })
  },

  getUserSegments: async () => {
    return apiClient.get('/stats/user-segments')
  },
}

export default {
  users: usersApi,
  stats: statsApi,
}
