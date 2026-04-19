import io
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


def test_upload_file(test_client):
    """Test file upload."""
    token = _login(test_client)
    headers = _auth(token)

    # Create test file
    file_content = b"This is a test document content for CLFMS"
    file = io.BytesIO(file_content)

    # Upload file
    response = test_client.post(
        "/api/v1/files/upload?file_type=document&description=Test%20document%20for%20CLFMS",
        files={"file": ("test_document.txt", file, "text/plain")},
        headers=headers,
    )

    assert response.status_code == 200, response.text
    data = response.json()
    assert data["success"] is True
    file_obj = data["data"]
    assert file_obj["file_name"] == "test_document.txt"
    assert file_obj["file_type"] == "document"
    assert file_obj["description"] == "Test document for CLFMS"
    assert file_obj["file_size"] > 0
    assert file_obj["mime_type"] == "text/plain"
    assert file_obj["virus_scan_status"] == "pending"


def test_upload_with_entity_reference(test_client):
    """Test uploading file linked to an entity."""
    token = _login(test_client)
    headers = _auth(token)

    # Create client first
    client_res = test_client.post(
        "/api/v1/clients",
        json={
            "company_name": "File Test Corp",
            "gstin": "09AABCT5555F1Z0",
            "state": "DL",
            "address": "Delhi",
            "contact_email": "files@test.com",
            "contact_phone": "9999999999",
        },
        headers=headers,
    )
    client_id = client_res.json()["data"]["id"]

    # Upload KYC document linked to client
    file_content = b"KYC Document Content"
    file = io.BytesIO(file_content)

    response = test_client.post(
        f"/api/v1/files/upload?file_type=kyc&entity_type=client&entity_id={client_id}&description=Client%20KYC%20Document",
        files={"file": ("kyc_document.pdf", file, "application/pdf")},
        headers=headers,
    )

    assert response.status_code == 200
    file_obj = response.json()["data"]
    assert file_obj["entity_type"] == "client"
    assert file_obj["entity_id"] == client_id
    assert file_obj["file_type"] == "kyc"


def test_list_files(test_client):
    """Test listing files."""
    token = _login(test_client)
    headers = _auth(token)

    # Upload multiple files
    for i in range(3):
        file_content = f"Test file {i}".encode()
        file = io.BytesIO(file_content)
        test_client.post(
            "/api/v1/files/upload?file_type=document",
            files={"file": (f"file_{i}.txt", file, "text/plain")},
            headers=headers,
        )

    # List files
    response = test_client.get(
        "/api/v1/files?skip=0&limit=10",
        headers=headers,
    )

    assert response.status_code == 200
    data = response.json()["data"]
    assert data["total"] >= 3
    assert len(data["files"]) >= 3


def test_get_file_metadata(test_client):
    """Test getting file metadata."""
    token = _login(test_client)
    headers = _auth(token)

    # Upload file
    file_content = b"Metadata test content"
    file = io.BytesIO(file_content)

    upload_res = test_client.post(
        "/api/v1/files/upload?file_type=document",
        files={"file": ("metadata_test.txt", file, "text/plain")},
        headers=headers,
    )
    file_id = upload_res.json()["data"]["id"]

    # Get metadata
    response = test_client.get(
        f"/api/v1/files/{file_id}/metadata",
        headers=headers,
    )

    assert response.status_code == 200
    metadata = response.json()["data"]
    assert metadata["id"] == file_id
    assert metadata["file_name"] == "metadata_test.txt"
    assert metadata["file_type"] == "document"
    assert metadata["version_count"] == 0


def test_get_file_details(test_client):
    """Test getting complete file details."""
    token = _login(test_client)
    headers = _auth(token)

    # Upload file
    file_content = b"File details test"
    file = io.BytesIO(file_content)

    upload_res = test_client.post(
        "/api/v1/files/upload?file_type=document&description=Test%20details",
        files={"file": ("details.txt", file, "text/plain")},
        headers=headers,
    )
    file_id = upload_res.json()["data"]["id"]

    # Get file details
    response = test_client.get(
        f"/api/v1/files/{file_id}",
        headers=headers,
    )

    assert response.status_code == 200
    file_obj = response.json()["data"]
    assert file_obj["id"] == file_id
    assert file_obj["description"] == "Test details"
    assert file_obj["versions"] == []


