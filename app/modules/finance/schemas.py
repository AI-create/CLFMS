from datetime import date, datetime
from typing import Optional

from pydantic import BaseModel


class CreateExpense(BaseModel):
    project_id: int
    amount: float
    category: str
    description: Optional[str] = None
    expense_date: Optional[date] = None


class UpdateExpense(BaseModel):
    project_id: Optional[int] = None
    amount: Optional[float] = None
    category: Optional[str] = None
    description: Optional[str] = None
    expense_date: Optional[date] = None


class ExpenseOut(BaseModel):
    id: int
    project_id: int
    amount: float
    category: str
    description: Optional[str] = None
    expense_date: Optional[date] = None
    created_at: datetime

    model_config = {"from_attributes": True}


class FinancialSummaryOut(BaseModel):
    project_id: int
    revenue: float
    cost: float
    profit: float
    margin: float
