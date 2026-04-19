from sqlalchemy.orm import Session
from datetime import datetime
from typing import Optional, List

from app.modules.leads.models import Lead, LeadFollowUp, LeadStatus, LeadSource
from app.modules.leads.schemas import LeadCreate, LeadUpdate, LeadConvertToClient, LeadFollowUpCreate, LeadFollowUpUpdate
from app.modules.clients.services import create_client as create_client_service
from app.modules.clients.schemas import CreateClient


class LeadService:
    @staticmethod
    def create_lead(db: Session, lead: LeadCreate) -> Lead:
        """Create a new lead."""
        db_lead = Lead(
            company_name=lead.company_name,
            contact_name=lead.contact_name,
            contact_email=lead.contact_email,
            contact_phone=lead.contact_phone,
            status=lead.status or LeadStatus.NEW,
            source=lead.source or LeadSource.OTHER,
            company_details=lead.company_details,
            notes=lead.notes,
        )
        db.add(db_lead)
        db.commit()
        db.refresh(db_lead)
        return db_lead

    @staticmethod
    def get_lead(db: Session, lead_id: int) -> Optional[Lead]:
        """Retrieve a lead by ID."""
        return db.query(Lead).filter(Lead.id == lead_id).first()

    @staticmethod
    def list_leads(
        db: Session,
        skip: int = 0,
        limit: int = 10,
        status: Optional[str] = None,
        source: Optional[str] = None,
    ) -> tuple[int, List[Lead]]:
        """List leads with optional filters."""
        query = db.query(Lead)

        if status:
            query = query.filter(Lead.status == status)
        if source:
            query = query.filter(Lead.source == source)

        total = query.count()
        leads = query.offset(skip).limit(limit).all()
        return total, leads

    @staticmethod
    def update_lead(db: Session, lead_id: int, lead: LeadUpdate) -> Optional[Lead]:
        """Update a lead."""
        db_lead = db.query(Lead).filter(Lead.id == lead_id).first()
        if not db_lead:
            return None

        update_data = lead.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_lead, field, value)

        db_lead.updated_at = datetime.utcnow()
        db.commit()
        db.refresh(db_lead)
        return db_lead

    @staticmethod
    def update_lead_status(db: Session, lead_id: int, status: LeadStatus) -> Optional[Lead]:
        """Update lead status."""
        db_lead = db.query(Lead).filter(Lead.id == lead_id).first()
        if not db_lead:
            return None

        db_lead.status = status
        db_lead.last_contacted_at = datetime.utcnow()
        db_lead.updated_at = datetime.utcnow()
        db.commit()
        db.refresh(db_lead)
        return db_lead

    @staticmethod
    def convert_lead_to_client(
        db: Session, lead_id: int, conversion_data: LeadConvertToClient
    ) -> Optional[Lead]:
        """Convert a lead to a client."""
        db_lead = db.query(Lead).filter(Lead.id == lead_id).first()
        if not db_lead:
            return None

        # Create client from lead
        client_create = CreateClient(
            company_name=db_lead.company_name,
            gstin=conversion_data.gstin,
            state=conversion_data.state,
            address=conversion_data.address,
            contact_email=db_lead.contact_email,
            contact_phone=db_lead.contact_phone,
        )
        new_client = create_client_service(db, client_create)

        # Update lead
        db_lead.converted_client_id = new_client.id
        db_lead.converted_at = datetime.utcnow()
        db_lead.status = LeadStatus.WON
        db.commit()
        db.refresh(db_lead)
        return db_lead

    @staticmethod
    def delete_lead(db: Session, lead_id: int) -> bool:
        """Delete a lead."""
        db_lead = db.query(Lead).filter(Lead.id == lead_id).first()
        if not db_lead:
            return False
        db.delete(db_lead)
        db.commit()
        return True

    @staticmethod
    def create_follow_up(db: Session, lead_id: int, follow_up: LeadFollowUpCreate) -> Optional[LeadFollowUp]:
        """Create a follow-up for a lead."""
        lead = db.query(Lead).filter(Lead.id == lead_id).first()
        if not lead:
            return None

        db_follow_up = LeadFollowUp(
            lead_id=lead_id,
            action=follow_up.action,
            notes=follow_up.notes,
            scheduled_date=follow_up.scheduled_date,
        )
        db.add(db_follow_up)
        db.commit()
        db.refresh(db_follow_up)
        return db_follow_up

    @staticmethod
    def get_follow_up(db: Session, follow_up_id: int) -> Optional[LeadFollowUp]:
        """Retrieve a follow-up by ID."""
        return db.query(LeadFollowUp).filter(LeadFollowUp.id == follow_up_id).first()

    @staticmethod
    def update_follow_up(db: Session, follow_up_id: int, follow_up: LeadFollowUpUpdate) -> Optional[LeadFollowUp]:
        """Update a follow-up."""
        db_follow_up = db.query(LeadFollowUp).filter(LeadFollowUp.id == follow_up_id).first()
        if not db_follow_up:
            return None

        update_data = follow_up.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_follow_up, field, value)

        db.commit()
        db.refresh(db_follow_up)
        return db_follow_up

    @staticmethod
    def complete_follow_up(db: Session, follow_up_id: int) -> Optional[LeadFollowUp]:
        """Mark a follow-up as completed."""
        db_follow_up = db.query(LeadFollowUp).filter(LeadFollowUp.id == follow_up_id).first()
        if not db_follow_up:
            return None

        db_follow_up.completed_date = datetime.utcnow()
        db.commit()
        db.refresh(db_follow_up)
        return db_follow_up
