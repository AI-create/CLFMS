from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

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


@router.get("/finance/project/{project_id}")
def project_financial_summary(
    project_id: int,
    db: Session = Depends(get_db),
    _user=Depends(require_roles(["admin", "finance"])),
):
    summary = finance_services.get_project_financial_summary(db, project_id=project_id)
    return api_success(FinancialSummaryOut(project_id=project_id, **summary))
