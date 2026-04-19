from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime
from enum import Enum


class OnboardingChecklistItemTypeEnum(str, Enum):
    NDA_SIGNED = "nda_signed"
    AGREEMENT_SIGNED = "agreement_signed"
    ADVANCE_PAYMENT_RECEIVED = "advance_payment_received"
    KYC_DOCUMENTS_UPLOADED = "kyc_documents_uploaded"
    LEGAL_REVIEW_APPROVED = "legal_review_approved"
    PAYMENT_METHOD_CONFIGURED = "payment_method_configured"
    CUSTOM = "custom"


class OnboardingChecklistItemCreate(BaseModel):
    item_type: OnboardingChecklistItemTypeEnum
    title: str
    description: Optional[str] = None
    notes: Optional[str] = None


class OnboardingChecklistItemUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    is_completed: Optional[bool] = None
    notes: Optional[str] = None


class OnboardingChecklistItemMarkComplete(BaseModel):
    notes: Optional[str] = None


class OnboardingChecklistItemResponse(BaseModel):
    id: int
    item_type: str
    title: str
    description: Optional[str]
    is_completed: bool
    completed_at: Optional[datetime]
    completed_by: Optional[int]
    notes: Optional[str]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class ClientOnboardingCreate(BaseModel):
    assigned_to: Optional[int] = None
    notes: Optional[str] = None


class ClientOnboardingUpdate(BaseModel):
    status: Optional[str] = None
    assigned_to: Optional[int] = None
    notes: Optional[str] = None


class ClientOnboardingResponse(BaseModel):
    id: int
    client_id: int
    status: str
    started_at: datetime
    completed_at: Optional[datetime]
    assigned_to: Optional[int]
    notes: Optional[str]
    created_at: datetime
    updated_at: datetime
    checklist_items: List[OnboardingChecklistItemResponse] = []

    class Config:
        from_attributes = True


class OnboardingProgressResponse(BaseModel):
    total_items: int
    completed_items: int
    progress_percentage: float
    status: str
    checklist: List[OnboardingChecklistItemResponse]

    class Config:
        from_attributes = True
