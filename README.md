# CLFMS - Client Lifecycle & Financial Management System

A comprehensive ERP system built with FastAPI for managing client lifecycles, projects, finances, operations, and research management.

## 🎯 Project Overview

CLFMS is a production-ready FastAPI application designed to streamline business operations with integrated financial tracking, project management, and comprehensive analytics.

**Current Status**: ✅ MVP Complete - 84 tests passing, 16 modules active

## 📋 Key Features

### Core Modules (17 Active)

1. **Authentication & Authorization**
   - JWT-based authentication
   - Role-based access control (RBAC)
   - User management with default admin setup

2. **Client Management**
   - Client lifecycle tracking
   - Lead management with conversion tracking
   - Client details and contact information

3. **Project Management**
   - Full project CRUD operations
   - Status tracking (active, completed, on-hold)
   - Budget and timeline management

4. **Financial Management**
   - FI-IO Module: Hourly/Project Income & Expense Tracking
   - Daily profit calculation and project profitability analysis
   - Live 30-day profit summary with analytics
   - Expense tracking and cost allocation

5. **Operations Management**
   - Employee management and attendance tracking
   - Activity logging with clock-in/out functionality
   - Task assignment and progress tracking
   - Daily hours calculation and employee summaries

6. **Research Management**
   - Research project tracking
   - Experiment management with methodology documentation
   - IP potential assessment
   - Reproducibility analysis

7. **Invoice & Payment Management**
   - Invoice generation and tracking
   - Payment recording with partial payment support
   - Overdue invoice tracking
   - Financial reconciliation

8. **Document Management**
   - File upload and version control
   - Document metadata tracking
   - File restoration capabilities

9. **Dashboard & Analytics**
   - Real-time KPI monitoring
   - Financial summary with income/expense breakdown
   - 30-day profit trends for visualization
   - Top performing projects ranking

10. **Additional Modules**
    - Task management
    - Onboarding tracking
    - Project closure management
    - Activity logging and audit trails
    - File management with versioning

## 🚀 API Endpoints Overview

### Authentication

- `POST /api/v1/auth/login` - User login
- `POST /api/v1/auth/logout` - User logout

### Clients

- `POST /api/v1/clients` - Create client
- `GET /api/v1/clients` - List clients
- `GET /api/v1/clients/{client_id}` - Get client details

### Projects

- `POST /api/v1/projects` - Create project
- `GET /api/v1/projects` - List projects
- `PUT /api/v1/projects/{project_id}` - Update project

### Financial (FI-IO)

- `POST /api/v1/hourly-incomes` - Record hourly income
- `GET /api/v1/hourly-incomes` - List hourly incomes
- `POST /api/v1/project-incomes` - Record project income
- `GET /api/v1/project-incomes` - List project incomes
- `POST /api/v1/hourly-expenses` - Record hourly expense
- `GET /api/v1/hourly-expenses` - List hourly expenses
- `POST /api/v1/project-expenses` - Record project expense
- `GET /api/v1/project-expenses` - List project expenses
- `GET /api/v1/daily-profit/{date}` - Get daily profit
- `GET /api/v1/daily-profits` - Get profit range
- `GET /api/v1/project-profit/{project_id}` - Get project profitability
- `GET /api/v1/live-profit-summary` - Get 30-day profit analytics

### Operations

- `POST /api/v1/employees` - Create employee
- `GET /api/v1/employees` - List employees
- `POST /api/v1/activities` - Log activity
- `GET /api/v1/activities` - List activities
- `POST /api/v1/clock-in` - Clock in employee
- `POST /api/v1/clock-out` - Clock out employee
- `POST /api/v1/task-assignments` - Assign task
- `GET /api/v1/daily-hours/{employee_id}/{date}` - Get daily hours
- `GET /api/v1/employee-summary/{employee_id}` - Get employee monthly summary

### Research

- `POST /api/v1/research-projects` - Create research project
- `GET /api/v1/research-projects` - List research projects
- `POST /api/v1/experiments` - Create experiment
- `GET /api/v1/research-logs` - Get research logs
- `GET /api/v1/ip-potential` - Get IP potential experiments
- `GET /api/v1/project-summary/{project_id}` - Get research project summary

