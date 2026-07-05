# Project File Structure & Organization

## Complete Directory Tree

```
user-tracking-dashboard/
│
├── 📄 index.html                 # HTML entry point
├── 📄 package.json               # NPM dependencies
├── 📄 vite.config.js             # Vite configuration
├── 📄 .env.example               # Environment variables template
│
├── 📁 src/
│   │
│   ├── 📄 main.jsx               # React entry point
│   ├── 📄 App.jsx                # Main app component
│   ├── 📄 App.css                # App-level styles
│   ├── 📄 index.css              # Global styles & CSS variables
│   │
│   ├── 📁 components/            # React components
│   │   │
│   │   ├── 📁 common/            # Reusable UI components
│   │   │   ├── 📄 Common.jsx      # Common components (Badge, Modal, etc)
│   │   │   └── 📄 components.css  # Common component styles
│   │   │
│   │   ├── 📁 layout/            # Page layout components
│   │   │   ├── 📄 Layout.jsx      # Header, Sidebar, Layout
│   │   │   └── 📄 layout.css      # Layout styles
│   │   │
│   │   ├── 📁 dashboard/         # Dashboard page
│   │   │   ├── 📄 DashboardPage.jsx  # Dashboard component
│   │   │   └── 📄 dashboard.css      # Dashboard styles
│   │   │
│   │   ├── 📁 users/             # Users page
│   │   │   ├── 📄 UsersPage.jsx      # Users table component
│   │   │   └── 📄 users.css          # Users table styles
│   │   │
│   │   └── 📁 reports/           # Reports page
│   │       ├── 📄 ReportsPage.jsx    # Reports component
│   │       └── 📄 reports.css        # Reports styles
│   │
│   ├── 📁 hooks/                 # Custom React hooks
│   │   └── 📄 useApi.js          # Data fetching hooks
│   │
│   ├── 📁 services/              # API & business logic
│   │   └── 📄 api.js             # Axios API client
│   │
│   └── 📁 utils/                 # Utility functions
│       └── 📄 formatters.js      # Number, date, string formatters
│
├── 📁 public/                    # Static assets (if needed)
│   └── (icon files, etc)
│
└── 📄 dist/                      # Build output (generated)
    └── (compiled files)
```

## File Descriptions

### Root Level Files

| File | Purpose |
|------|---------|
| `index.html` | HTML skeleton, entry point |
| `package.json` | Dependencies, scripts, metadata |
| `vite.config.js` | Vite build configuration |
| `.env.example` | Environment variables template |
| `README.md` | Project overview and guide |
| `SETUP.md` | Detailed setup and development guide |

### Entry Points

| File | Purpose |
|------|---------|
| `src/main.jsx` | React app initialization, ReactDOM.render() |
| `src/App.jsx` | Root component, routing logic |
| `src/index.css` | Global styles, CSS variables |
| `src/App.css` | App-specific styles |

### Components

#### Common Components (`src/components/common/`)
| File | Exports |
|------|---------|
| `Common.jsx` | LoadingSpinner, Badge, StatCard, Modal, Pagination, Alert, EmptyState, Tooltip, SkeletonRow, SkeletonCard |
| `components.css` | Styles for all common components |

#### Layout Components (`src/components/layout/`)
| File | Exports |
|------|---------|
| `Layout.jsx` | Header, Sidebar, Layout wrapper |
| `layout.css` | Layout and navigation styles |

#### Dashboard Page (`src/components/dashboard/`)
| File | Purpose |
|------|---------|
| `DashboardPage.jsx` | Summary stats, charts, top users |
| `dashboard.css` | Dashboard-specific styling |

#### Users Page (`src/components/users/`)
| File | Purpose |
|------|---------|
| `UsersPage.jsx` | Users table, filtering, search, details modal |
| `users.css` | Table and user component styles |

#### Reports Page (`src/components/reports/`)
| File | Purpose |
|------|---------|
| `ReportsPage.jsx` | Analytics, user segments, reports |
| `reports.css` | Reports page styling |

### Hooks (`src/hooks/`)

| Hook | Purpose |
|------|---------|
| `useApi()` | Generic data fetching with loading/error |
| `useUsers()` | Fetch paginated users |
| `useUserDetails()` | Fetch single user |
| `useSearchUsers()` | Search with debouncing |
| `useDashboardStats()` | Fetch dashboard summary |
| `useTokenTrends()` | Fetch token trends |
| `useUserSegments()` | Fetch user segments |
| `useRefetch()` | Manual refetch trigger |

### Services (`src/services/`)

| Service | Endpoints |
|---------|-----------|
| `api.js` | usersApi (getUsers, getUser, searchUsers, exportUsers), statsApi (getDashboardStats, getTokenTrends, getUserSegments) |

### Utils (`src/utils/`)

| Function | Purpose |
|----------|---------|
| `formatNumber()` | 1234567 → "1.2M" |
| `formatTokens()` | Format with commas |
| `formatDate()` | Date to readable format |
| `formatDateTime()` | Date and time format |
| `formatRelativeTime()` | "2 hours ago" format |
| `getStatusColor()` | Get color for badge |
| `getInitials()` | Get user initials |
| `truncate()` | Limit string length |
| `maskEmail()` | Hide email for privacy |
| `maskPhone()` | Hide phone number |
| `downloadCSV()` | Trigger CSV download |
| `calculatePercentChange()` | Calculate % change |
| `formatPercent()` | "87.5%" format |
| `getTrendColor()` | Color for trend indicator |

