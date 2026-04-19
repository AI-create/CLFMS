import pytest
from datetime import datetime


def test_create_lead(test_client, auth_headers):
    """Test creating a new lead."""
    response = test_client.post(
        "/api/v1/leads",
        json={
            "company_name": "Tech Startup Inc",
            "contact_name": "John Doe",
            "contact_email": "john@techstartup.com",
            "contact_phone": "9876543210",
            "source": "linkedin",
            "notes": "Interested in AI solutions",
        },
        headers=auth_headers,
    )
    assert response.status_code == 200, response.text
    data = response.json()
    assert data["success"] is True
    assert data["data"]["company_name"] == "Tech Startup Inc"
    assert data["data"]["status"] == "new"
    assert data["data"]["source"] == "linkedin"


def test_get_lead(test_client, auth_headers):
    """Test retrieving a lead by ID."""
    # Create lead first
    create_res = test_client.post(
        "/api/v1/leads",
        json={
            "company_name": "Test Company",
            "contact_name": "Jane Smith",
            "contact_email": "jane@testco.com",
            "contact_phone": "9999999999",
        },
        headers=auth_headers,
    )
    lead_id = create_res.json()["data"]["id"]

    # Retrieve lead
    response = test_client.get(f"/api/v1/leads/{lead_id}", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert data["data"]["id"] == lead_id
    assert data["data"]["company_name"] == "Test Company"


def test_list_leads(test_client, auth_headers):
    """Test listing leads with pagination."""
    # Create multiple leads
    for i in range(3):
        test_client.post(
            "/api/v1/leads",
            json={
                "company_name": f"Company {i}",
                "contact_name": f"Contact {i}",
                "contact_email": f"contact{i}@example.com",
                "contact_phone": "9999999999",
            },
            headers=auth_headers,
        )

    response = test_client.get(
        "/api/v1/leads?skip=0&limit=10", headers=auth_headers
    )
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert data["data"]["total"] >= 3
    assert len(data["data"]["items"]) >= 3


def test_list_leads_filter_by_status(test_client, auth_headers):
    """Test filtering leads by status."""
    # Create lead
    create_res = test_client.post(
        "/api/v1/leads",
        json={
            "company_name": "Filter Test Co",
            "contact_name": "Test Contact",
            "contact_email": "filter@test.com",
            "contact_phone": "9999999999",
            "status": "new",
        },
        headers=auth_headers,
    )
    lead_id = create_res.json()["data"]["id"]

    # Filter by status
    response = test_client.get(
        "/api/v1/leads?status=new", headers=auth_headers
    )
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    leads = data["data"]["items"]
    assert any(lead["id"] == lead_id for lead in leads)


def test_update_lead(test_client, auth_headers):
    """Test updating a lead."""
    # Create lead
    create_res = test_client.post(
        "/api/v1/leads",
        json={
            "company_name": "Original Name",
            "contact_name": "Original Contact",
            "contact_email": "original@test.com",
            "contact_phone": "9999999999",
        },
        headers=auth_headers,
    )
    lead_id = create_res.json()["data"]["id"]

    # Update lead
    response = test_client.put(
        f"/api/v1/leads/{lead_id}",
        json={"company_name": "Updated Name", "notes": "Updated notes"},
        headers=auth_headers,
    )
    assert response.status_code == 200
    data = response.json()
    assert data["data"]["company_name"] == "Updated Name"
    assert data["data"]["notes"] == "Updated notes"


def test_update_lead_status(test_client, auth_headers):
    """Test updating lead status."""
    # Create lead
    create_res = test_client.post(
        "/api/v1/leads",
        json={
            "company_name": "Status Test",
            "contact_name": "Test",
            "contact_email": "status@test.com",
            "contact_phone": "9999999999",
        },
        headers=auth_headers,
    )
    lead_id = create_res.json()["data"]["id"]

    # Update status
    response = test_client.patch(
        f"/api/v1/leads/{lead_id}/status?status=contacted",
        headers=auth_headers,
    )
    assert response.status_code == 200
    data = response.json()
    assert data["data"]["status"] == "contacted"


def test_convert_lead_to_client(test_client, auth_headers):
    """Test converting a lead to a client."""
    # Create lead
    create_res = test_client.post(
        "/api/v1/leads",
        json={
            "company_name": "Conversion Test Inc",
            "contact_name": "John Converter",
            "contact_email": "john@convertest.com",
            "contact_phone": "9876543210",
        },
        headers=auth_headers,
    )
    lead_id = create_res.json()["data"]["id"]

    # Convert to client
    response = test_client.post(
        f"/api/v1/leads/{lead_id}/convert-to-client",
        json={
            "gstin": "29ABCDE1234F1Z5",
            "state": "KA",
            "address": "Bangalore",
        },
        headers=auth_headers,
    )
    assert response.status_code == 200
    data = response.json()
    assert data["data"]["lead"]["status"] == "won"
    assert data["data"]["lead"]["converted_client_id"] is not None
    assert data["data"]["client_id"] is not None


def test_delete_lead(test_client, auth_headers):
    """Test deleting a lead."""
    # Create lead
    create_res = test_client.post(
        "/api/v1/leads",
        json={
            "company_name": "Delete Test",
            "contact_name": "Test",
            "contact_email": "delete@test.com",
            "contact_phone": "9999999999",
        },
        headers=auth_headers,
    )
    lead_id = create_res.json()["data"]["id"]

    # Delete lead
    response = test_client.delete(f"/api/v1/leads/{lead_id}", headers=auth_headers)
    assert response.status_code == 200
    assert response.json()["success"] is True

    # Verify deleted
    get_res = test_client.get(f"/api/v1/leads/{lead_id}", headers=auth_headers)
    assert get_res.status_code == 404


def test_create_follow_up(test_client, auth_headers):
    """Test creating a follow-up for a lead."""
    # Create lead
    create_res = test_client.post(
        "/api/v1/leads",
        json={
            "company_name": "Follow-up Test",
            "contact_name": "Test",
            "contact_email": "followup@test.com",
            "contact_phone": "9999999999",
        },
        headers=auth_headers,
    )
    lead_id = create_res.json()["data"]["id"]

    # Create follow-up
    response = test_client.post(
        f"/api/v1/leads/{lead_id}/follow-ups",
        json={
            "action": "Send proposal",
            "notes": "Follow up after 2 days",
        },
        headers=auth_headers,
    )
    assert response.status_code == 200
    data = response.json()
    assert data["data"]["action"] == "Send proposal"
    assert data["data"]["lead_id"] == lead_id


def test_get_lead_follow_ups(test_client, auth_headers):
    """Test retrieving follow-ups for a lead."""
    # Create lead
    create_res = test_client.post(
        "/api/v1/leads",
        json={
            "company_name": "Follow-ups List Test",
            "contact_name": "Test",
            "contact_email": "followups@test.com",
            "contact_phone": "9999999999",
        },
        headers=auth_headers,
    )
    lead_id = create_res.json()["data"]["id"]

    # Create multiple follow-ups
    for i in range(2):
        test_client.post(
            f"/api/v1/leads/{lead_id}/follow-ups",
            json={
                "action": f"Action {i}",
                "notes": f"Notes {i}",
            },
            headers=auth_headers,
        )

    # Get follow-ups
    response = test_client.get(
        f"/api/v1/leads/{lead_id}/follow-ups", headers=auth_headers
    )
    assert response.status_code == 200
    data = response.json()
    assert len(data["data"]["follow_ups"]) >= 2


def test_update_follow_up(test_client, auth_headers):
    """Test updating a follow-up."""
    # Create lead and follow-up
    create_res = test_client.post(
        "/api/v1/leads",
        json={
            "company_name": "Update Follow-up Test",
            "contact_name": "Test",
            "contact_email": "updatefu@test.com",
            "contact_phone": "9999999999",
        },
        headers=auth_headers,
    )
    lead_id = create_res.json()["data"]["id"]

    fu_res = test_client.post(
        f"/api/v1/leads/{lead_id}/follow-ups",
        json={"action": "Original action"},
        headers=auth_headers,
    )
    follow_up_id = fu_res.json()["data"]["id"]

    # Update follow-up
    response = test_client.put(
        f"/api/v1/leads/follow-ups/{follow_up_id}",
        json={"action": "Updated action", "notes": "Updated notes"},
        headers=auth_headers,
    )
    assert response.status_code == 200
    data = response.json()
    assert data["data"]["action"] == "Updated action"


def test_complete_follow_up(test_client, auth_headers):
    """Test marking a follow-up as completed."""
    # Create lead and follow-up
    create_res = test_client.post(
        "/api/v1/leads",
        json={
            "company_name": "Complete Follow-up Test",
            "contact_name": "Test",
            "contact_email": "completefu@test.com",
            "contact_phone": "9999999999",
        },
        headers=auth_headers,
    )
    lead_id = create_res.json()["data"]["id"]

    fu_res = test_client.post(
        f"/api/v1/leads/{lead_id}/follow-ups",
        json={"action": "Complete me"},
        headers=auth_headers,
    )
    follow_up_id = fu_res.json()["data"]["id"]

    # Complete follow-up
    response = test_client.patch(
        f"/api/v1/leads/follow-ups/{follow_up_id}/complete",
        headers=auth_headers,
    )
    assert response.status_code == 200
    data = response.json()
    assert data["data"]["completed_date"] is not None
