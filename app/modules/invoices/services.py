from datetime import date

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.modules.invoices.models import Invoice
from app.modules.invoices.schemas import GenerateInvoiceRequest
from app.services.invoice_service import generate_invoice, get_invoice, total_paid_for_invoice


def create_invoice_from_project(db: Session, payload: GenerateInvoiceRequest) -> Invoice:
    return generate_invoice(
        db,
        project_id=payload.project_id,
        type=payload.type,
        rate=payload.rate,
        due_days=payload.due_days,
        invoice_number=payload.invoice_number,
    )


def get_invoice_by_id(db: Session, invoice_id: int) -> Invoice | None:
    return get_invoice(db, invoice_id)


def list_invoices(
    db: Session,
    *,
    status: str | None,
    project_id: int | None,
    page: int,
    limit: int,
) -> tuple[list[Invoice], int]:
    filters = []
    if status:
        filters.append(Invoice.status == status)
    if project_id is not None:
        filters.append(Invoice.project_id == project_id)

    total_stmt = select(func.count()).select_from(Invoice)
    if filters:
        total_stmt = total_stmt.where(*filters)
    total = int(db.execute(total_stmt).scalar_one() or 0)

    stmt = select(Invoice).order_by(Invoice.id.desc())
    if filters:
        stmt = stmt.where(*filters)
    stmt = stmt.offset((page - 1) * limit).limit(limit)
    rows = db.execute(stmt).scalars().all()
    return rows, total


def send_invoice(db: Session, invoice_id: int) -> Invoice:
    inv = get_invoice_by_id(db, invoice_id)
    if not inv:
        raise ValueError("Invoice not found")
    if inv.status == "paid":
        return inv
    inv.status = "sent"
    db.add(inv)
    db.commit()
    db.refresh(inv)
    return inv


def mark_invoice_paid(db: Session, invoice_id: int) -> Invoice:
    inv = get_invoice_by_id(db, invoice_id)
    if not inv:
        raise ValueError("Invoice not found")
    inv.status = "paid"
    db.add(inv)
    db.commit()
    db.refresh(inv)
    return inv


def recalculate_overdue(db: Session) -> dict[str, int]:
    """
    Mark invoices as overdue if due_date < today, not paid, and still outstanding.
    Also unmark overdue if fully paid.
    """
    today = date.today()

    stmt = select(Invoice).where(Invoice.status != "paid")
    invoices = db.execute(stmt).scalars().all()

    updated = 0
    for inv in invoices:
        paid_total = total_paid_for_invoice(db, inv.id)
        outstanding = float(inv.total or 0.0) - float(paid_total or 0.0)
        if inv.total and outstanding <= 0:
            if inv.status != "paid":
                inv.status = "paid"
                updated += 1
            continue

        if inv.due_date and inv.due_date < today and outstanding > 0:
            if inv.status != "overdue":
                inv.status = "overdue"
                updated += 1
        else:
            # Keep 'sent' or 'draft' as-is; only clear overdue back to sent.
            if inv.status == "overdue":
                inv.status = "sent"
                updated += 1

    if updated:
        db.commit()

    return {"updated": updated, "scanned": len(invoices)}
