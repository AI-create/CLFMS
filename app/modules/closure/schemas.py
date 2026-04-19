from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime
from enum import Enum


class ClosureStatusEnum(str, Enum):
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    ON_HOLD = "on_hold"
    ARCHIVED = "archived"


class ClosureChecklistItemCreate(BaseModel):
    title: str
    description: Optional[str] = None
    notes: Optional[str] = None


class ClosureChecklistItemUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    is_completed: Optional[bool] = None
    notes: Optional[str] = None


class ClosureChecklistItemResponse(BaseModel):
    id: int
    title: str
    description: Optional[str]
    is_completed: bool
    completed_at: Optional[datetime]
    notes: Optional[str]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class ProjectClosureCreate(BaseModel):
    deliverables_description: Optional[str] = None
    closure_notes: Optional[str] = None


class ProjectClosureUpdate(BaseModel):
    status: Optional[ClosureStatusEnum] = None
    deliverables_description: Optional[str] = None
    deliverables_completed: Optional[bool] = None
    deliverables_notes: Optional[str] = None
    final_invoice_id: Optional[int] = None
    client_feedback: Optional[str] = None
    client_satisfaction_rating: Optional[int] = None
    closure_notes: Optional[str] = None
    archival_reason: Optional[str] = None


class ProjectClosureMarkDeliverablesComplete(BaseModel):
    notes: Optional[str] = None


class ProjectClosureMarkFinalPaymentReceived(BaseModel):
    amount: float
    notes: Optional[str] = None


class ProjectClosureArchive(BaseModel):
    reason: Optional[str] = None


class ProjectClosureResponse(BaseModel):
    id: int
    project_id: int
    status: str
    
    deliverables_description: Optional[str]
    deliverables_completed: bool
    deliverables_completed_at: Optional[datetime]
    deliverables_notes: Optional[str]
    
    final_invoice_generated: bool
    final_invoice_id: Optional[int]
    
    final_payment_received: bool
    final_payment_date: Optional[datetime]
    final_payment_amount: Optional[float]
    
    client_feedback: Optional[str]
    client_satisfaction_rating: Optional[int]
    
    total_revenue: float
    total_costs: float
    final_profit: float
    
    closure_notes: Optional[str]
    archival_reason: Optional[str]
    
    closure_initiated_at: datetime
    closure_completed_at: Optional[datetime]
    archived_at: Optional[datetime]
    
    created_at: datetime
    updated_at: datetime
    closure_items: List[ClosureChecklistItemResponse] = []

    class Config:
        from_attributes = True


class ProjectClosureProgressResponse(BaseModel):
    total_items: int
    completed_items: int
    progress_percentage: float
    deliverables_completed: bool
    final_payment_received: bool
    status: str
    checklist: List[ClosureChecklistItemResponse]

    class Config:
        from_attributes = True
