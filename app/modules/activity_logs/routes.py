from fastapi import APIRouter, Depends, Query
from datetime import datetime
from typing import Optional
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.response import api_success, api_error
from app.core.security import require_roles
from app.modules.activity_logs.schemas import (
    ActivityLogResponse,
    ActivityLogListResponse,
    ActivitySummary,
    UserActivitySummary,
    EntityAuditTrail,
)
from app.modules.activity_logs.services import ActivityLogService

router = APIRouter(prefix="/activity-logs", tags=["Activity Logs"])


@router.get("", response_model=dict)
def get_activity_logs(
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    entity_type: Optional[str] = Query(None),
    entity_id: Optional[int] = Query(None),
    action: Optional[str] = Query(None),
    user_email: Optional[str] = Query(None),
    action_status: Optional[str] = Query(None),
    start_date: Optional[datetime] = Query(None),
    end_date: Optional[datetime] = Query(None),
    db: Session = Depends(get_db),
    _user=Depends(require_roles(["admin", "finance", "project_manager", "researcher"])),
):
    """Get activity logs with optional filtering."""
    logs, total = ActivityLogService.get_activity_logs(
        db=db,
        skip=skip,
        limit=limit,
        entity_type=entity_type,
        entity_id=entity_id,
        action=action,
        user_email=user_email,
        action_status=action_status,
        start_date=start_date,
        end_date=end_date,
    )
    
    response = ActivityLogListResponse(
        total=total,
        skip=skip,
        limit=limit,
        logs=[ActivityLogResponse.from_orm(log).model_dump() for log in logs]
    )
    
    return api_success(response.model_dump())


@router.get("/entity/{entity_type}/{entity_id}", response_model=dict)
def get_entity_audit_trail(
    entity_type: str,
    entity_id: int,
    db: Session = Depends(get_db),
    _user=Depends(require_roles(["admin", "finance", "project_manager", "researcher"])),
):
    """Get complete audit trail for a specific entity."""
    logs = ActivityLogService.get_entity_audit_trail(db, entity_type, entity_id)
    history = ActivityLogService.get_entity_modification_history(db, entity_type, entity_id)
    
    audit_trail = EntityAuditTrail(
        entity_type=history["entity_type"],
        entity_id=history["entity_id"],
        entity_name=history["entity_name"],
        created_at=history["created_at"],
        created_by=history["created_by"],
        last_modified_at=history["last_modified_at"],
        last_modified_by=history["last_modified_by"],
        modification_count=history["modification_count"],
        audit_trail=[ActivityLogResponse.from_orm(log).model_dump() for log in logs]
    )
    
    return api_success(audit_trail.model_dump())


@router.get("/summary/activity", response_model=dict)
def get_activity_summary(
    days: int = Query(7, ge=1, le=90),
    db: Session = Depends(get_db),
    _user=Depends(require_roles(["admin", "finance"])),
):
    """Get overall activity summary for the past N days."""
    summary = ActivityLogService.get_activity_summary(db, days)
    
    response = ActivitySummary(
        total_actions=summary["total_actions"],
        actions_by_type=summary["actions_by_type"],
        actions_by_status=summary["actions_by_status"],
        recent_logs=[ActivityLogResponse.from_orm(log).model_dump() for log in summary["recent_logs"]]
    )
    
    return api_success(response.model_dump())


@router.get("/summary/user/{user_email}", response_model=dict)
def get_user_activity_summary(
    user_email: str,
    db: Session = Depends(get_db),
    _user=Depends(require_roles(["admin", "finance", "project_manager", "researcher"])),
):
    """Get activity summary for a specific user."""
    summary = ActivityLogService.get_user_activity_summary(db, user_email)
    
    response = UserActivitySummary(
        user_email=summary["user_email"],
        total_actions=summary["total_actions"],
        last_action_at=summary["last_action_at"],
        actions_today=summary["actions_today"],
        actions_by_type=summary["actions_by_type"],
    )
    
    return api_success(response.model_dump())


@router.get("/recent", response_model=dict)
def get_recent_activity(
    limit: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
    _user=Depends(require_roles(["admin", "finance", "project_manager", "researcher"])),
):
    """Get recent activity across all entities."""
    logs = ActivityLogService.get_recent_activity(db, limit)
    
    return api_success({
        "count": len(logs),
        "logs": [ActivityLogResponse.from_orm(log).model_dump() for log in logs]
    })


@router.get("/failed-actions", response_model=dict)
def get_failed_actions(
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    db: Session = Depends(get_db),
    _user=Depends(require_roles(["admin", "finance"])),
):
    """Get all failed actions for debugging."""
    logs, total = ActivityLogService.get_failed_actions(db, skip, limit)
    
    response = ActivityLogListResponse(
        total=total,
        skip=skip,
        limit=limit,
        logs=[ActivityLogResponse.from_orm(log).model_dump() for log in logs]
    )
    
    return api_success(response.model_dump())


@router.post("/cleanup", response_model=dict)
def cleanup_old_logs(
    days: int = Query(90, ge=30, le=365),
    db: Session = Depends(get_db),
    _user=Depends(require_roles(["admin"])),
):
    """Delete activity logs older than N days (default 90)."""
    deleted_count = ActivityLogService.cleanup_old_logs(db, days)
    
    return api_success({
        "deleted_count": deleted_count,
        "message": f"Deleted {deleted_count} activity logs older than {days} days"
    })
