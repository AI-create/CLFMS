from pydantic import BaseModel
from typing import Optional


class KpiOut(BaseModel):
    revenue: float
    profit: float
    pending_payments: float
    active_projects: int


class IncomeBreakdownOut(BaseModel):
    legacy_payments: float
    hourly_income: float
    project_income: float


class ExpenseBreakdownOut(BaseModel):
    legacy_expenses: float
    hourly_expenses: float
    project_expenses: float


class FinancialSummaryOut(BaseModel):
    total_income: float
    total_expense: float
    total_profit: float
    profit_margin: float
    income_breakdown: IncomeBreakdownOut
    expense_breakdown: ExpenseBreakdownOut


class DailyProfitTrendOut(BaseModel):
    date: str
    income: float
    expense: float
    profit: float
    margin: float


class ProjectStatsOut(BaseModel):
    project_id: int
    project_name: str
    income: float
    expense: float
    profit: float
    margin: float

