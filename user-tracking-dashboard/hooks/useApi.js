import { useState, useEffect, useCallback } from 'react'
import { usersApi, statsApi } from '../services/api'

/**
 * Generic API hook for fetching data
 */
export function useApi(apiCall, dependencies = []) {
  const [data, setData] = useState(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)

  useEffect(() => {
    let isMounted = true

    const fetchData = async () => {
      try {
        setLoading(true)
        setError(null)
        const response = await apiCall()
        if (isMounted) {
          setData(response.data)
        }
      } catch (err) {
        if (isMounted) {
          setError(err.response?.data?.message || err.message || 'An error occurred')
        }
      } finally {
        if (isMounted) {
          setLoading(false)
        }
      }
    }

    fetchData()

    return () => {
      isMounted = false
    }
  }, dependencies)

  return { data, loading, error }
}

/**
 * Fetch all users with pagination and filtering
 */
export function useUsers(page = 1, limit = 20, filters = {}, refreshKey = 0) {
  return useApi(
    () => usersApi.getUsers(page, limit, filters),
    [page, limit, JSON.stringify(filters), refreshKey]
  )
}

/**
 * Fetch single user details
 */
export function useUserDetails(userId) {
  return useApi(
    () => usersApi.getUser(userId),
    [userId]
  )
}

/**
 * Search users
 */
export function useSearchUsers(query = '', field = 'name') {
  const [results, setResults] = useState([])
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)

  useEffect(() => {
    if (!query.trim()) {
      setResults([])
      return
    }

    let isMounted = true
    const timer = setTimeout(async () => {
      try {
        setLoading(true)
        const response = await usersApi.searchUsers(query, field)
        if (isMounted) {
          setResults(response.data.users || [])
        }
      } catch (err) {
        if (isMounted) {
          setError(err.message)
        }
      } finally {
        if (isMounted) {
          setLoading(false)
        }
      }
    }, 300) // Debounce

    return () => {
      clearTimeout(timer)
      isMounted = false
    }
  }, [query, field])

  return { results, loading, error }
}

/**
 * Fetch dashboard stats
 */
export function useDashboardStats() {
  return useApi(() => statsApi.getDashboardStats(), [])
}

/**
 * Fetch token usage trends
 */
export function useTokenTrends(days = 30) {
  return useApi(
    () => statsApi.getTokenTrends(days),
    [days]
  )
}

/**
 * Fetch user segments
 */
export function useUserSegments() {
  return useApi(() => statsApi.getUserSegments(), [])
}

/**
 * Manual refetch hook for pagination/filtering changes
 */
export function useRefetch() {
  const [refetchKey, setRefetchKey] = useState(0)
  const refetch = useCallback(() => {
    setRefetchKey((prev) => prev + 1)
  }, [])
  return { refetchKey, refetch }
}
