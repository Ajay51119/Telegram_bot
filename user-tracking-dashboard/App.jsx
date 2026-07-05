import React, { useState, useEffect } from 'react'
import { Header, Sidebar, Layout } from './components/layout/Layout'
import DashboardPage from './components/dashboard/DashboardPage'
import UsersPage from './components/users/UsersPage'
import ReportsPage from './components/reports/ReportsPage'
import './App.css'

/**
 * Settings/Admin Page (Placeholder)
 */
function SettingsPage() {
  return (
    <div className="settings-page">
      <h1>Settings</h1>
      <div className="settings-card">
        <h3>General Settings</h3>
        <div className="setting-item">
          <label>API Base URL</label>
          <input type="text" value={import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000/api'} readOnly />
        </div>
        <div className="setting-item">
          <label>Auto-refresh interval (seconds)</label>
          <input type="number" placeholder="300" defaultValue="300" />
        </div>
        <button className="btn-primary">Save Settings</button>
      </div>

      <div className="settings-card">
        <h3>Account & Security</h3>
        <button className="btn-danger">Change Password</button>
        <button className="btn-secondary" style={{ marginLeft: '10px' }}>Logout</button>
      </div>
    </div>
  )
}

/**
 * Main App Component
 */
export default function App() {
  const [activeTab, setActiveTab] = useState('dashboard')
  const [lastSync, setLastSync] = useState(new Date().toLocaleTimeString())

  // Update last sync time periodically
  useEffect(() => {
    const interval = setInterval(() => {
      setLastSync(new Date().toLocaleTimeString())
    }, 60000) // Update every minute

    return () => clearInterval(interval)
  }, [])

  // Render active page
  const renderPage = () => {
    switch (activeTab) {
      case 'dashboard':
        return <DashboardPage />
      case 'users':
        return <UsersPage />
      case 'reports':
        return <ReportsPage />
      case 'settings':
        return <SettingsPage />
      default:
        return <DashboardPage />
    }
  }

  return (
    <Layout
      header={
        <Header
          title={
            activeTab === 'dashboard'
              ? 'Dashboard'
              : activeTab === 'users'
              ? 'All Users'
              : activeTab === 'reports'
              ? 'Reports'
              : 'Settings'
          }
          lastSync={lastSync}
        />
      }
      sidebar={
        <Sidebar
          activeTab={activeTab}
          onTabChange={setActiveTab}
        />
      }
    >
      {renderPage()}
    </Layout>
  )
}
