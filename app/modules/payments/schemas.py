from datetime import date, datetime
from typing import Optional

from pydantic import BaseModel


class CreatePayment(BaseModel):
    invoice_id: int
    amount: float
    payment_date: Optional[date] = None
    method: Optional[str] = None
    reference: Optional[str] = None


class PaymentOut(BaseModel):
    id: int
    invoice_id: int
    amount: float
    payment_date: Optional[date] = None
    method: Optional[str] = None
    reference: Optional[str] = None
    created_at: datetime

    model_config = {"from_attributes": True}
