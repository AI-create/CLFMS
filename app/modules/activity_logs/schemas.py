from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional, List, Dict, Any
from enum import Enum


class ActivityActionEnum(str, Enum):
    CREATE = "create"
    READ = "read"
    UPDATE = "update"
    DELETE = "delete"
    UPLOAD = "upload"
    DOWNLOAD = "download"
    SEND = "send"
    APPROVE = "approve"
    REJECT = "reject"
    EXPORT = "export"
    LOGIN = "login"
    LOGOUT = "logout"
    OTHER = "other"


class ActivityLogResponse(BaseModel):
    id: int
    user_id: Optional[int] = None
    user_email: Optional[str] = None
    action: str
    action_status: str
    entity_type: str
    entity_id: Optional[int] = None
    entity_name: Optional[str] = None
    description: Optional[str] = None
    old_values: Optional[Dict[str, Any]] = None
    new_values: Optional[Dict[str, Any]] = None
    changes_summary: Optional[str] = None
    ip_address: Optional[str] = None
    request_method: Optional[str] = None
    request_path: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True


class ActivityLogListResponse(BaseModel):
    total: int
    skip: int
    limit: int
    logs: List[ActivityLogResponse]


class ActivityLogQuery(BaseModel):
    skip: int = Field(0, ge=0)
    limit: int = Field(10, ge=1, le=100)
    entity_type: Optional[str] = None
    entity_id: Optional[int] = None
    action: Optional[str] = None
    user_email: Optional[str] = None
    action_status: Optional[str] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None


class ActivitySummary(BaseModel):
    total_actions: int
    actions_by_type: Dict[str, int]
    actions_by_status: Dict[str, int]
    recent_logs: List[ActivityLogResponse]


class UserActivitySummary(BaseModel):
    user_email: str
    total_actions: int
    last_action_at: Optional[datetime] = None
    actions_today: int
    actions_by_type: Dict[str, int]


class EntityAuditTrail(BaseModel):
    entity_type: str
    entity_id: int
    entity_name: Optional[str] = None
    created_at: Optional[datetime] = None
    created_by: Optional[str] = None
    last_modified_at: Optional[datetime] = None
    last_modified_by: Optional[str] = None
    modification_count: int
    audit_trail: List[ActivityLogResponse]
