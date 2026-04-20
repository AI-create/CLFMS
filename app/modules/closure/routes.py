from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.orm import Session
import logging

from app.core.database import get_db
from app.core.response import api_success, api_error
from app.core.security import require_roles
from app.modules.closure.models import ProjectClosure, ClosureStatus
from app.modules.closure.schemas import (
    ClosureChecklistItemCreate,
    ClosureChecklistItemUpdate,
    ClosureChecklistItemResponse,
    ProjectClosureCreate,
    ProjectClosureUpdate,
    ProjectClosureMarkDeliverablesComplete,
    ProjectClosureMarkFinalPaymentReceived,
    ProjectClosureArchive,
    ProjectClosureResponse,
    ProjectClosureProgressResponse,
)
from app.modules.closure.services import ClosureService

logger = logging.getLogger("clfms")

router = APIRouter(prefix="/closure", tags=["Closure"])


@router.post("/projects/{project_id}/initiate", response_model=dict)
def initiate_closure(
    project_id: int,
    payload: ProjectClosureCreate,
    db: Session = Depends(get_db),
    _user=Depends(require_roles(["admin", "project_manager", "pm"])),
):
    """Initiate closure process for a project."""
    closure = ClosureService.initiate_project_closure(db, project_id, payload)
    return api_success(ProjectClosureResponse.from_orm(closure).model_dump())


@router.get("/projects/{project_id}", response_model=dict)
def get_project_closure(
    project_id: int,
    db: Session = Depends(get_db),
    _user=Depends(require_roles(["admin", "project_manager", "pm", "finance"])),
):
    """Get closure status for a project."""
    closure = ClosureService.get_project_closure(db, project_id)
    if not closure:
        return api_error("NOT_FOUND", "Closure not initiated for this project", 404)

    return api_success(ProjectClosureResponse.from_orm(closure).model_dump())


@router.get("/projects/{project_id}/progress", response_model=dict)
def get_closure_progress(
    project_id: int,
    db: Session = Depends(get_db),
    _user=Depends(require_roles(["admin", "project_manager", "pm", "finance"])),
):
    """Get closure progress metrics."""
    closure = ClosureService.get_project_closure(db, project_id)
    if not closure:
        return api_error("NOT_FOUND", "Closure not initiated for this project", 404)

    progress = ClosureService.get_closure_progress(db, project_id)
    items = ClosureService.get_closure_checklist_items(db, project_id)

    response = ProjectClosureProgressResponse(
        total_items=progress["total_items"],
        completed_items=progress["completed_items"],
        progress_percentage=progress["progress_percentage"],
        deliverables_completed=closure.deliverables_completed,
        final_payment_received=closure.final_payment_received,
        status=closure.status,
        checklist=[ClosureChecklistItemResponse.from_orm(item) for item in items],
    )
    return api_success(response.model_dump())


@router.put("/projects/{project_id}", response_model=dict)
def update_closure(
    project_id: int,
    payload: ProjectClosureUpdate,
    db: Session = Depends(get_db),
    _user=Depends(require_roles(["admin", "project_manager", "pm", "finance"])),
):
    """Update closure record."""
    closure = ClosureService.update_project_closure(db, project_id, payload)
    if not closure:
        return api_error("NOT_FOUND", "Closure not found", 404)

    return api_success(ProjectClosureResponse.from_orm(closure).model_dump())


@router.post("/projects/{project_id}/mark-deliverables-complete", response_model=dict)
def mark_deliverables_complete(
    project_id: int,
    payload: ProjectClosureMarkDeliverablesComplete,
    db: Session = Depends(get_db),
    _user=Depends(require_roles(["admin", "project_manager", "pm"])),
):
    """Mark deliverables as complete."""
    closure = ClosureService.mark_deliverables_complete(db, project_id, payload.notes)
    if not closure:
        return api_error("NOT_FOUND", "Closure not found", 404)

    return api_success(ProjectClosureResponse.from_orm(closure).model_dump())


@router.post("/projects/{project_id}/mark-payment-received", response_model=dict)
def mark_payment_received(
    project_id: int,
    payload: ProjectClosureMarkFinalPaymentReceived,
    db: Session = Depends(get_db),
    _user=Depends(require_roles(["admin", "finance"])),
):
    """Record receipt of final payment."""
    closure = ClosureService.mark_final_payment_received(
        db, project_id, payload.amount, payload.notes
    )
    if not closure:
        return api_error("NOT_FOUND", "Closure not found", 404)

    return api_success(ProjectClosureResponse.from_orm(closure).model_dump())


@router.post("/projects/{project_id}/mark-completed", response_model=dict)
def mark_closure_completed(
    project_id: int,
    db: Session = Depends(get_db),
    _user=Depends(require_roles(["admin", "project_manager", "pm"])),
):
    """Mark project closure as completed."""
    closure = ClosureService.mark_closure_completed(db, project_id)
    if not closure:
        return api_error("NOT_FOUND", "Closure not found", 404)

    return api_success(ProjectClosureResponse.from_orm(closure).model_dump())


