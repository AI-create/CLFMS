from pydantic import BaseModel


class KpiOut(BaseModel):
    revenue: float
    profit: float
    pending_payments: float
    active_projects: int

