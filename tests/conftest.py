import os

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


import pytest


@pytest.fixture(scope="session")
def test_client() -> TestClient:
    with TestClient(app) as client:
        yield client


@pytest.fixture
def auth_headers(test_client):
    """Get authenticated headers for tests."""
    res = test_client.post(
        "/api/v1/auth/login",
        json={"email": settings.default_admin_email, "password": settings.default_admin_password},
    )
    token = res.json()["data"]["token"]
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture(autouse=True)
def cleanup_db():
    # Keep the seeded `users` table but wipe everything else between tests.
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


