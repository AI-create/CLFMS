"""FI-IO Routes"""
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from datetime import date

from app.core.database import get_db
from app.core.response import api_error, api_success
from app.core.security import require_roles
from app.modules.fiio import services
from app.modules.fiio.schemas import (
    CreateHourlyIncome,
    UpdateHourlyIncome,
    CreateProjectIncome,
    UpdateProjectIncome,
    CreateHourlyExpense,
    UpdateHourlyExpense,
    CreateProjectExpense,
    UpdateProjectExpense,
    HourlyIncomeOut,
    ProjectIncomeOut,
    HourlyExpenseOut,
    ProjectExpenseOut,
    DailyProfitOut,
    ProjectProfitOut,
    PaginatedHourlyIncomes,
    PaginatedProjectIncomes,
    PaginatedHourlyExpenses,
    PaginatedProjectExpenses,
)
from app.services.activity_logging_service import log_activity


router = APIRouter(tags=["FI-IO"])


# ===== HOURLY INCOME ENDPOINTS =====

@router.post("/hourly-incomes")
def create_hourly_income(
    payload: CreateHourlyIncome,
    db: Session = Depends(get_db),
    _user=Depends(require_roles(["admin", "finance", "operations"])),
):
    """Create hourly income record"""
    income = services.FIIOService.create_hourly_income(db, payload)
    
    log_activity(
        db=db,
        user_email=_user.get("email"),
        action="create",
        entity_type="hourly_income",
        entity_id=income.id,
        entity_name=f"Income {income.amount}",
        new_values=payload.model_dump(),
        description=f"Created hourly income: {income.amount}"
    )
    
    return api_success(HourlyIncomeOut.model_validate(income))


@router.get("/hourly-incomes")
def list_hourly_incomes(
    employee_id: int | None = Query(None),
    project_id: int | None = Query(None),
    date_from: date | None = Query(None),
    date_to: date | None = Query(None),
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
    _user=Depends(require_roles(["admin", "finance", "operations", "project_manager"])),
):
    """List hourly incomes"""
    incomes, total = services.FIIOService.list_hourly_incomes(
        db,
        employee_id=employee_id,
        project_id=project_id,
        date_from=date_from,
        date_to=date_to,
        page=page,
        limit=limit,
    )
    
    return api_success(
        PaginatedHourlyIncomes(
            data=[HourlyIncomeOut.model_validate(i) for i in incomes],
            meta={"total": total, "page": page, "limit": limit},
        ).model_dump()
    )


@router.get("/hourly-incomes/{income_id}")
def get_hourly_income(
    income_id: int,
    db: Session = Depends(get_db),
    _user=Depends(require_roles(["admin", "finance", "operations", "project_manager"])),
):
    """Get hourly income by ID"""
    income = services.FIIOService.get_hourly_income(db, income_id)
    if not income:
        return api_error("NOT_FOUND", "Hourly income not found", http_status=404)
    return api_success(HourlyIncomeOut.model_validate(income))


@router.put("/hourly-incomes/{income_id}")
def update_hourly_income(
    income_id: int,
    payload: UpdateHourlyIncome,
    db: Session = Depends(get_db),
    _user=Depends(require_roles(["admin", "finance"])),
):
    """Update hourly income"""
    income = services.FIIOService.update_hourly_income(
        db, income_id, payload.model_dump(exclude_unset=True)
    )
    if not income:
        return api_error("NOT_FOUND", "Hourly income not found", http_status=404)
    
    log_activity(
        db=db,
        user_email=_user.get("email"),
        action="update",
        entity_type="hourly_income",
        entity_id=income.id,
        entity_name=f"Income {income.amount}",
        new_values=payload.model_dump(exclude_unset=True),
        description=f"Updated hourly income: {income.amount}"
    )
    
    return api_success(HourlyIncomeOut.model_validate(income))


@router.delete("/hourly-incomes/{income_id}")
def delete_hourly_income(
    income_id: int,
    db: Session = Depends(get_db),
    _user=Depends(require_roles(["admin", "finance"])),
):
    """Delete hourly income"""
    income = services.FIIOService.get_hourly_income(db, income_id)
    if not income:
        return api_error("NOT_FOUND", "Hourly income not found", http_status=404)
    db.delete(income)
    db.commit()
    log_activity(
        db=db,
        user_email=_user.get("email"),
        action="delete",
        entity_type="hourly_income",
        entity_id=income_id,
        entity_name=f"Income #{income_id}",
        description=f"Deleted hourly income #{income_id}",
    )
    return api_success({"deleted": True})


