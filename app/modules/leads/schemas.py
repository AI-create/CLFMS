from pydantic import BaseModel, EmailStr, Field
from datetime import datetime
from typing import Optional, List
from enum import Enum


class LeadStatusEnum(str, Enum):
    NEW = "new"
    CONTACTED = "contacted"
    QUALIFIED = "qualified"
    WON = "won"
    LOST = "lost"


class LeadSourceEnum(str, Enum):
    LINKEDIN = "linkedin"
    REFERRAL = "referral"
    WEBSITE = "website"
    EMAIL = "email"
    PHONE = "phone"
    OTHER = "other"


class LeadFollowUpBase(BaseModel):
    action: str
    notes: Optional[str] = None
    scheduled_date: Optional[datetime] = None


class LeadFollowUpCreate(LeadFollowUpBase):
    pass


class LeadFollowUpUpdate(BaseModel):
    action: Optional[str] = None
    notes: Optional[str] = None
    scheduled_date: Optional[datetime] = None
    completed_date: Optional[datetime] = None


class LeadFollowUpResponse(LeadFollowUpBase):
    id: int
    lead_id: int
    completed_date: Optional[datetime]
    created_at: datetime

    class Config:
        from_attributes = True


class LeadBase(BaseModel):
    company_name: str
    contact_name: str
    contact_email: EmailStr
    contact_phone: str
    status: Optional[LeadStatusEnum] = LeadStatusEnum.NEW
    source: Optional[LeadSourceEnum] = LeadSourceEnum.OTHER
    company_details: Optional[str] = None
    notes: Optional[str] = None


class LeadCreate(LeadBase):
    pass


class LeadUpdate(BaseModel):
    company_name: Optional[str] = None
    contact_name: Optional[str] = None
    contact_email: Optional[EmailStr] = None
    contact_phone: Optional[str] = None
    status: Optional[LeadStatusEnum] = None
    source: Optional[LeadSourceEnum] = None
    company_details: Optional[str] = None
    notes: Optional[str] = None


class LeadResponse(LeadBase):
    id: int
    created_at: datetime
    updated_at: datetime
    last_contacted_at: Optional[datetime]
    converted_client_id: Optional[int]
    converted_at: Optional[datetime]
    follow_ups: List[LeadFollowUpResponse] = []

    class Config:
        from_attributes = True


class LeadConvertToClient(BaseModel):
    gstin: str = Field(..., description="GST Identification Number")
    state: str = Field(..., description="State code (e.g., KA for Karnataka)")
    address: str
    advance_payment: Optional[float] = None


class LeadList(BaseModel):
    total: int
    items: List[LeadResponse]
