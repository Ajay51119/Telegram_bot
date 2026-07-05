import React, { useState, useEffect } from 'react'
import { useDashboardStats, useTokenTrends } from '../../hooks/useApi'
import { LoadingSpinner, SkeletonCard, StatCard, EmptyState, Alert } from '../common/Common'
import { formatNumber, formatPercent, calculatePercentChange } from '../../utils/formatters'
import './dashboard.css'

/**
 * Simple line chart for trends
 */
function SimpleLineChart({ data, height = 200 }) {
  if (!data || data.length === 0) {
    return <div style={{ height, textAlign: 'center', color: 'var(--color-gray-400)' }}>No data</div>
  }

  const values = data.map((d) => d.value)
  const maxValue = Math.max(...values)
  const minValue = Math.min(...values)
  const range = maxValue - minValue || 1

  const points = values.map((val, idx) => {
    const x = (idx / (values.length - 1 || 1)) * 100
    const y = 100 - ((val - minValue) / range) * 100
    return `${x},${y}`
  })

  return (
    <svg viewBox="0 0 100 100" preserveAspectRatio="none" style={{ height, width: '100%' }}>
      <polyline points={points.join(' ')} fill="none" stroke="var(--color-primary)" strokeWidth="1" />
      <polyline points={points.join(' ')} fill="url(#gradient)" fillOpacity="0.1" />
      <defs>
        <linearGradient id="gradient" x1="0%" y1="0%" x2="0%" y2="100%">
          <stop offset="0%" stopColor="var(--color-primary)" />
          <stop offset="100%" stopColor="var(--color-primary)" stopOpacity="0" />
        </linearGradient>
      </defs>
    </svg>
  )
}

/**
 * Dashboard Overview Page
 */
export default function DashboardPage() {
  const { data: stats, loading: statsLoading, error: statsError } = useDashboardStats()
  const { data: trends, loading: trendsLoading } = useTokenTrends(30)
  const [selectedMetric, setSelectedMetric] = useState('tokens')

  if (statsError) {
    return (
      <div className="dashboard-page">
        <Alert type="error" message={statsError} />
      </div>
    )
  }

  const isLoading = statsLoading

  return (
    <div className="dashboard-page">
      <div className="dashboard-header">
        <h1>Dashboard</h1>
        <p className="subtitle">Real-time overview of your bot users and token consumption</p>
      </div>

      {/* Key Metrics Grid */}
      <section className="dashboard-section">
        <h2 className="section-title">Key Metrics</h2>
        
        <div className="stats-grid">
          {isLoading ? (
            <>
              <SkeletonCard />
              <SkeletonCard />
              <SkeletonCard />
              <SkeletonCard />
            </>
          ) : (
            <>
              <StatCard
                title="Total Users"
                value={formatNumber(stats?.total_users || 0)}
                subtitle={`${stats?.new_users_this_month || 0} new this month`}
                trend={stats?.user_growth_trend || 0}
                icon="👥"
              />
              
              <StatCard
                title="Active Today"
                value={formatNumber(stats?.active_users_today || 0)}
                subtitle={`${formatPercent((stats?.active_users_today || 0) / (stats?.total_users || 1) * 100)} of total`}
                icon="🟢"
              />
              
              <StatCard
                title="Total Tokens Used"
                value={formatNumber(stats?.total_tokens_used || 0)}
                subtitle="Cumulative consumption"
                icon="⚡"
              />
              
              <StatCard
                title="Avg Tokens/User"
                value={formatNumber(stats?.avg_tokens_per_user || 0)}
                subtitle={`${stats?.total_users || 0} users analyzed`}
                icon="📊"
              />
            </>
          )}
        </div>
      </section>

      {/* Token Trends Chart */}
      <section className="dashboard-section">
        <div className="chart-header">
          <h2 className="section-title">Token Usage Trend (Last 30 Days)</h2>
          <div className="chart-controls">
            <button
              className={`btn-ghost btn-sm ${selectedMetric === 'tokens' ? 'active' : ''}`}
              onClick={() => setSelectedMetric('tokens')}
            >
              Total Tokens
            </button>
            <button
              className={`btn-ghost btn-sm ${selectedMetric === 'users' ? 'active' : ''}`}
              onClick={() => setSelectedMetric('users')}
            >
              Active Users
            </button>
          </div>
        </div>
        
        <div className="chart-container">
          {trendsLoading ? (
            <div style={{ display: 'flex', justifyContent: 'center', padding: '40px' }}>
              <LoadingSpinner />
            </div>
          ) : trends && trends.length > 0 ? (
            <SimpleLineChart data={trends} height={300} />
          ) : (
            <EmptyState title="No data yet" description="Token usage data will appear here" />
          )}
        </div>
      </section>

      {/* Additional Stats */}
      <section className="dashboard-section">
        <h2 className="section-title">User Engagement</h2>
        
        <div className="stats-row">
          {isLoading ? (
            <>
              <SkeletonCard lines={2} />
              <SkeletonCard lines={2} />
              <SkeletonCard lines={2} />
            </>
          ) : (
            <>
              <div className="stat-box">
                <p className="stat-label">Onboarding Completion</p>
                <div className="progress-bar">
                  <div
                    className="progress-fill"
                    style={{
                      width: `${((stats?.onboarding_completion_rate || 0) * 100).toFixed(1)}%`,
                    }}
                  ></div>
                </div>
                <p className="stat-percentage">
                  {formatPercent((stats?.onboarding_completion_rate || 0) * 100)}
                </p>
              </div>
              
              <div className="stat-box">
                <p className="stat-label">Active Users This Month</p>
                <p className="stat-big-number">{formatNumber(stats?.active_users_this_month || 0)}</p>
                <p className="stat-detail">
                  {((stats?.active_users_this_month || 0) / (stats?.total_users || 1) * 100).toFixed(1)}% of total
                </p>
              </div>
              
              <div className="stat-box">
                <p className="stat-label">Avg Interactions/User</p>
                <p className="stat-big-number">
                  {(((stats?.total_tokens_used || 0) / (stats?.avg_tokens_per_user || 1)) / 1000).toFixed(1)}K
                </p>
                <p className="stat-detail">Cumulative API calls</p>
              </div>
            </>
          )}
        </div>
      </section>

      {/* Top Users */}
      {!isLoading && stats?.most_active_users && stats.most_active_users.length > 0 && (
        <section className="dashboard-section">
          <h2 className="section-title">Top Active Users</h2>
          
          <div className="top-users-list">
            {stats.most_active_users.slice(0, 5).map((user, idx) => (
              <div key={idx} className="top-user-item">
                <span className="user-rank">#{idx + 1}</span>
                <div className="user-info">
                  <p className="user-name">{user.name}</p>
                  <p className="user-meta">{formatNumber(user.tokens_used)} tokens</p>
                </div>
                <p className="user-interactions">{user.interactions} interactions</p>
              </div>
            ))}
          </div>
        </section>
      )}
    </div>
  )
}
