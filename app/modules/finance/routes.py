from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from typing import Optional

from app.core.database import get_db
from app.core.response import api_error, api_success
from app.core.security import require_roles
from app.modules.finance import services as finance_services
from app.modules.finance.schemas import CreateExpense, ExpenseOut, FinancialSummaryOut


router = APIRouter(tags=["Finance"])


@router.post("/expenses")
def create_expense(
    payload: CreateExpense,
    db: Session = Depends(get_db),
    _user=Depends(require_roles(["admin", "finance"])),
):
    expense = finance_services.create_expense(db, payload)
    return api_success(ExpenseOut.model_validate(expense))


@router.get("/expenses")
def list_expenses(
    project_id: Optional[int] = Query(None),
    category: Optional[str] = Query(None),
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
    _user=Depends(require_roles(["admin", "finance"])),
):
    expenses, total = finance_services.list_expenses(
        db, project_id=project_id, category=category, page=page, limit=limit
    )
    return api_success({
        "data": [ExpenseOut.model_validate(e).model_dump() for e in expenses],
        "meta": {"total": total, "page": page, "limit": limit},
    })


@router.get("/finance/project/{project_id}")
def project_financial_summary(
    project_id: int,
    db: Session = Depends(get_db),
    _user=Depends(require_roles(["admin", "finance"])),
):
    summary = finance_services.get_project_financial_summary(db, project_id=project_id)
    return api_success(FinancialSummaryOut(project_id=project_id, **summary))
