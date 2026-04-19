# CLFMS API Configuration Guide

## Environment Variables

Create a `.env` file in the project root with these variables:

```env
# Database Configuration
DATABASE_URL=sqlite:///./clfms.db
# For PostgreSQL: postgresql://user:password@localhost/clfms

# Security
SECRET_KEY=your-super-secret-key-change-this-in-production
JWT_ALGORITHM=HS256
JWT_EXPIRATION_HOURS=24

# Admin Configuration
ADMIN_EMAIL=admin@clfms.local
ADMIN_PASSWORD=admin123

# Application Settings
COMPANY_STATE=KA
DEBUG=True
LOG_LEVEL=INFO

# CORS Configuration
CORS_ORIGINS=["http://localhost:3000", "http://localhost:8000"]
CORS_CREDENTIALS=True
CORS_METHODS=["GET", "POST", "PUT", "DELETE", "OPTIONS"]
CORS_HEADERS=["*"]

# Rate Limiting
RATE_LIMIT_REQUESTS=1000
RATE_LIMIT_PERIOD=3600

# File Upload
MAX_UPLOAD_SIZE=52428800  # 50MB
ALLOWED_FILE_TYPES=["pdf", "docx", "xlsx", "jpg", "png", "txt"]
```

## API Endpoints Reference

### Authentication Endpoints

- `POST /api/v1/auth/login` - User login (returns JWT token)
- `POST /api/v1/auth/logout` - User logout

### Dashboard Analytics

- `GET /api/v1/dashboard/kpis` - Get key performance indicators
- `GET /api/v1/dashboard/financial-summary` - Get financial overview
- `GET /api/v1/dashboard/profit-trend` - Get 30-day profit trends
- `GET /api/v1/dashboard/top-projects` - Get top projects by profitability

### Client Management

- `POST /api/v1/clients` - Create new client
- `GET /api/v1/clients` - List all clients (paginated)
- `GET /api/v1/clients/{client_id}` - Get client details
- `PUT /api/v1/clients/{client_id}` - Update client

### Project Management

- `POST /api/v1/projects` - Create project
- `GET /api/v1/projects` - List projects (with filters)
- `GET /api/v1/projects/{project_id}` - Get project details
- `PUT /api/v1/projects/{project_id}` - Update project

### Financial Management (FI-IO Module)

**Hourly Income:**

- `POST /api/v1/hourly-incomes` - Record hourly income
- `GET /api/v1/hourly-incomes` - List hourly incomes (with date filters)
- `GET /api/v1/hourly-incomes/{income_id}` - Get income details
- `PUT /api/v1/hourly-incomes/{income_id}` - Update hourly income

**Project Income:**

- `POST /api/v1/project-incomes` - Record project income
- `GET /api/v1/project-incomes` - List project incomes

**Hourly Expense:**

- `POST /api/v1/hourly-expenses` - Record hourly expense
- `GET /api/v1/hourly-expenses` - List hourly expenses

**Project Expense:**

- `POST /api/v1/project-expenses` - Record project expense
- `GET /api/v1/project-expenses` - List project expenses

**Profit Analytics:**

- `GET /api/v1/daily-profit/{date}` - Get profit for specific date
- `GET /api/v1/daily-profits?date_from={}&date_to={}` - Get profit range
- `GET /api/v1/project-profit/{project_id}` - Get project profitability
- `GET /api/v1/live-profit-summary?days=30` - Get 30-day summary

### Operations Management

**Employees:**

- `POST /api/v1/employees` - Create employee
- `GET /api/v1/employees` - List employees
- `GET /api/v1/employees/{employee_id}` - Get employee details
- `PUT /api/v1/employees/{employee_id}` - Update employee

**Time Tracking:**

- `POST /api/v1/clock-in` - Clock in employee
- `POST /api/v1/clock-out` - Clock out employee
- `GET /api/v1/daily-hours/{employee_id}/{date}` - Get daily hours
- `GET /api/v1/employee-summary/{employee_id}` - Get employee monthly summary

**Activities:**

- `POST /api/v1/activities` - Log activity
- `GET /api/v1/activities` - List activities

**Tasks:**

- `POST /api/v1/task-assignments` - Assign task
- `GET /api/v1/task-assignments` - List task assignments
- `PUT /api/v1/task-assignments/{task_id}` - Update task

### Research Management

