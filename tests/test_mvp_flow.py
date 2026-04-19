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


def test_end_to_end_invoice_payment_finance_summary(test_client):
    token = _login(test_client)
    headers = _auth(token)

    client_res = test_client.post(
        "/api/v1/clients",
        json={
            "company_name": "ABC Pvt Ltd",
            "gstin": "29ABCDE1234F1Z5",
            "state": "KA",
            "address": "Bangalore",
            "contact_email": "acct@abc.com",
            "contact_phone": "9999999999",
        },
        headers=headers,
    )
    assert client_res.status_code == 200, client_res.text
    client_id = client_res.json()["data"]["id"]

    project_res = test_client.post(
        "/api/v1/projects",
        json={
            "client_id": client_id,
            "name": "Genome Research",
            "status": "active",
            "start_date": "2026-04-01",
        },
        headers=headers,
    )
    assert project_res.status_code == 200, project_res.text
    project_id = project_res.json()["data"]["id"]

    task_res = test_client.post(
        "/api/v1/tasks",
        json={
            "project_id": project_id,
            "title": "DNA Analysis",
            "status": "todo",
            "estimated_hours": 5,
        },
        headers=headers,
    )
    assert task_res.status_code == 200, task_res.text
    task_id = task_res.json()["data"]["id"]

    time_res = test_client.post(
        "/api/v1/time-logs",
        json={"task_id": task_id, "hours": 5, "log_date": "2026-04-16", "notes": "Lab work"},
        headers=headers,
    )
    assert time_res.status_code == 200, time_res.text

    invoice_res = test_client.post(
        "/api/v1/invoices/generate",
        json={"project_id": project_id, "type": "hourly", "rate": 20000, "due_days": 30},
        headers=headers,
    )
    assert invoice_res.status_code == 200, invoice_res.text
    invoice = invoice_res.json()["data"]
    invoice_id = invoice["id"]
    invoice_total = float(invoice["total"])
    assert invoice["status"] == "draft"

    pay_res = test_client.post(
        "/api/v1/payments",
        json={"invoice_id": invoice_id, "amount": invoice_total, "payment_date": "2026-04-16", "method": "bank_transfer"},
        headers=headers,
    )
    assert pay_res.status_code == 200, pay_res.text

    summary_res = test_client.get(f"/api/v1/finance/project/{project_id}", headers=headers)
    assert summary_res.status_code == 200, summary_res.text
    summary = summary_res.json()["data"]
    assert float(summary["profit"]) == invoice_total


def test_rbac_rejects_finance_for_sales_role(test_client):
    admin_token = _login(test_client)
    admin_headers = _auth(admin_token)

    client_res = test_client.post(
        "/api/v1/clients",
        json={"company_name": "Client X", "state": "KA"},
        headers=admin_headers,
    )
    assert client_res.status_code == 200, client_res.text
    client_id = client_res.json()["data"]["id"]

    project_res = test_client.post(
        "/api/v1/projects",
        json={"client_id": client_id, "name": "Project X", "status": "active", "start_date": "2026-04-01"},
        headers=admin_headers,
    )
    assert project_res.status_code == 200, project_res.text
    project_id = project_res.json()["data"]["id"]

    sales_token = create_access_token(subject=settings.default_admin_email, role="sales")
    sales_headers = _auth(sales_token)

    expense_res = test_client.post(
        "/api/v1/expenses",
        json={"project_id": project_id, "amount": 1000, "category": "lab_material"},
        headers=sales_headers,
    )
    assert expense_res.status_code == 403


