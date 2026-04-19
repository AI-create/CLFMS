from datetime import date, datetime
from typing import Optional

from pydantic import BaseModel


class CreateTask(BaseModel):
    project_id: int
    title: str
    description: Optional[str] = None
    status: Optional[str] = "todo"
    priority: Optional[str] = None
    assigned_to: Optional[int] = None
    estimated_hours: Optional[float] = None


class TaskOut(BaseModel):
    id: int
    project_id: int
    title: str
    description: Optional[str] = None
    status: str
    priority: Optional[str] = None
    assigned_to: Optional[int] = None
    estimated_hours: Optional[float] = None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class CreateTimeLog(BaseModel):
    task_id: int
    hours: float
    log_date: Optional[date] = None
    notes: Optional[str] = None
    user_id: Optional[int] = None


class TimeLogOut(BaseModel):
    id: int
    task_id: int
    user_id: Optional[int] = None
    hours: float
    log_date: Optional[date] = None
    notes: Optional[str] = None
    created_at: datetime

    model_config = {"from_attributes": True}
