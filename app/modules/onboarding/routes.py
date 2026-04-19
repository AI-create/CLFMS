from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.response import api_success, api_error
from app.core.security import get_current_user, require_roles
from app.modules.onboarding.schemas import (
    OnboardingChecklistItemCreate,
    OnboardingChecklistItemUpdate,
    OnboardingChecklistItemMarkComplete,
    OnboardingChecklistItemResponse,
    ClientOnboardingCreate,
    ClientOnboardingUpdate,
    ClientOnboardingResponse,
    OnboardingProgressResponse,
)
from app.modules.onboarding.services import OnboardingService

router = APIRouter(prefix="/onboarding", tags=["Onboarding"])


@router.post("/clients/{client_id}/init", response_model=dict)
def initialize_onboarding(
    client_id: int,
    payload: ClientOnboardingCreate,
    db: Session = Depends(get_db),
    current_user=Depends(require_roles(["admin", "sales"])),
):
    """Initialize onboarding for a client with default checklist items."""
    # Check if onboarding already exists
    existing = OnboardingService.get_client_onboarding(db, client_id)
    if existing:
        return api_error("ALREADY_EXISTS", "Onboarding already initialized for this client", 400)

    onboarding = OnboardingService.create_client_onboarding(db, client_id, payload)
    return api_success(ClientOnboardingResponse.from_orm(onboarding).model_dump())


@router.get("/clients/{client_id}", response_model=dict)
def get_client_onboarding(
    client_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    """Get onboarding status and checklist for a client."""
    onboarding = OnboardingService.get_client_onboarding(db, client_id)
    if not onboarding:
        return api_error("NOT_FOUND", "Onboarding not initialized for this client", 404)

    return api_success(ClientOnboardingResponse.from_orm(onboarding).model_dump())


@router.get("/clients/{client_id}/progress", response_model=dict)
def get_onboarding_progress(
    client_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    """Get onboarding progress metrics."""
    onboarding = OnboardingService.get_client_onboarding(db, client_id)
    if not onboarding:
        return api_error("NOT_FOUND", "Onboarding not initialized for this client", 404)

    progress = OnboardingService.get_onboarding_progress(db, client_id)
    items = OnboardingService.get_checklist_items(db, client_id)

    response = OnboardingProgressResponse(
        total_items=progress["total_items"],
        completed_items=progress["completed_items"],
        progress_percentage=progress["progress_percentage"],
        status=onboarding.status,
        checklist=[OnboardingChecklistItemResponse.from_orm(item) for item in items],
    )
    return api_success(response.model_dump())


@router.put("/clients/{client_id}", response_model=dict)
def update_client_onboarding(
    client_id: int,
    payload: ClientOnboardingUpdate,
    db: Session = Depends(get_db),
    current_user=Depends(require_roles(["admin", "sales"])),
):
    """Update onboarding record."""
    onboarding = OnboardingService.update_client_onboarding(db, client_id, payload)
    if not onboarding:
        return api_error("NOT_FOUND", "Onboarding not found", 404)

    return api_success(ClientOnboardingResponse.from_orm(onboarding).model_dump())


@router.post("/clients/{client_id}/checklist", response_model=dict)
def add_checklist_item(
    client_id: int,
    payload: OnboardingChecklistItemCreate,
    db: Session = Depends(get_db),
    current_user=Depends(require_roles(["admin", "sales"])),
):
    """Add a new checklist item for a client."""
    try:
        item = OnboardingService.add_checklist_item(db, client_id, payload)
        return api_success(OnboardingChecklistItemResponse.from_orm(item).model_dump())
    except ValueError as e:
        return api_error("NOT_FOUND", str(e), 404)


@router.get("/clients/{client_id}/checklist", response_model=dict)
def get_checklist_items(
    client_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    """Get all checklist items for a client."""
    items = OnboardingService.get_checklist_items(db, client_id)
    return api_success(
        {"items": [OnboardingChecklistItemResponse.from_orm(item).model_dump() for item in items]}
    )


@router.get("/checklist-items/{item_id}", response_model=dict)
def get_checklist_item(
    item_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    """Get a specific checklist item."""
    item = OnboardingService.get_checklist_item(db, item_id)
    if not item:
        return api_error("NOT_FOUND", "Checklist item not found", 404)

    return api_success(OnboardingChecklistItemResponse.from_orm(item).model_dump())


@router.put("/checklist-items/{item_id}", response_model=dict)
def update_checklist_item(
    item_id: int,
    payload: OnboardingChecklistItemUpdate,
    db: Session = Depends(get_db),
    current_user=Depends(require_roles(["admin", "sales"])),
):
    """Update a checklist item."""
    item = OnboardingService.update_checklist_item(db, item_id, payload)
    if not item:
        return api_error("NOT_FOUND", "Checklist item not found", 404)

    return api_success(OnboardingChecklistItemResponse.from_orm(item).model_dump())


@router.post("/checklist-items/{item_id}/complete", response_model=dict)
def mark_item_complete(
    item_id: int,
    payload: OnboardingChecklistItemMarkComplete,
    db: Session = Depends(get_db),
    current_user=Depends(require_roles(["admin", "sales"])),
):
    """Mark a checklist item as complete."""
    item = OnboardingService.mark_checklist_item_complete(
        db, item_id, notes=payload.notes
    )
    if not item:
        return api_error("NOT_FOUND", "Checklist item not found", 404)

    return api_success(OnboardingChecklistItemResponse.from_orm(item).model_dump())


@router.delete("/checklist-items/{item_id}", response_model=dict)
def delete_checklist_item(
    item_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(require_roles(["admin"])),
):
    """Delete a checklist item."""
    success = OnboardingService.delete_checklist_item(db, item_id)
    if not success:
        return api_error("NOT_FOUND", "Checklist item not found", 404)

    return api_success({"message": "Checklist item deleted successfully"})
