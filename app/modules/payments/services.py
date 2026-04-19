from datetime import date

from sqlalchemy import select, func
from sqlalchemy.orm import Session

from app.modules.invoices.models import Invoice
from app.modules.payments.models import Payment
from app.modules.payments.schemas import CreatePayment
from app.services.invoice_service import get_invoice, total_paid_for_invoice


def create_payment(db: Session, payload: CreatePayment) -> Payment:
    invoice = get_invoice(db, payload.invoice_id)
    if not invoice:
        raise ValueError("Invoice not found")

    payment_date = payload.payment_date or date.today()

    payment = Payment(
        invoice_id=payload.invoice_id,
        amount=float(payload.amount),
        payment_date=payment_date,
        method=payload.method,
        reference=payload.reference,
    )

    db.add(payment)
    db.commit()
    db.refresh(payment)

    # Update invoice status based on cash received.
    paid_total = total_paid_for_invoice(db, invoice.id)
    if invoice.total and paid_total >= float(invoice.total):
        invoice.status = "paid"
    else:
        # If it is past due, mark overdue.
        if invoice.due_date and invoice.due_date < date.today() and invoice.status != "paid":
            invoice.status = "overdue"

    db.add(invoice)
    db.commit()
    return payment


def outstanding_invoices(db: Session) -> list[tuple[Invoice, float]]:
    today = date.today()

    # Compute outstanding = total - paid (paid derived from payments sum).
    stmt = (
        select(
            Invoice,
            func.coalesce(func.sum(Payment.amount), 0.0).label("paid_total"),
        )
        .join(Payment, Payment.invoice_id == Invoice.id, isouter=True)
        .group_by(Invoice.id)
    )

    invoices = db.execute(stmt).all()
    results: list[tuple[Invoice, float]] = []
    for inv, paid_total in invoices:
        paid_total_f = float(paid_total or 0.0)
        outstanding = float(inv.total or 0.0) - paid_total_f
        if inv.status != "paid" and outstanding > 0:
            results.append((inv, paid_total_f))
    return results
