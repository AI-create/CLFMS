from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import Optional

from app.core.database import get_db
from app.core.response import api_success, api_error
from app.core.security import get_current_user
from app.modules.leads.schemas import (
    LeadCreate,
    LeadUpdate,
    LeadResponse,
    LeadList,
    LeadConvertToClient,
    LeadFollowUpCreate,
    LeadFollowUpUpdate,
    LeadFollowUpResponse,
    LeadStatusEnum,
    LeadSourceEnum,
)
from app.modules.leads.services import LeadService
from app.modules.leads.models import LeadStatus, LeadSource

router = APIRouter(prefix="/leads", tags=["leads"])


@router.post("", response_model=dict)
def create_lead(lead: LeadCreate, db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    """Create a new lead."""
    new_lead = LeadService.create_lead(db, lead)
    return api_success(LeadResponse.from_orm(new_lead).model_dump())


@router.get("/{lead_id}", response_model=dict)
def get_lead(lead_id: int, db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    """Retrieve a lead by ID."""
    lead = LeadService.get_lead(db, lead_id)
    if not lead:
        return api_error("not_found", "Lead not found", 404)
    return api_success(LeadResponse.from_orm(lead).model_dump())


@router.get("", response_model=dict)
def list_leads(
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    status: Optional[str] = Query(None),
    source: Optional[str] = Query(None),
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    """List all leads with optional filters."""
    total, leads = LeadService.list_leads(db, skip=skip, limit=limit, status=status, source=source)
    lead_list = LeadList(
        total=total,
        items=[LeadResponse.from_orm(lead) for lead in leads],
    )
    return api_success(lead_list.model_dump())


@router.put("/{lead_id}", response_model=dict)
def update_lead(
    lead_id: int,
    lead: LeadUpdate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    """Update a lead."""
    updated_lead = LeadService.update_lead(db, lead_id, lead)
    if not updated_lead:
        return api_error("not_found", "Lead not found", 404)
    return api_success(LeadResponse.from_orm(updated_lead).model_dump())


@router.patch("/{lead_id}/status", response_model=dict)
def update_lead_status(
    lead_id: int,
    status: LeadStatusEnum,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    """Update lead status."""
    lead_status = LeadStatus(status.value)
    updated_lead = LeadService.update_lead_status(db, lead_id, lead_status)
    if not updated_lead:
        return api_error("not_found", "Lead not found", 404)
    return api_success(LeadResponse.from_orm(updated_lead).model_dump())


@router.post("/{lead_id}/convert-to-client", response_model=dict)
def convert_lead_to_client(
    lead_id: int,
    conversion_data: LeadConvertToClient,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    """Convert a lead to a client."""
    converted_lead = LeadService.convert_lead_to_client(db, lead_id, conversion_data)
    if not converted_lead:
        return api_error("not_found", "Lead not found", 404)
    return api_success(
        {
            "lead": LeadResponse.from_orm(converted_lead).model_dump(),
            "client_id": converted_lead.converted_client_id,
        }
    )


@router.delete("/{lead_id}", response_model=dict)
def delete_lead(lead_id: int, db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    """Delete a lead."""
    deleted = LeadService.delete_lead(db, lead_id)
    if not deleted:
        return api_error("not_found", "Lead not found", 404)
    return api_success({"message": "Lead deleted successfully"})


# Follow-up endpoints
@router.post("/{lead_id}/follow-ups", response_model=dict)
def create_follow_up(
    lead_id: int,
    follow_up: LeadFollowUpCreate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    """Create a follow-up for a lead."""
    new_follow_up = LeadService.create_follow_up(db, lead_id, follow_up)
    if not new_follow_up:
        return api_error("not_found", "Lead not found", 404)
    return api_success(LeadFollowUpResponse.from_orm(new_follow_up).model_dump())


@router.get("/{lead_id}/follow-ups", response_model=dict)
def get_lead_follow_ups(lead_id: int, db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    """Get all follow-ups for a lead."""
    lead = LeadService.get_lead(db, lead_id)
    if not lead:
        return api_error("not_found", "Lead not found", 404)
    return api_success(
        {
            "lead_id": lead_id,
            "follow_ups": [LeadFollowUpResponse.from_orm(fu).model_dump() for fu in lead.follow_ups],
        }
    )


@router.put("/follow-ups/{follow_up_id}", response_model=dict)
def update_follow_up(
    follow_up_id: int,
    follow_up: LeadFollowUpUpdate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    """Update a follow-up."""
    updated_follow_up = LeadService.update_follow_up(db, follow_up_id, follow_up)
    if not updated_follow_up:
        return api_error("not_found", "Follow-up not found", 404)
    return api_success(LeadFollowUpResponse.from_orm(updated_follow_up).model_dump())


@router.patch("/follow-ups/{follow_up_id}/complete", response_model=dict)
def complete_follow_up(
    follow_up_id: int, db: Session = Depends(get_db), current_user=Depends(get_current_user)
):
    """Mark a follow-up as completed."""
    completed_follow_up = LeadService.complete_follow_up(db, follow_up_id)
    if not completed_follow_up:
        return api_error("not_found", "Follow-up not found", 404)
    return api_success(LeadFollowUpResponse.from_orm(completed_follow_up).model_dump())
