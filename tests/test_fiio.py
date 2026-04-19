"""Tests for FI-IO Module"""
import os
import pytest

# Configure an isolated DB + JWT secret BEFORE importing the app.
os.environ.setdefault("DATABASE_URL", "sqlite:///./test_clfms.db")
os.environ.setdefault("SECRET_KEY", "test-secret-key")
os.environ.setdefault("COMPANY_STATE", "KA")
os.environ.setdefault("ADMIN_EMAIL", "admin@test.local")
os.environ.setdefault("ADMIN_PASSWORD", "admin123")
os.environ.setdefault("ADMIN_ROLE", "admin")

from fastapi.testclient import TestClient
from app.core.database import Base, SessionLocal
from app.core.config import settings
from app.main import app
from datetime import date, timedelta


def _login(client):
    """Login and get token"""
    res = client.post(
        "/api/v1/auth/login",
        json={"email": settings.default_admin_email, "password": settings.default_admin_password},
    )
    assert res.status_code == 200, res.text
    body = res.json()
    assert body["success"] is True
    return body["data"]["token"]


def _auth(token: str) -> dict:
    """Get auth headers"""
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture(scope="session")
def test_client() -> TestClient:
    with TestClient(app) as client:
        yield client


@pytest.fixture(autouse=True)
def cleanup_db():
    """Clean up database between tests"""
    db = SessionLocal()
    try:
        skip = {"users"}
        for table in reversed(Base.metadata.sorted_tables):
            if table.name in skip:
                continue
            db.execute(table.delete())
        db.commit()
    finally:
        db.close()


def test_create_hourly_income(test_client):
    """Test creating hourly income"""
    token = _login(test_client)
    headers = _auth(token)

    res = test_client.post(
        "/api/v1/hourly-incomes",
        json={
            "employee_id": 1,
            "income_date": str(date.today()),
            "hours_billed": 8.0,
            "hourly_rate": 75.0,
            "income_type": "hourly_billing",
        },
        headers=headers,
    )
    assert res.status_code == 200
    data = res.json()["data"]
    assert data["hours_billed"] == 8.0
    assert data["hourly_rate"] == 75.0
    assert data["amount"] == 600.0


def test_list_hourly_incomes(test_client):
    """Test listing hourly incomes"""
    token = _login(test_client)
    headers = _auth(token)

    # Create incomes
    for i in range(2):
        test_client.post(
            "/api/v1/hourly-incomes",
            json={
                "employee_id": i + 1,
                "income_date": str(date.today()),
                "hours_billed": 8.0,
                "hourly_rate": 75.0,
            },
            headers=headers,
        )

    # List incomes
    res = test_client.get(
        "/api/v1/hourly-incomes",
        headers=headers,
    )
    assert res.status_code == 200
    body = res.json()["data"]
    assert len(body["data"]) == 2


def test_create_project_income(test_client):
    """Test creating project income"""
    token = _login(test_client)
    headers = _auth(token)

    res = test_client.post(
        "/api/v1/project-incomes",
        json={
            "project_id": 1,
            "client_id": 1,
            "income_date": str(date.today()),
            "amount": 5000.0,
            "income_type": "project_revenue",
        },
        headers=headers,
    )
    assert res.status_code == 200
    data = res.json()["data"]
    assert data["amount"] == 5000.0
    assert data["project_id"] == 1


def test_create_hourly_expense(test_client):
    """Test creating hourly expense"""
    token = _login(test_client)
    headers = _auth(token)

    res = test_client.post(
        "/api/v1/hourly-expenses",
        json={
            "employee_id": 1,
            "expense_date": str(date.today()),
            "hours_worked": 8.0,
            "hourly_cost": 50.0,
            "expense_type": "salary",
        },
        headers=headers,
    )
    assert res.status_code == 200
    data = res.json()["data"]
    assert data["hours_worked"] == 8.0
    assert data["hourly_cost"] == 50.0
    assert data["amount"] == 400.0


