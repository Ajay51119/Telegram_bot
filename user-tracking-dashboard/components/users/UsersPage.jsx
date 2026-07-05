import React, { useEffect, useState } from 'react'
import { useUsers, useSearchUsers } from '../../hooks/useApi'
import { usersApi } from '../../services/api'
import {
  LoadingSpinner,
  SkeletonRow,
  Badge,
  Pagination,
  EmptyState,
  Alert,
  Modal,
} from '../common/Common'
import {
  formatNumber,
  formatDate,
  formatRelativeTime,
  maskPhone,
  truncate,
  downloadCSV,
} from '../../utils/formatters'
import './users.css'

function UserFilters({ filters, onFilterChange }) {
  return (
    <div className="filters-panel">
      <div className="filter-group">
        <label htmlFor="status-filter" className="filter-label">
          Status
        </label>
        <select
          id="status-filter"
          className="filter-select"
          value={filters.status || ''}
          onChange={(e) =>
            onFilterChange({
              ...filters,
              status: e.target.value || undefined,
            })
          }
        >
          <option value="">All Statuses</option>
          <option value="active">Active</option>
          <option value="limit_reached">Limit Reached</option>
        </select>
      </div>

      <div className="filter-group">
        <label htmlFor="onboarding-filter" className="filter-label">
          Onboarding
        </label>
        <select
          id="onboarding-filter"
          className="filter-select"
          value={filters.onboarding_stage || ''}
          onChange={(e) =>
            onFilterChange({
              ...filters,
              onboarding_stage: e.target.value || undefined,
            })
          }
        >
          <option value="">All Stages</option>
          <option value="onboarding_complete">Complete</option>
          <option value="awaiting_name">Awaiting Name</option>
          <option value="awaiting_email">Awaiting Email</option>
          <option value="new">New</option>
        </select>
      </div>

      <div className="filter-group">
        <label htmlFor="tokens-filter" className="filter-label">
          Min Tokens
        </label>
        <input
          id="tokens-filter"
          type="number"
          className="filter-input"
          placeholder="0"
          value={filters.min_tokens || ''}
          onChange={(e) =>
            onFilterChange({
              ...filters,
              min_tokens: e.target.value ? parseInt(e.target.value) : undefined,
            })
          }
        />
      </div>

      <button className="btn-ghost btn-sm" onClick={() => onFilterChange({})}>
        Clear Filters
      </button>
    </div>
  )
}

