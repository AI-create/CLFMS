from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.response import api_error, api_success
from app.core.security import require_roles
from app.modules.payments import services as payment_services
from app.modules.payments.schemas import CreatePayment, PaymentOut
from app.modules.invoices.models import Invoice
from sqlalchemy import desc


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


@router.get("/payments")
def list_payments(
    invoice_id: int | None = None,
    page: int = 1,
    limit: int = 20,
    db: Session = Depends(get_db),
    _user=Depends(require_roles(["admin", "finance"])),
):
    query = db.query(Payment)
    if invoice_id:
        query = query.filter(Payment.invoice_id == invoice_id)
    total = query.count()
    payments = query.order_by(desc(Payment.created_at)).offset((page - 1) * limit).limit(limit).all()
    return api_success(
        {
            "data": [PaymentOut.model_validate(p) for p in payments],
            "meta": {"total": total, "page": page, "limit": limit},
        }
    )


@router.delete("/payments/{payment_id}")
def delete_payment(
    payment_id: int,
    db: Session = Depends(get_db),
    _user=Depends(require_roles(["admin", "finance"])),
):
    payment = db.query(Payment).filter(Payment.id == payment_id).first()
    if not payment:
        return api_error("NOT_FOUND", "Payment not found", http_status=404)
    db.delete(payment)
    db.commit()
    return api_success({"deleted": True})


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