## Component Hierarchy

```
App
├── Layout
│   ├── Header
│   │   ├── Logo
│   │   ├── Title
│   │   ├── Sync Info
│   │   └── User Avatar
│   ├── Sidebar
│   │   ├── Logo
│   │   ├── Nav Items (Dashboard, Users, Reports, Settings)
│   │   └── Version
│   └── Main Content
│       ├── DashboardPage
│       │   ├── Stat Cards (4x)
│       │   ├── Chart Section
│       │   ├── Engagement Stats (3x)
│       │   └── Top Users List
│       ├── UsersPage
│       │   ├── Header
│       │   ├── Search Bar
│       │   ├── Filters Panel
│       │   ├── Users Table
│       │   ├── Pagination
│       │   └── User Details Modal
│       ├── ReportsPage
│       │   ├── User Segments Chart
│       │   ├── Segment Stats Cards
│       │   ├── Feature Adoption Table
│       │   └── Export Buttons
│       └── SettingsPage
│           ├── General Settings
│           └── Account & Security
```

## Component Sizes & Props

### StatCard
```jsx
<StatCard
  title="Total Users"
  value="1.2K"
  subtitle="42 new this month"
  trend={12.5}
  icon="👥"
/>
```

### Badge
```jsx
<Badge status="active" />        // Green
<Badge status="inactive" />      // Yellow
<Badge status="churned" />       // Red
<Badge status="completed" />     // Green
```

### Modal
```jsx
<Modal
  isOpen={true}
  onClose={() => {}}
  title="User Details"
  size="md"  // sm, md, lg
  footer={<button>Close</button>}
>
  Content here
</Modal>
```

## CSS Variable Reference

### Colors
```css
--color-primary: #3b82f6           /* Blue */
--color-secondary: #8b5cf6         /* Purple */
--color-success: #10b981           /* Green */
--color-warning: #f59e0b           /* Orange */
--color-danger: #ef4444            /* Red */
--color-gray-50 to --color-gray-900 /* 10 shades */
```

### Typography
```css
--font-display: Sora               /* Headings */
--font-body: Sora                  /* Body text */
--font-mono: JetBrains Mono        /* Numbers */

--text-xs: 12px
--text-sm: 14px
--text-base: 16px
--text-lg: 18px
--text-xl: 20px
--text-2xl: 24px
--text-3xl: 32px
```

### Spacing (8px base)
```css
--space-1: 4px
--space-2: 8px
--space-3: 12px
--space-4: 16px
--space-6: 24px
--space-8: 32px
--space-10: 40px
--space-12: 48px
```

### Shadows
```css
--shadow-sm: subtle
--shadow-md: medium
--shadow-lg: large
--shadow-xl: extra large
```

## Data Flow Diagram

```
User Action (Click, Type, etc)
         ↓
Component State Update
         ↓
Custom Hook Triggered
         ↓
API Service Called
         ↓
Axios Request (with auth)
         ↓
Backend API Response
         ↓
Data Parsed & Stored
         ↓
Component Re-render
         ↓
UI Updated with Formatters
```

## Import Paths

### Absolute Imports (using src/)
```javascript
import { useUsers } from '@/hooks/useApi'
import { formatNumber } from '@/utils/formatters'
import DashboardPage from '@/components/dashboard/DashboardPage'
```

### Relative Imports (from files)
```javascript
import { Badge, StatCard } from '../../components/common/Common'
import { usersApi } from '../../services/api'
```

## Build Output Structure

```
dist/
├── index.html           # Minified HTML
├── assets/
│   ├── index-xxx.js    # Main bundle
│   ├── vendor-xxx.js   # React, axios
│   └── style-xxx.css   # Minified CSS
└── .vite-manifest.json # Asset manifest
```

## Key Stats

| Metric | Value |
|--------|-------|
| Total Components | 15+ |
| Custom Hooks | 8 |
| CSS Files | 7 |
| API Endpoints | 6 |
| Utility Functions | 15+ |
| Lines of Code | ~2500 |
| Bundle Size (gzipped) | ~80KB |

## File Naming Conventions

- **Components:** PascalCase (e.g., `DashboardPage.jsx`)
- **Hooks:** camelCase with `use` prefix (e.g., `useUsers.js`)
- **Utils:** camelCase (e.g., `formatters.js`)
- **Styles:** kebab-case matching component (e.g., `dashboard.css`)
- **Constants:** UPPER_SNAKE_CASE (rarely used in this project)

## Development Workflow

1. **Add new feature**
   - Create component in `components/[name]/`
   - Add styles in matching `.css` file
   - Export from component file
   - Import and use in parent component

2. **Add new API endpoint**
   - Add method to `services/api.js`
   - Create hook in `hooks/useApi.js` if needed
   - Use hook in component

3. **Add utility function**
   - Add to `utils/formatters.js`
   - Export and use in components
   - Document with JSDoc comments

4. **Modify theme**
   - Edit CSS variables in `index.css`
   - All components automatically use new theme

---

This structure keeps the project organized, scalable, and easy to maintain.
