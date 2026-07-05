# User Tracking Dashboard - Setup & Development Guide

## 📋 Project Overview

A comprehensive React dashboard for tracking Telegram bot users, displaying real-time metrics including token usage, user activity, onboarding progress, and detailed analytics.

**Key Features:**
- ✅ Real-time user tracking dashboard
- ✅ Advanced filtering, sorting, and search
- ✅ Token consumption analytics per user
- ✅ User segmentation and reports
- ✅ Responsive design (mobile, tablet, desktop)
- ✅ CSV export functionality
- ✅ Skeleton loaders and error handling

---

## 🚀 Quick Start

### Prerequisites
- Node.js 16+ and npm/yarn
- Backend API running on `http://localhost:8000` (or configured URL)
- SQLite database with users table

### Installation

```bash
# 1. Install dependencies
npm install

# 2. Create .env file from example
cp .env.example .env

# 3. Update .env with your backend URL
# VITE_API_BASE_URL=http://localhost:8000/api

# 4. Start development server
npm run dev
```

The dashboard will be available at `http://localhost:5173`

---

## 📁 Project Structure

```
src/
├── components/
│   ├── common/
│   │   ├── Common.jsx          # Reusable UI components
│   │   └── components.css      # Component styles
│   ├── layout/
│   │   ├── Layout.jsx          # Header, Sidebar, Layout
│   │   └── layout.css
│   ├── dashboard/
│   │   ├── DashboardPage.jsx   # Dashboard overview
│   │   └── dashboard.css
│   ├── users/
│   │   ├── UsersPage.jsx       # Users table & filtering
│   │   └── users.css
│   └── reports/
│       ├── ReportsPage.jsx     # Analytics & reports
│       └── reports.css
├── hooks/
│   └── useApi.js               # Custom hooks for data fetching
├── services/
│   └── api.js                  # Centralized API calls
├── utils/
│   └── formatters.js           # Helper functions
├── App.jsx                     # Main app component
├── App.css
├── index.css                   # Global styles
├── main.jsx                    # Entry point
├── index.html
├── package.json
├── vite.config.js
└── .env.example
```

---

## 🔧 Configuration

### Environment Variables

Create a `.env` file in the root directory:

```env
# Backend API
VITE_API_BASE_URL=http://localhost:8000/api

# Auth
VITE_JWT_TOKEN_KEY=auth_token

# Logging
VITE_LOG_LEVEL=info

# Features
VITE_ENABLE_REPORTS=true
VITE_ENABLE_EXPORTS=true
VITE_ENABLE_ADMIN_SETTINGS=true
```

### API Configuration

The app uses axios with automatic JWT token injection. Tokens are stored in localStorage under the key `auth_token`.

**API Base URL Setup:**
```javascript
// Automatically uses VITE_API_BASE_URL from .env
// Falls back to http://localhost:8000/api
```

---

## 📡 Backend API Requirements

Your backend must provide these endpoints:

### 1. Get Users (Paginated)
```
GET /api/users?page=1&limit=20&sort_by=last_active&order=desc
```
**Response:**
```json
{
  "users": [
    {
      "user_id": "uuid",
      "telegram_id": 123456,
      "name": "John Doe",
      "email": "john@example.com",
      "phone": "+91XXXXXXXXXX",
      "designation": "Software Engineer",
      "skills": ["Python", "React"],
      "resume_filename": "resume.pdf",
      "onboarding_stage": "completed",
      "tokens_used": 45230,
      "tokens_used_this_month": 12450,
      "total_interactions": 156,
      "created_at": "2024-01-15T10:30:00Z",
      "updated_at": "2024-06-28T14:22:00Z",
      "last_active": "2024-06-28T09:45:00Z",
      "status": "active"
    }
  ],
  "total": 342,
  "page": 1,
  "limit": 20,
  "total_pages": 18
}
```

### 2. Get Dashboard Stats
```
GET /api/stats/dashboard
```
**Response:**
```json
{
  "total_users": 342,
  "active_users_today": 28,
  "active_users_this_month": 156,
  "total_tokens_used": 15234890,
  "avg_tokens_per_user": 44510,
  "new_users_this_month": 42,
  "onboarding_completion_rate": 0.87,
  "most_active_users": [
    { "name": "User1", "interactions": 320, "tokens_used": 95000 }
  ]
}
```

### 3. Get Token Trends
```
GET /api/stats/token-trends?days=30
```

### 4. Get User Segments
```
GET /api/stats/user-segments
```

### 5. Search Users
```
GET /api/users/search?q=john&field=name
```

### 6. Export Users
```
GET /api/users/export?format=csv
```

---

## 🎨 Design & Styling

### Design Tokens
All colors, spacing, and typography are defined as CSS variables in `index.css`:

```css
:root {
  --color-primary: #3b82f6
  --color-success: #10b981
  --color-warning: #f59e0b
  --color-danger: #ef4444
  
  --space-2: 8px
  --space-4: 16px
  --space-6: 24px
  /* ... etc */
}
```

### Responsive Breakpoints
- **Desktop:** 1024px+
- **Tablet:** 768px - 1023px
- **Mobile:** < 768px

All components are fully responsive with mobile-first design.

---

## 🪝 Custom Hooks

### useUsers(page, limit, filters)
Fetch paginated users with filtering
```javascript
const { data, loading, error } = useUsers(1, 20, { status: 'active' })
```

### useUserDetails(userId)
Fetch single user details
```javascript
const { data: user, loading, error } = useUserDetails('user-id-123')
```

### useDashboardStats()
Fetch dashboard summary stats
```javascript
const { data: stats, loading, error } = useDashboardStats()
```

