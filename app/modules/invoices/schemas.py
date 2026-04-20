from datetime import date, datetime
from typing import Literal, Optional

from pydantic import BaseModel


InvoiceStatus = Literal["draft", "sent", "paid", "overdue"]


class GenerateInvoiceRequest(BaseModel):
    project_id: int
    type: Literal["hourly", "fixed", "milestone"] = "hourly"

    # For MVP: only `hourly` uses this rate directly. Other types can be added later.
    rate: float = 0.0
    due_days: int = 30
    invoice_number: Optional[str] = None


class UpdateInvoiceRequest(BaseModel):
    status: Optional[InvoiceStatus] = None
    due_date: Optional[date] = None
    issued_date: Optional[date] = None
    subtotal: Optional[float] = None
    cgst: Optional[float] = None
    sgst: Optional[float] = None
    igst: Optional[float] = None
    total: Optional[float] = None


class InvoiceItemOut(BaseModel):
    id: int
    description: str
    quantity: float
    rate: float
    amount: float

    model_config = {"from_attributes": True}


class InvoiceOut(BaseModel):
    id: int
    project_id: int
    invoice_number: str
    subtotal: float
    cgst: float
    sgst: float
    igst: float
    total: float
    status: InvoiceStatus
    issued_date: Optional[date] = None
    due_date: Optional[date] = None
    created_at: datetime

    model_config = {"from_attributes": True}