def test_update_file_metadata(test_client):
    """Test updating file metadata."""
    token = _login(test_client)
    headers = _auth(token)

    # Upload file
    file_content = b"Update test"
    file = io.BytesIO(file_content)

    upload_res = test_client.post(
        "/api/v1/files/upload?file_type=document",
        files={"file": ("update_test.txt", file, "text/plain")},
        headers=headers,
    )
    file_id = upload_res.json()["data"]["id"]

    # Update metadata
    response = test_client.put(
        f"/api/v1/files/{file_id}",
        json={
            "description": "Updated description",
            "file_type": "report"
        },
        headers=headers,
    )

    assert response.status_code == 200
    updated = response.json()["data"]
    assert updated["description"] == "Updated description"
    assert updated["file_type"] == "report"


def test_delete_file(test_client):
    """Test soft delete file."""
    token = _login(test_client)
    headers = _auth(token)

    # Upload file
    file_content = b"Delete test"
    file = io.BytesIO(file_content)

    upload_res = test_client.post(
        "/api/v1/files/upload?file_type=document",
        files={"file": ("delete_test.txt", file, "text/plain")},
        headers=headers,
    )
    file_id = upload_res.json()["data"]["id"]

    # Delete file
    delete_res = test_client.delete(
        f"/api/v1/files/{file_id}",
        headers=headers,
    )
    assert delete_res.status_code == 200

    # Try to get deleted file (should not found as soft delete)
    get_res = test_client.get(
        f"/api/v1/files/{file_id}",
        headers=headers,
    )
    assert get_res.status_code == 404


def test_create_file_version(test_client):
    """Test creating a new version of a file."""
    token = _login(test_client)
    headers = _auth(token)

    # Upload initial file
    file_content = b"Version 1 content"
    file = io.BytesIO(file_content)

    upload_res = test_client.post(
        "/api/v1/files/upload?file_type=document",
        files={"file": ("versioned_file.txt", file, "text/plain")},
        headers=headers,
    )
    file_id = upload_res.json()["data"]["id"]

    # Create new version
    new_content = b"Version 2 content - updated"
    new_file = io.BytesIO(new_content)

    version_res = test_client.post(
        f"/api/v1/files/{file_id}/new-version",
        files={"file": ("versioned_file.txt", new_file, "text/plain")},
        data={
            "change_notes": "Updated content with corrections"
        },
        headers=headers,
    )

    assert version_res.status_code == 200
    result = version_res.json()["data"]
    assert "file" in result
    assert "new_version" in result
    assert result["new_version"]["version_number"] == 1


def test_get_file_versions(test_client):
    """Test getting all versions of a file."""
    token = _login(test_client)
    headers = _auth(token)

    # Upload initial file
    file_content = b"Initial content"
    file = io.BytesIO(file_content)

    upload_res = test_client.post(
        "/api/v1/files/upload?file_type=document",
        files={"file": ("versions_test.txt", file, "text/plain")},
        headers=headers,
    )
    file_id = upload_res.json()["data"]["id"]

    # Create 2 versions
    for i in range(2):
        content = f"Version {i+2} content".encode()
        new_file = io.BytesIO(content)
        test_client.post(
            f"/api/v1/files/{file_id}/new-version",
            files={"file": ("versions_test.txt", new_file, "text/plain")},
            data={"change_notes": f"Update {i+1}"},
            headers=headers,
        )

    # Get versions
    response = test_client.get(
        f"/api/v1/files/{file_id}/versions",
        headers=headers,
    )

    assert response.status_code == 200
    data = response.json()["data"]
    assert data["file_id"] == file_id
    assert data["version_count"] == 2
    assert len(data["versions"]) == 2


