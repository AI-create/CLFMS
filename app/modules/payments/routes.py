from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.response import api_error, api_success
from app.core.security import require_roles
from app.modules.payments import services as payment_services
from app.modules.payments.schemas import CreatePayment, PaymentOut
from app.modules.invoices.models import Invoice


router = APIRouter(tags=["Payments"])


@router.post("/payments")
def create_payment(
    payload: CreatePayment,
    db: Session = Depends(get_db),
    _user=Depends(require_roles(["admin", "finance"])),
):
    try:
        payment = payment_services.create_payment(db, payload)
    except ValueError:
        return api_error("NOT_FOUND", "Invoice not found", http_status=404)
    return api_success(PaymentOut.model_validate(payment))


@router.get("/payments/outstanding")
def get_outstanding(
    db: Session = Depends(get_db),
    _user=Depends(require_roles(["admin", "finance"])),
):
    rows = payment_services.outstanding_invoices(db)
    data = [
        {
            "invoice_id": inv.id,
            "invoice_number": inv.invoice_number,
            "status": inv.status,
            "total": float(inv.total or 0.0),
            "paid_total": float(paid_total or 0.0),
            "outstanding": float(inv.total or 0.0) - float(paid_total or 0.0),
        }
        for inv, paid_total in rows
    ]
    return api_success(data)
