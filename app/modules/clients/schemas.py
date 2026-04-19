from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class CreateClient(BaseModel):
    company_name: str
    gstin: Optional[str] = None
    state: Optional[str] = None
    address: Optional[str] = None
    contact_email: Optional[str] = None
    contact_phone: Optional[str] = None


class ClientOut(BaseModel):
    id: int
    company_name: str
    gstin: Optional[str] = None
    state: Optional[str] = None
    address: Optional[str] = None
    contact_email: Optional[str] = None
    contact_phone: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class PaginatedClients(BaseModel):
    data: list[ClientOut]
    meta: dict