@router.post("/projects/{project_id}/archive", response_model=dict)
def archive_project(
    project_id: int,
    payload: ProjectClosureArchive,
    db: Session = Depends(get_db),
    _user=Depends(require_roles(["admin", "project_manager", "pm"])),
):
    """Archive a completed project."""
    closure = ClosureService.archive_project(db, project_id, payload.reason)
    if not closure:
        return api_error("NOT_FOUND", "Closure not found", 404)

    return api_success(ProjectClosureResponse.from_orm(closure).model_dump())


@router.post("/projects/{project_id}/checklist", response_model=dict)
def add_checklist_item(
    project_id: int,
    payload: ClosureChecklistItemCreate,
    db: Session = Depends(get_db),
    _user=Depends(require_roles(["admin", "project_manager", "pm"])),
):
    """Add a custom checklist item."""
    try:
        item = ClosureService.add_closure_checklist_item(db, project_id, payload)
        return api_success(ClosureChecklistItemResponse.from_orm(item).model_dump())
    except ValueError as e:
        logger.warning("Closure checklist add rejected for project_id=%s: %s", project_id, e)
        return api_error("NOT_FOUND", "Project or closure not found", 404)


@router.get("/projects/{project_id}/checklist", response_model=dict)
def get_checklist_items(
    project_id: int,
    db: Session = Depends(get_db),
    _user=Depends(require_roles(["admin", "project_manager", "pm", "finance"])),
):
    """Get closure checklist items."""
    items = ClosureService.get_closure_checklist_items(db, project_id)
    return api_success(
        {"items": [ClosureChecklistItemResponse.from_orm(item).model_dump() for item in items]}
    )


@router.get("/checklist-items/{item_id}", response_model=dict)
def get_checklist_item(
    item_id: int,
    db: Session = Depends(get_db),
    _user=Depends(require_roles(["admin", "project_manager", "pm", "finance"])),
):
    """Get a specific checklist item."""
    item = ClosureService.get_closure_checklist_item(db, item_id)
    if not item:
        return api_error("NOT_FOUND", "Checklist item not found", 404)

    return api_success(ClosureChecklistItemResponse.from_orm(item).model_dump())


@router.put("/checklist-items/{item_id}", response_model=dict)
def update_checklist_item(
    item_id: int,
    payload: ClosureChecklistItemUpdate,
    db: Session = Depends(get_db),
    _user=Depends(require_roles(["admin", "project_manager", "pm"])),
):
    """Update a checklist item."""
    item = ClosureService.update_closure_checklist_item(db, item_id, payload)
    if not item:
        return api_error("NOT_FOUND", "Checklist item not found", 404)

    return api_success(ClosureChecklistItemResponse.from_orm(item).model_dump())


@router.post("/checklist-items/{item_id}/complete", response_model=dict)
def mark_item_complete(
    item_id: int,
    payload: ClosureChecklistItemUpdate,
    db: Session = Depends(get_db),
    _user=Depends(require_roles(["admin", "project_manager", "pm"])),
):
    """Mark a checklist item as complete."""
    item = ClosureService.mark_closure_item_complete(db, item_id, payload.notes)
    if not item:
        return api_error("NOT_FOUND", "Checklist item not found", 404)

    return api_success(ClosureChecklistItemResponse.from_orm(item).model_dump())


@router.delete("/checklist-items/{item_id}", response_model=dict)
def delete_checklist_item(
    item_id: int,
    db: Session = Depends(get_db),
    _user=Depends(require_roles(["admin"])),
):
    """Delete a checklist item."""
    success = ClosureService.delete_closure_checklist_item(db, item_id)
    if not success:
        return api_error("NOT_FOUND", "Checklist item not found", 404)

    return api_success({"message": "Checklist item deleted successfully"})


@router.get("/project-locks", response_model=dict)
def get_project_locks(
    db: Session = Depends(get_db),
    _user=Depends(require_roles(["admin", "project_manager", "pm", "finance"])),
):
    """Return lock status for all projects that have a closure record.

    Lock rules:
    - completed / archived  → can_edit=False, can_delete=False
    - escalation            → can_edit=True,  can_delete=False
    - in_progress / on_hold → not locked (omitted from result)
    """
    closures = db.execute(select(ProjectClosure)).scalars().all()
    locks = {}
    for c in closures:
        if c.status in (ClosureStatus.COMPLETED, ClosureStatus.ARCHIVED):
            locks[c.project_id] = {"status": c.status, "can_edit": False, "can_delete": False}
        elif c.status == ClosureStatus.ESCALATION:
            locks[c.project_id] = {"status": c.status, "can_edit": True, "can_delete": False}
    return api_success(locks)
