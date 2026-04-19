from sqlalchemy import select, func
from sqlalchemy.orm import Session

from app.modules.finance.models import Expense
from app.modules.finance.schemas import CreateExpense
from app.modules.invoices.models import Invoice
from app.modules.payments.models import Payment


def create_expense(db: Session, payload: CreateExpense) -> Expense:
    expense = Expense(
        project_id=payload.project_id,
        amount=float(payload.amount),
        category=payload.category,
        description=payload.description,
        expense_date=payload.expense_date,
    )
    db.add(expense)
    db.commit()
    db.refresh(expense)
    return expense


def get_project_financial_summary(db: Session, *, project_id: int) -> dict[str, float]:
    # Revenue = cash received from payments for invoices under this project.
    revenue_stmt = (
        select(func.coalesce(func.sum(Payment.amount), 0.0))
        .select_from(Payment)
        .join(Invoice, Invoice.id == Payment.invoice_id)
        .where(Invoice.project_id == project_id)
    )
    revenue = db.execute(revenue_stmt).scalar_one()

    cost_stmt = select(func.coalesce(func.sum(Expense.amount), 0.0)).where(Expense.project_id == project_id)
    cost = db.execute(cost_stmt).scalar_one()

    revenue = float(revenue or 0.0)
    cost = float(cost or 0.0)
    profit = revenue - cost
    margin = (profit / revenue) if revenue else 0.0

    return {
        "revenue": revenue,
        "cost": cost,
        "profit": profit,
        "margin": margin,
    }
