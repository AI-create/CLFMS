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


def test_project_closure_flow(test_client):
    """Test complete project closure flow."""
    token = _login(test_client)
    headers = _auth(token)

    # Create a client
    client_res = test_client.post(
        "/api/v1/clients",
        json={
            "company_name": "Closure Test Corp",
            "gstin": "09AABCT1234F1Z0",
            "state": "DL",
            "address": "Delhi",
            "contact_email": "closure@corp.com",
            "contact_phone": "9011223344",
        },
        headers=headers,
    )
    client_id = client_res.json()["data"]["id"]

    # Create a project
    project_res = test_client.post(
        "/api/v1/projects",
        json={
            "client_id": client_id,
            "name": "Closure Project",
            "status": "active",
            "start_date": "2026-04-01",
        },
        headers=headers,
    )
    project_id = project_res.json()["data"]["id"]

    # Initiate closure
    closure_res = test_client.post(
        f"/api/v1/closure/projects/{project_id}/initiate",
        json={
            "deliverables_description": "Complete web application with all features",
            "closure_notes": "Project completed on time",
        },
        headers=headers,
    )
    assert closure_res.status_code == 200, closure_res.text
    closure = closure_res.json()["data"]
    assert closure["status"] == "in_progress"
    assert len(closure["closure_items"]) == 6  # Default items

    # Get closure progress
    progress_res = test_client.get(
        f"/api/v1/closure/projects/{project_id}/progress",
        headers=headers,
    )
    assert progress_res.status_code == 200
    progress = progress_res.json()["data"]
    assert progress["total_items"] == 6
    assert progress["completed_items"] == 0
    assert progress["progress_percentage"] == 0.0

    # Mark deliverables as complete
    deliv_res = test_client.post(
        f"/api/v1/closure/projects/{project_id}/mark-deliverables-complete",
        json={"notes": "All deliverables accepted by client"},
        headers=headers,
    )
    assert deliv_res.status_code == 200
    assert deliv_res.json()["data"]["deliverables_completed"] is True

    # Mark payment received
    payment_res = test_client.post(
        f"/api/v1/closure/projects/{project_id}/mark-payment-received",
        json={"amount": 50000.0, "notes": "Final payment received"},
        headers=headers,
    )
    assert payment_res.status_code == 200
    assert payment_res.json()["data"]["final_payment_received"] is True

    # Complete closure checklist items
    checklist_items = closure["closure_items"]
    for item in checklist_items[:3]:
        complete_res = test_client.post(
            f"/api/v1/closure/checklist-items/{item['id']}/complete",
            json={"notes": f"Completed: {item['title']}"},
            headers=headers,
        )
        assert complete_res.status_code == 200

    # Mark closure as completed
    complete_res = test_client.post(
        f"/api/v1/closure/projects/{project_id}/mark-completed",
        json={},
        headers=headers,
    )
    assert complete_res.status_code == 200
    assert complete_res.json()["data"]["status"] == "completed"

    # Archive project
    archive_res = test_client.post(
        f"/api/v1/closure/projects/{project_id}/archive",
        json={"reason": "Project successfully delivered and archived"},
        headers=headers,
    )
    assert archive_res.status_code == 200
    assert archive_res.json()["data"]["status"] == "archived"


def test_add_custom_closure_item(test_client):
    """Test adding custom closure checklist items."""
    token = _login(test_client)
    headers = _auth(token)

    # Create client and project
    client_res = test_client.post(
        "/api/v1/clients",
        json={
            "company_name": "Custom Closure Corp",
            "gstin": "08AABCT5678F1Z0",
            "state": "RJ",
            "address": "Jaipur",
            "contact_email": "custom@closure.com",
            "contact_phone": "9922334455",
        },
        headers=headers,
    )
    client_id = client_res.json()["data"]["id"]

    project_res = test_client.post(
        "/api/v1/projects",
        json={
            "client_id": client_id,
            "name": "Custom Closure Project",
            "status": "active",
            "start_date": "2026-04-05",
        },
        headers=headers,
    )
    project_id = project_res.json()["data"]["id"]

    # Initiate closure
    init_res = test_client.post(
        f"/api/v1/closure/projects/{project_id}/initiate",
        json={},
        headers=headers,
    )
    assert init_res.status_code == 200

    # Add custom checklist item
    custom_res = test_client.post(
        f"/api/v1/closure/projects/{project_id}/checklist",
        json={
            "title": "Security Audit Completion",
            "description": "Complete security audit and address findings",
            "notes": "Due before project sign-off",
        },
        headers=headers,
    )
    assert custom_res.status_code == 200, custom_res.text
    custom_item = custom_res.json()["data"]
    assert custom_item["title"] == "Security Audit Completion"


