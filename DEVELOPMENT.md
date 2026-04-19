# CLFMS Development Setup Guide

## Prerequisites

- Python 3.10 or higher
- pip package manager
- Git
- Docker & Docker Compose (optional, for containerized deployment)

## Quick Start

### 1. Clone and Setup

```bash
# Clone repository
git clone https://github.com/AI-create/CLFMS.git
cd CLFMS

# Create and activate virtual environment
python -m venv venv

# On Windows
venv\Scripts\activate

# On macOS/Linux
source venv/bin/activate
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Environment Configuration

Create a `.env` file in the project root:

```env
# Database
DATABASE_URL=sqlite:///./clfms.db

# Authentication
SECRET_KEY=your-secret-key-here-change-in-production
ADMIN_EMAIL=admin@clfms.local
ADMIN_PASSWORD=admin123

# Application
COMPANY_STATE=KA
DEBUG=True
```

### 4. Run the Application

```bash
# Development server with auto-reload
uvicorn app.main:app --reload

# Production server
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

Server will be available at `http://localhost:8000`

## Access Points

- **API Docs (Swagger)**: http://localhost:8000/docs
- **Alternative API Docs (ReDoc)**: http://localhost:8000/redoc
- **Health Check**: http://localhost:8000/api/v1/

## Testing

```bash
# Run all tests
pytest tests/ -v

# Run specific test file
pytest tests/test_fiio.py -v

# Run specific test
pytest tests/test_fiio.py::test_create_hourly_income -v

# Run with coverage
pytest tests/ --cov=app

# Run with output
pytest tests/ -s
```

## Project Structure

```
CLFMS/
├── app/
│   ├── main.py                 # Application entry point
│   ├── core/
│   │   ├── config.py          # Configuration settings
│   │   ├── database.py        # Database setup
│   │   ├── security.py        # Auth and security
│   │   └── response.py        # Response formatting
│   ├── middleware/
│   │   ├── auth.py            # Authentication middleware
│   │   └── logging.py         # Request logging
│   ├── modules/               # Feature modules
│   │   ├── auth/              # Authentication
│   │   ├── clients/           # Client management
│   │   ├── projects/          # Project management
│   │   ├── fiio/              # Financial tracking
│   │   ├── operations/        # Operations management
│   │   ├── research/          # Research management
│   │   ├── invoices/          # Invoice management
│   │   ├── payments/          # Payment tracking
│   │   ├── dashboard/         # Analytics dashboard
│   │   └── ...                # Additional modules
│   └── services/              # Cross-module services
│       └── activity_logging_service.py  # Audit trail
├── tests/                     # Test suite
│   ├── test_fiio.py
│   ├── test_operations.py
│   ├── test_research.py
│   ├── test_mvp_flow.py
│   └── ...
├── alembic/                   # Database migrations
├── templates/                 # HTML templates
├── static/                    # Static files
├── requirements.txt           # Python dependencies
├── Dockerfile                 # Container configuration
├── docker-compose.yml         # Container orchestration
├── README.md                  # Project documentation
└── .gitignore                # Git ignore rules
```

## Module Architecture

Each module follows this standard structure:

```
module_name/
├── __init__.py           # Package initialization
├── models.py             # SQLAlchemy ORM models
├── schemas.py            # Pydantic validation schemas
├── services.py           # Business logic services
├── routes.py             # FastAPI endpoints
```

### Example: Creating a New Endpoint

1. **Define Model** (`models.py`):

```python
from app.core.database import Base
from sqlalchemy import Column, Integer, String

class MyEntity(Base):
    __tablename__ = "my_entities"

    id = Column(Integer, primary_key=True)
    name = Column(String(255))
```

2. **Define Schema** (`schemas.py`):

```python
from pydantic import BaseModel

class CreateMyEntity(BaseModel):
    name: str

class MyEntityOut(BaseModel):
    id: int
    name: str
```

3. **Define Service** (`services.py`):

