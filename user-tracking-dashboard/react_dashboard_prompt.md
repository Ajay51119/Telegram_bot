# React User Tracking Dashboard - Detailed Implementation Prompt

## Project Overview
Build a comprehensive React dashboard for tracking all Telegram bot users. The dashboard should display user profiles, activity metrics, and token consumption per user in a clean, responsive interface.

---

## 1. Context & Prerequisites

### Existing Backend Architecture
- **Database**: SQLite with users table containing: user_id, telegram_id, name, email, phone, designation, skills, resume_filename, onboarding_stage, created_at, updated_at, last_active
- **API Framework**: FastAPI (or Flask/Django - specify your current backend)
- **Bot**: Telegram bot using LangGraph agents
- **LLM Integration**: Groq and OpenRouter via LangChain
- **Current Gap**: No token usage tracking per user (needs to be added to backend)

### Database Schema Extension (Must be added to backend first)
Before building the dashboard, ensure your backend includes:
```
users table additions:
- tokens_used (INTEGER, default 0) - cumulative tokens consumed per user
- tokens_used_this_month (INTEGER, default 0) - rolling monthly counter
- last_api_call (TIMESTAMP) - for activity tracking
- total_interactions (INTEGER, default 0) - number of LLM interactions
```

---

## 2. Backend API Endpoints Required

The dashboard needs these FastAPI endpoints (implement before React build):

### 2.1 Get All Users (Paginated)
```
GET /api/users?page=1&limit=20&sort_by=last_active&order=desc
Response:
{
  "users": [
    {
      "user_id": "uuid",
      "telegram_id": 123456,
      "name": "John Doe",
      "email": "john@example.com",
      "phone": "+91XXXXXXXXXX",
      "designation": "Software Engineer",
      "skills": ["Python", "React", "SQL"],
      "resume_filename": "resume.pdf",
      "onboarding_stage": "completed",
      "tokens_used": 45230,
      "tokens_used_this_month": 12450,
      "total_interactions": 156,
      "created_at": "2024-01-15T10:30:00Z",
      "updated_at": "2024-06-28T14:22:00Z",
      "last_active": "2024-06-28T09:45:00Z",
      "status": "active" | "inactive" | "churned"
    }
  ],
  "total": 342,
  "page": 1,
  "limit": 20,
  "total_pages": 18
}
```

### 2.2 Get Single User Details
```
GET /api/users/{user_id}
Response: Single user object with full details + token usage breakdown
```

### 2.3 Get Dashboard Summary Stats
```
GET /api/stats/dashboard
Response:
{
  "total_users": 342,
  "active_users_today": 28,
  "active_users_this_month": 156,
  "total_tokens_used": 15234890,
  "avg_tokens_per_user": 44510,
  "new_users_this_month": 42,
  "onboarding_completion_rate": 0.87,
  "most_active_users": [
    { "name": "User1", "interactions": 320, "tokens_used": 95000 },
    ...
  ],
  "token_usage_breakdown": {
    "query_generation": 0.35,
    "resume_optimization": 0.28,
    "cover_letter": 0.25,
    "other": 0.12
  }
}
```

### 2.4 Search Users
```
GET /api/users/search?q=john&field=name
Response: Array of matching users
```

### 2.5 Export Users Data
```
GET /api/users/export?format=csv
Response: CSV file download
```

---

## 3. React Dashboard Components & Features

### 3.1 Main Layout
- **Header**: Logo, title "User Tracking Dashboard", user logout button, last sync timestamp
- **Sidebar Navigation**: 
  - Dashboard (overview stats)
  - All Users (table view)
  - User Details (individual user modal/page)
  - Reports (token usage trends, user segments)
  - Settings (if admin)
- **Main Content Area**: Dynamic based on selected section

### 3.2 Dashboard Overview Section
Display summary cards showing:
- Total Users (with trend indicator)
- Active Users Today / This Month
- Total Tokens Consumed (with sparkline chart)
- Average Tokens Per User
- Onboarding Completion Rate (%)
- New Users This Month

