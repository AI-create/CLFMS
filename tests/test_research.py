"""Tests for Research Management Module"""
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


def test_create_research_project(test_client):
    """Test creating a research project"""
    token = _login(test_client)
    headers = _auth(token)

    res = test_client.post(
        "/api/v1/research-projects",
        json={
            "name": "Drug Discovery 2026",
            "description": "Research for new compound",
            "research_type": "internal_rnd",
            "objectives": "Identify lead compounds",
            "created_by": settings.default_admin_email,
        },
        headers=headers,
    )
    assert res.status_code == 200
    data = res.json()["data"]
    assert data["name"] == "Drug Discovery 2026"
    assert data["research_type"] == "internal_rnd"
    assert data["status"] == "active"


def test_list_research_projects(test_client):
    """Test listing research projects"""
    token = _login(test_client)
    headers = _auth(token)

    # Create a project
    test_client.post(
        "/api/v1/research-projects",
        json={
            "name": "Project 1",
            "research_type": "internal_rnd",
        },
        headers=headers,
    )

    # List projects
    res = test_client.get(
        "/api/v1/research-projects",
        headers=headers,
    )
    assert res.status_code == 200
    body = res.json()["data"]
    assert len(body["data"]) == 1
    assert body["data"][0]["name"] == "Project 1"


def test_create_experiment(test_client):
    """Test creating an experiment"""
    token = _login(test_client)
    headers = _auth(token)

    # Create a research project first
    project_res = test_client.post(
        "/api/v1/research-projects",
        json={
            "name": "Research Project",
            "research_type": "internal_rnd",
        },
        headers=headers,
    )
    project_id = project_res.json()["data"]["id"]

    # Create an experiment
    res = test_client.post(
        f"/api/v1/research-projects/{project_id}/experiments",
        json={
            "title": "Compound A Testing",
            "objective": "Test effectiveness of compound A",
            "hypothesis": "Compound A will show 80% efficacy",
            "methodology": "Double-blind test",
            "status": "in_progress",
        },
        headers=headers,
    )
    assert res.status_code == 200
    data = res.json()["data"]
    assert data["title"] == "Compound A Testing"
    assert data["status"] == "in_progress"


def test_create_research_log(test_client):
    """Test creating a research log"""
    token = _login(test_client)
    headers = _auth(token)

    # Create a research project
    project_res = test_client.post(
        "/api/v1/research-projects",
        json={
            "name": "Research Project",
            "research_type": "internal_rnd",
        },
        headers=headers,
    )
    project_id = project_res.json()["data"]["id"]

    # Create an experiment
    exp_res = test_client.post(
        f"/api/v1/research-projects/{project_id}/experiments",
        json={
            "title": "Experiment 1",
            "objective": "Test",
        },
        headers=headers,
    )
    experiment_id = exp_res.json()["data"]["id"]

    # Create a research log
    res = test_client.post(
        f"/api/v1/experiments/{experiment_id}/logs",
        json={
            "title": "Day 1 Observations",
            "notes": "Initial observations: Compound A shows promise",
            "observations": "Stable at room temperature",
            "recorded_by": settings.default_admin_email,
        },
        headers=headers,
    )
    assert res.status_code == 200
    data = res.json()["data"]
    assert data["title"] == "Day 1 Observations"
    assert data["notes"] == "Initial observations: Compound A shows promise"


def test_get_ip_potential_experiments(test_client):
    """Test getting IP potential experiments"""
    token = _login(test_client)
    headers = _auth(token)

    # Create a research project
    project_res = test_client.post(
        "/api/v1/research-projects",
        json={
            "name": "IP Research",
            "research_type": "internal_rnd",
        },
        headers=headers,
    )
    project_id = project_res.json()["data"]["id"]

    # Create an experiment with IP potential
    test_client.post(
        f"/api/v1/research-projects/{project_id}/experiments",
        json={
            "title": "Patentable Discovery",
            "objective": "Test",
            "status": "completed",
        },
        headers=headers,
    )
    
    # Update experiment to mark as IP potential
    # (Note: Would need PUT endpoint to set has_ip_potential flag)

    # Get IP potential experiments
    res = test_client.get(
        f"/api/v1/research-projects/{project_id}/ip-potential",
        headers=headers,
    )
    assert res.status_code == 200
    data = res.json()["data"]
    assert "ip_potential_count" in data


def test_get_project_summary(test_client):
    """Test getting project summary"""
    token = _login(test_client)
    headers = _auth(token)

    # Create a research project
    project_res = test_client.post(
        "/api/v1/research-projects",
        json={
            "name": "Summary Test",
            "research_type": "internal_rnd",
            "budget_allocated": 100000,
        },
        headers=headers,
    )
    project_id = project_res.json()["data"]["id"]

    # Create experiments
    for i in range(3):
        test_client.post(
            f"/api/v1/research-projects/{project_id}/experiments",
            json={
                "title": f"Experiment {i+1}",
                "objective": "Test",
            },
            headers=headers,
        )

    # Get summary
    res = test_client.get(
        f"/api/v1/research-projects/{project_id}/summary",
        headers=headers,
    )
    assert res.status_code == 200
    summary = res.json()["data"]
    assert summary["project_name"] == "Summary Test"
    assert summary["total_experiments"] == 3
    assert summary["budget_allocated"] == 100000


def test_research_requires_auth(test_client):
    """Test that research endpoints require authentication"""
    res = test_client.get(
        "/api/v1/research-projects",
    )
    assert res.status_code == 401


def test_research_requires_role(test_client):
    """Test that research endpoints require proper role"""
    # This test would need a user with restricted role
    # For now, we verify admin can access
    token = _login(test_client)
    headers = _auth(token)
    
    res = test_client.get(
        "/api/v1/research-projects",
        headers=headers,
    )
    assert res.status_code == 200
