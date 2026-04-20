"""Research Management Routes"""
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from datetime import datetime

from app.core.database import get_db
from app.core.response import api_error, api_success
from app.core.security import require_roles
from app.modules.research import services
from app.modules.research.schemas import (
    CreateResearchProject,
    UpdateResearchProject,
    CreateExperiment,
    CreateResearchLog,
    ResearchProjectOut,
    ExperimentOut,
    ResearchLogOut,
    PaginatedResearchProjects,
    PaginatedExperiments,
)
from app.services.activity_logging_service import log_activity


router = APIRouter(tags=["Research"])


# ===== RESEARCH PROJECTS =====

@router.post("/research-projects")
def create_research_project(
    payload: CreateResearchProject,
    db: Session = Depends(get_db),
    _user=Depends(require_roles(["admin", "finance", "project_manager"])),
):
    """Create a new research project"""
    project = services.ResearchService.create_research_project(db, payload)
    
    # Log the activity
    log_activity(
        db=db,
        user_email=_user.get("email"),
        action="create",
        entity_type="research_project",
        entity_id=project.id,
        entity_name=payload.name,
        new_values=payload.model_dump(),
        description=f"Created research project: {payload.name}"
    )
    
    return api_success(ResearchProjectOut.model_validate(project))


@router.get("/research-projects")
def list_research_projects(
    client_id: int | None = Query(None),
    research_type: str | None = Query(None),
    status: str | None = Query(None),
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
    _user=Depends(require_roles(["admin", "finance", "project_manager"])),
):
    """List research projects with filters"""
    projects, total = services.ResearchService.list_research_projects(
        db,
        client_id=client_id,
        research_type=research_type,
        status=status,
        page=page,
        limit=limit,
    )
    
    return api_success(
        PaginatedResearchProjects(
            data=[ResearchProjectOut.model_validate(p) for p in projects],
            meta={"total": total, "page": page, "limit": limit},
        ).model_dump()
    )


@router.get("/research-projects/{project_id}")
def get_research_project(
    project_id: int,
    db: Session = Depends(get_db),
    _user=Depends(require_roles(["admin", "finance", "project_manager"])),
):
    """Get a research project by ID"""
    project = services.ResearchService.get_research_project(db, project_id)
    if not project:
        return api_error("NOT_FOUND", "Research project not found", http_status=404)
    return api_success(ResearchProjectOut.model_validate(project))


@router.put("/research-projects/{project_id}")
def update_research_project(
    project_id: int,
    payload: UpdateResearchProject,
    db: Session = Depends(get_db),
    _user=Depends(require_roles(["admin", "finance", "project_manager"])),
):
    """Update a research project"""
    project = services.ResearchService.update_research_project(db, project_id, payload)
    if not project:
        return api_error("NOT_FOUND", "Research project not found", http_status=404)
    
    # Log the activity
    log_activity(
        db=db,
        user_email=_user.get("email"),
        action="update",
        entity_type="research_project",
        entity_id=project.id,
        entity_name=project.name,
        new_values=payload.model_dump(exclude_unset=True),
        description=f"Updated research project: {project.name}"
    )
    
    return api_success(ResearchProjectOut.model_validate(project))


@router.get("/research-projects/{project_id}/summary")
def get_project_summary(
    project_id: int,
    db: Session = Depends(get_db),
    _user=Depends(require_roles(["admin", "finance", "project_manager"])),
):
    """Get a summary of research project activity"""
    summary = services.ResearchService.get_project_summary(db, project_id)
    if not summary:
        return api_error("NOT_FOUND", "Research project not found", http_status=404)
    return api_success(summary)


# ===== EXPERIMENTS =====

@router.post("/research-projects/{project_id}/experiments")
def create_experiment(
    project_id: int,
    payload: CreateExperiment,
    db: Session = Depends(get_db),
    _user=Depends(require_roles(["admin", "finance", "project_manager"])),
):
    """Create an experiment for a research project"""
    # Verify project exists
    project = services.ResearchService.get_research_project(db, project_id)
    if not project:
        return api_error("NOT_FOUND", "Research project not found", http_status=404)
    
    experiment = services.ResearchService.create_experiment(db, project_id, payload)
    
    # Log the activity
    log_activity(
        db=db,
        user_email=_user.get("email"),
        action="create",
        entity_type="experiment",
        entity_id=experiment.id,
        entity_name=payload.title,
        new_values=payload.model_dump(),
        description=f"Created experiment: {payload.title}"
    )
    
    return api_success(ExperimentOut.model_validate(experiment))


@router.get("/research-projects/{project_id}/experiments")
def list_experiments(
    project_id: int,
    status: str | None = Query(None),
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
    _user=Depends(require_roles(["admin", "finance", "project_manager"])),
):
    """List experiments for a project"""
    # Verify project exists
    project = services.ResearchService.get_research_project(db, project_id)
    if not project:
        return api_error("NOT_FOUND", "Research project not found", http_status=404)
    
    experiments, total = services.ResearchService.list_experiments(
        db,
        project_id=project_id,
        status=status,
        page=page,
        limit=limit,
    )
    
    return api_success(
        PaginatedExperiments(
            data=[ExperimentOut.model_validate(e) for e in experiments],
            meta={"total": total, "page": page, "limit": limit},
        ).model_dump()
    )


