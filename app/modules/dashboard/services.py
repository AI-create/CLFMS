from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.modules.finance.models import Expense
from app.modules.invoices.models import Invoice
from app.modules.payments.models import Payment
from app.modules.projects.models import Project


def get_kpis(db: Session) -> dict[str, float | int]:
    revenue_stmt = select(func.coalesce(func.sum(Payment.amount), 0.0))
    revenue = float(db.execute(revenue_stmt).scalar_one() or 0.0)

    cost_stmt = select(func.coalesce(func.sum(Expense.amount), 0.0))
    cost = float(db.execute(cost_stmt).scalar_one() or 0.0)

    # Pending payments = total invoiced - total paid.
    invoiced_stmt = select(func.coalesce(func.sum(Invoice.total), 0.0))
    invoiced = float(db.execute(invoiced_stmt).scalar_one() or 0.0)
    pending = max(invoiced - revenue, 0.0)

    active_stmt = select(func.count()).select_from(Project).where(Project.status == "active")
    active_projects = int(db.execute(active_stmt).scalar_one() or 0)

    profit = revenue - cost
    return {
        "revenue": revenue,
        "profit": profit,
        "pending_payments": pending,
        "active_projects": active_projects,
    }

