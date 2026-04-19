from datetime import datetime, timedelta
from app.core.security import create_access_token
from app.core.config import settings


def _login(client):
    res = client.post(
        "/api/v1/auth/login",
        json={"email": settings.default_admin_email, "password": settings.default_admin_password},
    )
    assert res.status_code == 200, res.text
    body = res.json()
    assert body["success"] is True
    return body["data"]["token"]


def _auth(token: str) -> dict:
    return {"Authorization": f"Bearer {token}"}


def test_activity_log_creation(test_client):
    """Test creating activity logs through API."""
    token = _login(test_client)
    headers = _auth(token)

    # Create a client (this should be logged)
    client_res = test_client.post(
        "/api/v1/clients",
        json={
            "company_name": "Activity Test Corp",
            "gstin": "09AABCT1111F1Z0",
            "state": "DL",
            "address": "Delhi",
            "contact_email": "activity@test.com",
            "contact_phone": "9011223344",
        },
        headers=headers,
    )
    assert client_res.status_code == 200
    
    # Check that activity was logged
    logs_res = test_client.get(
        "/api/v1/activity-logs?entity_type=client&limit=10",
        headers=headers,
    )
    assert logs_res.status_code == 200
    logs = logs_res.json()["data"]["logs"]
    # There should be at least one log for client creation
    assert len(logs) > 0


def test_get_activity_logs_with_filters(test_client):
    """Test querying activity logs with filters."""
    token = _login(test_client)
    headers = _auth(token)

    # Create multiple clients
    for i in range(3):
        test_client.post(
            "/api/v1/clients",
            json={
                "company_name": f"Filter Test Corp {i}",
                "gstin": f"0{i}AABCT2222F1Z0",
                "state": "DL",
                "address": "Delhi",
                "contact_email": f"filter{i}@test.com",
                "contact_phone": f"901122334{i}",
            },
            headers=headers,
        )

    # Get logs without filter
    logs_res = test_client.get(
        "/api/v1/activity-logs?limit=20",
        headers=headers,
    )
    assert logs_res.status_code == 200
    all_logs = logs_res.json()["data"]["logs"]
    assert len(all_logs) > 0

    # Filter by entity_type
    client_logs_res = test_client.get(
        "/api/v1/activity-logs?entity_type=client&limit=20",
        headers=headers,
    )
    assert client_logs_res.status_code == 200
    client_logs = client_logs_res.json()["data"]["logs"]
    assert all(log["entity_type"] == "client" for log in client_logs)
    assert len(client_logs) >= 3

    # Filter by action
    create_logs_res = test_client.get(
        "/api/v1/activity-logs?action=create&limit=20",
        headers=headers,
    )
    assert create_logs_res.status_code == 200
    create_logs = create_logs_res.json()["data"]["logs"]
    assert all(log["action"] == "create" for log in create_logs)


def test_entity_audit_trail(test_client):
    """Test getting audit trail for specific entity."""
    token = _login(test_client)
    headers = _auth(token)

    # Create a client
    client_res = test_client.post(
        "/api/v1/clients",
        json={
            "company_name": "Audit Trail Test",
            "gstin": "09AABCT3333F1Z0",
            "state": "DL",
            "address": "Delhi",
            "contact_email": "audit@test.com",
            "contact_phone": "9011223344",
        },
        headers=headers,
    )
    client_id = client_res.json()["data"]["id"]

    # Update the client
    test_client.put(
        f"/api/v1/clients/{client_id}",
        json={
            "company_name": "Audit Trail Test Updated",
            "address": "New Delhi",
        },
        headers=headers,
    )

    # Get audit trail for this client
    trail_res = test_client.get(
        f"/api/v1/activity-logs/entity/client/{client_id}",
        headers=headers,
    )
    assert trail_res.status_code == 200
    trail = trail_res.json()["data"]
    assert trail["entity_type"] == "client"
    assert trail["entity_id"] == client_id
    assert trail["modification_count"] >= 1
    assert len(trail["audit_trail"]) >= 1


def test_activity_summary(test_client):
    """Test getting activity summary."""
    token = _login(test_client)
    headers = _auth(token)

    # Perform some actions
    test_client.post(
        "/api/v1/clients",
        json={
            "company_name": "Summary Test",
            "gstin": "09AABCT4444F1Z0",
            "state": "DL",
            "address": "Delhi",
            "contact_email": "summary@test.com",
            "contact_phone": "9011223344",
        },
        headers=headers,
    )

    # Get activity summary
    summary_res = test_client.get(
        "/api/v1/activity-logs/summary/activity?days=7",
        headers=headers,
    )
    assert summary_res.status_code == 200
    summary = summary_res.json()["data"]
    assert summary["total_actions"] > 0
    assert "actions_by_type" in summary
    assert "actions_by_status" in summary
    assert "recent_logs" in summary


