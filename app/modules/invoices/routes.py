from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.response import api_error, api_success
from app.core.security import require_roles
from app.modules.invoices.schemas import GenerateInvoiceRequest, InvoiceOut, UpdateInvoiceRequest
from app.modules.invoices import services as invoice_services
from app.services.activity_logging_service import log_activity
from app.services.billing_service import run_auto_billing


router = APIRouter(tags=["Invoices"])


@router.post("/invoices/generate")
def generate(
    payload: GenerateInvoiceRequest,
    db: Session = Depends(get_db),
    _user=Depends(require_roles(["admin", "finance"])),
):
    try:
        inv = invoice_services.create_invoice_from_project(db, payload)
    except ValueError:
        return api_error("NOT_FOUND", "Project not found", http_status=404)
    
    # Log the activity
    log_activity(
        db=db,
        user_email=_user.get("email"),
        action="create",
        entity_type="invoice",
        entity_id=inv.id,
        entity_name=f"Invoice {inv.invoice_number}",
        new_values={"project_id": payload.project_id},
        description=f"Generated invoice {inv.invoice_number} from project {payload.project_id}"
    )
    
    return api_success(InvoiceOut.model_validate(inv))


@router.get("/invoices/{invoice_id}")
def get_one(
    invoice_id: int,
    db: Session = Depends(get_db),
    _user=Depends(require_roles(["admin", "finance"])),
):
    inv = invoice_services.get_invoice_by_id(db, invoice_id)
    if not inv:
        return api_error("NOT_FOUND", "Invoice not found", http_status=404)
    return api_success(InvoiceOut.model_validate(inv))


@router.get("/invoices")
def list_invoices(
    status: str | None = None,
    project_id: int | None = None,
    page: int = 1,
    limit: int = 20,
    db: Session = Depends(get_db),
    _user=Depends(require_roles(["admin", "finance"])),
):
    page = max(page, 1)
    limit = min(max(limit, 1), 100)
    rows, total = invoice_services.list_invoices(db, status=status, project_id=project_id, page=page, limit=limit)
    return api_success(
        {
            "data": [InvoiceOut.model_validate(i) for i in rows],
            "meta": {"total": total, "page": page, "limit": limit},
        }
    )


@router.post("/invoices/{invoice_id}/send")
def send_invoice(
    invoice_id: int,
    db: Session = Depends(get_db),
    _user=Depends(require_roles(["admin", "finance"])),
):
    try:
        inv = invoice_services.send_invoice(db, invoice_id)
    except ValueError:
        return api_error("NOT_FOUND", "Invoice not found", http_status=404)
    
    # Log the activity
    log_activity(
        db=db,
        user_email=_user.get("email"),
        action="send",
        entity_type="invoice",
        entity_id=invoice_id,
        entity_name=f"Invoice {inv.invoice_number}",
        description=f"Sent invoice {inv.invoice_number}"
    )
    
    return api_success(InvoiceOut.model_validate(inv))


@router.post("/invoices/{invoice_id}/mark-paid")
def mark_paid(
    invoice_id: int,
    db: Session = Depends(get_db),
    _user=Depends(require_roles(["admin"])),
):
    # Admin override. Normal flow should go through /payments.
    try:
        inv = invoice_services.mark_invoice_paid(db, invoice_id)
    except ValueError:
        return api_error("NOT_FOUND", "Invoice not found", http_status=404)
    
    # Log the activity
    log_activity(
        db=db,
        user_email=_user.get("email"),
        action="update",
        entity_type="invoice",
        entity_id=invoice_id,
        entity_name=f"Invoice {inv.invoice_number}",
        new_values={"status": "paid"},
        description=f"Marked invoice {inv.invoice_number} as paid"
    )
    
    return api_success(InvoiceOut.model_validate(inv))


@router.post("/invoices/recalculate-overdue")
def recalc_overdue(
    db: Session = Depends(get_db),
    _user=Depends(require_roles(["admin", "finance"])),
):
    result = invoice_services.recalculate_overdue(db)
    
    # Log the activity
    log_activity(
        db=db,
        user_email=_user.get("email"),
        action="update",
        entity_type="invoice",
        description="Recalculated overdue invoices"
    )
    
    return api_success(result)


@router.put("/invoices/{invoice_id}")
def update_invoice(
    invoice_id: int,
    payload: UpdateInvoiceRequest,
    db: Session = Depends(get_db),
    _user=Depends(require_roles(["admin", "finance"])),
):
    try:
        inv = invoice_services.update_invoice(db, invoice_id, payload)
    except ValueError:
        return api_error("NOT_FOUND", "Invoice not found", http_status=404)

    log_activity(
        db=db,
        user_email=_user.get("email"),
        action="update",
        entity_type="invoice",
        entity_id=invoice_id,
        entity_name=f"Invoice {inv.invoice_number}",
        new_values=payload.model_dump(exclude_unset=True),
        description=f"Updated invoice {inv.invoice_number}",
    )

    return api_success(InvoiceOut.model_validate(inv))


@router.delete("/invoices/{invoice_id}")
def delete_invoice(
    invoice_id: int,
    db: Session = Depends(get_db),
    _user=Depends(require_roles(["admin"])),
):
    try:
        invoice_services.delete_invoice(db, invoice_id)
    except ValueError:
        return api_error("NOT_FOUND", "Invoice not found", http_status=404)

    log_activity(
        db=db,
        user_email=_user.get("email"),
        action="delete",
        entity_type="invoice",
        entity_id=invoice_id,
        description=f"Deleted invoice #{invoice_id}",
    )

    return api_success({"deleted": True})


@router.post("/invoices/auto-generate")
def auto_generate_invoices(
    db: Session = Depends(get_db),
    _user=Depends(require_roles(["admin", "finance"])),
):
    """Run automatic billing for all projects with auto_billing_enabled=True
    whose next_billing_date is today or past."""
    result = run_auto_billing(db)

    log_activity(
        db=db,
        user_email=_user.get("email"),
        action="create",
        entity_type="invoice",
        description=f"Auto-billing run: {result['generated']} invoice(s) generated",
    )

    return api_success(result)
