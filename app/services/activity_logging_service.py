"""Service for logging user activities."""
from datetime import datetime, timezone, date
from sqlalchemy.orm import Session
from app.modules.activity_logs.models import ActivityLog


def _serialize_value(value):
    """Convert non-JSON-serializable types to serializable ones."""
    if isinstance(value, (datetime, date)):
        return value.isoformat()
    elif isinstance(value, dict):
        return {k: _serialize_value(v) for k, v in value.items()}
    elif isinstance(value, (list, tuple)):
        return [_serialize_value(v) for v in value]
    return value


def log_activity(
    db: Session,
    user_email: str,
    action: str,
    entity_type: str,
    entity_id: int | None = None,
    entity_name: str | None = None,
    new_values: dict | None = None,
    old_values: dict | None = None,
    description: str | None = None,
    action_status: str = "success",
    request_method: str | None = None,
    request_path: str | None = None,
) -> ActivityLog:
    """Log a user activity.

    Args:
        db: Database session
        user_email: Email of the user performing the action
        action: Action performed (e.g., 'create', 'update', 'delete')
        entity_type: Type of entity (e.g., 'client', 'invoice', 'project')
        entity_id: ID of the entity being acted upon
        entity_name: Name/title of the entity
        new_values: New values for the entity
        old_values: Previous values (for updates)
        description: Human-readable description
        action_status: Status of the action ('success' or 'failure')
        request_method: HTTP method
        request_path: Request path

    Returns:
        The created ActivityLog entry
    """
    # Serialize values to ensure JSON compatibility
    cleaned_new_values = _serialize_value(new_values) if new_values else {}
    cleaned_old_values = _serialize_value(old_values) if old_values else None
    
    activity_log = ActivityLog(
        user_email=user_email,
        action=action,
        entity_type=entity_type,
        entity_id=entity_id,
        entity_name=entity_name,
        new_values=cleaned_new_values,
        old_values=cleaned_old_values,
        description=description,
        action_status=action_status,
        request_method=request_method,
        request_path=request_path,
        created_at=datetime.now(timezone.utc),
    )
    db.add(activity_log)
    db.commit()
    db.refresh(activity_log)
    return activity_log
