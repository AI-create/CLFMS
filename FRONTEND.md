# CLFMS Frontend Development Guide

## Overview

The CLFMS Frontend is a modern React dashboard application built with Vite, Tailwind CSS, and Recharts. It provides real-time analytics, financial tracking, and project management interfaces integrated with the FastAPI backend.

## Quick Start

### Prerequisites

- Node.js 16+ with npm or yarn
- FastAPI backend running on port 8000
- Git

### Setup & Development

```bash
# Navigate to frontend directory
cd frontend

# Install dependencies
npm install

# Start development server
npm run dev
```

The development server runs on `http://localhost:5173` with hot module replacement enabled.

### Building for Production

```bash
# Build the frontend
npm run build

# Output is placed in: app/static/frontend/
```

## Architecture

### Component Structure

```
src/
├── App.jsx                 # Main app container & data fetching
├── index.css              # Global styles with Tailwind
├── main.jsx               # React entry point
└── components/
    ├── Header.jsx         # Top navigation & branding
    ├── KPICard.jsx        # Metric cards with trends
    ├── FinancialSummary.jsx  # Income/expense breakdown
    ├── ProfitTrend.jsx    # 30-day profit visualization
    └── TopProjects.jsx    # Top projects ranking
```

### Data Flow

1. **App.jsx** - Main component that handles API calls
2. **useEffect Hook** - Fetches data from backend on mount
3. **State Management** - Uses React hooks (useState) for component state
4. **Auto-refresh** - Updates data every 5 minutes
5. **Child Components** - Display the data in various visualizations

### API Endpoints

The frontend connects to these backend endpoints:

```
GET /api/v1/dashboard/kpis
├─ Returns: { total_revenue, total_expenses, net_profit, pending_payments, trends }

GET /api/v1/dashboard/financial-summary
├─ Returns: { total_income, total_expenses, daily_breakdown, income_breakdown }

GET /api/v1/dashboard/profit-trend
├─ Returns: { trends: [{ date, profit, income, expenses }] }

GET /api/v1/dashboard/top-projects
├─ Returns: { projects: [{ name, status, revenue, expenses, profit }] }
```

## Development

### Adding a New Component

1. Create component file in `src/components/ComponentName.jsx`
2. Import in `App.jsx`
3. Add to JSX with props
4. Style with Tailwind CSS classes

Example:

```jsx
// src/components/CustomMetric.jsx
export default function CustomMetric({ title, value }) {
  return (
    <div className="card-lg">
      <h3 className="metric-label">{title}</h3>
      <p className="metric-value">{value}</p>
    </div>
  )
}

// In App.jsx
import CustomMetric from './components/CustomMetric'
// ... in JSX
<CustomMetric title="Example" value="123" />
```

### Styling

The frontend uses Tailwind CSS for styling with custom theme extensions:

**Colors:**
- `primary-*` - Primary brand color (sky blue)
- `success` - Green for positive metrics
- `warning` - Orange for warnings
- `danger` - Red for negative metrics

**Component Classes:**
- `.card` - Base card style
- `.card-lg` - Large card with padding
- `.metric-label` - Small metric labels
- `.metric-value` - Large metric values
- `.btn-primary`, `.btn-secondary` - Button styles

### Tailwind Configuration

Edit `tailwind.config.js` to customize:
- Color scheme
- Typography
- Spacing
- Breakpoints

Example:

```js
// tailwind.config.js
theme: {
  extend: {
    colors: {
      primary: { /* custom colors */ }
    }
  }
}
```

### Environment Variables

Create `.env.local` for development:

```
VITE_API_URL=http://localhost:8000
VITE_API_PREFIX=/api/v1
```

Then use in code:

```jsx
const API_URL = import.meta.env.VITE_API_PREFIX
```

## Charting

The frontend uses **Recharts** for data visualization. Examples:

### Line Chart (Profit Trend)

```jsx
import { LineChart, Line, XAxis, YAxis } from 'recharts'

<LineChart data={data}>
  <XAxis dataKey="date" />
  <YAxis />
  <Line type="monotone" dataKey="profit" stroke="#0ea5e9" />
</LineChart>
```

### Bar Chart (Financial Summary)

```jsx
import { BarChart, Bar } from 'recharts'

<BarChart data={data}>
  <Bar dataKey="income" fill="#3b82f6" />
  <Bar dataKey="expenses" fill="#f59e0b" />
</BarChart>
```

