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


class ProjectOut(BaseModel):
    id: int
    client_id: int
    name: str
    description: Optional[str] = None
    status: str
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    budget: Optional[float] = None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}
