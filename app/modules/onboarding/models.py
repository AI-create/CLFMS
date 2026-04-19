import enum
from datetime import datetime

from sqlalchemy import Column, DateTime, Integer, String, Boolean, ForeignKey, Enum, Text, func
from sqlalchemy.orm import relationship

from app.core.database import Base


class OnboardingChecklistItemType(str, enum.Enum):
    NDA_SIGNED = "nda_signed"
    AGREEMENT_SIGNED = "agreement_signed"
    ADVANCE_PAYMENT_RECEIVED = "advance_payment_received"
    KYC_DOCUMENTS_UPLOADED = "kyc_documents_uploaded"
    LEGAL_REVIEW_APPROVED = "legal_review_approved"
    PAYMENT_METHOD_CONFIGURED = "payment_method_configured"
    CUSTOM = "custom"


class OnboardingChecklistItem(Base):
    __tablename__ = "onboarding_checklist_items"

    id = Column(Integer, primary_key=True, index=True)
    onboarding_id = Column(Integer, ForeignKey("client_onboardings.id", ondelete="CASCADE"), nullable=False, index=True)
    client_id = Column(Integer, ForeignKey("clients.id", ondelete="CASCADE"), nullable=False, index=True)
    
    item_type = Column(Enum(OnboardingChecklistItemType), nullable=False, index=True)
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    
    is_completed = Column(Boolean, default=False, index=True)
    completed_at = Column(DateTime(timezone=True), nullable=True)
    completed_by = Column(Integer, nullable=True)  # user_id who marked as completed
    
    notes = Column(Text, nullable=True)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    
    def __repr__(self):
        return f"<OnboardingChecklistItem {self.id}: {self.item_type}>"


class ClientOnboarding(Base):
    __tablename__ = "client_onboardings"

    id = Column(Integer, primary_key=True, index=True)
    client_id = Column(Integer, ForeignKey("clients.id", ondelete="CASCADE"), nullable=False, unique=True, index=True)
    
    status = Column(String, default="in_progress", index=True)  # in_progress, completed, on_hold
    started_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    completed_at = Column(DateTime(timezone=True), nullable=True)
    
    assigned_to = Column(Integer, nullable=True)  # user_id responsible for onboarding
    
    notes = Column(Text, nullable=True)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    
    # Relationships
    checklist_items = relationship("OnboardingChecklistItem", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<ClientOnboarding {self.id}: client_id={self.client_id}>"