- `POST /api/v1/research-projects` - Create research project
- `GET /api/v1/research-projects` - List research projects
- `POST /api/v1/experiments` - Create experiment
- `GET /api/v1/research-logs` - Get research logs
- `GET /api/v1/ip-potential` - Get IP potential experiments
- `GET /api/v1/project-summary/{project_id}` - Get research summary

### Invoices & Payments

- `POST /api/v1/invoices` - Create invoice
- `GET /api/v1/invoices` - List invoices
- `PUT /api/v1/invoices/{invoice_id}` - Update invoice
- `POST /api/v1/payments` - Record payment
- `GET /api/v1/payments` - List payments

### File Management

- `POST /api/v1/files/upload` - Upload file
- `GET /api/v1/files` - List files
- `GET /api/v1/files/{file_id}` - Get file metadata
- `PUT /api/v1/files/{file_id}` - Update file
- `DELETE /api/v1/files/{file_id}` - Delete file

### Activity Logs

- `GET /api/v1/activity-logs` - Get audit trail
- `GET /api/v1/activity-logs/{entity_type}` - Get logs for entity type

## Request/Response Format

### Standard Response Format

**Success Response:**

```json
{
  "success": true,
  "data": {
    "id": 1,
    "name": "Example",
    ...
  }
}
```

**Error Response:**

```json
{
  "success": false,
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Invalid request data",
    "details": [
      {
        "field": "email",
        "message": "Invalid email format"
      }
    ]
  }
}
```

### Authentication Header

All protected endpoints require:

```
Authorization: Bearer <JWT_TOKEN>
```

## Common Query Parameters

**Pagination:**

- `page` (default: 1) - Page number
- `limit` (default: 20, max: 100) - Results per page

**Filtering:**

- `date_from` - Start date (YYYY-MM-DD)
- `date_to` - End date (YYYY-MM-DD)
- `status` - Filter by status
- `project_id` - Filter by project

**Sorting:**

- `sort_by` - Field to sort by
- `sort_order` - asc or desc

## Role-Based Access Control

**Admin Role**

- Access: All endpoints
- Permissions: Full system access

**Finance Role**

- Access: Financial data, invoices, payments, dashboard
- Restrictions: Cannot modify user roles

**Sales Role**

- Access: Clients, leads, projects, invoices
- Restrictions: No access to operations or payroll

**Operations Role**

- Access: Employees, activities, tasks, time tracking
- Restrictions: No access to financial data

**Project Manager Role**

- Access: Projects, tasks, dashboard, analytics
- Restrictions: Limited to assigned projects

**Employee Role**

- Access: Limited self-service options
- Restrictions: View only own data

## Testing API Endpoints

### Using cURL

**Login:**

```bash
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "admin@clfms.local",
    "password": "admin123"
  }'
```

**Get Dashboard KPIs:**

```bash
curl -X GET http://localhost:8000/api/v1/dashboard/kpis \
  -H "Authorization: Bearer YOUR_TOKEN"
```

**Create Project:**

```bash
curl -X POST http://localhost:8000/api/v1/projects \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "New Project",
    "client_id": 1,
    "status": "active",
    "budget": 50000
  }'
```

### Using Postman

1. Import collection from `postman-collection.json` (if available)
2. Set up environment variables in Postman
3. Use pre-configured requests for all endpoints

## Error Codes

- `400` - Bad Request (validation error)
- `401` - Unauthorized (missing/invalid token)
- `403` - Forbidden (insufficient permissions)
- `404` - Not Found
- `409` - Conflict (duplicate entry)
- `422` - Unprocessable Entity (invalid data)
- `429` - Too Many Requests (rate limited)
- `500` - Internal Server Error

## Performance Optimization Tips

1. **Always use pagination** for list endpoints
2. **Filter results** to reduce data transfer
3. **Use date ranges** for historical queries
4. **Cache frequently accessed data** (KPIs, top projects)
5. **Batch operations** when possible
6. **Use indexes** on commonly queried fields

## Deployment Considerations

- **Set `DEBUG=False`** in production
- **Use strong `SECRET_KEY`** (minimum 32 characters)
- **Configure HTTPS** with SSL certificates
- **Setup database backups** (daily minimum)
- **Monitor API logs** for errors
- **Setup alert notifications** for critical errors
- **Configure rate limiting** to prevent abuse
- **Use environment-specific configs** (dev/staging/prod)

## Support & Documentation

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **Health Check**: http://localhost:8000/api/v1/

For more information, see README.md and DEVELOPMENT.md
