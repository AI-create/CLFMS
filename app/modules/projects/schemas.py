from datetime import date, datetime
from typing import Optional

from pydantic import BaseModel


class CreateProject(BaseModel):
    client_id: int
    name: str
    description: Optional[str] = None
    status: Optional[str] = "active"
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    budget: Optional[float] = None
    # Billing configuration
    billing_type: Optional[str] = None           # 'upfront' | 'in_arrears'
    billing_cycle: Optional[str] = None          # 'one_time' | 'monthly' | 'quarterly' | 'yearly'
    billing_rate: Optional[float] = None         # fixed fee (upfront) or hourly rate (in_arrears)
    auto_billing_enabled: Optional[bool] = False
    next_billing_date: Optional[date] = None


class ProjectOut(BaseModel):
    id: int
    client_id: int
    name: str
    description: Optional[str] = None
    status: str
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    budget: Optional[float] = None
    # Billing configuration
    billing_type: Optional[str] = None
    billing_cycle: Optional[str] = None
    billing_rate: Optional[float] = None
    auto_billing_enabled: bool = False
    last_billed_date: Optional[date] = None
    next_billing_date: Optional[date] = None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}
