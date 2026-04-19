# CLFMS Frontend

React dashboard for the CLFMS (Client Financial & Logistics Management System) application.

## Features

- **Real-time KPI Dashboard** - Key performance indicators with trends
- **Financial Analytics** - Income, expenses, and profit visualization
- **30-Day Profit Trend** - Historical profit data with best/worst day analytics
- **Top Projects** - Ranked projects by profitability
- **Responsive Design** - Works on desktop, tablet, and mobile
- **Live Data Updates** - Automatic refresh every 5 minutes

## Technology Stack

- **React 18** - UI framework
- **Vite** - Build tool and dev server
- **Tailwind CSS** - Utility-first CSS framework
- **Recharts** - React charting library
- **Axios** - HTTP client
- **Lucide React** - Icon library

## Prerequisites

- Node.js 16+ and npm/yarn
- FastAPI backend running on `http://localhost:8000`

## Installation

```bash
cd frontend
npm install
```

## Development

Start the development server with hot module replacement:

```bash
npm run dev
```

The app will be available at `http://localhost:5173` and will proxy API requests to the backend.

## Building for Production

Build the frontend for production deployment:

```bash
npm run build
```

This outputs the built files to `app/static/frontend/`, which are served by FastAPI.

## Deployment

The frontend is built to `app/static/frontend/` and served by FastAPI. When the backend is running, navigate to `http://localhost:8000` to access the dashboard.

### In Docker

The frontend is built as part of the Docker image:

```bash
docker build -t clfms .
docker run -p 8000:8000 clfms
```

## API Integration

The dashboard connects to the following API endpoints:

- `GET /api/v1/dashboard/kpis` - Key performance indicators
- `GET /api/v1/dashboard/financial-summary` - Financial summary and breakdown
- `GET /api/v1/dashboard/profit-trend` - 30-day profit trend
- `GET /api/v1/dashboard/top-projects` - Top performing projects

## Troubleshooting

### API Connection Issues

If the dashboard shows "Failed to load dashboard data":

1. Verify the backend is running: `curl http://localhost:8000/api/v1/dashboard/kpis`
2. Check CORS configuration in `app/core/config.py`
3. Verify API endpoints are accessible from your network

### Build Issues

```bash
# Clear node_modules and reinstall
rm -rf node_modules package-lock.json
npm install
npm run build
```

## Project Structure

```
frontend/
├── index.html              # HTML entry point
├── package.json            # Dependencies
├── vite.config.js          # Vite configuration
├── tailwind.config.js      # Tailwind CSS config
├── postcss.config.js       # PostCSS config
└── src/
    ├── main.jsx            # React entry point
    ├── App.jsx             # Main App component
    ├── index.css           # Global styles
    └── components/
        ├── Header.jsx      # Top navigation bar
        ├── KPICard.jsx     # KPI metric cards
        ├── FinancialSummary.jsx  # Income/expense breakdown
        ├── ProfitTrend.jsx  # Profit trend chart
        └── TopProjects.jsx  # Top projects list
```

## Contributing

1. Create a feature branch: `git checkout -b feature/amazing-feature`
2. Make your changes and test locally: `npm run dev`
3. Build for production: `npm run build`
4. Commit your changes: `git commit -m 'Add amazing feature'`
5. Push to the branch: `git push origin feature/amazing-feature`
6. Open a Pull Request

## License

This project is proprietary software.

## Support

For issues or questions, contact the development team or open an issue in the main repository.
