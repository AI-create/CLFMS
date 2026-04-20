"""
Automatic billing service — generates invoices based on project billing configuration.

Billing types:
  upfront    — Invoice issued BEFORE/AT the billing period (fixed fee, SaaS/subscription).
               Amount = billing_rate (the agreed fixed fee per cycle).
  in_arrears — Invoice issued AFTER the billing period ends (usage-based, enterprise).
               Amount = total_hours_logged × billing_rate (hourly).

Billing cycles: one_time | monthly | quarterly | yearly
Auto-billing runs when next_billing_date <= today and auto_billing_enabled = True.
"""

import calendar
from datetime import date, timedelta

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.modules.clients.models import Client
from app.modules.invoices.models import Invoice, InvoiceItem
from app.modules.projects.models import Project
from app.modules.tasks import services as tasks_services
from app.services.gst_service import calculate_gst
from app.services.invoice_service import generate_invoice_number


# ---------------------------------------------------------------------------
# Date helpers (no external deps)
# ---------------------------------------------------------------------------

def _add_months(d: date, months: int) -> date:
    month = d.month - 1 + months
    year = d.year + month // 12
    month = month % 12 + 1
    max_day = calendar.monthrange(year, month)[1]
    return date(year, month, min(d.day, max_day))


def _next_billing_date(from_date: date, cycle: str) -> date | None:
    """Return the next billing date after `from_date` for the given cycle.
    Returns None for 'one_time' (no repeat)."""
    if cycle == "monthly":
        return _add_months(from_date, 1)
    elif cycle == "quarterly":
        return _add_months(from_date, 3)
    elif cycle == "yearly":
        try:
            return from_date.replace(year=from_date.year + 1)
        except ValueError:  # Feb 29 in non-leap year
            return date(from_date.year + 1, 2, 28)
    return None  # one_time — no next date


# ---------------------------------------------------------------------------
# Invoice generation helpers
# ---------------------------------------------------------------------------

def _client_state(db: Session, client_id: int) -> str | None:
    client = db.execute(select(Client).where(Client.id == client_id)).scalar_one_or_none()
    return client.state if client else None


def generate_upfront_invoice(db: Session, project: Project) -> Invoice:
    """Fixed-amount invoice covering the NEXT billing period (issued upfront)."""
    client_state = _client_state(db, project.client_id)
    amount = float(project.billing_rate or 0.0)
    gst = calculate_gst(subtotal=amount, client_state=client_state)

    today = date.today()
    cycle = project.billing_cycle or "one_time"
    period_end = _next_billing_date(today, cycle) or today
    due_date = today + timedelta(days=30)

    inv = Invoice(
        project_id=project.id,
        invoice_number=generate_invoice_number(),
        subtotal=amount,
        cgst=gst["cgst"],
        sgst=gst["sgst"],
        igst=gst["igst"],
        total=gst["total"],
        status="sent",        # Upfront invoices are auto-sent
        issued_date=today,
        due_date=due_date,
    )
    db.add(inv)
    db.flush()

    db.add(InvoiceItem(
        invoice_id=inv.id,
        description=f"Upfront billing ({cycle}) \u2014 {today} to {period_end}",
        quantity=1,
        rate=amount,
        amount=amount,
    ))
    db.commit()
    db.refresh(inv)
    return inv


def generate_arrears_invoice(db: Session, project: Project) -> Invoice:
    """Usage-based invoice for hours worked since last billing date."""
    client_state = _client_state(db, project.client_id)
    total_hours = tasks_services.total_hours_for_project(db, project_id=project.id)
    rate = float(project.billing_rate or 0.0)
    subtotal = total_hours * rate
    gst = calculate_gst(subtotal=subtotal, client_state=client_state)

    today = date.today()
    period_start = project.last_billed_date or project.start_date or today
    due_date = today + timedelta(days=30)
    cycle = project.billing_cycle or "one_time"

    inv = Invoice(
        project_id=project.id,
        invoice_number=generate_invoice_number(),
        subtotal=subtotal,
        cgst=gst["cgst"],
        sgst=gst["sgst"],
        igst=gst["igst"],
        total=gst["total"],
        status="sent",
        issued_date=today,
        due_date=due_date,
    )
    db.add(inv)
    db.flush()

    db.add(InvoiceItem(
        invoice_id=inv.id,
        description=f"Usage billing ({total_hours:.2f} hrs \u00d7 \u20b9{rate}/hr) \u2014 {period_start} to {today}",
        quantity=total_hours,
        rate=rate,
        amount=subtotal,
    ))
    db.commit()
    db.refresh(inv)
    return inv


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def trigger_project_billing(db: Session, project_id: int) -> dict:
    """Manually trigger billing for a single project regardless of schedule."""
    project = db.execute(select(Project).where(Project.id == project_id)).scalar_one_or_none()
    if not project:
        raise ValueError("Project not found")
    if not project.billing_type:
        raise ValueError("Project has no billing_type configured")

    today = date.today()
    if project.billing_type == "upfront":
        inv = generate_upfront_invoice(db, project)
    else:
        inv = generate_arrears_invoice(db, project)

    # Advance billing dates
    cycle = project.billing_cycle or "one_time"
    project.last_billed_date = today
    project.next_billing_date = _next_billing_date(today, cycle)
    db.add(project)
    db.commit()

    return {
        "project_id": project.id,
        "project_name": project.name,
        "invoice_id": inv.id,
        "invoice_number": inv.invoice_number,
        "billing_type": project.billing_type,
        "total": float(inv.total or 0),
    }


def run_auto_billing(db: Session) -> dict:
    """
    Scan all active projects with auto_billing_enabled=True and generate
    invoices for those whose next_billing_date is today or in the past.
    """
    today = date.today()

    stmt = select(Project).where(
        Project.auto_billing_enabled.is_(True),
        Project.billing_type.isnot(None),
        Project.next_billing_date.isnot(None),
        Project.next_billing_date <= today,
        Project.status == "active",
    )
    projects = db.execute(stmt).scalars().all()

    generated = []
    errors = []

    for project in projects:
        try:
            if project.billing_type == "upfront":
                inv = generate_upfront_invoice(db, project)
            else:
                inv = generate_arrears_invoice(db, project)

            cycle = project.billing_cycle or "one_time"
            project.last_billed_date = today
            project.next_billing_date = _next_billing_date(today, cycle)
            db.add(project)
            db.commit()

            generated.append({
                "project_id": project.id,
                "project_name": project.name,
                "invoice_id": inv.id,
                "invoice_number": inv.invoice_number,
                "billing_type": project.billing_type,
                "total": float(inv.total or 0),
            })
        except Exception as exc:
            db.rollback()
            errors.append({"project_id": project.id, "error": str(exc)})

    return {
        "processed": len(projects),
        "generated": len(generated),
        "errors": len(errors),
        "invoices": generated,
        "error_details": errors,
    }