def test_closure_update(test_client):
    """Test updating closure record."""
    token = _login(test_client)
    headers = _auth(token)

    # Setup
    client_res = test_client.post(
        "/api/v1/clients",
        json={
            "company_name": "Update Closure Corp",
            "gstin": "07AABCT9012F1Z0",
            "state": "UP",
            "address": "Lucknow",
            "contact_email": "update@closure.com",
            "contact_phone": "8833445566",
        },
        headers=headers,
    )
    client_id = client_res.json()["data"]["id"]

    project_res = test_client.post(
        "/api/v1/projects",
        json={
            "client_id": client_id,
            "name": "Update Closure Project",
            "status": "active",
            "start_date": "2026-04-10",
        },
        headers=headers,
    )
    project_id = project_res.json()["data"]["id"]

    init_res = test_client.post(
        f"/api/v1/closure/projects/{project_id}/initiate",
        json={},
        headers=headers,
    )
    assert init_res.status_code == 200

    # Update closure record
    update_res = test_client.put(
        f"/api/v1/closure/projects/{project_id}",
        json={
            "status": "on_hold",
            "client_feedback": "Waiting for final sign-off",
            "client_satisfaction_rating": 5,
        },
        headers=headers,
    )
    assert update_res.status_code == 200, update_res.text
    updated = update_res.json()["data"]
    assert updated["status"] == "on_hold"
    assert updated["client_satisfaction_rating"] == 5


def test_closure_not_found(test_client):
    """Test closure endpoints with non-existent project."""
    token = _login(test_client)
    headers = _auth(token)

    # Try to get closure for non-existent project
    res = test_client.get(
        "/api/v1/closure/projects/9999",
        headers=headers,
    )
    assert res.status_code == 404
    assert res.json()["success"] is False


def test_closure_checklist_operations(test_client):
    """Test closure checklist item operations."""
    token = _login(test_client)
    headers = _auth(token)

    # Setup project
    client_res = test_client.post(
        "/api/v1/clients",
        json={
            "company_name": "Checklist Closure Corp",
            "gstin": "10AABCT3456F1Z0",
            "state": "MP",
            "address": "Bhopal",
            "contact_email": "checklist@closure.com",
            "contact_phone": "7744556677",
        },
        headers=headers,
    )
    client_id = client_res.json()["data"]["id"]

    project_res = test_client.post(
        "/api/v1/projects",
        json={
            "client_id": client_id,
            "name": "Checklist Project",
            "status": "active",
            "start_date": "2026-04-12",
        },
        headers=headers,
    )
    project_id = project_res.json()["data"]["id"]

    init_res = test_client.post(
        f"/api/v1/closure/projects/{project_id}/initiate",
        json={},
        headers=headers,
    )
    closure = init_res.json()["data"]
    first_item_id = closure["closure_items"][0]["id"]

    # Get checklist items
    items_res = test_client.get(
        f"/api/v1/closure/projects/{project_id}/checklist",
        headers=headers,
    )
    assert items_res.status_code == 200
    assert len(items_res.json()["data"]["items"]) == 6

    # Get single item
    item_res = test_client.get(
        f"/api/v1/closure/checklist-items/{first_item_id}",
        headers=headers,
    )
    assert item_res.status_code == 200
    assert item_res.json()["data"]["id"] == first_item_id

    # Update item
    update_res = test_client.put(
        f"/api/v1/closure/checklist-items/{first_item_id}",
        json={"title": "Updated Title", "is_completed": True},
        headers=headers,
    )
    assert update_res.status_code == 200
    assert update_res.json()["data"]["title"] == "Updated Title"

    # Delete item
    delete_res = test_client.delete(
        f"/api/v1/closure/checklist-items/{first_item_id}",
        headers=headers,
    )
    assert delete_res.status_code == 200