For more examples, see the component files.

## Performance

### Optimizations

1. **Code Splitting** - Vite automatically splits component code
2. **Lazy Loading** - Components load on demand
3. **Memoization** - Use React.memo() for expensive components
4. **API Caching** - 5-minute auto-refresh reduces API calls

### Build Optimization

```bash
# Build with source maps for debugging (larger)
npm run build -- --sourcemap

# Build without source maps (smaller)
npm run build
```

## Testing

### Manual Testing Checklist

- [ ] Dashboard loads without errors
- [ ] KPI cards display correct values
- [ ] Financial summary chart renders
- [ ] Profit trend shows 30-day data
- [ ] Top projects list populated
- [ ] Auto-refresh works (check network tab)
- [ ] Responsive on mobile/tablet
- [ ] Error message displays on API failure
- [ ] Loading state shows while fetching

### Testing with Mock Data

Update `App.jsx` to use mock data for development:

```jsx
// Mock data for testing
const mockKPIs = {
  total_revenue: 50000,
  total_expenses: 25000,
  net_profit: 25000,
  pending_payments: 5000,
}

// Use in component
setKpis(mockKPIs)
```

## Deployment

### Static Site Hosting

The frontend is built to `app/static/frontend/` and served by FastAPI:

1. Build the frontend: `npm run build`
2. Built files are in: `app/static/frontend/dist/`
3. FastAPI serves from: `http://localhost:8000/`

### Docker Deployment

The Dockerfile handles frontend build automatically:

```bash
# Build image with frontend included
docker build -t clfms .

# Run container
docker run -p 8000:8000 clfms
```

### Separate Deployment (Advanced)

To deploy frontend separately:

1. Build: `npm run build`
2. Upload `dist/` contents to CDN or static host
3. Configure CORS in FastAPI for API calls
4. Update `vite.config.js` API proxy

## Troubleshooting

### Issue: "Failed to load dashboard data"

**Causes & Solutions:**
1. Backend not running - Start backend: `uvicorn app.main:app --reload`
2. CORS error - Check `cors_origins` in `app/core/config.py`
3. Wrong API URL - Verify `API_URL` in App.jsx
4. API endpoint not found - Check backend routers are registered

### Issue: Build errors

```bash
# Clear cache and reinstall
rm -rf node_modules package-lock.json
npm install
npm run build
```

### Issue: Styling not applied

1. Rebuild Tailwind CSS: `npm run build` (regenerates styles)
2. Clear browser cache (Ctrl+Shift+Delete)
3. Check class names in components

### Issue: Hot reload not working

1. Restart dev server: Ctrl+C, then `npm run dev`
2. Check no port 5173 conflicts: `lsof -i :5173`
3. Clear `.vite` directory cache

## Best Practices

### Component Development

1. **Single Responsibility** - Each component does one thing
2. **Props Validation** - Accept and validate all props
3. **Error Handling** - Handle data loading errors gracefully
4. **Accessibility** - Use semantic HTML and ARIA labels
5. **Performance** - Avoid unnecessary re-renders

### Code Organization

```jsx
// Recommended order:
1. Imports
2. Constants
3. Component definition
4. Props interface (if using TypeScript)
5. Exported component
```

### Naming Conventions

- Components: PascalCase (`KPICard.jsx`)
- Files: Match component name
- CSS Classes: kebab-case (`metric-label`)
- Functions: camelCase (`fetchData`)
- Constants: UPPER_SNAKE_CASE (`API_URL`)

## Contributing

1. Create feature branch: `git checkout -b feature/dashboard-enhancement`
2. Make changes and test locally: `npm run dev`
3. Build and verify: `npm run build`
4. Commit: `git commit -m 'Add dashboard enhancement'`
5. Push and create PR

## Resources

- [React Documentation](https://react.dev)
- [Vite Guide](https://vitejs.dev)
- [Tailwind CSS](https://tailwindcss.com)
- [Recharts Examples](https://recharts.org/examples)
- [Lucide Icons](https://lucide.dev)

## Support

For questions or issues:
1. Check this guide
2. Review component source code
3. Check browser console for errors
4. Open issue in main repository

---

*Last Updated: April 19, 2026*
*Frontend Version: 1.0.0*
