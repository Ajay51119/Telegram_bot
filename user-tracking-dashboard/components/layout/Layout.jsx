import React, { useState } from 'react'
import './layout.css'

/**
 * Header component
 */
export function Header({ title = 'Dashboard', lastSync = null, onLogout = null }) {
  return (
    <header className="header">
      <div className="header-content">
        <div className="header-left">
          <h1 className="header-title">{title}</h1>
        </div>
        
        <div className="header-right">
          {lastSync && (
            <div className="sync-info">
              <span className="sync-dot"></span>
              <span className="sync-text">Last sync: {lastSync}</span>
            </div>
          )}
          
          <div className="header-user">
            <div className="user-avatar">A</div>
            {onLogout && (
              <button className="btn-ghost btn-sm" onClick={onLogout} title="Logout">
                ⊢
              </button>
            )}
          </div>
        </div>
      </div>
    </header>
  )
}

/**
 * Sidebar navigation component
 */
export function Sidebar({ activeTab = 'dashboard', onTabChange = null }) {
  const [isOpen, setIsOpen] = useState(false)
  
  const tabs = [
    {
      id: 'dashboard',
      label: 'Dashboard',
      icon: '📊',
    },
    {
      id: 'users',
      label: 'All Users',
      icon: '👥',
    },
    {
      id: 'reports',
      label: 'Reports',
      icon: '📈',
    },
    {
      id: 'settings',
      label: 'Settings',
      icon: '⚙️',
    },
  ]
  
  const handleTabClick = (id) => {
    onTabChange?.(id)
    setIsOpen(false)
  }
  
  return (
    <>
      <button className="sidebar-toggle" onClick={() => setIsOpen(!isOpen)}>
        ☰
      </button>
      
      <aside className={`sidebar ${isOpen ? 'open' : ''}`}>
        <div className="sidebar-header">
          <h2 className="sidebar-logo">📱 Bot Analytics</h2>
        </div>
        
        <nav className="sidebar-nav">
          {tabs.map((tab) => (
            <button
              key={tab.id}
              className={`nav-item ${activeTab === tab.id ? 'active' : ''}`}
              onClick={() => handleTabClick(tab.id)}
            >
              <span className="nav-icon">{tab.icon}</span>
              <span className="nav-label">{tab.label}</span>
            </button>
          ))}
        </nav>
        
        <div className="sidebar-footer">
          <p className="sidebar-version">v1.0.0</p>
        </div>
      </aside>
      
      {isOpen && (
        <div className="sidebar-overlay" onClick={() => setIsOpen(false)}></div>
      )}
    </>
  )
}

/**
 * Layout wrapper component
 */
export function Layout({ header, sidebar, children }) {
  return (
    <div className="layout">
      {header && <div className="layout-header">{header}</div>}
      
      <div className="layout-container">
        {sidebar && <div className="layout-sidebar">{sidebar}</div>}
        <main className="layout-main">
          <div className="layout-content">{children}</div>
        </main>
      </div>
    </div>
  )
}