# ===== PROJECT INCOME ENDPOINTS =====

@router.post("/project-incomes")
def create_project_income(
    payload: CreateProjectIncome,
    db: Session = Depends(get_db),
    _user=Depends(require_roles(["admin", "finance", "operations"])),
):
    """Create project income record"""
    income = services.FIIOService.create_project_income(db, payload)
    
    log_activity(
        db=db,
        user_email=_user.get("email"),
        action="create",
        entity_type="project_income",
        entity_id=income.id,
        entity_name=f"Income {income.amount}",
        new_values=payload.model_dump(),
        description=f"Created project income: {income.amount}"
    )
    
    return api_success(ProjectIncomeOut.model_validate(income))


@router.get("/project-incomes")
def list_project_incomes(
    project_id: int | None = Query(None),
    date_from: date | None = Query(None),
    date_to: date | None = Query(None),
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
    _user=Depends(require_roles(["admin", "finance", "operations", "project_manager"])),
):
    """List project incomes"""
    incomes, total = services.FIIOService.list_project_incomes(
        db,
        project_id=project_id,
        date_from=date_from,
        date_to=date_to,
        page=page,
        limit=limit,
    )
    
    return api_success(
        PaginatedProjectIncomes(
            data=[ProjectIncomeOut.model_validate(i) for i in incomes],
            meta={"total": total, "page": page, "limit": limit},
        ).model_dump()
    )


@router.delete("/project-incomes/{income_id}")
def delete_project_income(
    income_id: int,
    db: Session = Depends(get_db),
    _user=Depends(require_roles(["admin", "finance"])),
):
    """Delete project income"""
    income = services.FIIOService.get_project_income(db, income_id)
    if not income:
        return api_error("NOT_FOUND", "Project income not found", http_status=404)
    db.delete(income)
    db.commit()
    log_activity(
        db=db,
        user_email=_user.get("email"),
        action="delete",
        entity_type="project_income",
        entity_id=income_id,
        entity_name=f"Income #{income_id}",
        description=f"Deleted project income #{income_id}",
    )
    return api_success({"deleted": True})


# ===== HOURLY EXPENSE ENDPOINTS =====

@router.post("/hourly-expenses")
def create_hourly_expense(
    payload: CreateHourlyExpense,
    db: Session = Depends(get_db),
    _user=Depends(require_roles(["admin", "finance", "operations"])),
):
    """Create hourly expense record"""
    expense = services.FIIOService.create_hourly_expense(db, payload)
    
    log_activity(
        db=db,
        user_email=_user.get("email"),
        action="create",
        entity_type="hourly_expense",
        entity_id=expense.id,
        entity_name=f"Expense {expense.amount}",
        new_values=payload.model_dump(),
        description=f"Created hourly expense: {expense.amount}"
    )
    
    return api_success(HourlyExpenseOut.model_validate(expense))


@router.get("/hourly-expenses")
def list_hourly_expenses(
    employee_id: int | None = Query(None),
    project_id: int | None = Query(None),
    date_from: date | None = Query(None),
    date_to: date | None = Query(None),
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
    _user=Depends(require_roles(["admin", "finance", "operations", "project_manager"])),
):
    """List hourly expenses"""
    expenses, total = services.FIIOService.list_hourly_expenses(
        db,
        employee_id=employee_id,
        project_id=project_id,
        date_from=date_from,
        date_to=date_to,
        page=page,
        limit=limit,
    )
    
    return api_success(
        PaginatedHourlyExpenses(
            data=[HourlyExpenseOut.model_validate(e) for e in expenses],
            meta={"total": total, "page": page, "limit": limit},
        ).model_dump()
    )


@router.delete("/hourly-expenses/{expense_id}")
def delete_hourly_expense(
    expense_id: int,
    db: Session = Depends(get_db),
    _user=Depends(require_roles(["admin", "finance"])),
):
    """Delete hourly expense"""
    expense = services.FIIOService.get_hourly_expense(db, expense_id)
    if not expense:
        return api_error("NOT_FOUND", "Hourly expense not found", http_status=404)
    db.delete(expense)
    db.commit()
    log_activity(
        db=db,
        user_email=_user.get("email"),
        action="delete",
        entity_type="hourly_expense",
        entity_id=expense_id,
        entity_name=f"Expense #{expense_id}",
        description=f"Deleted hourly expense #{expense_id}",
    )
    return api_success({"deleted": True})


# ===== PROJECT EXPENSE ENDPOINTS =====

