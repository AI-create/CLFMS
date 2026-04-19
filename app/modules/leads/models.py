from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, Text, ForeignKey, Enum
from sqlalchemy.orm import relationship
import enum

from app.core.database import Base


class LeadStatus(str, enum.Enum):
    NEW = "new"
    CONTACTED = "contacted"
    QUALIFIED = "qualified"
    WON = "won"
    LOST = "lost"


class LeadSource(str, enum.Enum):
    LINKEDIN = "linkedin"
    REFERRAL = "referral"
    WEBSITE = "website"
    EMAIL = "email"
    PHONE = "phone"
    OTHER = "other"


class Lead(Base):
    __tablename__ = "leads"

    id = Column(Integer, primary_key=True, index=True)
    company_name = Column(String(255), nullable=False, index=True)
    contact_name = Column(String(255), nullable=False)
    contact_email = Column(String(255), nullable=False, unique=True, index=True)
    contact_phone = Column(String(20), nullable=False)
    
    status = Column(Enum(LeadStatus), default=LeadStatus.NEW, index=True)
    source = Column(Enum(LeadSource), default=LeadSource.OTHER)
    
    company_details = Column(Text, nullable=True)  # JSON or detailed info
    notes = Column(Text, nullable=True)
    
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    last_contacted_at = Column(DateTime, nullable=True)
    
    # When lead is converted to client
    converted_client_id = Column(Integer, ForeignKey("clients.id"), nullable=True, index=True)
    converted_at = Column(DateTime, nullable=True)
    
    # Relationships
    follow_ups = relationship("LeadFollowUp", back_populates="lead", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Lead {self.id}: {self.company_name}>"


class LeadFollowUp(Base):
    __tablename__ = "lead_follow_ups"

    id = Column(Integer, primary_key=True, index=True)
    lead_id = Column(Integer, ForeignKey("leads.id"), nullable=False, index=True)
    
    action = Column(String(255), nullable=False)
    notes = Column(Text, nullable=True)
    scheduled_date = Column(DateTime, nullable=True)
    completed_date = Column(DateTime, nullable=True)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    lead = relationship("Lead", back_populates="follow_ups")
    
    def __repr__(self):
        return f"<LeadFollowUp {self.id}: Lead {self.lead_id}>"