def test_restore_file_version(test_client):
    """Test restoring file to previous version."""
    token = _login(test_client)
    headers = _auth(token)

    # Upload initial file
    file_content = b"Original content"
    file = io.BytesIO(file_content)

    upload_res = test_client.post(
        "/api/v1/files/upload?file_type=document",
        files={"file": ("restore_test.txt", file, "text/plain")},
        headers=headers,
    )
    file_id = upload_res.json()["data"]["id"]

    # Create version 1
    new_content = b"Modified content v1"
    new_file = io.BytesIO(new_content)
    test_client.post(
        f"/api/v1/files/{file_id}/new-version",
        files={"file": ("restore_test.txt", new_file, "text/plain")},
        data={"change_notes": "First update"},
        headers=headers,
    )

    # Restore to version 1 (should backup current and restore v1)
    restore_res = test_client.post(
        f"/api/v1/files/{file_id}/restore-version",
        json={
            "version_number": 1,
            "restore_notes": "Restoring to previous stable version"
        },
        headers=headers,
    )

    assert restore_res.status_code == 200
    restored_file = restore_res.json()["data"]
    assert restored_file["id"] == file_id


def test_list_files_with_filters(test_client):
    """Test listing files with various filters."""
    token = _login(test_client)
    headers = _auth(token)

    # Create client
    client_res = test_client.post(
        "/api/v1/clients",
        json={
            "company_name": "Filter Test Corp",
            "gstin": "10AABCT6666F1Z0",
            "state": "RJ",
            "address": "Jaipur",
            "contact_email": "filter@test.com",
            "contact_phone": "8888888888",
        },
        headers=headers,
    )
    client_id = client_res.json()["data"]["id"]

    # Upload documents
    file_types = ["document", "kyc", "agreement"]
    for file_type in file_types:
        content = f"File of type {file_type}".encode()
        file = io.BytesIO(content)
        test_client.post(
            f"/api/v1/files/upload?file_type={file_type}&entity_type=client&entity_id={client_id}",
            files={"file": (f"{file_type}_file.txt", file, "text/plain")},
            headers=headers,
        )

    # Filter by file_type
    response = test_client.get(
        "/api/v1/files?file_type=kyc",
        headers=headers,
    )
    assert response.status_code == 200
    data = response.json()["data"]
    assert len(data["files"]) >= 1
    assert all(f["file_type"] == "kyc" for f in data["files"])

    # Filter by entity
    response = test_client.get(
        f"/api/v1/files?entity_type=client&entity_id={client_id}",
        headers=headers,
    )
    assert response.status_code == 200
    data = response.json()["data"]
    assert len(data["files"]) >= 3


def test_invalid_file_type(test_client):
    """Test uploading file with invalid extension."""
    token = _login(test_client)
    headers = _auth(token)

    file_content = b"Invalid file content"
    file = io.BytesIO(file_content)

    response = test_client.post(
        "/api/v1/files/upload?file_type=document",
        files={"file": ("invalid_file.exe", file, "application/x-msdownload")},
        headers=headers,
    )

    assert response.status_code == 400
    resp_data = response.json()
    # Response could have "detail" key or "error" -> "message"
    message = resp_data.get("detail", resp_data.get("error", {}).get("message", ""))
    assert "not allowed" in message.lower()


def test_file_not_found(test_client):
    """Test accessing non-existent file."""
    token = _login(test_client)
    headers = _auth(token)

    response = test_client.get(
        "/api/v1/files/9999/metadata",
        headers=headers,
    )

    assert response.status_code == 404
    assert response.json()["success"] is False


def test_upload_requires_auth(test_client):
    """Test that file upload requires authentication."""
    file_content = b"Test content"
    file = io.BytesIO(file_content)

    response = test_client.post(
        "/api/v1/files/upload",
        files={"file": ("test.txt", file, "text/plain")},
        data={"file_type": "document"},
    )

    assert response.status_code in [401, 403]
