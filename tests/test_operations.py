"""Tests for Operations Management Module"""
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


def test_create_employee(test_client):
    """Test creating an employee"""
    token = _login(test_client)
    headers = _auth(token)

    res = test_client.post(
        "/api/v1/employees",
        json={
            "email": "john@company.com",
            "name": "John Doe",
            "employee_id": "EMP001",
            "department": "Engineering",
            "designation": "Senior Developer",
            "hourly_rate": 75.0,
            "date_of_joining": "2023-01-15",
        },
        headers=headers,
    )
    assert res.status_code == 200
    data = res.json()["data"]
    assert data["name"] == "John Doe"
    assert data["email"] == "john@company.com"
    assert data["status"] == "active"


def test_list_employees(test_client):
    """Test listing employees"""
    token = _login(test_client)
    headers = _auth(token)

    # Create employees
    for i in range(3):
        test_client.post(
            "/api/v1/employees",
            json={
                "email": f"emp{i}@company.com",
                "name": f"Employee {i}",
                "employee_id": f"EMP{i:03d}",
                "department": "Engineering",
            },
            headers=headers,
        )

    # List employees
    res = test_client.get(
        "/api/v1/employees",
        headers=headers,
    )
    assert res.status_code == 200
    body = res.json()["data"]
    assert len(body["data"]) == 3


def test_create_activity(test_client):
    """Test creating an activity"""
    token = _login(test_client)
    headers = _auth(token)

    # Create employee
    emp_res = test_client.post(
        "/api/v1/employees",
        json={
            "email": "dev@company.com",
            "name": "Developer",
            "employee_id": "EMP001",
        },
        headers=headers,
    )
    emp_id = emp_res.json()["data"]["id"]

    # Create activity
    res = test_client.post(
        f"/api/v1/employees/{emp_id}/activities",
        json={
            "activity_date": str(date.today()),
            "title": "Backend API Development",
            "description": "Working on user authentication module",
            "hours_spent": 8.5,
            "billable": True,
        },
        headers=headers,
    )
    assert res.status_code == 200
    data = res.json()["data"]
    assert data["title"] == "Backend API Development"
    assert data["hours_spent"] == 8.5
    assert data["status"] == "in_progress"


def test_list_activities_for_employee(test_client):
    """Test listing activities for employee"""
    token = _login(test_client)
    headers = _auth(token)

    # Create employee
    emp_res = test_client.post(
        "/api/v1/employees",
        json={"email": "emp@company.com", "name": "Developer", "employee_id": "EMP001"},
        headers=headers,
    )
    emp_id = emp_res.json()["data"]["id"]

    # Create activities
    for i in range(2):
        test_client.post(
            f"/api/v1/employees/{emp_id}/activities",
            json={
                "activity_date": str(date.today()),
                "title": f"Activity {i}",
                "hours_spent": 4.0,
            },
            headers=headers,
        )

    # List activities
    res = test_client.get(
        f"/api/v1/employees/{emp_id}/activities",
        headers=headers,
    )
    assert res.status_code == 200
    body = res.json()["data"]
    assert len(body["data"]) == 2


def test_clock_in_out(test_client):
    """Test clock-in and clock-out"""
    token = _login(test_client)
    headers = _auth(token)

    # Create employee
    emp_res = test_client.post(
        "/api/v1/employees",
        json={"email": "emp@company.com", "name": "Developer", "employee_id": "EMP001"},
        headers=headers,
    )
    emp_id = emp_res.json()["data"]["id"]

    # Clock-in
    clock_in_res = test_client.post(
        f"/api/v1/employees/{emp_id}/clock-in",
        json={"attendance_date": str(date.today())},
        headers=headers,
    )
    assert clock_in_res.status_code == 200
    attendance_data = clock_in_res.json()["data"]
    assert attendance_data["status"] == "clocked_in"
    assert attendance_data["clock_out_time"] is None

    # Clock-out
    clock_out_res = test_client.post(
        f"/api/v1/employees/{emp_id}/clock-out",
        json={"break_minutes": 0},
        headers=headers,
    )
    assert clock_out_res.status_code == 200
    attendance_data = clock_out_res.json()["data"]
    assert attendance_data["status"] == "clocked_out"
    assert attendance_data["clock_out_time"] is not None
    assert attendance_data["worked_hours"] >= 0  # Can be 0 if very quick clock-in/out


def test_list_attendances(test_client):
    """Test listing attendances"""
    token = _login(test_client)
    headers = _auth(token)

    # Create employee
    emp_res = test_client.post(
        "/api/v1/employees",
        json={"email": "emp@company.com", "name": "Developer", "employee_id": "EMP001"},
        headers=headers,
    )
    emp_id = emp_res.json()["data"]["id"]

    # Clock-in and clock-out
    test_client.post(
        f"/api/v1/employees/{emp_id}/clock-in",
        json={"attendance_date": str(date.today())},
        headers=headers,
    )
    test_client.post(
        f"/api/v1/employees/{emp_id}/clock-out",
        json={"break_minutes": 0},
        headers=headers,
    )

    # List attendances
    res = test_client.get(
        f"/api/v1/employees/{emp_id}/attendances",
        headers=headers,
    )
    assert res.status_code == 200
    body = res.json()["data"]
    assert body["meta"]["total"] == 1


