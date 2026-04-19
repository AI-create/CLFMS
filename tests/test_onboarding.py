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


def test_create_and_manage_onboarding(test_client):
    """Test creating a client and initializing onboarding with checklist."""
    token = _login(test_client)
    headers = _auth(token)

    # Create a client
    client_res = test_client.post(
        "/api/v1/clients",
        json={
            "company_name": "Tech Solutions Inc",
            "gstin": "18AABCT1234F1Z0",
            "state": "MH",
            "address": "Mumbai",
            "contact_email": "onboarding@techsol.com",
            "contact_phone": "9876543210",
        },
        headers=headers,
    )
    assert client_res.status_code == 200, client_res.text
    client_id = client_res.json()["data"]["id"]

    # Initialize onboarding
    onboarding_res = test_client.post(
        f"/api/v1/onboarding/clients/{client_id}/init",
        json={"assigned_to": None, "notes": "Standard onboarding process"},
        headers=headers,
    )
    assert onboarding_res.status_code == 200, onboarding_res.text
    onboarding = onboarding_res.json()["data"]
    assert onboarding["status"] == "in_progress"
    assert len(onboarding["checklist_items"]) == 4  # Default items

    # Get onboarding progress
    progress_res = test_client.get(
        f"/api/v1/onboarding/clients/{client_id}/progress",
        headers=headers,
    )
    assert progress_res.status_code == 200, progress_res.text
    progress = progress_res.json()["data"]
    assert progress["total_items"] == 4
    assert progress["completed_items"] == 0
    assert progress["progress_percentage"] == 0.0

    # Mark first checklist item as complete
    checklist_items = onboarding["checklist_items"]
    first_item_id = checklist_items[0]["id"]
    
    complete_res = test_client.post(
        f"/api/v1/onboarding/checklist-items/{first_item_id}/complete",
        json={"notes": "NDA received and signed"},
        headers=headers,
    )
    assert complete_res.status_code == 200, complete_res.text
    completed_item = complete_res.json()["data"]
    assert completed_item["is_completed"] is True
    assert completed_item["notes"] == "NDA received and signed"

    # Check progress again
    progress_res = test_client.get(
        f"/api/v1/onboarding/clients/{client_id}/progress",
        headers=headers,
    )
    assert progress_res.status_code == 200
    progress = progress_res.json()["data"]
    assert progress["completed_items"] == 1
    assert progress["progress_percentage"] == 25.0

    # Mark remaining items as complete
    for item in checklist_items[1:]:
        complete_res = test_client.post(
            f"/api/v1/onboarding/checklist-items/{item['id']}/complete",
            json={"notes": f"Completed: {item['title']}"},
            headers=headers,
        )
        assert complete_res.status_code == 200

    # Check final progress - should show completed status
    progress_res = test_client.get(
        f"/api/v1/onboarding/clients/{client_id}/progress",
        headers=headers,
    )
    assert progress_res.status_code == 200
    progress = progress_res.json()["data"]
    assert progress["completed_items"] == 4
    assert progress["progress_percentage"] == 100.0
    assert progress["status"] == "completed"


def test_add_custom_checklist_item(test_client):
    """Test adding a custom checklist item."""
    token = _login(test_client)
    headers = _auth(token)

    # Create a client
    client_res = test_client.post(
        "/api/v1/clients",
        json={
            "company_name": "Custom Corp",
            "gstin": "27AABCT5678F1Z0",
            "state": "TN",
            "address": "Chennai",
            "contact_email": "custom@corp.com",
            "contact_phone": "9988776655",
        },
        headers=headers,
    )
    client_id = client_res.json()["data"]["id"]

    # Initialize onboarding
    init_res = test_client.post(
        f"/api/v1/onboarding/clients/{client_id}/init",
        json={},
        headers=headers,
    )
    assert init_res.status_code == 200

    # Add a custom checklist item
    custom_res = test_client.post(
        f"/api/v1/onboarding/clients/{client_id}/checklist",
        json={
            "item_type": "custom",
            "title": "Quarterly Business Review Setup",
            "description": "Schedule and conduct first QBR",
            "notes": "To be scheduled within 30 days",
        },
        headers=headers,
    )
    assert custom_res.status_code == 200, custom_res.text
    custom_item = custom_res.json()["data"]
    assert custom_item["item_type"] == "custom"
    assert custom_item["title"] == "Quarterly Business Review Setup"


def test_update_onboarding_status(test_client):
    """Test updating onboarding status."""
    token = _login(test_client)
    headers = _auth(token)

    # Create client and initialize onboarding
    client_res = test_client.post(
        "/api/v1/clients",
        json={
            "company_name": "Status Test Corp",
            "gstin": "06AABCT9012F1Z0",
            "state": "GJ",
            "address": "Ahmedabad",
            "contact_email": "status@corp.com",
            "contact_phone": "8899776655",
        },
        headers=headers,
    )
    client_id = client_res.json()["data"]["id"]

    init_res = test_client.post(
        f"/api/v1/onboarding/clients/{client_id}/init",
        json={"notes": "Initial setup"},
        headers=headers,
    )
    assert init_res.status_code == 200

    # Update onboarding status to on_hold
    update_res = test_client.put(
        f"/api/v1/onboarding/clients/{client_id}",
        json={"status": "on_hold", "notes": "Waiting for client approval"},
        headers=headers,
    )
    assert update_res.status_code == 200, update_res.text
    updated = update_res.json()["data"]
    assert updated["status"] == "on_hold"
    assert updated["notes"] == "Waiting for client approval"


def test_onboarding_not_found(test_client):
    """Test onboarding endpoints with non-existent client."""
    token = _login(test_client)
    headers = _auth(token)

    # Try to get onboarding for non-existent client
    res = test_client.get(
        "/api/v1/onboarding/clients/9999",
        headers=headers,
    )
    assert res.status_code == 404
    assert res.json()["success"] is False