def test_user_activity_summary(test_client):
    """Test getting user activity summary."""
    token = _login(test_client)
    headers = _auth(token)

    # Perform an action
    test_client.post(
        "/api/v1/clients",
        json={
            "company_name": "User Summary Test",
            "gstin": "09AABCT5555F1Z0",
            "state": "DL",
            "address": "Delhi",
            "contact_email": "usersummary@test.com",
            "contact_phone": "9011223344",
        },
        headers=headers,
    )

    # Get user activity summary
    user_summary_res = test_client.get(
        f"/api/v1/activity-logs/summary/user/{settings.default_admin_email}",
        headers=headers,
    )
    assert user_summary_res.status_code == 200
    user_summary = user_summary_res.json()["data"]
    assert user_summary["user_email"] == settings.default_admin_email
    assert user_summary["total_actions"] > 0
    assert "actions_by_type" in user_summary
    assert user_summary["actions_today"] >= 0


def test_recent_activity(test_client):
    """Test getting recent activity."""
    token = _login(test_client)
    headers = _auth(token)

    # Perform an action
    test_client.post(
        "/api/v1/clients",
        json={
            "company_name": "Recent Activity Test",
            "gstin": "09AABCT6666F1Z0",
            "state": "DL",
            "address": "Delhi",
            "contact_email": "recent@test.com",
            "contact_phone": "9011223344",
        },
        headers=headers,
    )

    # Get recent activity
    recent_res = test_client.get(
        "/api/v1/activity-logs/recent?limit=20",
        headers=headers,
    )
    assert recent_res.status_code == 200
    recent = recent_res.json()["data"]
    assert recent["count"] > 0
    assert len(recent["logs"]) > 0
    # Most recent should be the client creation
    assert recent["logs"][0]["action"] == "create"


def test_failed_actions_endpoint(test_client):
    """Test getting failed actions."""
    token = _login(test_client)
    headers = _auth(token)

    # Get failed actions (should be empty or have few)
    failed_res = test_client.get(
        "/api/v1/activity-logs/failed-actions?limit=10",
        headers=headers,
    )
    assert failed_res.status_code == 200
    failed = failed_res.json()["data"]
    assert "total" in failed
    assert "logs" in failed


def test_pagination_in_activity_logs(test_client):
    """Test pagination in activity logs."""
    token = _login(test_client)
    headers = _auth(token)

    # Create multiple clients to have more logs
    for i in range(5):
        test_client.post(
            "/api/v1/clients",
            json={
                "company_name": f"Pagination Test {i}",
                "gstin": f"0{i}AABCT7777F1Z0",
                "state": "DL",
                "address": "Delhi",
                "contact_email": f"pagination{i}@test.com",
                "contact_phone": f"901122334{i}",
            },
            headers=headers,
        )

    # Get page 1 with limit 3
    page1_res = test_client.get(
        "/api/v1/activity-logs?skip=0&limit=3",
        headers=headers,
    )
    assert page1_res.status_code == 200
    page1 = page1_res.json()["data"]
    assert len(page1["logs"]) <= 3
    total = page1["total"]

    # Get page 2
    page2_res = test_client.get(
        "/api/v1/activity-logs?skip=3&limit=3",
        headers=headers,
    )
    assert page2_res.status_code == 200
    page2 = page2_res.json()["data"]
    assert page2["skip"] == 3

    # Verify different logs on different pages
    if page1["logs"] and page2["logs"]:
        page1_ids = [log["id"] for log in page1["logs"]]
        page2_ids = [log["id"] for log in page2["logs"]]
        # Pages should have different logs (unless total is 3 or less)
        if total > 3:
            assert len(set(page1_ids) & set(page2_ids)) == 0


def test_activity_log_requires_auth(test_client):
    """Test that activity log endpoints require authentication."""
    # Try to get logs without auth
    res = test_client.get("/api/v1/activity-logs")
    assert res.status_code in [401, 403]


def test_activity_log_requires_admin_role(test_client):
    """Test that cleanup requires admin role."""
    # Login as admin first to verify it works
    token = _login(test_client)
    headers = _auth(token)

    cleanup_res = test_client.post(
        "/api/v1/activity-logs/cleanup?days=90",
        headers=headers,
    )
    # Should succeed with admin role
    assert cleanup_res.status_code == 200


def test_activity_log_content_structure(test_client):
    """Test the structure of activity log entries."""
    token = _login(test_client)
    headers = _auth(token)

    # Create a client
    test_client.post(
        "/api/v1/clients",
        json={
            "company_name": "Structure Test",
            "gstin": "09AABCT8888F1Z0",
            "state": "DL",
            "address": "Delhi",
            "contact_email": "structure@test.com",
            "contact_phone": "9011223344",
        },
        headers=headers,
    )

    # Get logs
    logs_res = test_client.get(
        "/api/v1/activity-logs?limit=1",
        headers=headers,
    )
    assert logs_res.status_code == 200
    logs = logs_res.json()["data"]["logs"]
    assert len(logs) > 0
    
    log = logs[0]
    # Check required fields
    assert "id" in log
    assert "action" in log
    assert "entity_type" in log
    assert "created_at" in log
    assert "action_status" in log
    assert "user_email" in log