### useSearchUsers(query, field)
Search users with debouncing
```javascript
const { results, loading, error } = useSearchUsers('john', 'name')
```

---

## 🛠️ Utility Functions

### Formatters
```javascript
formatNumber(1234567)           // → "1.2M"
formatTokens(45230)             // → "45,230"
formatDate('2024-01-15T...')   // → "Jan 15, 2024"
formatRelativeTime('...')       // → "2 hours ago"
formatPercent(0.875)            // → "87.5%"
maskPhone('+91XXXXXXXXXX')      // → "+91****XXXX"
truncate('long text', 30)       // → "long text..."
```

---

## 📊 Components

### Common Components
- `<LoadingSpinner />` - Animated loading indicator
- `<Badge status="active" />` - Status badges
- `<StatCard />` - Dashboard metrics
- `<Modal />` - Dialog/modal windows
- `<Pagination />` - Page navigation
- `<Alert />` - Error/warning messages
- `<EmptyState />` - No data placeholder

### Layout Components
- `<Header />` - Top navigation bar
- `<Sidebar />` - Left navigation panel
- `<Layout />` - Main page wrapper

---

## 🔐 Authentication

The app expects JWT tokens in localStorage. Add auth interceptors:

```javascript
// src/services/api.js handles this automatically
// Token is read from localStorage.getItem('auth_token')
// And injected in Authorization header: Bearer {token}

// On 401 response, user is redirected to login
```

To integrate with your auth system:
1. Store JWT token in `localStorage.setItem('auth_token', token)`
2. Tokens are automatically included in all API requests
3. Implement logout to clear token and redirect

---

## 📈 Performance Optimization

### Implemented:
- ✅ Lazy component loading
- ✅ Memoization with React.memo
- ✅ Debounced search (300ms)
- ✅ Pagination to avoid large DOM trees
- ✅ Skeleton loaders instead of spinners
- ✅ CSS variables for theme colors
- ✅ Optimized CSS with no redundancy

### Further Improvements:
- Implement React Query for advanced caching
- Add Service Worker for offline support
- Virtualize long tables with windowing
- Split code into dynamic imports by route

---

## 🧪 Testing & Debugging

### Development Tools:
```bash
# Start with hot reload
npm run dev

# Build for production
npm run build

# Preview production build
npm run preview
```

### Browser DevTools:
1. React DevTools browser extension
2. Network tab to inspect API calls
3. Console for error messages
4. LocalStorage to check auth token

### Mock API for Testing:
If backend isn't ready, create mock responses in `services/api.js`:

```javascript
export const usersApi = {
  getUsers: async () => ({
    data: {
      users: [...],
      total: 10,
      page: 1,
      total_pages: 1
    }
  })
}
```

---

## 🚢 Deployment

### Build
```bash
npm run build
# Creates optimized dist/ folder
```

### Deploy to Vercel (Recommended)
```bash
npm i -g vercel
vercel
# Follow prompts, set VITE_API_BASE_URL env var
```

### Deploy to Netlify
```bash
npm run build
# Upload dist/ folder to Netlify
# Set build command: npm run build
# Set publish directory: dist
```

### Deploy to AWS S3 + CloudFront
```bash
npm run build
aws s3 sync dist/ s3://your-bucket-name
# Configure CloudFront distribution
```

### Environment Variables in Production
Set these in your deployment platform:
- `VITE_API_BASE_URL` - Production API URL
- `VITE_LOG_LEVEL` - "error" for production

---

## 📝 Common Tasks

### Add New Page/Section
1. Create component in `components/[name]/[Name]Page.jsx`
2. Add styles in `components/[name]/[name].css`
3. Import in `App.jsx`
4. Add to sidebar navigation in `Layout.jsx`

### Modify Colors
Edit CSS variables in `index.css`:
```css
:root {
  --color-primary: #your-color;
  /* other changes */
}
```

### Add New API Endpoint
1. Add method to `services/api.js`
2. Create custom hook in `hooks/useApi.js`
3. Use hook in component with `useApi()`

### Change Pagination Size
```javascript
// In UsersPage.jsx
const [limit, setLimit] = useState(50) // Change from 20 to 50
```

---

## 🐛 Troubleshooting

### "Cannot find module" errors
```bash
npm install
```

### API 404 errors
- Check `VITE_API_BASE_URL` in .env
- Verify backend is running on correct port
- Check CORS configuration on backend

### Token/Auth errors
- Clear localStorage: `localStorage.clear()`
- Re-login to get new token
- Check token expiration

### Styling not applied
- Clear browser cache (Ctrl+Shift+R)
- Check CSS specificity in DevTools
- Verify CSS file is imported

### Performance issues
- Check Network tab for slow API responses
- Reduce number of table rows displayed
- Enable minification in build

---

## 📚 Resources

- **React Docs:** https://react.dev
- **Vite Docs:** https://vitejs.dev
- **Axios Docs:** https://axios-http.com
- **CSS Variables:** https://developer.mozilla.org/en-US/docs/Web/CSS/--*

---

## 📞 Support

For issues or questions:
1. Check the troubleshooting section above
2. Review API endpoint requirements
3. Check browser console for errors
4. Verify backend is responding correctly

---

## 📄 License

This project is part of the Bot Analytics system. All rights reserved.

---

## 🎯 Next Steps

1. **Install dependencies:** `npm install`
2. **Configure .env:** Copy `.env.example` to `.env` and update API URL
3. **Start dev server:** `npm run dev`
4. **Implement backend endpoints** (see API Requirements section)
5. **Test with real data** from your database
6. **Deploy** to production

Good luck! 🚀