def test_partial_payment_keeps_invoice_outstanding(test_client):
    token = _login(test_client)
    headers = _auth(token)

    client_res = test_client.post(
        "/api/v1/clients",
        json={"company_name": "Partial Pay Client", "state": "KA"},
        headers=headers,
    )
    assert client_res.status_code == 200, client_res.text
    client_id = client_res.json()["data"]["id"]

    project_res = test_client.post(
        "/api/v1/projects",
        json={"client_id": client_id, "name": "Partial Pay Project", "status": "active"},
        headers=headers,
    )
    assert project_res.status_code == 200, project_res.text
    project_id = project_res.json()["data"]["id"]

    task_res = test_client.post(
        "/api/v1/tasks",
        json={"project_id": project_id, "title": "Task A", "estimated_hours": 10},
        headers=headers,
    )
    assert task_res.status_code == 200, task_res.text
    task_id = task_res.json()["data"]["id"]

    time_res = test_client.post(
        "/api/v1/time-logs",
        json={"task_id": task_id, "hours": 10, "log_date": "2026-04-16"},
        headers=headers,
    )
    assert time_res.status_code == 200, time_res.text

    invoice_res = test_client.post(
        "/api/v1/invoices/generate",
        json={"project_id": project_id, "type": "hourly", "rate": 1000, "due_days": 30},
        headers=headers,
    )
    assert invoice_res.status_code == 200, invoice_res.text
    invoice = invoice_res.json()["data"]
    invoice_id = invoice["id"]
    invoice_total = float(invoice["total"])

    partial_amount = invoice_total / 2
    pay_res = test_client.post(
        "/api/v1/payments",
        json={"invoice_id": invoice_id, "amount": partial_amount, "payment_date": "2026-04-16", "method": "bank_transfer"},
        headers=headers,
    )
    assert pay_res.status_code == 200, pay_res.text

    invoice_get_res = test_client.get(f"/api/v1/invoices/{invoice_id}", headers=headers)
    assert invoice_get_res.status_code == 200, invoice_get_res.text
    current_invoice = invoice_get_res.json()["data"]
    assert current_invoice["status"] == "draft"

    outstanding_res = test_client.get("/api/v1/payments/outstanding", headers=headers)
    assert outstanding_res.status_code == 200, outstanding_res.text
    outstanding = outstanding_res.json()["data"]
    match = next((item for item in outstanding if item["invoice_id"] == invoice_id), None)
    assert match is not None
    assert float(match["paid_total"]) == partial_amount
    assert float(match["outstanding"]) == invoice_total - partial_amount


def test_second_payment_marks_invoice_paid_and_removes_outstanding(test_client):
    token = _login(test_client)
    headers = _auth(token)

    client_res = test_client.post(
        "/api/v1/clients",
        json={"company_name": "Full Pay Client", "state": "KA"},
        headers=headers,
    )
    client_id = client_res.json()["data"]["id"]

    project_res = test_client.post(
        "/api/v1/projects",
        json={"client_id": client_id, "name": "Full Pay Project", "status": "active"},
        headers=headers,
    )
    project_id = project_res.json()["data"]["id"]

    task_res = test_client.post(
        "/api/v1/tasks",
        json={"project_id": project_id, "title": "Task B", "estimated_hours": 4},
        headers=headers,
    )
    task_id = task_res.json()["data"]["id"]

    test_client.post(
        "/api/v1/time-logs",
        json={"task_id": task_id, "hours": 4, "log_date": "2026-04-16"},
        headers=headers,
    )

    invoice_res = test_client.post(
        "/api/v1/invoices/generate",
        json={"project_id": project_id, "type": "hourly", "rate": 5000, "due_days": 30},
        headers=headers,
    )
    invoice = invoice_res.json()["data"]
    invoice_id = invoice["id"]
    invoice_total = float(invoice["total"])

    first = invoice_total * 0.25
    second = invoice_total - first

    first_pay = test_client.post(
        "/api/v1/payments",
        json={"invoice_id": invoice_id, "amount": first, "payment_date": "2026-04-16", "method": "bank_transfer"},
        headers=headers,
    )
    assert first_pay.status_code == 200, first_pay.text

    second_pay = test_client.post(
        "/api/v1/payments",
        json={"invoice_id": invoice_id, "amount": second, "payment_date": "2026-04-17", "method": "bank_transfer"},
        headers=headers,
    )
    assert second_pay.status_code == 200, second_pay.text

    invoice_get_res = test_client.get(f"/api/v1/invoices/{invoice_id}", headers=headers)
    assert invoice_get_res.status_code == 200, invoice_get_res.text
    current_invoice = invoice_get_res.json()["data"]
    assert current_invoice["status"] == "paid"

    outstanding_res = test_client.get("/api/v1/payments/outstanding", headers=headers)
    assert outstanding_res.status_code == 200, outstanding_res.text
    outstanding = outstanding_res.json()["data"]
    assert all(item["invoice_id"] != invoice_id for item in outstanding)


