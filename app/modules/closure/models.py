import enum
from datetime import datetime

from sqlalchemy import Column, DateTime, Integer, String, Boolean, ForeignKey, Enum, Text, Float, func
from sqlalchemy.orm import relationship

from app.core.database import Base


class ClosureStatus(str, enum.Enum):
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    ON_HOLD = "on_hold"
    ARCHIVED = "archived"
    ESCALATION = "escalation"


class ProjectClosure(Base):
    __tablename__ = "project_closures"

    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey("projects.id", ondelete="CASCADE"), nullable=False, unique=True, index=True)
    
    status = Column(Enum(ClosureStatus), default=ClosureStatus.IN_PROGRESS, index=True)
    
    # Deliverables tracking
    deliverables_description = Column(Text, nullable=True)  # What was delivered
    deliverables_completed = Column(Boolean, default=False, index=True)
    deliverables_completed_at = Column(DateTime(timezone=True), nullable=True)
    deliverables_notes = Column(Text, nullable=True)
    
    # Final invoice
    final_invoice_generated = Column(Boolean, default=False, index=True)
    final_invoice_id = Column(Integer, nullable=True)  # Reference to invoices.id
    
    # Payment
    final_payment_received = Column(Boolean, default=False, index=True)
    final_payment_date = Column(DateTime(timezone=True), nullable=True)
    final_payment_amount = Column(Float, nullable=True)
    
    # Client feedback
    client_feedback = Column(Text, nullable=True)
    client_satisfaction_rating = Column(Integer, nullable=True)  # 1-5 scale
    
    # Project financials summary
    total_revenue = Column(Float, default=0.0)
    total_costs = Column(Float, default=0.0)
    final_profit = Column(Float, default=0.0)
    
    # Closure details
    closed_by = Column(Integer, nullable=True)  # user_id
    closure_notes = Column(Text, nullable=True)
    archival_reason = Column(Text, nullable=True)
    
    # Timestamps
    closure_initiated_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    closure_completed_at = Column(DateTime(timezone=True), nullable=True)
    archived_at = Column(DateTime(timezone=True), nullable=True)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    
    # Relationships
    closure_items = relationship("ClosureChecklist", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<ProjectClosure {self.id}: project_id={self.project_id}>"


class ClosureChecklist(Base):
    __tablename__ = "closure_checklists"

    id = Column(Integer, primary_key=True, index=True)
    closure_id = Column(Integer, ForeignKey("project_closures.id", ondelete="CASCADE"), nullable=False, index=True)
    project_id = Column(Integer, ForeignKey("projects.id", ondelete="CASCADE"), nullable=False, index=True)
    
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    
    is_completed = Column(Boolean, default=False, index=True)
    completed_at = Column(DateTime(timezone=True), nullable=True)
    
    notes = Column(Text, nullable=True)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    
    def __repr__(self):
        return f"<ClosureChecklist {self.id}: {self.title}>"