def test_create_task_assignment(test_client):
    """Test creating a task assignment"""
    token = _login(test_client)
    headers = _auth(token)

    # Create employee
    emp_res = test_client.post(
        "/api/v1/employees",
        json={"email": "emp@company.com", "name": "Developer", "employee_id": "EMP001"},
        headers=headers,
    )
    emp_id = emp_res.json()["data"]["id"]

    # Create task assignment
    res = test_client.post(
        "/api/v1/task-assignments",
        json={
            "title": "Build User Dashboard",
            "description": "Create responsive user dashboard",
            "assigned_to_id": emp_id,
            "priority": "high",
            "estimated_hours": 40.0,
            "due_date": str(date.today() + timedelta(days=7)),
        },
        headers=headers,
    )
    assert res.status_code == 200
    data = res.json()["data"]
    assert data["title"] == "Build User Dashboard"
    assert data["priority"] == "high"
    assert data["status"] == "assigned"


def test_list_task_assignments(test_client):
    """Test listing task assignments"""
    token = _login(test_client)
    headers = _auth(token)

    # Create employee
    emp_res = test_client.post(
        "/api/v1/employees",
        json={"email": "emp@company.com", "name": "Developer", "employee_id": "EMP001"},
        headers=headers,
    )
    emp_id = emp_res.json()["data"]["id"]

    # Create tasks
    for i in range(2):
        test_client.post(
            "/api/v1/task-assignments",
            json={
                "title": f"Task {i}",
                "assigned_to_id": emp_id,
            },
            headers=headers,
        )

    # List tasks
    res = test_client.get(
        "/api/v1/task-assignments",
        headers=headers,
    )
    assert res.status_code == 200
    body = res.json()["data"]
    assert len(body["data"]) == 2


def test_update_task_assignment(test_client):
    """Test updating task assignment status"""
    token = _login(test_client)
    headers = _auth(token)

    # Create employee
    emp_res = test_client.post(
        "/api/v1/employees",
        json={"email": "emp@company.com", "name": "Developer", "employee_id": "EMP001"},
        headers=headers,
    )
    emp_id = emp_res.json()["data"]["id"]

    # Create task
    task_res = test_client.post(
        "/api/v1/task-assignments",
        json={"title": "Task", "assigned_to_id": emp_id},
        headers=headers,
    )
    task_id = task_res.json()["data"]["id"]

    # Update task
    res = test_client.put(
        f"/api/v1/task-assignments/{task_id}",
        json={"status": "in_progress", "completed_percentage": 50},
        headers=headers,
    )
    assert res.status_code == 200
    data = res.json()["data"]
    assert data["status"] == "in_progress"
    assert data["completed_percentage"] == 50


def test_get_daily_hours(test_client):
    """Test getting daily hours for employee"""
    token = _login(test_client)
    headers = _auth(token)

    # Create employee
    emp_res = test_client.post(
        "/api/v1/employees",
        json={"email": "emp@company.com", "name": "Developer", "employee_id": "EMP001"},
        headers=headers,
    )
    emp_id = emp_res.json()["data"]["id"]

    # Create activities
    for hours in [4.0, 3.5, 2.0]:
        test_client.post(
            f"/api/v1/employees/{emp_id}/activities",
            json={
                "activity_date": str(date.today()),
                "title": f"Activity {hours}h",
                "hours_spent": hours,
                "billable": True,
            },
            headers=headers,
        )

    # Get daily hours
    res = test_client.get(
        f"/api/v1/employees/{emp_id}/daily-hours",
        headers=headers,
    )
    assert res.status_code == 200
    data = res.json()["data"]
    assert data["billable_hours"] == 9.5


def test_get_employee_summary(test_client):
    """Test getting employee monthly summary"""
    token = _login(test_client)
    headers = _auth(token)

    # Create employee
    emp_res = test_client.post(
        "/api/v1/employees",
        json={
            "email": "emp@company.com",
            "name": "Developer",
            "employee_id": "EMP001",
            "hourly_rate": 100.0,
        },
        headers=headers,
    )
    emp_id = emp_res.json()["data"]["id"]

    # Create activities
    test_client.post(
        f"/api/v1/employees/{emp_id}/activities",
        json={
            "activity_date": str(date.today()),
            "title": "Development",
            "hours_spent": 8.0,
            "billable": True,
        },
        headers=headers,
    )

    # Get summary
    today = date.today()
    res = test_client.get(
        f"/api/v1/employees/{emp_id}/summary?year={today.year}&month={today.month}",
        headers=headers,
    )
    assert res.status_code == 200
    data = res.json()["data"]
    assert data["employee_id"] == emp_id
    assert data["billable_hours"] == 8.0
    assert data["estimated_revenue"] == 800.0


def test_operations_requires_auth(test_client):
    """Test that operations endpoints require authentication"""
    res = test_client.get("/api/v1/employees")
    assert res.status_code == 401