def test_missing_task_returns_404_for_time_log(test_client):
    token = _login(test_client)
    headers = _auth(token)

    res = test_client.post(
        "/api/v1/time-logs",
        json={"task_id": 9999, "hours": 3, "log_date": "2026-04-16"},
        headers=headers,
    )
    assert res.status_code == 404
    body = res.json()
    assert body["success"] is False
    assert body["error"]["code"] == "NOT_FOUND"


def test_unauthenticated_requests_are_rejected(test_client):
    res = test_client.get("/api/v1/clients")
    assert res.status_code == 401


def test_invoice_send_list_filter_and_overdue_recalc(test_client):
    token = _login(test_client)
    headers = _auth(token)

    c = test_client.post("/api/v1/clients", json={"company_name": "Inv Life Client", "state": "KA"}, headers=headers).json()
    client_id = c["data"]["id"]
    p = test_client.post("/api/v1/projects", json={"client_id": client_id, "name": "Inv Life Project"}, headers=headers).json()
    project_id = p["data"]["id"]
    t = test_client.post("/api/v1/tasks", json={"project_id": project_id, "title": "Work"}, headers=headers).json()
    task_id = t["data"]["id"]
    test_client.post("/api/v1/time-logs", json={"task_id": task_id, "hours": 2}, headers=headers)

    inv_res = test_client.post(
        "/api/v1/invoices/generate",
        json={"project_id": project_id, "type": "hourly", "rate": 1000, "due_days": -1},
        headers=headers,
    )
    assert inv_res.status_code == 200, inv_res.text
    invoice_id = inv_res.json()["data"]["id"]

    sent_res = test_client.post(f"/api/v1/invoices/{invoice_id}/send", headers=headers)
    assert sent_res.status_code == 200, sent_res.text
    assert sent_res.json()["data"]["status"] == "sent"

    list_sent = test_client.get("/api/v1/invoices?status=sent", headers=headers)
    assert list_sent.status_code == 200, list_sent.text
    sent_ids = [i["id"] for i in list_sent.json()["data"]["data"]]
    assert invoice_id in sent_ids

    recalc = test_client.post("/api/v1/invoices/recalculate-overdue", headers=headers)
    assert recalc.status_code == 200, recalc.text

    inv_get = test_client.get(f"/api/v1/invoices/{invoice_id}", headers=headers)
    assert inv_get.status_code == 200, inv_get.text
    assert inv_get.json()["data"]["status"] == "overdue"


def test_dashboard_kpis_and_document_generation(test_client):
    token = _login(test_client)
    headers = _auth(token)

    c = test_client.post("/api/v1/clients", json={"company_name": "Dash Client", "state": "KA"}, headers=headers).json()
    client_id = c["data"]["id"]
    p = test_client.post("/api/v1/projects", json={"client_id": client_id, "name": "Dash Project"}, headers=headers).json()
    project_id = p["data"]["id"]

    t = test_client.post("/api/v1/tasks", json={"project_id": project_id, "title": "Work"}, headers=headers).json()
    task_id = t["data"]["id"]
    test_client.post("/api/v1/time-logs", json={"task_id": task_id, "hours": 1}, headers=headers)

    inv_res = test_client.post(
        "/api/v1/invoices/generate",
        json={"project_id": project_id, "type": "hourly", "rate": 1000, "due_days": 30},
        headers=headers,
    )
    invoice = inv_res.json()["data"]
    invoice_id = invoice["id"]
    total = float(invoice["total"])

    pay_res = test_client.post("/api/v1/payments", json={"invoice_id": invoice_id, "amount": total}, headers=headers)
    assert pay_res.status_code == 200, pay_res.text

    kpis = test_client.get("/api/v1/dashboard/kpis", headers=headers)
    assert kpis.status_code == 200, kpis.text
    kpi = kpis.json()["data"]
    assert "revenue" in kpi and "profit" in kpi and "pending_payments" in kpi and "active_projects" in kpi

    doc_res = test_client.post("/api/v1/documents/generate", json={"type": "invoice", "entity_id": invoice_id}, headers=headers)
    assert doc_res.status_code == 200, doc_res.text
    doc = doc_res.json()["data"]
    doc_id = doc["id"]

    dl = test_client.get(f"/api/v1/documents/{doc_id}/download", headers=headers)
    assert dl.status_code == 200
    assert f"Invoice {invoice['invoice_number']}".encode() in dl.content

