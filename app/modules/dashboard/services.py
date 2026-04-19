from sqlalchemy import func, select, and_
from sqlalchemy.orm import Session
from datetime import date, timedelta

from app.modules.finance.models import Expense
from app.modules.invoices.models import Invoice
from app.modules.payments.models import Payment
from app.modules.projects.models import Project
from app.modules.fiio.models import HourlyIncome, ProjectIncome, HourlyExpense, ProjectExpense, DailyProfit


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


def get_financial_summary(db: Session) -> dict:
    """Get comprehensive financial summary including FI-IO data"""
    # Legacy payments/expenses
    revenue_stmt = select(func.coalesce(func.sum(Payment.amount), 0.0))
    legacy_revenue = float(db.execute(revenue_stmt).scalar_one() or 0.0)

    cost_stmt = select(func.coalesce(func.sum(Expense.amount), 0.0))
    legacy_cost = float(db.execute(cost_stmt).scalar_one() or 0.0)

    # FI-IO data (more granular)
    hourly_income_stmt = select(func.coalesce(func.sum(HourlyIncome.amount), 0.0))
    hourly_income = float(db.execute(hourly_income_stmt).scalar_one() or 0.0)

    project_income_stmt = select(func.coalesce(func.sum(ProjectIncome.amount), 0.0))
    project_income = float(db.execute(project_income_stmt).scalar_one() or 0.0)

    hourly_expense_stmt = select(func.coalesce(func.sum(HourlyExpense.amount), 0.0))
    hourly_expense = float(db.execute(hourly_expense_stmt).scalar_one() or 0.0)

    project_expense_stmt = select(func.coalesce(func.sum(ProjectExpense.amount), 0.0))
    project_expense = float(db.execute(project_expense_stmt).scalar_one() or 0.0)

    total_income = legacy_revenue + hourly_income + project_income
    total_expense = legacy_cost + hourly_expense + project_expense
    total_profit = total_income - total_expense
    profit_margin = (total_profit / total_income * 100) if total_income > 0 else 0.0

    return {
        "total_income": round(total_income, 2),
        "total_expense": round(total_expense, 2),
        "total_profit": round(total_profit, 2),
        "profit_margin": round(profit_margin, 2),
        "income_breakdown": {
            "legacy_payments": round(legacy_revenue, 2),
            "hourly_income": round(hourly_income, 2),
            "project_income": round(project_income, 2),
        },
        "expense_breakdown": {
            "legacy_expenses": round(legacy_cost, 2),
            "hourly_expenses": round(hourly_expense, 2),
            "project_expenses": round(project_expense, 2),
        },
    }


def get_30day_trend(db: Session) -> list[dict]:
    """Get 30-day profit trend"""
    end_date = date.today()
    start_date = end_date - timedelta(days=29)

    daily_profits = db.query(DailyProfit).filter(
        and_(
            DailyProfit.profit_date >= start_date,
            DailyProfit.profit_date <= end_date,
        )
    ).order_by(DailyProfit.profit_date.asc()).all()

    result = []
    current = start_date
    while current <= end_date:
        profit = next((p for p in daily_profits if p.profit_date == current), None)
        if profit:
            result.append({
                "date": str(current),
                "income": round(profit.total_income, 2),
                "expense": round(profit.total_expense, 2),
                "profit": round(profit.total_profit, 2),
                "margin": round(profit.profit_margin, 2),
            })
        else:
            result.append({
                "date": str(current),
                "income": 0.0,
                "expense": 0.0,
                "profit": 0.0,
                "margin": 0.0,
            })
        current += timedelta(days=1)

    return result


def get_top_projects(db: Session, limit: int = 5) -> list[dict]:
    """Get top performing projects by profit"""
    projects = db.query(Project).all()
    
    project_stats = []
    for project in projects:
        income = db.execute(
            select(func.coalesce(func.sum(HourlyIncome.amount) + func.sum(ProjectIncome.amount), 0.0))
            .select_from(HourlyIncome)
            .where(HourlyIncome.project_id == project.id)
        ).scalar_one() or 0.0

        expense = db.execute(
            select(func.coalesce(func.sum(HourlyExpense.amount) + func.sum(ProjectExpense.amount), 0.0))
            .select_from(HourlyExpense)
            .where(HourlyExpense.project_id == project.id)
        ).scalar_one() or 0.0

        profit = income - expense
        profit_margin = (profit / income * 100) if income > 0 else 0.0

        project_stats.append({
            "project_id": project.id,
            "project_name": project.name,
            "income": round(income, 2),
            "expense": round(expense, 2),
            "profit": round(profit, 2),
            "margin": round(profit_margin, 2),
        })

    # Sort by profit descending and return top N
    return sorted(project_stats, key=lambda x: x["profit"], reverse=True)[:limit]