@router.post("/project-expenses")
def create_project_expense(
    payload: CreateProjectExpense,
    db: Session = Depends(get_db),
    _user=Depends(require_roles(["admin", "finance", "operations"])),
):
    """Create project expense record"""
    expense = services.FIIOService.create_project_expense(db, payload)
    
    log_activity(
        db=db,
        user_email=_user.get("email"),
        action="create",
        entity_type="project_expense",
        entity_id=expense.id,
        entity_name=f"Expense {expense.amount}",
        new_values=payload.model_dump(),
        description=f"Created project expense: {expense.amount}"
    )
    
    return api_success(ProjectExpenseOut.model_validate(expense))


@router.get("/project-expenses")
def list_project_expenses(
    project_id: int | None = Query(None),
    date_from: date | None = Query(None),
    date_to: date | None = Query(None),
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
    _user=Depends(require_roles(["admin", "finance", "operations", "project_manager"])),
):
    """List project expenses"""
    expenses, total = services.FIIOService.list_project_expenses(
        db,
        project_id=project_id,
        date_from=date_from,
        date_to=date_to,
        page=page,
        limit=limit,
    )
    
    return api_success(
        PaginatedProjectExpenses(
            data=[ProjectExpenseOut.model_validate(e) for e in expenses],
            meta={"total": total, "page": page, "limit": limit},
        ).model_dump()
    )


@router.delete("/project-expenses/{expense_id}")
def delete_project_expense(
    expense_id: int,
    db: Session = Depends(get_db),
    _user=Depends(require_roles(["admin", "finance"])),
):
    """Delete project expense"""
    expense = services.FIIOService.get_project_expense(db, expense_id)
    if not expense:
        return api_error("NOT_FOUND", "Project expense not found", http_status=404)
    db.delete(expense)
    db.commit()
    log_activity(
        db=db,
        user_email=_user.get("email"),
        action="delete",
        entity_type="project_expense",
        entity_id=expense_id,
        entity_name=f"Expense #{expense_id}",
        description=f"Deleted project expense #{expense_id}",
    )
    return api_success({"deleted": True})


# ===== PROFIT ANALYTICS =====

@router.get("/daily-profit/{profit_date}")
def get_daily_profit(
    profit_date: date,
    db: Session = Depends(get_db),
    _user=Depends(require_roles(["admin", "finance", "project_manager"])),
):
    """Get daily profit for a specific date"""
    profit = services.FIIOService.get_daily_profit(db, profit_date)
    if not profit:
        return api_error("NOT_FOUND", "Daily profit not found", http_status=404)
    return api_success(DailyProfitOut.model_validate(profit))


@router.get("/daily-profits")
def get_daily_profits(
    date_from: date = Query(None),
    date_to: date = Query(None),
    db: Session = Depends(get_db),
    _user=Depends(require_roles(["admin", "finance", "project_manager"])),
):
    """Get daily profits for date range"""
    if not date_from or not date_to:
        return api_error("BAD_REQUEST", "date_from and date_to are required", http_status=400)
    
    if date_from > date_to:
        return api_error("BAD_REQUEST", "date_from must be before date_to", http_status=400)
    
    profits = services.FIIOService.get_daily_profits(db, date_from, date_to)
    return api_success({
        "data": [DailyProfitOut.model_validate(p).model_dump() for p in profits],
        "meta": {"total": len(profits), "date_from": str(date_from), "date_to": str(date_to)},
    })


@router.get("/project-profit/{project_id}")
def get_project_profit(
    project_id: int,
    db: Session = Depends(get_db),
    _user=Depends(require_roles(["admin", "finance", "project_manager"])),
):
    """Get profit analysis for a project"""
    profit = services.FIIOService.get_project_profit(db, project_id)
    if not profit:
        return api_error("NOT_FOUND", "Project not found", http_status=404)
    return api_success(ProjectProfitOut.model_validate(profit))


@router.get("/live-profit-summary")
def get_live_profit_summary(
    days: int = Query(30, ge=1, le=365),
    db: Session = Depends(get_db),
    _user=Depends(require_roles(["admin", "finance"])),
):
    """Get live profit summary for last N days"""
    summary = services.FIIOService.get_live_profit_summary(db, days)
    return api_success(summary)


@router.get("/intelligence")
def get_intelligence(
    days: int = Query(30, ge=1, le=365),
    db: Session = Depends(get_db),
    _user=Depends(require_roles(["admin", "finance"])),
):
    """
    Financial Intelligence Overview — auto-aggregates income and expenses
    from ALL company modules (invoices, payments, finance, operations).
    Returns hourly earnings rate and earning potential analysis.
    """
    data = services.FIIOService.get_intelligence(db, days)
    return api_success(data)