Optional: Mini charts using Recharts
- Line chart: Token consumption trend (last 30 days)
- Pie chart: Token usage by feature type
- Bar chart: Top 10 most active users

### 3.3 All Users Table
**Column Headers:**
1. Name (searchable, sortable)
2. Email (searchable)
3. Designation
4. Phone (masked for privacy)
5. Onboarding Stage (badge: completed/in_progress/not_started)
6. Tokens Used (total, sortable)
7. Tokens This Month (sortable)
8. Total Interactions (sortable)
9. Last Active (relative time, sortable)
10. Status (badge: active/inactive/churned)
11. Actions (View Details, Edit, Delete)

**Table Features:**
- Pagination (20 rows per page, configurable)
- Sorting: Click column header to sort ascending/descending
- Filtering by:
  - Onboarding stage (dropdown)
  - Status (active/inactive/churned)
  - Date range (created/last_active)
  - Token usage range (min-max slider)
- Search: Global search by name/email (real-time)
- Responsive: Stack to vertical on mobile, horizontal scroll on smaller tablets
- Export: Button to export visible/filtered data as CSV

**Row Interactions:**
- Click row to expand and show more details (skills, resume filename, etc.)
- Hover to show action buttons (View, Edit, Delete)
- Highlight rows based on status (inactive = faded, active = normal)

### 3.4 User Details Modal/Page
When clicking "View Details" on a user:
- Profile section: Name, email, phone, designation
- Skills: Tags or badges
- Resume: Filename with download link (if available)
- Token Stats:
  - Total tokens used: Large number display
  - Tokens this month: Number + progress bar
  - Total interactions: Counter
  - Average tokens per interaction: Calculated metric
- Activity Timeline: Last 10 interactions (timestamps, token counts)
- Onboarding Progress: Steps completed (as % or visual progress bar)
- Account History:
  - Created date
  - Last updated
  - Last active
- Actions: Edit, Download Resume, Delete Account, Send Message

### 3.5 Reports Section (Optional but Recommended)
- Token Usage Trends: Line chart over 30/60/90 days
- User Segments: Pie/donut chart (high users, medium users, low users)
- Onboarding Funnel: Sankey or step diagram
- Feature Adoption: Which features consume most tokens

---

## 4. Technical Stack & Libraries

### Frontend Setup
- **Framework**: React 18+ with functional components
- **State Management**: React Context API or Zustand (keep it lightweight, not Redux unless complex)
- **HTTP Client**: axios or fetch API (wrap in custom hook)
- **UI Component Library**: Shadcn/ui (recommended) or Material-UI or Chakra UI
- **Charts**: Recharts (lightweight, React-native)
- **Icons**: lucide-react or Heroicons
- **Tables**: TanStack React Table v8 (for advanced features like sorting, filtering, pagination)
- **Styling**: Tailwind CSS (or CSS Modules if using Chakra/MUI)
- **Routing**: React Router v6 (for navigation between sections)
- **Notifications**: React Hot Toast or Sonner (for alerts/feedback)
- **Date Handling**: Day.js or date-fns (for formatting timestamps)
- **Data Validation**: Zod or Yup

### Recommended Folder Structure
```
src/
├── components/
│   ├── Dashboard/
│   │   ├── DashboardOverview.jsx
│   │   ├── StatCard.jsx
│   │   └── TrendChart.jsx
│   ├── Users/
│   │   ├── UsersTable.jsx
│   │   ├── UserFilters.jsx
│   │   ├── UserSearch.jsx
│   │   └── UserDetailsModal.jsx
│   ├── Layout/
│   │   ├── Header.jsx
│   │   ├── Sidebar.jsx
│   │   └── Layout.jsx
│   └── Common/
│       ├── LoadingSpinner.jsx
│       ├── ErrorBoundary.jsx
│       └── ConfirmDialog.jsx
├── hooks/
│   ├── useUsers.js (fetch all users)
│   ├── useUserDetails.js (fetch single user)
│   ├── useDashboardStats.js (fetch summary stats)
│   └── useApi.js (generic API hook)
├── services/
│   └── api.js (all API calls centralized)
├── context/
│   └── AuthContext.js (user auth state, if needed)
├── pages/
│   ├── DashboardPage.jsx
│   ├── UsersPage.jsx
│   └── ReportsPage.jsx
├── utils/
│   ├── formatters.js (format numbers, dates, etc.)
│   ├── constants.js (API URLs, pagination limits)
│   └── validators.js
├── App.jsx
└── main.jsx (entry point)
```

