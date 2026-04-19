"""FI-IO Schemas"""
from datetime import datetime, date
from typing import Optional, List
from pydantic import BaseModel


# ===== HOURLY INCOME SCHEMAS =====

class CreateHourlyIncome(BaseModel):
    activity_id: Optional[int] = None
    employee_id: int
    project_id: Optional[int] = None
    client_id: Optional[int] = None
    income_date: date
    income_type: str = "hourly_billing"
    hours_billed: float
    hourly_rate: float
    description: Optional[str] = None


class UpdateHourlyIncome(BaseModel):
    hours_billed: Optional[float] = None
    hourly_rate: Optional[float] = None
    status: Optional[str] = None
    description: Optional[str] = None


class HourlyIncomeOut(BaseModel):
    id: int
    activity_id: Optional[int]
    employee_id: int
    project_id: Optional[int]
    client_id: Optional[int]
    income_date: date
    income_type: str
    hours_billed: float
    hourly_rate: float
    amount: float
    description: Optional[str]
    status: str
    invoice_id: Optional[int]
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


# ===== PROJECT INCOME SCHEMAS =====

class CreateProjectIncome(BaseModel):
    project_id: int
    client_id: int
    income_date: date
    income_type: str = "project_revenue"
    amount: float
    description: Optional[str] = None


class UpdateProjectIncome(BaseModel):
    amount: Optional[float] = None
    status: Optional[str] = None
    description: Optional[str] = None


class ProjectIncomeOut(BaseModel):
    id: int
    project_id: int
    client_id: int
    income_date: date
    income_type: str
    amount: float
    description: Optional[str]
    status: str
    invoice_id: Optional[int]
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


# ===== HOURLY EXPENSE SCHEMAS =====

class CreateHourlyExpense(BaseModel):
    activity_id: Optional[int] = None
    employee_id: int
    expense_date: date
    expense_type: str = "salary"
    hours_worked: float
    hourly_cost: float
    description: Optional[str] = None
    project_id: Optional[int] = None


class UpdateHourlyExpense(BaseModel):
    hours_worked: Optional[float] = None
    hourly_cost: Optional[float] = None
    status: Optional[str] = None
    description: Optional[str] = None


class HourlyExpenseOut(BaseModel):
    id: int
    activity_id: Optional[int]
    employee_id: int
    expense_date: date
    expense_type: str
    hours_worked: float
    hourly_cost: float
    amount: float
    description: Optional[str]
    status: str
    project_id: Optional[int]
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


# ===== PROJECT EXPENSE SCHEMAS =====

class CreateProjectExpense(BaseModel):
    project_id: int
    expense_date: date
    expense_type: str = "materials"
    amount: float
    description: Optional[str] = None
    vendor: Optional[str] = None


class UpdateProjectExpense(BaseModel):
    amount: Optional[float] = None
    status: Optional[str] = None
    description: Optional[str] = None
    vendor: Optional[str] = None


class ProjectExpenseOut(BaseModel):
    id: int
    project_id: int
    expense_date: date
    expense_type: str
    amount: float
    description: Optional[str]
    vendor: Optional[str]
    status: str
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


# ===== PROFIT SCHEMAS =====

class DailyProfitOut(BaseModel):
    id: int
    profit_date: date
    total_income: float
    total_expense: float
    total_profit: float
    profit_margin: float
    active_hours: float
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class ProjectProfitOut(BaseModel):
    id: int
    project_id: int
    total_income: float
    total_expense: float
    total_profit: float
    profit_margin: float
    hours_billed: float
    break_even_point: Optional[float]
    last_updated: datetime

    model_config = {"from_attributes": True}


# ===== PAGINATION SCHEMAS =====

class PaginatedHourlyIncomes(BaseModel):
    data: List[HourlyIncomeOut]
    meta: dict


class PaginatedProjectIncomes(BaseModel):
    data: List[ProjectIncomeOut]
    meta: dict


class PaginatedHourlyExpenses(BaseModel):
    data: List[HourlyExpenseOut]
    meta: dict


class PaginatedProjectExpenses(BaseModel):
    data: List[ProjectExpenseOut]
    meta: dict