### Invoices & Payments

- `POST /api/v1/invoices` - Create invoice
- `GET /api/v1/invoices` - List invoices
- `POST /api/v1/payments` - Record payment
- `GET /api/v1/payments` - List payments

### Dashboard

- `GET /api/v1/dashboard/kpis` - Get KPIs
- `GET /api/v1/dashboard/financial-summary` - Get financial overview
- `GET /api/v1/dashboard/profit-trend` - Get 30-day profit trend
- `GET /api/v1/dashboard/top-projects` - Get top projects by profit

## 🔐 Role-Based Access Control

Available roles:

- `admin` - Full system access
- `finance` - Financial operations access
- `sales` - Sales and client management
- `operations` - Operations management
- `project_manager` - Project oversight
- `employee` - Basic access

## 📊 Testing

**Test Coverage**: 84 tests, all passing

Run tests:

```bash
pytest tests/ -v
```

Run specific module tests:

```bash
pytest tests/test_fiio.py -v
pytest tests/test_operations.py -v
pytest tests/test_research.py -v
```

## 🛠 Technology Stack

- **Framework**: FastAPI with Python 3.10+
- **Database**: SQLAlchemy ORM with SQLite (MVP), PostgreSQL ready
- **Authentication**: JWT with role-based access control
- **Validation**: Pydantic v2
- **Testing**: Pytest with TestClient
- **Deployment**: Docker & Docker Compose

## 📦 Installation

1. **Clone repository**:

   ```bash
   git clone https://github.com/AI-create/CLFMS.git
   cd CLFMS
   ```

2. **Create virtual environment**:

   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**:

   ```bash
   pip install -r requirements.txt
   ```

4. **Configure environment**:

   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   ```

5. **Run migrations** (if using Alembic):

   ```bash
   alembic upgrade head
   ```

6. **Start server**:
   ```bash
   uvicorn app.main:app --reload
   ```

Access API at: http://localhost:8000
Swagger docs: http://localhost:8000/docs
ReDoc: http://localhost:8000/redoc

## 🐳 Docker Deployment

Build and run with Docker Compose:

```bash
docker-compose up -d
```

## 📝 Environment Configuration

Key environment variables:

- `DATABASE_URL` - Database connection string
- `SECRET_KEY` - JWT signing key
- `ADMIN_EMAIL` - Default admin email
- `ADMIN_PASSWORD` - Default admin password
- `COMPANY_STATE` - Company state (default: KA)

## 🚦 Project Status

### Completed ✅

- Authentication and user management
- All 17 modules with full CRUD operations
- Financial tracking (FI-IO) with profit calculations
- Operations management with time tracking
- Research project management
- Dashboard with analytics
- Activity logging and audit trails
- Role-based access control
- 84 comprehensive tests
- Git repository initialization

### Recent Enhancements

- Dashboard financial analytics with 30-day trends
- Project profitability analysis
- Income/expense breakdown by type
- Live profit summary with best/worst day metrics

## 🔄 Recent Commits

1. **Enhance dashboard module with financial analytics**
   - Added financial summary endpoint with breakdown
   - Added profit trend visualization
   - Added top projects ranking
   - All tests passing

2. **Git repository initialization**
   - Initialized git repo
   - Added .gitignore
   - Configured GitHub remote

3. **Complete FI-IO Module**
   - 16 REST endpoints
   - 10 passing tests
   - Profit calculation engine
   - Daily and project-level analytics

## 📈 Next Steps

- [ ] Advanced filtering and search capabilities
- [ ] Export to PDF/Excel reports
- [ ] Email notifications for overdue payments
- [ ] Mobile app integration
- [ ] Advanced analytics dashboard
- [ ] Multi-currency support
- [ ] API rate limiting
- [ ] Webhooks for integrations
- [ ] Production deployment setup

## 🤝 Contributing

1. Create a feature branch
2. Make changes and ensure tests pass
3. Commit with descriptive messages
4. Push and create a pull request

## 📄 License

Internal project - All rights reserved

## 📞 Support

For issues or questions, contact the development team.

---

**Built with ❤️ using FastAPI**