@router.get("/experiments/{experiment_id}")
def get_experiment(
    experiment_id: int,
    db: Session = Depends(get_db),
    _user=Depends(require_roles(["admin", "finance", "project_manager"])),
):
    """Get an experiment by ID"""
    experiment = services.ResearchService.get_experiment(db, experiment_id)
    if not experiment:
        return api_error("NOT_FOUND", "Experiment not found", http_status=404)
    return api_success(ExperimentOut.model_validate(experiment))


@router.put("/experiments/{experiment_id}")
def update_experiment(
    experiment_id: int,
    payload: dict,
    db: Session = Depends(get_db),
    _user=Depends(require_roles(["admin", "finance", "project_manager"])),
):
    """Update an experiment"""
    experiment = services.ResearchService.update_experiment(db, experiment_id, payload)
    if not experiment:
        return api_error("NOT_FOUND", "Experiment not found", http_status=404)
    
    # Log the activity
    log_activity(
        db=db,
        user_email=_user.get("email"),
        action="update",
        entity_type="experiment",
        entity_id=experiment.id,
        entity_name=experiment.title,
        new_values=payload,
        description=f"Updated experiment: {experiment.title}"
    )
    
    return api_success(ExperimentOut.model_validate(experiment))


# ===== RESEARCH LOGS =====

@router.post("/experiments/{experiment_id}/logs")
def create_research_log(
    experiment_id: int,
    payload: CreateResearchLog,
    db: Session = Depends(get_db),
    _user=Depends(require_roles(["admin", "finance", "project_manager"])),
):
    """Create a research log for an experiment"""
    experiment = services.ResearchService.get_experiment(db, experiment_id)
    if not experiment:
        return api_error("NOT_FOUND", "Experiment not found", http_status=404)
    
    log = services.ResearchService.create_research_log(
        db, experiment.research_project_id, experiment_id, payload
    )
    
    # Log the activity
    log_activity(
        db=db,
        user_email=_user.get("email"),
        action="create",
        entity_type="research_log",
        entity_id=log.id,
        entity_name=payload.title or "Research Log",
        new_values=payload.model_dump(),
        description=f"Created research log for experiment {experiment_id}"
    )
    
    return api_success(ResearchLogOut.model_validate(log))


@router.get("/experiments/{experiment_id}/logs")
def get_experiment_logs(
    experiment_id: int,
    db: Session = Depends(get_db),
    _user=Depends(require_roles(["admin", "finance", "project_manager"])),
):
    """Get all logs for an experiment"""
    experiment = services.ResearchService.get_experiment(db, experiment_id)
    if not experiment:
        return api_error("NOT_FOUND", "Experiment not found", http_status=404)
    
    logs = services.ResearchService.get_experiment_logs(db, experiment_id)
    return api_success({"logs": [ResearchLogOut.model_validate(log).model_dump() for log in logs]})


# ===== IP & SPECIAL QUERIES =====

@router.get("/research-projects/{project_id}/ip-potential")
def get_ip_potential_experiments(
    project_id: int,
    db: Session = Depends(get_db),
    _user=Depends(require_roles(["admin", "finance", "project_manager"])),
):
    """Get experiments with IP potential from a project"""
    # Verify project exists
    project = services.ResearchService.get_research_project(db, project_id)
    if not project:
        return api_error("NOT_FOUND", "Research project not found", http_status=404)
    
    experiments = services.ResearchService.get_ip_potential_experiments(db, project_id)
    return api_success({
        "ip_potential_count": len(experiments),
        "experiments": [ExperimentOut.model_validate(e).model_dump() for e in experiments]
    })


@router.get("/research-projects/{project_id}/reproducible")
def get_reproducible_experiments(
    project_id: int,
    db: Session = Depends(get_db),
    _user=Depends(require_roles(["admin", "finance", "project_manager"])),
):
    """Get reproducible experiments from a project"""
    # Verify project exists
    project = services.ResearchService.get_research_project(db, project_id)
    if not project:
        return api_error("NOT_FOUND", "Research project not found", http_status=404)
    
    experiments = services.ResearchService.get_reproducible_experiments(db, project_id)
    return api_success({
        "reproducible_count": len(experiments),
        "experiments": [ExperimentOut.model_validate(e).model_dump() for e in experiments]
    })


@router.delete("/research-projects/{project_id}")
def delete_research_project(
    project_id: int,
    db: Session = Depends(get_db),
    _user=Depends(require_roles(["admin", "project_manager"])),
):
    project = services.ResearchService.get_research_project(db, project_id)
    if not project:
        return api_error("NOT_FOUND", "Research project not found", http_status=404)

    name = project.name
    services.ResearchService.delete_research_project(db, project_id)

    log_activity(
        db=db,
        user_email=_user.get("email"),
        action="delete",
        entity_type="research_project",
        entity_id=project_id,
        entity_name=name,
        description=f"Deleted research project: {name}"
    )

    return api_success({"message": f"Research project '{name}' deleted successfully"})