---

## 5. Key Features to Implement

### 5.1 Data Fetching & Caching
- Fetch all users on component mount (useEffect)
- Implement pagination to avoid loading 300+ rows at once
- Cache data for 5 minutes to reduce API calls
- Show loading skeleton while fetching
- Handle errors gracefully (show error message, retry button)

### 5.2 Real-time Filtering & Search
- Filter by onboarding stage, status, date range, token range
- Search as user types (debounce API calls to 300ms)
- Combine filters (e.g., "active" + "tokens > 50000" + "designation = Engineer")
- Show "X results found" count
- Clear filters button

### 5.3 Table Interactions
- Click column headers to sort (ascending/descending toggle)
- Show visual indicator (arrow icon) on sorted column
- Multi-select rows (checkboxes) for bulk actions (future: bulk email, delete, etc.)
- Single-click row expansion for quick preview
- Double-click or button for full details modal

### 5.4 Responsive Design
- Desktop: Full table with all columns visible
- Tablet (768px+): Hide non-critical columns (phone), keep essential ones
- Mobile (<768px): Collapse table to card view, show name, email, last_active, token_used prominently
- Fixed header, scrollable body for tables

### 5.5 Performance Optimizations
- Lazy load charts (don't render if not visible)
- Virtualize long tables (only render visible rows) using TanStack React Table
- Memoize components to prevent unnecessary re-renders (React.memo)
- Debounce search input (300ms delay before API call)
- Implement infinite scroll or load-more button instead of pagination if preferred

### 5.6 Authentication & Security
- Assume JWT-based auth (token in localStorage or httpOnly cookie)
- Add Authorization header to all API requests
- Redirect to login if 401 response
- Handle token refresh if expired
- (Optional) Show current user role/permissions

---

## 6. UI/UX Specifications

### Color Scheme
- Primary: Blue (#3b82f6 or similar)
- Success: Green (#10b981)
- Warning: Yellow/Orange (#f59e0b)
- Danger/Error: Red (#ef4444)
- Neutral: Gray (#6b7280, #9ca3af, #e5e7eb)
- Background: White or very light gray (#f9fafb)
- Text: Dark gray (#1f2937)

### Typography
- Headings (H1): 28-32px, bold, color primary
- Subheadings (H2): 20-24px, semi-bold
- Body text: 14-16px, regular
- Small text (captions, labels): 12-13px, gray
- Monospace for numbers: tokens_used, interaction counts (use font-family: 'Courier New' or similar)

### Spacing & Layout
- Use consistent 8px or 16px spacing grid
- Card padding: 16-24px
- Section gap: 24-32px
- Table row height: 48-56px

### Interactive Elements
- Buttons: Primary (filled), Secondary (outline), Tertiary (ghost/text)
- Hover states: Subtle background color change, slight shadow lift
- Disabled state: Opacity 0.5, no cursor
- Loading state: Spinner or skeleton loader
- Success feedback: Toast notification or inline success message

---

## 7. Error Handling & Edge Cases

### Handle These Scenarios
1. **No API Connection**: Show offline banner, retry button
2. **Empty Results**: "No users found" message with empty state illustration
3. **Slow Loading**: Show skeleton loaders, progress indicator
4. **API Errors**: Display user-friendly error message (not raw error)
5. **Invalid Data**: Gracefully handle null/undefined values in table (show "-" or "N/A")
6. **Large Numbers**: Format tokens (1M+, 1K+, etc.) for readability
7. **Timezone Issues**: Display timestamps in user's local timezone (or specify UTC)
8. **Missing Resume**: If resume_filename is null, show "No resume uploaded" badge

---

## 8. Token Tracking Implementation (Backend Note)

### What to Track
Each time a user makes an LLM call:
1. Extract token count from LLM response (Groq and OpenRouter APIs return this)
2. Increment `tokens_used` and `tokens_used_this_month` in database
3. Increment `total_interactions` counter
4. Update `last_api_call` timestamp

### Backend Code Pseudocode (LangChain Integration)
```python
from langchain_groq import ChatGroq  # or OpenRouter equivalent

def call_llm(user_id, prompt):
    response = chat.invoke(prompt)  # Groq/OpenRouter returns token counts
    tokens = response.usage.total_tokens  # Extract from response
    
    # Update user in DB
    db.update_user(user_id, {
        'tokens_used': User.tokens_used + tokens,
        'tokens_used_this_month': User.tokens_used_this_month + tokens,
        'total_interactions': User.total_interactions + 1,
        'last_api_call': datetime.utcnow()
    })
    
    return response
```

---

## 9. Acceptance Criteria / Testing Checklist

### Functional Requirements
- [ ] Dashboard loads and displays summary stats without errors
- [ ] Users table displays all 300+ users (paginated, not all at once)
- [ ] Sorting works on all columns (ascending/descending)
- [ ] Filtering by onboarding stage, status, date range works correctly
- [ ] Search finds users by name/email in <500ms
- [ ] Click "View Details" opens modal with full user info
- [ ] Export CSV button downloads all visible/filtered users
- [ ] Responsive design works on mobile (375px), tablet (768px), desktop (1024px+)
- [ ] Charts render without errors
- [ ] Token usage numbers are accurate (matches backend data)

### Non-Functional Requirements
- [ ] Page loads in <2 seconds (with cached data)
- [ ] Search/filter debounced (no lag while typing)
- [ ] Handle 500+ users without UI lag (virtualize table)
- [ ] API error handling shows user-friendly messages
- [ ] All timestamps display in correct timezone
- [ ] Mobile layout is touch-friendly (button sizes 44x44px minimum)

### Code Quality
- [ ] No console errors/warnings
- [ ] Components are reusable and well-documented
- [ ] API calls centralized in service file
- [ ] State management is simple and predictable
- [ ] Environment variables for API URL (development vs production)

---

## 10. Future Enhancements (Out of Scope for Initial Build)

- User activity audit log (who accessed what, when)
- Admin ability to reset/edit user tokens
- Email notifications for inactive users
- User segmentation and cohort analysis
- A/B testing dashboard integration
- Webhooks to trigger actions on user milestones
- Dark mode toggle
- Custom report builder (query builder UI)
- Integration with analytics (Segment, Mixpanel)
- Rate limiting dashboard (API usage alerts)

---

## 11. Deployment Notes

- Environment variables needed:
  - `REACT_APP_API_BASE_URL` - Backend API URL
  - `REACT_APP_JWT_TOKEN_KEY` - LocalStorage key for auth token
  - `REACT_APP_LOG_LEVEL` - Debug/info/error
- Build: `npm run build` outputs to `dist/`
- Deploy to Vercel, Netlify, or AWS S3 + CloudFront
- Set up CI/CD pipeline (GitHub Actions recommended)
- Configure CORS on backend to allow frontend domain

---

## 12. Success Metrics

Once deployed, monitor:
- Page load time (target: <2s)
- Time to first paint (target: <1s)
- API response times (target: <500ms for user list)
- User engagement (DAU, feature adoption)
- Error rate (target: <1%)
- Uptime (target: 99.9%)

---

## Summary

This prompt covers:
1. ✅ Backend API design (5 key endpoints)
2. ✅ React component structure and layout
3. ✅ Data fetching, filtering, sorting, pagination
4. ✅ Token tracking requirements
5. ✅ Responsive design and UX
6. ✅ Error handling and edge cases
7. ✅ Performance optimization techniques
8. ✅ Testing and deployment guidelines

**Next Steps**: Implement backend API endpoints first, then build React components in parallel. Test with real data from your SQLite database. Deploy and monitor performance.