function UserDetailsModal({ user, isOpen, onClose, onSaveLimit, onDeleteUser }) {
  const [draftLimit, setDraftLimit] = useState(100)
  const [draftName, setDraftName] = useState('')
  const [draftEmail, setDraftEmail] = useState('')
  const [draftPhone, setDraftPhone] = useState('')
  const [draftDesignation, setDraftDesignation] = useState('')
  const [draftProfile, setDraftProfile] = useState('')
  const [saving, setSaving] = useState(false)
  const [deleting, setDeleting] = useState(false)
  const [message, setMessage] = useState('')

  useEffect(() => {
    if (user) {
      setDraftLimit(user.token_limit || 100)
      setDraftName(user.name || user.username || '')
      setDraftEmail(user.email || '')
      setDraftPhone(user.phone || '')
      setDraftDesignation(user.designation || '')
      setDraftProfile(user.profile || '')
      setMessage('')
    }
  }, [user])

  if (!user) return null

  const handleSave = async () => {
    setSaving(true)
    setMessage('')
    try {
      await onSaveLimit(user.telegram_id, {
        token_limit: Number(draftLimit),
        username: draftName,
        email: draftEmail,
        phone: draftPhone,
        designation: draftDesignation,
        profile: draftProfile,
      })
      setMessage('User updated successfully')
    } catch (error) {
      setMessage(error.response?.data?.message || 'Unable to update user')
    } finally {
      setSaving(false)
    }
  }

  const handleDelete = async () => {
    if (!window.confirm('Delete this user and all stored details?')) return
    setDeleting(true)
    setMessage('')
    try {
      await onDeleteUser(user.telegram_id)
      setMessage('User deleted successfully')
      onClose()
    } catch (error) {
      setMessage(error.response?.data?.message || 'Unable to delete user')
    } finally {
      setDeleting(false)
    }
  }

  return (
    <Modal
      isOpen={isOpen}
      onClose={onClose}
      title={user.name || user.username || user.telegram_id}
      size="md"
      footer={
        <div className="modal-actions">
          <button className="btn-secondary btn-sm" onClick={onClose}>
            Close
          </button>
          {user.resume_text && (
            <button className="btn-primary btn-sm" onClick={() => window.alert(user.resume_text)}>
              View Resume
            </button>
          )}
        </div>
      }
    >
      <div className="user-details-content">
        {message && <Alert type={message.includes('success') ? 'success' : 'error'} message={message} />}

        <div className="detail-section">
          <h3>Contact Information</h3>
          <div className="detail-row">
            <span className="detail-label">Name:</span>
            <input
              type="text"
              className="filter-input"
              value={draftName}
              onChange={(e) => setDraftName(e.target.value)}
            />
          </div>
          <div className="detail-row">
            <span className="detail-label">Email:</span>
            <input
              type="email"
              className="filter-input"
              value={draftEmail}
              onChange={(e) => setDraftEmail(e.target.value)}
            />
          </div>
          <div className="detail-row">
            <span className="detail-label">Phone:</span>
            <input
              type="text"
              className="filter-input"
              value={draftPhone}
              onChange={(e) => setDraftPhone(e.target.value)}
            />
          </div>
        </div>

        <div className="detail-section">
          <h3>Profile & Resume</h3>
          <div className="detail-row">
            <span className="detail-label">Designation:</span>
            <input
              type="text"
              className="filter-input"
              value={draftDesignation}
              onChange={(e) => setDraftDesignation(e.target.value)}
            />
          </div>
          <div className="detail-row">
            <span className="detail-label">Profile:</span>
            <input
              type="text"
              className="filter-input"
              value={draftProfile}
              onChange={(e) => setDraftProfile(e.target.value)}
            />
          </div>
          <div className="detail-row">
            <span className="detail-label">Skills:</span>
            <div className="skills-tags">
              {user.skills && user.skills.length > 0 ? (
                user.skills.map((skill, i) => (
                  <span key={i} className="skill-tag">
                    {skill}
                  </span>
                ))
              ) : (
                <span className="text-gray-500">No skills listed</span>
              )}
            </div>
          </div>
          <div className="detail-row">
            <span className="detail-label">Resume:</span>
            <span className="detail-value">{user.resume_text ? 'Stored in database' : 'No resume yet'}</span>
          </div>
        </div>

        <div className="detail-section">
          <h3>Token Usage</h3>
          <div className="detail-row">
            <span className="detail-label">Token Limit:</span>
            <span className="detail-value">{formatNumber(user.token_limit || 0)}</span>
          </div>
          <div className="detail-row">
            <span className="detail-label">Tokens Used:</span>
            <span className="detail-value">{formatNumber(user.tokens_used || 0)}</span>
          </div>
          <div className="detail-row">
            <span className="detail-label">Interactions:</span>
            <span className="detail-value">{formatNumber(user.total_interactions || 0)}</span>
          </div>
        </div>

        <div className="detail-section">
          <h3>Edit Token Limit</h3>
          <div className="detail-row">
            <input
              type="number"
              className="filter-input"
              value={draftLimit}
              min="1"
              onChange={(e) => setDraftLimit(e.target.value)}
            />
            <button className="btn-primary btn-sm" onClick={handleSave} disabled={saving}>
              {saving ? 'Saving…' : 'Save'}
            </button>
          </div>
          <p className="subtitle">When the limit is hit, the bot will ask the user to recharge their wallet.</p>
        </div>

        <div className="detail-section">
          <h3>Danger Zone</h3>
          <button className="btn-danger btn-sm" onClick={handleDelete} disabled={deleting}>
            {deleting ? 'Deleting…' : 'Delete User'}
          </button>
        </div>

        <div className="detail-section">
          <h3>Account Activity</h3>
          <div className="detail-row">
            <span className="detail-label">Created:</span>
            <span className="detail-value">{formatDate(user.created_at)}</span>
          </div>
          <div className="detail-row">
            <span className="detail-label">Last Active:</span>
            <span className="detail-value">{formatRelativeTime(user.updated_at || user.last_active)}</span>
          </div>
          <div className="detail-row">
            <span className="detail-label">Status:</span>
            <span>
              <Badge status={user.status} />
            </span>
          </div>
          <div className="detail-row">
            <span className="detail-label">Onboarding:</span>
            <span>
              <Badge status={user.onboarding_stage} />
            </span>
          </div>
        </div>
      </div>
    </Modal>
  )
}

