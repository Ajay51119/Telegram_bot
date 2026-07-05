# 📱 Bot User Analytics Dashboard

A modern, fully-featured React dashboard for tracking Telegram bot users with real-time metrics, advanced filtering, and comprehensive analytics.

![Version](https://img.shields.io/badge/version-1.0.0-blue)
![React](https://img.shields.io/badge/react-18.2+-61DAFB?logo=react)
![Vite](https://img.shields.io/badge/vite-5.0+-646CFF?logo=vite)
![License](https://img.shields.io/badge/license-MIT-green)

## ✨ Features

### Dashboard
- **Real-time statistics** - Total users, active today, token consumption
- **Token trends** - 30-day visualization of token usage patterns
- **Top active users** - Leaderboard of most engaged users
- **Engagement metrics** - Onboarding completion rate, monthly actives
- **Responsive cards** - Mobile-friendly stat displays

### User Management
- **Advanced table** - Sort by any column, responsive layout
- **Smart filtering** - By status, onboarding stage, token range
- **Real-time search** - Find users by name or email (debounced)
- **User details modal** - Complete profile with skills, contact info, token history
- **CSV export** - Download filtered user data

### Reports & Analytics
- **User segmentation** - High/Medium/Low usage + Inactive users
- **Feature adoption** - Token consumption by feature type
- **Usage statistics** - Detailed metrics per segment
- **Export capabilities** - Generate CSV and PDF reports

### Technical Excellence
- ✅ **Fully responsive** - Works perfectly on mobile, tablet, desktop
- ✅ **Performance optimized** - Skeleton loaders, debouncing, pagination
- ✅ **Error handling** - Graceful failures with user-friendly messages
- ✅ **Modern stack** - React 18, Vite, Axios, no external UI library required
- ✅ **Accessible** - Keyboard navigation, proper ARIA labels
- ✅ **Themeable** - CSS variables for easy customization

## 🎯 Quick Start

### Prerequisites
- Node.js 16+
- Backend API running

### Installation
```bash
# Clone or download the project
git clone <repo-url>
cd user-tracking-dashboard

# Install dependencies
npm install

# Configure environment
cp .env.example .env
# Edit .env and set VITE_API_BASE_URL

# Start development server
npm run dev
```

Open http://localhost:5173 in your browser.

## 📁 Project Structure

```
src/
├── components/        # React components
│   ├── common/       # Reusable UI elements
│   ├── layout/       # Header, Sidebar
│   ├── dashboard/    # Dashboard page
│   ├── users/        # Users table page
│   └── reports/      # Reports page
├── hooks/            # Custom React hooks
├── services/         # API service layer
├── utils/            # Helper functions
├── App.jsx           # Main component
└── index.css         # Global styles
```

## 🔧 Configuration

### Environment Variables
```env
VITE_API_BASE_URL=http://localhost:8000/api
VITE_JWT_TOKEN_KEY=auth_token
VITE_LOG_LEVEL=info
VITE_ENABLE_REPORTS=true
```

### Backend API
Your backend must provide these endpoints:
- `GET /api/users` - Paginated user list
- `GET /api/stats/dashboard` - Dashboard metrics
- `GET /api/stats/token-trends` - Token trends
- `GET /api/stats/user-segments` - User segmentation data
- `GET /api/users/search` - User search
- `GET /api/users/export` - CSV export

See [SETUP.md](./SETUP.md#-backend-api-requirements) for detailed API specs.

## 🎨 Design

### Color Palette
```
Primary Blue:    #3b82f6
Success Green:   #10b981
Warning Orange:  #f59e0b
Danger Red:      #ef4444
Neutrals:        Gray 50-900
```

### Typography
- Display: Sora (sans-serif)
- Body: Sora (sans-serif)
- Mono: JetBrains Mono

### Responsive
- Mobile: < 768px
- Tablet: 768px - 1023px
- Desktop: 1024px+

## 🚀 Development

### Available Scripts

```bash
# Development server with hot reload
npm run dev

# Build for production
npm run build

# Preview production build locally
npm run preview

# Run linter
npm run lint
```

### Code Style
- Functional components with React Hooks
- Custom hooks for data fetching
- CSS variables for theming
- BEM-like naming for CSS classes

## 📊 Data Flow

```
API Service (services/api.js)
         ↓
    Custom Hooks (hooks/useApi.js)
         ↓
    Components with State
         ↓
    Render UI with Formatters
```

## 🔐 Authentication

The app automatically includes JWT tokens in all API requests:
1. Token stored in `localStorage.getItem('auth_token')`
2. Injected in `Authorization: Bearer {token}` header
3. 401 responses redirect to login

## 🧪 Testing

### Development Testing
```bash
npm run dev
# Browse to http://localhost:5173
# Open DevTools (F12) to inspect network, console, etc.
```

### Production Build
```bash
npm run build
npm run preview
```

## 📦 Deployment

### Vercel (Recommended)
```bash
npm i -g vercel
vercel
```

### Netlify
```bash
npm run build
# Upload dist/ folder
```

### Docker
```dockerfile
FROM node:18-alpine
WORKDIR /app
COPY package*.json ./
RUN npm install
COPY . .
RUN npm run build
EXPOSE 3000
CMD ["npm", "run", "preview"]
```

## 📚 Documentation

- [Setup Guide](./SETUP.md) - Detailed setup and configuration
- [API Reference](./SETUP.md#-backend-api-requirements) - Backend requirements
- [Component Guide](./SETUP.md#-components) - Component documentation
- [Styling Guide](./SETUP.md#-design--styling) - Design system

## 🐛 Troubleshooting

### API errors
- Verify `VITE_API_BASE_URL` in .env
- Check backend is running and accessible
- Review API response in Network tab

### Auth errors
- Clear localStorage and login again
- Check token expiration
- Verify CORS is configured on backend

### Styling issues
- Hard refresh browser (Ctrl+Shift+R)
- Clear build cache: `npm run build` fresh
- Check CSS variables in DevTools

See [SETUP.md Troubleshooting](./SETUP.md#-troubleshooting) for more.

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see LICENSE file for details.

## 👥 Team

Built with ❤️ for bot analytics and user tracking.

## 📞 Support

For issues, questions, or suggestions:
1. Check [SETUP.md](./SETUP.md) documentation
2. Review API endpoint specifications
3. Check browser console for errors
4. Verify backend responses in Network tab

## 🎯 Roadmap

- [ ] Dark mode toggle
- [ ] Advanced filtering UI
- [ ] Custom date range picker
- [ ] User activity timeline
- [ ] Email notification alerts
- [ ] Admin audit log
- [ ] API rate limiting dashboard
- [ ] Webhook integration
- [ ] A/B testing dashboard
- [ ] Real-time updates with WebSocket

## 📈 Performance Metrics

Target metrics for production:
- Page load: < 2 seconds
- First paint: < 1 second
- API response: < 500ms
- Table pagination: Instant
- Search debounce: 300ms
- Error rate: < 1%
- Uptime: 99.9%

## 🔗 Links

- [React Documentation](https://react.dev)
- [Vite Documentation](https://vitejs.dev)
- [Axios Documentation](https://axios-http.com)

---

**Version:** 1.0.0  
**Last Updated:** June 2024  
**Status:** Production Ready ✅
