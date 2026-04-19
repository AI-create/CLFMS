import secrets
from datetime import date, timedelta

from sqlalchemy import select, func
from sqlalchemy.orm import Session

from app.modules.clients.models import Client
from app.modules.invoices.models import Invoice, InvoiceItem
from app.modules.projects.models import Project
from app.modules.tasks import services as tasks_services
from app.services.gst_service import calculate_gst


def generate_invoice_number() -> str:
    # Good enough for MVP: human-readable + low collision probability.
    return f"INV-{date.today().strftime('%Y%m%d')}-{secrets.token_hex(3).upper()}"


def generate_invoice(
    db: Session,
    *,
    project_id: int,
    type: str,
    rate: float,
    due_days: int,
    invoice_number: str | None = None,
) -> Invoice:
    project = db.execute(select(Project).where(Project.id == project_id)).scalar_one_or_none()
    if not project:
        raise ValueError("Project not found")

    client = db.execute(select(Client).where(Client.id == project.client_id)).scalar_one_or_none()
    client_state = client.state if client else None

    total_hours = tasks_services.total_hours_for_project(db, project_id=project_id)
    rate = float(rate or 0.0)

    # For MVP, we treat `fixed` and `milestone` the same as hourly scaling.
    subtotal = total_hours * rate
    gst = calculate_gst(subtotal=subtotal, client_state=client_state)

    issued_date = date.today()
    due_date = issued_date + timedelta(days=int(due_days or 0))

    inv = Invoice(
        project_id=project_id,
        invoice_number=invoice_number or generate_invoice_number(),
        subtotal=subtotal,
        cgst=gst["cgst"],
        sgst=gst["sgst"],
        igst=gst["igst"],
        total=gst["total"],
        status="draft",
        issued_date=issued_date,
        due_date=due_date,
    )
    db.add(inv)
    db.flush()  # get inv.id for item

    db.add(
        InvoiceItem(
            invoice_id=inv.id,
            description=f"Work ({type})",
            quantity=total_hours,
            rate=rate,
            amount=subtotal,
        )
    )

    db.commit()
    db.refresh(inv)
    return inv


def get_invoice(db: Session, invoice_id: int) -> Invoice | None:
    return db.execute(select(Invoice).where(Invoice.id == invoice_id)).scalar_one_or_none()


def total_paid_for_invoice(db: Session, invoice_id: int) -> float:
    # Payments include partials; revenue is realized cash-in, not invoice issuance.
    from app.modules.payments.models import Payment

    stmt = select(func.coalesce(func.sum(Payment.amount), 0.0)).where(Payment.invoice_id == invoice_id)
    total = db.execute(stmt).scalar_one()
    return float(total or 0.0)
