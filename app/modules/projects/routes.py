from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.response import api_error, api_success
from app.core.security import require_roles
from app.modules.projects import services
from app.modules.projects.schemas import CreateProject, ProjectOut
from app.services.activity_logging_service import log_activity
from app.services.billing_service import trigger_project_billing


router = APIRouter(tags=["Projects"])


@router.post("/projects")
def create_project(
    payload: CreateProject,
    db: Session = Depends(get_db),
    _user=Depends(require_roles(["admin", "project_manager", "pm", "sales", "operations", "finance"])),
):
    project = services.create_project(db, payload)
    
    # Log the activity
    log_activity(
        db=db,
        user_email=_user.get("email"),
        action="create",
        entity_type="project",
        entity_id=project.id,
        entity_name=payload.name,
        new_values=payload.model_dump(),
        description=f"Created project: {payload.name}"
    )
    
    return api_success(ProjectOut.model_validate(project))


@router.get("/projects")
def list_projects(
    client_id: int | None = None,
    page: int = 1,
    limit: int = 20,
    db: Session = Depends(get_db),
    _user=Depends(require_roles(["admin", "project_manager", "pm", "sales", "operations", "finance"])),
):
    page = max(page, 1)
    limit = min(max(limit, 1), 100)

    rows, total = services.list_projects(db, client_id=client_id, page=page, limit=limit)
    return api_success(
        {
            "data": [ProjectOut.model_validate(p) for p in rows],
            "meta": {"total": total, "page": page, "limit": limit},
        }
    )


@router.get("/projects/{project_id}")
def get_project(
    project_id: int,
    db: Session = Depends(get_db),
    _user=Depends(require_roles(["admin", "project_manager", "pm", "sales", "operations", "finance"])),
):
    project = services.get_project(db, project_id)
    if not project:
        return api_error("NOT_FOUND", "Project not found", http_status=404)
    return api_success(ProjectOut.model_validate(project))


@router.delete("/projects/{project_id}")
def delete_project(
    project_id: int,
    db: Session = Depends(get_db),
    _user=Depends(require_roles(["admin", "project_manager", "pm"])),
):
    project = services.get_project(db, project_id)
    if not project:
        return api_error("NOT_FOUND", "Project not found", http_status=404)

    name = project.name
    services.delete_project(db, project_id)

    log_activity(
        db=db,
        user_email=_user.get("email"),
        action="delete",
        entity_type="project",
        entity_id=project_id,
        entity_name=name,
        description=f"Deleted project: {name}"
    )

    return api_success({"message": f"Project '{name}' deleted successfully"})


@router.put("/projects/{project_id}")
def update_project(
    project_id: int,
    payload: CreateProject,
    db: Session = Depends(get_db),
    _user=Depends(require_roles(["admin", "project_manager", "pm", "sales", "operations", "finance"])),
):
    project = services.update_project(db, project_id, payload)
    if not project:
        return api_error("NOT_FOUND", "Project not found", http_status=404)
    return api_success(ProjectOut.model_validate(project))


@router.post("/projects/{project_id}/trigger-billing")
def trigger_billing(
    project_id: int,
    db: Session = Depends(get_db),
    _user=Depends(require_roles(["admin", "finance"])),
):
    """Manually trigger invoice generation for a project based on its billing_type.
    Works regardless of auto_billing_enabled or next_billing_date schedule."""
    try:
        result = trigger_project_billing(db, project_id)
    except ValueError as exc:
        return api_error("BAD_REQUEST", str(exc), http_status=400)

    log_activity(
        db=db,
        user_email=_user.get("email"),
        action="create",
        entity_type="invoice",
        entity_id=result["invoice_id"],
        entity_name=result["invoice_number"],
        description=f"Triggered {result['billing_type']} billing for project {project_id} → {result['invoice_number']}",
    )

    return api_success(result)
