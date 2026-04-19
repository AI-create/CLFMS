from datetime import datetime, timedelta
from typing import Optional, List, Dict, Any, Tuple
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, desc

from app.modules.activity_logs.models import ActivityLog, ActivityActionEnum


class ActivityLogService:
    
    @staticmethod
    def create_activity_log(
        db: Session,
        user_id: Optional[int] = None,
        user_email: Optional[str] = None,
        action: str = "other",
        entity_type: str = "unknown",
        entity_id: Optional[int] = None,
        entity_name: Optional[str] = None,
        description: Optional[str] = None,
        old_values: Optional[Dict[str, Any]] = None,
        new_values: Optional[Dict[str, Any]] = None,
        action_status: str = "success",
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
        request_method: Optional[str] = None,
        request_path: Optional[str] = None,
    ) -> ActivityLog:
        """Create a new activity log entry."""
        # Generate changes summary from old_values and new_values
        changes_summary = None
        if old_values and new_values:
            changed_fields = []
            for key in set(list(old_values.keys()) + list(new_values.keys())):
                old_val = old_values.get(key)
                new_val = new_values.get(key)
                if old_val != new_val:
                    changed_fields.append(key)
            changes_summary = ", ".join(changed_fields) if changed_fields else None
        
        activity_log = ActivityLog(
            user_id=user_id,
            user_email=user_email,
            action=action,
            action_status=action_status,
            entity_type=entity_type,
            entity_id=entity_id,
            entity_name=entity_name,
            description=description,
            old_values=old_values,
            new_values=new_values,
            changes_summary=changes_summary,
            ip_address=ip_address,
            user_agent=user_agent,
            request_method=request_method,
            request_path=request_path,
        )
        
        db.add(activity_log)
        db.commit()
        db.refresh(activity_log)
        return activity_log

    @staticmethod
    def get_activity_logs(
        db: Session,
        skip: int = 0,
        limit: int = 10,
        entity_type: Optional[str] = None,
        entity_id: Optional[int] = None,
        action: Optional[str] = None,
        user_email: Optional[str] = None,
        action_status: Optional[str] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
    ) -> Tuple[List[ActivityLog], int]:
        """Get activity logs with optional filtering."""
        query = db.query(ActivityLog)
        
        if entity_type:
            query = query.filter(ActivityLog.entity_type == entity_type)
        
        if entity_id:
            query = query.filter(ActivityLog.entity_id == entity_id)
        
        if action:
            query = query.filter(ActivityLog.action == action)
        
        if user_email:
            query = query.filter(ActivityLog.user_email == user_email)
        
        if action_status:
            query = query.filter(ActivityLog.action_status == action_status)
        
        if start_date:
            query = query.filter(ActivityLog.created_at >= start_date)
        
        if end_date:
            query = query.filter(ActivityLog.created_at <= end_date)
        
        total = query.count()
        logs = query.order_by(desc(ActivityLog.created_at)).offset(skip).limit(limit).all()
        
        return logs, total

    @staticmethod
    def get_entity_audit_trail(
        db: Session,
        entity_type: str,
        entity_id: int,
    ) -> List[ActivityLog]:
        """Get all activity logs for a specific entity."""
        return db.query(ActivityLog).filter(
            and_(
                ActivityLog.entity_type == entity_type,
                ActivityLog.entity_id == entity_id
            )
        ).order_by(desc(ActivityLog.created_at)).all()

    @staticmethod
    def get_activity_summary(
        db: Session,
        days: int = 7,
    ) -> Dict[str, Any]:
        """Get activity summary for the past N days."""
        start_date = datetime.utcnow() - timedelta(days=days)
        
        total_logs = db.query(ActivityLog).filter(
            ActivityLog.created_at >= start_date
        ).count()
        
        # Group by action
        action_counts = {}
        action_logs = db.query(ActivityLog.action).filter(
            ActivityLog.created_at >= start_date
        ).all()
        for log in action_logs:
            action = log[0]
            action_counts[action] = action_counts.get(action, 0) + 1
        
        # Group by status
        status_counts = {}
        status_logs = db.query(ActivityLog.action_status).filter(
            ActivityLog.created_at >= start_date
        ).all()
        for log in status_logs:
            status = log[0]
            status_counts[status] = status_counts.get(status, 0) + 1
        
        # Recent logs
        recent_logs = db.query(ActivityLog).filter(
            ActivityLog.created_at >= start_date
        ).order_by(desc(ActivityLog.created_at)).limit(10).all()
        
        return {
            "total_actions": total_logs,
            "actions_by_type": action_counts,
            "actions_by_status": status_counts,
            "recent_logs": recent_logs,
        }

    @staticmethod
    def get_user_activity_summary(
        db: Session,
        user_email: str,
    ) -> Dict[str, Any]:
        """Get activity summary for a specific user."""
        user_logs = db.query(ActivityLog).filter(
            ActivityLog.user_email == user_email
        ).order_by(desc(ActivityLog.created_at)).all()
        
        total_actions = len(user_logs)
        last_action_at = user_logs[0].created_at if user_logs else None
        
        # Actions today
        today_start = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
        today_logs = [
            log for log in user_logs
            if log.created_at >= today_start
        ]
        actions_today = len(today_logs)
        
        # Actions by type
        action_counts = {}
        for log in user_logs:
            action = log.action
            action_counts[action] = action_counts.get(action, 0) + 1
        
        return {
            "user_email": user_email,
            "total_actions": total_actions,
            "last_action_at": last_action_at,
            "actions_today": actions_today,
            "actions_by_type": action_counts,
        }

    @staticmethod
    def get_entity_modification_history(
        db: Session,
        entity_type: str,
        entity_id: int,
    ) -> Dict[str, Any]:
        """Get detailed modification history for an entity."""
        logs = db.query(ActivityLog).filter(
            and_(
                ActivityLog.entity_type == entity_type,
                ActivityLog.entity_id == entity_id
            )
        ).order_by(ActivityLog.created_at).all()
        
        if not logs:
            return {
                "entity_type": entity_type,
                "entity_id": entity_id,
                "entity_name": None,
                "created_at": None,
                "created_by": None,
                "last_modified_at": None,
                "last_modified_by": None,
                "modification_count": 0,
                "audit_trail": [],
            }
        
        # Find creation and last modification
        creation_log = None
        last_modification_log = None
        
        for log in logs:
            if log.action == "create":
                creation_log = log
            if log.action in ["update", "delete"]:
                last_modification_log = log
        
        # If no explicit create log, use first log
        if not creation_log and logs:
            creation_log = logs[0]
        
        # If no modification, last modification is creation
        if not last_modification_log and creation_log:
            last_modification_log = creation_log
        
        return {
            "entity_type": entity_type,
            "entity_id": entity_id,
            "entity_name": logs[-1].entity_name if logs else None,
            "created_at": creation_log.created_at if creation_log else None,
            "created_by": creation_log.user_email if creation_log else None,
            "last_modified_at": last_modification_log.created_at if last_modification_log else None,
            "last_modified_by": last_modification_log.user_email if last_modification_log else None,
            "modification_count": len([log for log in logs if log.action != "read"]),
            "audit_trail": logs,
        }

    @staticmethod
    def get_recent_activity(
        db: Session,
        limit: int = 20,
    ) -> List[ActivityLog]:
        """Get recent activity across all entities."""
        return db.query(ActivityLog).order_by(
            desc(ActivityLog.created_at)
        ).limit(limit).all()

    @staticmethod
    def get_failed_actions(
        db: Session,
        skip: int = 0,
        limit: int = 10,
    ) -> Tuple[List[ActivityLog], int]:
        """Get all failed actions."""
        query = db.query(ActivityLog).filter(
            ActivityLog.action_status == "failed"
        )
        total = query.count()
        logs = query.order_by(desc(ActivityLog.created_at)).offset(skip).limit(limit).all()
        return logs, total

    @staticmethod
    def cleanup_old_logs(
        db: Session,
        days: int = 90,
    ) -> int:
        """Delete activity logs older than N days. Returns count of deleted rows."""
        cutoff_date = datetime.utcnow() - timedelta(days=days)
        deleted_count = db.query(ActivityLog).filter(
            ActivityLog.created_at < cutoff_date
        ).delete()
        db.commit()
        return deleted_count
