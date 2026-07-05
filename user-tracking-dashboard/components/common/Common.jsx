import React from 'react'
import './components.css'

/**
 * Loading spinner component
 */
export function LoadingSpinner({ size = 'md', color = 'var(--color-primary)' }) {
  const sizeClass = `spinner-${size}`
  return (
    <div className={`spinner ${sizeClass}`} style={{ borderTopColor: color }} />
  )
}

/**
 * Skeleton loader for tables
 */
export function SkeletonRow({ columns = 5 }) {
  return (
    <tr>
      {Array.from({ length: columns }).map((_, i) => (
        <td key={i}>
          <div className="skeleton skeleton-text"></div>
        </td>
      ))}
    </tr>
  )
}

/**
 * Skeleton loader for cards
 */
export function SkeletonCard({ lines = 3 }) {
  return (
    <div className="card">
      <div className="skeleton skeleton-heading"></div>
      {Array.from({ length: lines }).map((_, i) => (
        <div key={i} className="skeleton skeleton-text" style={{ marginTop: '8px' }}></div>
      ))}
    </div>
  )
}

/**
 * Status badge component
 */
export function Badge({ status, label = null }) {
  const colors = {
    active: { bg: '#d1fae5', text: '#065f46' },
    inactive: { bg: '#fef3c7', text: '#78350f' },
    churned: { bg: '#fee2e2', text: '#7f1d1d' },
    completed: { bg: '#d1fae5', text: '#065f46' },
    in_progress: { bg: '#fef3c7', text: '#78350f' },
    not_started: { bg: '#f3f4f6', text: '#4b5563' },
  }
  
  const color = colors[status] || colors.not_started
  
  return (
    <span
      className="badge"
      style={{
        backgroundColor: color.bg,
        color: color.text,
      }}
    >
      {label || status}
    </span>
  )
}

/**
 * Card component
 */
export function Card({ children, className = '', onClick = null }) {
  return (
    <div className={`card ${className}`} onClick={onClick}>
      {children}
    </div>
  )
}

/**
 * Stat card for dashboard
 */
export function StatCard({ title, value, subtitle = null, trend = null, icon = null }) {
  return (
    <Card className="stat-card">
      <div className="stat-header">
        <div>
          <p className="stat-title">{title}</p>
          <h3 className="stat-value">{value}</h3>
        </div>
        {icon && <div className="stat-icon">{icon}</div>}
      </div>
      
      {(subtitle || trend) && (
        <div className="stat-footer">
          {subtitle && <p className="stat-subtitle">{subtitle}</p>}
          {trend && (
            <span className={`trend trend-${trend > 0 ? 'up' : trend < 0 ? 'down' : 'flat'}`}>
              {trend > 0 ? '↑' : trend < 0 ? '↓' : '→'} {Math.abs(trend).toFixed(1)}%
            </span>
          )}
        </div>
      )}
    </Card>
  )
}

/**
 * Modal/Dialog component
 */
export function Modal({ isOpen, onClose, title, children, footer = null, size = 'md' }) {
  if (!isOpen) return null
  
  return (
    <div className="modal-overlay" onClick={onClose}>
      <div className={`modal modal-${size}`} onClick={(e) => e.stopPropagation()}>
        <div className="modal-header">
          <h2>{title}</h2>
          <button className="btn-ghost" onClick={onClose}>
            ✕
          </button>
        </div>
        
        <div className="modal-body">
          {children}
        </div>
        
        {footer && (
          <div className="modal-footer">
            {footer}
          </div>
        )}
      </div>
    </div>
  )
}

/**
 * Empty state component
 */
export function EmptyState({ icon = '📭', title = 'No data', description = '', action = null }) {
  return (
    <div className="empty-state">
      <div className="empty-icon">{icon}</div>
      <h3>{title}</h3>
      {description && <p>{description}</p>}
      {action && <div className="empty-action">{action}</div>}
    </div>
  )
}

/**
 * Error alert component
 */
export function Alert({ type = 'error', message, onClose = null }) {
  const colors = {
    error: { bg: 'var(--color-danger-light)', text: 'var(--color-danger)', border: 'var(--color-danger)' },
    warning: { bg: 'var(--color-warning-light)', text: 'var(--color-warning)', border: 'var(--color-warning)' },
    success: { bg: 'var(--color-success-light)', text: 'var(--color-success)', border: 'var(--color-success)' },
    info: { bg: '#dbeafe', text: 'var(--color-primary)', border: 'var(--color-primary)' },
  }
  
  const color = colors[type] || colors.error
  
  return (
    <div
      className="alert"
      style={{
        backgroundColor: color.bg,
        color: color.text,
        borderLeftColor: color.border,
      }}
    >
      <div className="alert-content">{message}</div>
      {onClose && (
        <button className="btn-ghost btn-sm" onClick={onClose}>
          ✕
        </button>
      )}
    </div>
  )
}

/**
 * Pagination component
 */
export function Pagination({ page, totalPages, onPageChange }) {
  const pages = []
  const maxVisible = 5
  
  let startPage = Math.max(1, page - Math.floor(maxVisible / 2))
  let endPage = Math.min(totalPages, startPage + maxVisible - 1)
  startPage = Math.max(1, endPage - maxVisible + 1)
  
  if (startPage > 1) {
    pages.push(
      <button
        key="first"
        className="btn-ghost btn-sm"
        onClick={() => onPageChange(1)}
      >
        «
      </button>
    )
  }
  
  for (let i = startPage; i <= endPage; i++) {
    pages.push(
      <button
        key={i}
        className={`btn-ghost btn-sm ${i === page ? 'active' : ''}`}
        onClick={() => onPageChange(i)}
      >
        {i}
      </button>
    )
  }
  
  if (endPage < totalPages) {
    pages.push(
      <button
        key="last"
        className="btn-ghost btn-sm"
        onClick={() => onPageChange(totalPages)}
      >
        »
      </button>
    )
  }
  
  return <div className="pagination">{pages}</div>
}

/**
 * Tooltip component
 */
export function Tooltip({ text, children }) {
  return (
    <div className="tooltip-container">
      {children}
      <div className="tooltip">{text}</div>
    </div>
  )
}