function UserSearch({ onSearch }) {
  const [query, setQuery] = useState('')
  const { results } = useSearchUsers(query)

  const handleSearch = (value) => {
    setQuery(value)
    onSearch(value)
  }

  return (
    <div className="search-wrapper">
      <input
        type="text"
        className="search-input"
        placeholder="Search by name or email..."
        value={query}
        onChange={(e) => handleSearch(e.target.value)}
      />
      <span className="search-icon">🔍</span>
    </div>
  )
}

export default function UsersPage() {
  const [page, setPage] = useState(1)
  const [limit] = useState(20)
  const [filters, setFilters] = useState({})
  const [sortBy, setSortBy] = useState('updated_at')
  const [sortOrder, setSortOrder] = useState('desc')
  const [selectedUser, setSelectedUser] = useState(null)
  const [isDetailModalOpen, setIsDetailModalOpen] = useState(false)
  const [searchQuery, setSearchQuery] = useState('')
  const [refreshKey, setRefreshKey] = useState(0)
  const [bulkLimit, setBulkLimit] = useState('100')
  const [bulkSaving, setBulkSaving] = useState(false)
  const [bulkMessage, setBulkMessage] = useState('')

  const { data: usersData, loading: usersLoading, error: usersError } = useUsers(
    page,
    limit,
    {
      ...filters,
      sort_by: sortBy,
      order: sortOrder,
      search: searchQuery,
    },
    refreshKey
  )

  const users = usersData?.users || []
  const totalPages = usersData?.total_pages || 1
  const totalUsers = usersData?.total || 0

  const handleSort = (column) => {
    if (sortBy === column) {
      setSortOrder(sortOrder === 'asc' ? 'desc' : 'asc')
    } else {
      setSortBy(column)
      setSortOrder('desc')
    }
    setPage(1)
  }

  const handleExport = () => {
    const headers = ['Name', 'Email', 'Designation', 'Token Limit', 'Tokens Used', 'Interactions', 'Status']
    const rows = users.map((u) => [
      u.name || u.username || u.telegram_id,
      u.email || '—',
      u.designation || 'N/A',
      u.token_limit || 0,
      u.tokens_used || 0,
      u.total_interactions || 0,
      u.status || 'active',
    ])

    const csv =
      [headers, ...rows].map((row) => row.map((cell) => `"${cell}"`).join(',')).join('\n') + '\n'
    downloadCSV(csv, `users-export-${new Date().toISOString().split('T')[0]}.csv`)
  }

  const handleViewDetails = (user) => {
    setSelectedUser(user)
    setIsDetailModalOpen(true)
  }

  const handleSaveUserLimit = async (telegramId, limit) => {
    await usersApi.updateUser(telegramId, { token_limit: limit })
    setRefreshKey((prev) => prev + 1)
  }

  const handleBulkLimitSave = async () => {
    setBulkSaving(true)
    setBulkMessage('')
    try {
      await usersApi.setGlobalTokenLimit(Number(bulkLimit))
      setRefreshKey((prev) => prev + 1)
      setBulkMessage('Token limit applied to all users')
    } catch (error) {
      setBulkMessage(error.response?.data?.message || 'Unable to update token limits')
    } finally {
      setBulkSaving(false)
    }
  }

  return (
    <div className="users-page">
      <div className="users-header">
        <div>
          <h1>All Telegram Users</h1>
          <p className="subtitle">
            {totalUsers > 0 ? `${totalUsers} total users • Showing ${users.length} per page` : 'No users yet'}
          </p>
        </div>
        <div style={{ display: 'flex', gap: '10px', flexWrap: 'wrap', alignItems: 'center' }}>
          <input
            type="number"
            className="filter-input"
            value={bulkLimit}
            min="1"
            onChange={(e) => setBulkLimit(e.target.value)}
            style={{ minWidth: '120px' }}
          />
          <button className="btn-primary btn-sm" onClick={handleBulkLimitSave} disabled={bulkSaving}>
            {bulkSaving ? 'Saving…' : 'Set All Limits'}
          </button>
          <button className="btn-primary" onClick={handleExport} disabled={users.length === 0}>
            📥 Export CSV
          </button>
        </div>
      </div>

      {bulkMessage && <Alert type={bulkMessage.includes('applied') ? 'success' : 'error'} message={bulkMessage} />}
      {usersError && <Alert type="error" message={usersError} />}

      <div className="users-controls">
        <UserSearch onSearch={setSearchQuery} />
        <UserFilters
          filters={filters}
          onFilterChange={(f) => {
            setFilters(f)
            setPage(1)
          }}
        />
      </div>

      {usersLoading && users.length === 0 ? (
        <div className="table-loading">
          <LoadingSpinner />
        </div>
      ) : users.length === 0 ? (
        <EmptyState icon="👥" title="No users found" description="Try adjusting your filters or search query" />
      ) : (
        <>
          <div className="table-container">
            <table className="users-table">
              <thead>
                <tr>
                  <th onClick={() => handleSort('name')} className="sortable">
                    Name {sortBy === 'name' && <span>{sortOrder === 'asc' ? '↑' : '↓'}</span>}
                  </th>
                  <th onClick={() => handleSort('email')} className="sortable">
                    Email {sortBy === 'email' && <span>{sortOrder === 'asc' ? '↑' : '↓'}</span>}
                  </th>
                  <th>Designation</th>
                  <th onClick={() => handleSort('tokens_used')} className="sortable text-right">
                    Tokens {sortBy === 'tokens_used' && <span>{sortOrder === 'asc' ? '↑' : '↓'}</span>}
                  </th>
                  <th onClick={() => handleSort('total_interactions')} className="sortable text-right">
                    Interactions {sortBy === 'total_interactions' && <span>{sortOrder === 'asc' ? '↑' : '↓'}</span>}
                  </th>
                  <th>Status</th>
                  <th onClick={() => handleSort('updated_at')} className="sortable">
                    Last Active {sortBy === 'updated_at' && <span>{sortOrder === 'asc' ? '↑' : '↓'}</span>}
                  </th>
                  <th>Actions</th>
                </tr>
              </thead>
              <tbody>
                {usersLoading && <SkeletonRow columns={8} />}
                {users.map((user) => (
                  <tr key={user.user_id || user.telegram_id}>
                    <td className="cell-name">
                      <div className="user-cell">
                        <div className="user-avatar">{(user.name || user.username || user.telegram_id || 'U').charAt(0).toUpperCase()}</div>
                        <span>{truncate(user.name || user.username || user.telegram_id, 30)}</span>
                      </div>
                    </td>
                    <td className="cell-email">
                      <a href={`mailto:${user.email}`}>{truncate(user.email || '—', 25)}</a>
                    </td>
                    <td>{user.designation || '—'}</td>
                    <td className="cell-number">{formatNumber(user.tokens_used || 0)}</td>
                    <td className="cell-number">{formatNumber(user.total_interactions || 0)}</td>
                    <td>
                      <Badge status={user.status} />
                    </td>
                    <td className="cell-time">{formatRelativeTime(user.updated_at || user.last_active)}</td>
                    <td className="cell-actions">
                      <button className="btn-ghost btn-sm" onClick={() => handleViewDetails(user)} title="View details">
                        👁️
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>

          {totalPages > 1 && <Pagination page={page} totalPages={totalPages} onPageChange={setPage} />}
        </>
      )}

      <UserDetailsModal
        user={selectedUser}
        isOpen={isDetailModalOpen}
        onClose={() => setIsDetailModalOpen(false)}
        onSaveLimit={handleSaveUserLimit}
        onDeleteUser={async (telegramId) => {
          await usersApi.deleteUser(telegramId)
          setRefreshKey((prev) => prev + 1)
        }}
      />
    </div>
  )
}
