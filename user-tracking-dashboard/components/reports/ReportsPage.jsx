import React from 'react'
import { useUserSegments } from '../../hooks/useApi'
import { LoadingSpinner, SkeletonCard, StatCard, EmptyState } from '../common/Common'
import { formatNumber, formatPercent } from '../../utils/formatters'
import './reports.css'

/**
 * Simple pie chart representation
 */
function SimplePieChart({ data, size = 200 }) {
  if (!data || data.length === 0) {
    return (
      <div style={{ height: size, display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
        <div>No data</div>
      </div>
    )
  }

  const total = data.reduce((sum, d) => sum + d.value, 0)
  let currentAngle = 0
  const segments = data.map((d, i) => {
    const sliceAngle = (d.value / total) * 360
    const startAngle = currentAngle
    const endAngle = currentAngle + sliceAngle
    const colors = ['#3b82f6', '#8b5cf6', '#10b981', '#f59e0b']
    const color = colors[i % colors.length]
    currentAngle = endAngle
    return { ...d, startAngle, endAngle, color }
  })

  const radius = size / 2
  const cx = radius
  const cy = radius

  const pathData = segments.map((seg) => {
    const start = ((seg.startAngle - 90) * Math.PI) / 180
    const end = ((seg.endAngle - 90) * Math.PI) / 180
    const x1 = cx + radius * Math.cos(start)
    const y1 = cy + radius * Math.sin(start)
    const x2 = cx + radius * Math.cos(end)
    const y2 = cy + radius * Math.sin(end)
    const largeArc = seg.endAngle - seg.startAngle > 180 ? 1 : 0

    return `M ${cx} ${cy} L ${x1} ${y1} A ${radius} ${radius} 0 ${largeArc} 1 ${x2} ${y2} Z`
  })

  return (
    <svg width={size} height={size} viewBox={`0 0 ${size} ${size}`}>
      {pathData.map((path, i) => (
        <path key={i} d={path} fill={segments[i].color} stroke="white" strokeWidth="2" />
      ))}
    </svg>
  )
}

/**
 * Reports Page
 */
export default function ReportsPage() {
  const { data: segments, loading: segmentsLoading, error: segmentsError } = useUserSegments()

  const userSegmentData = [
    { label: 'High Usage (>50K tokens)', value: segments?.high_usage_count || 0 },
    { label: 'Medium Usage (10K-50K)', value: segments?.medium_usage_count || 0 },
    { label: 'Low Usage (<10K)', value: segments?.low_usage_count || 0 },
    { label: 'Inactive', value: segments?.inactive_count || 0 },
  ]

  const totalUsers = userSegmentData.reduce((sum, d) => sum + d.value, 0)

  return (
    <div className="reports-page">
      <div className="reports-header">
        <h1>Reports & Analytics</h1>
        <p className="subtitle">Detailed insights into user segments and behavior patterns</p>
      </div>

      {/* User Segments */}
      <section className="reports-section">
        <div className="section-container">
          <div className="section-content">
            <h2 className="section-title">User Segments by Token Usage</h2>

            {segmentsLoading ? (
              <div className="chart-loading">
                <LoadingSpinner />
              </div>
            ) : (
              <div className="chart-wrapper">
                <SimplePieChart data={userSegmentData} size={240} />
              </div>
            )}
          </div>

          <div className="section-legend">
            {userSegmentData.map((segment, i) => (
              <div key={i} className="legend-item">
                <span className="legend-color" style={{ backgroundColor: ['#3b82f6', '#8b5cf6', '#10b981', '#f59e0b'][i] }}></span>
                <div className="legend-content">
                  <p className="legend-label">{segment.label}</p>
                  <p className="legend-value">
                    {segment.value} users ({formatPercent((segment.value / totalUsers) * 100)})
                  </p>
                </div>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Usage Statistics */}
      <section className="reports-section">
        <h2 className="section-title">Token Usage Statistics</h2>
        
        <div className="stats-grid">
          {segmentsLoading ? (
            <>
              <SkeletonCard />
              <SkeletonCard />
              <SkeletonCard />
              <SkeletonCard />
            </>
          ) : (
            <>
              <StatCard
                title="High Usage Users"
                value={formatNumber(segments?.high_usage_count || 0)}
                subtitle="Very active with bot"
                icon="🔥"
              />
              
              <StatCard
                title="Medium Usage Users"
                value={formatNumber(segments?.medium_usage_count || 0)}
                subtitle="Moderately engaged"
                icon="📈"
              />
              
              <StatCard
                title="Low Usage Users"
                value={formatNumber(segments?.low_usage_count || 0)}
                subtitle="Minimal interactions"
                icon="📉"
              />
              
              <StatCard
                title="Inactive Users"
                value={formatNumber(segments?.inactive_count || 0)}
                subtitle="No recent activity"
                icon="💤"
              />
            </>
          )}
        </div>
      </section>

      {/* Detailed Metrics */}
      <section className="reports-section">
        <h2 className="section-title">Feature Adoption by Token Type</h2>
        
        {segmentsLoading ? (
          <div className="metrics-loading">
            <LoadingSpinner />
          </div>
        ) : (
          <div className="metrics-table">
            <div className="metric-row metric-header">
              <span>Feature</span>
              <span>Tokens Used</span>
              <span>% of Total</span>
            </div>
            
            {segments?.feature_breakdown ? (
              Object.entries(segments.feature_breakdown).map(([feature, data], i) => (
                <div key={i} className="metric-row">
                  <span className="metric-feature">{feature}</span>
                  <span className="metric-value">{formatNumber(data.tokens)}</span>
                  <span className="metric-percent">{formatPercent(data.percentage)}</span>
                </div>
              ))
            ) : (
              <div className="metric-empty">No feature data available</div>
            )}
          </div>
        )}
      </section>

      {/* Export Section */}
      <section className="reports-section">
        <h2 className="section-title">Generate Reports</h2>
        
        <div className="export-buttons">
          <button className="btn-primary">📊 Export User Segments (CSV)</button>
          <button className="btn-secondary">📈 Export Token Trends (CSV)</button>
          <button className="btn-secondary">📋 Export Full Analytics (PDF)</button>
        </div>
      </section>
    </div>
  )
}
