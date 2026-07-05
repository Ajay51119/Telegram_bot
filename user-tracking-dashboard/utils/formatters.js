/**
 * Format large numbers with K, M, B suffixes
 */
export function formatNumber(num) {
  if (num == null) return 'N/A'
  if (num >= 1000000) return `${(num / 1000000).toFixed(1)}M`
  if (num >= 1000) return `${(num / 1000).toFixed(1)}K`
  return num.toLocaleString()
}

/**
 * Format token count with better readability
 */
export function formatTokens(tokens) {
  if (tokens == null) return 'N/A'
  return tokens.toLocaleString()
}

/**
 * Format date to human readable format
 */
export function formatDate(dateString) {
  if (!dateString) return 'N/A'
  const date = new Date(dateString)
  return date.toLocaleDateString('en-US', {
    year: 'numeric',
    month: 'short',
    day: 'numeric',
  })
}

/**
 * Format date and time
 */
export function formatDateTime(dateString) {
  if (!dateString) return 'N/A'
  const date = new Date(dateString)
  return date.toLocaleDateString('en-US', {
    year: 'numeric',
    month: 'short',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit',
  })
}

/**
 * Format relative time (e.g., "2 hours ago")
 */
export function formatRelativeTime(dateString) {
  if (!dateString) return 'N/A'
  
  const date = new Date(dateString)
  const now = new Date()
  const diffMs = now - date
  const diffSecs = Math.floor(diffMs / 1000)
  const diffMins = Math.floor(diffSecs / 60)
  const diffHours = Math.floor(diffMins / 60)
  const diffDays = Math.floor(diffHours / 24)
  
  if (diffSecs < 60) return 'just now'
  if (diffMins < 60) return `${diffMins}m ago`
  if (diffHours < 24) return `${diffHours}h ago`
  if (diffDays < 7) return `${diffDays}d ago`
  if (diffDays < 30) return `${Math.floor(diffDays / 7)}w ago`
  
  return formatDate(dateString)
}

/**
 * Get badge color based on status
 */
export function getStatusColor(status) {
  const colors = {
    active: 'var(--color-success)',
    inactive: 'var(--color-warning)',
    churned: 'var(--color-danger)',
    completed: 'var(--color-success)',
    in_progress: 'var(--color-warning)',
    not_started: 'var(--color-gray-400)',
  }
  return colors[status] || 'var(--color-gray-500)'
}

/**
 * Get badge background color
 */
export function getStatusBgColor(status) {
  const colors = {
    active: 'var(--color-success-light)',
    inactive: 'var(--color-warning-light)',
    churned: 'var(--color-danger-light)',
    completed: 'var(--color-success-light)',
    in_progress: 'var(--color-warning-light)',
    not_started: 'var(--color-gray-100)',
  }
  return colors[status] || 'var(--color-gray-100)'
}

/**
 * Get initials from name
 */
export function getInitials(name) {
  if (!name) return 'U'
  return name
    .split(' ')
    .map((n) => n[0])
    .join('')
    .toUpperCase()
    .slice(0, 2)
}

/**
 * Truncate string to length
 */
export function truncate(str, length = 50) {
  if (!str) return ''
  return str.length > length ? str.substring(0, length) + '...' : str
}

/**
 * Mask email (show first 3 chars + domain)
 */
export function maskEmail(email) {
  if (!email) return 'N/A'
  const [localPart, domain] = email.split('@')
  const masked = localPart.substring(0, 3) + '****'
  return `${masked}@${domain}`
}

/**
 * Mask phone number
 */
export function maskPhone(phone) {
  if (!phone) return 'N/A'
  return phone.replace(/(\d{2})\d+(\d{2})/, '$1****$2')
}

/**
 * Download CSV file
 */
export function downloadCSV(csvContent, filename = 'users-export.csv') {
  const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' })
  const link = document.createElement('a')
  const url = URL.createObjectURL(blob)
  
  link.setAttribute('href', url)
  link.setAttribute('download', filename)
  link.style.visibility = 'hidden'
  
  document.body.appendChild(link)
  link.click()
  document.body.removeChild(link)
}

/**
 * Calculate percentage change
 */
export function calculatePercentChange(current, previous) {
  if (!previous || previous === 0) return 0
  return ((current - previous) / previous) * 100
}

/**
 * Format percentage
 */
export function formatPercent(value) {
  if (value == null) return 'N/A'
  return `${value.toFixed(1)}%`
}

/**
 * Get color for trend indicator (green up, red down)
 */
export function getTrendColor(change) {
  if (change > 0) return 'var(--color-success)'
  if (change < 0) return 'var(--color-danger)'
  return 'var(--color-gray-500)'
}