def test_create_project_expense(test_client):
    """Test creating project expense"""
    token = _login(test_client)
    headers = _auth(token)

    res = test_client.post(
        "/api/v1/project-expenses",
        json={
            "project_id": 1,
            "expense_date": str(date.today()),
            "amount": 1500.0,
            "expense_type": "materials",
            "vendor": "Supplier Inc",
        },
        headers=headers,
    )
    assert res.status_code == 200
    data = res.json()["data"]
    assert data["amount"] == 1500.0
    assert data["vendor"] == "Supplier Inc"


def test_get_daily_profit(test_client):
    """Test getting daily profit"""
    token = _login(test_client)
    headers = _auth(token)

    today = date.today()

    # Create income and expense
    test_client.post(
        "/api/v1/hourly-incomes",
        json={
            "employee_id": 1,
            "income_date": str(today),
            "hours_billed": 8.0,
            "hourly_rate": 100.0,
        },
        headers=headers,
    )

    test_client.post(
        "/api/v1/hourly-expenses",
        json={
            "employee_id": 1,
            "expense_date": str(today),
            "hours_worked": 8.0,
            "hourly_cost": 30.0,
        },
        headers=headers,
    )

    # Get daily profit
    res = test_client.get(
        f"/api/v1/daily-profit/{today}",
        headers=headers,
    )
    assert res.status_code == 200
    data = res.json()["data"]
    assert data["total_income"] == 800.0
    assert data["total_expense"] == 240.0
    assert data["total_profit"] == 560.0


def test_get_daily_profits_range(test_client):
    """Test getting daily profits for date range"""
    token = _login(test_client)
    headers = _auth(token)

    today = date.today()

    # Create income for multiple days
    for i in range(3):
        test_date = today - timedelta(days=i)
        test_client.post(
            "/api/v1/hourly-incomes",
            json={
                "employee_id": 1,
                "income_date": str(test_date),
                "hours_billed": 8.0,
                "hourly_rate": 75.0,
            },
            headers=headers,
        )

    # Get range
    res = test_client.get(
        f"/api/v1/daily-profits?date_from={today - timedelta(days=5)}&date_to={today}",
        headers=headers,
    )
    assert res.status_code == 200
    body = res.json()["data"]
    assert len(body["data"]) == 3


def test_get_project_profit(test_client):
    """Test getting project profit"""
    token = _login(test_client)
    headers = _auth(token)

    # Create project income and expense
    test_client.post(
        "/api/v1/project-incomes",
        json={
            "project_id": 1,
            "client_id": 1,
            "income_date": str(date.today()),
            "amount": 10000.0,
        },
        headers=headers,
    )

    test_client.post(
        "/api/v1/project-expenses",
        json={
            "project_id": 1,
            "expense_date": str(date.today()),
            "amount": 3000.0,
        },
        headers=headers,
    )

    # Get project profit
    res = test_client.get(
        "/api/v1/project-profit/1",
        headers=headers,
    )
    assert res.status_code == 200
    data = res.json()["data"]
    assert data["total_income"] == 10000.0
    assert data["total_expense"] == 3000.0
    assert data["total_profit"] == 7000.0


def test_get_live_profit_summary(test_client):
    """Test getting live profit summary"""
    token = _login(test_client)
    headers = _auth(token)

    # Create transactions
    test_client.post(
        "/api/v1/hourly-incomes",
        json={
            "employee_id": 1,
            "income_date": str(date.today()),
            "hours_billed": 10.0,
            "hourly_rate": 100.0,
        },
        headers=headers,
    )

    test_client.post(
        "/api/v1/hourly-expenses",
        json={
            "employee_id": 1,
            "expense_date": str(date.today()),
            "hours_worked": 10.0,
            "hourly_cost": 40.0,
        },
        headers=headers,
    )

    # Get summary
    res = test_client.get(
        "/api/v1/live-profit-summary?days=30",
        headers=headers,
    )
    assert res.status_code == 200
    data = res.json()["data"]
    assert data["total_income"] == 1000.0
    assert data["total_expense"] == 400.0
    assert data["total_profit"] == 600.0


def test_fiio_requires_auth(test_client):
    """Test that FI-IO endpoints require authentication"""
    res = test_client.get("/api/v1/hourly-incomes")
    assert res.status_code == 401