```python
from sqlalchemy.orm import Session

class MyService:
    @staticmethod
    def create(db: Session, payload: CreateMyEntity):
        entity = MyEntity(name=payload.name)
        db.add(entity)
        db.commit()
        db.refresh(entity)
        return entity
```

4. **Define Route** (`routes.py`):

```python
from fastapi import APIRouter, Depends

router = APIRouter(tags=["MyModule"])

@router.post("/my-entities")
def create_my_entity(
    payload: CreateMyEntity,
    db: Session = Depends(get_db),
    _user=Depends(require_roles(["admin"]))
):
    entity = MyService.create(db, payload)
    return api_success(MyEntityOut.model_validate(entity))
```

## Authentication

### Login

```bash
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "admin@clfms.local",
    "password": "admin123"
  }'
```

Response:

```json
{
  "success": true,
  "data": {
    "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "token_type": "bearer"
  }
}
```

### Using Token

```bash
curl -X GET http://localhost:8000/api/v1/dashboard/kpis \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
```

## API Examples

### Create a Client

```bash
curl -X POST http://localhost:8000/api/v1/clients \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Acme Corp",
    "email": "contact@acme.local",
    "phone": "555-0100",
    "address": "123 Main St"
  }'
```

### Create a Project

```bash
curl -X POST http://localhost:8000/api/v1/projects \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Website Redesign",
    "client_id": 1,
    "status": "active",
    "start_date": "2026-04-19",
    "end_date": "2026-06-30",
    "budget": 50000.0
  }'
```

### Record Income

```bash
curl -X POST http://localhost:8000/api/v1/hourly-incomes \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "employee_id": 1,
    "project_id": 1,
    "income_date": "2026-04-19",
    "hours_billed": 8.0,
    "hourly_rate": 100.0,
    "income_type": "hourly_billing"
  }'
```

## Debugging

### Enable Debug Logging

Set in `.env`:

```env
DEBUG=True
LOG_LEVEL=DEBUG
```

### View Database

Using SQLite CLI:

```bash
sqlite3 clfms.db

# List tables
.tables

# Query data
SELECT * FROM users;
```

## Common Issues

### Port Already in Use

```bash
# Find process using port 8000
lsof -i :8000

# Kill process
kill -9 <PID>
```

### Database Locked

Delete the SQLite database and restart:

```bash
rm clfms.db
# Restart application
```

### Import Errors

Ensure virtual environment is activated and dependencies installed:

```bash
source venv/bin/activate
pip install -r requirements.txt
```

## Performance Tips

1. **Use Pagination** - Always paginate list endpoints
2. **Index Queries** - Add indexes for frequently queried fields
3. **Cache Results** - Use Redis for frequently accessed data
4. **Connection Pooling** - Configure database connection pools
5. **Async Operations** - Consider async tasks for heavy processing

## Deployment

### Docker Deployment

```bash
# Build image
docker build -t clfms:latest .

# Run container
docker run -p 8000:8000 clfms:latest

# Or use Docker Compose
docker-compose up -d
```

### Production Checklist

- [ ] Change `SECRET_KEY` to a strong random value
- [ ] Set `DEBUG=False`
- [ ] Use PostgreSQL instead of SQLite
- [ ] Setup environment variables securely
- [ ] Configure proper logging
- [ ] Setup monitoring and alerts
- [ ] Enable CORS appropriately
- [ ] Setup SSL/TLS certificates
- [ ] Configure reverse proxy (nginx)
- [ ] Setup database backups

## Contributing

1. Create feature branch: `git checkout -b feature/your-feature`
2. Make changes and test: `pytest tests/ -v`
3. Commit: `git commit -m "description"`
4. Push: `git push origin feature/your-feature`
5. Create Pull Request

## Resources

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [SQLAlchemy Documentation](https://docs.sqlalchemy.org/)
- [Pydantic Documentation](https://docs.pydantic.dev/)
- [Pytest Documentation](https://docs.pytest.org/)

## Support

For issues or questions:

1. Check existing issues in GitHub
2. Create a new issue with details
3. Contact development team

---

Happy coding! 🚀
