from sqlalchemy import Column, Integer, String, DateTime, Text, JSON, Boolean
from datetime import datetime
import enum

from app.core.database import Base


class ActivityActionEnum(str, enum.Enum):
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


class ActivityLog(Base):
    __tablename__ = "activity_logs"

    id = Column(Integer, primary_key=True, index=True)
    
    # User information
    user_id = Column(Integer, nullable=True)  # Can be None for system actions
    user_email = Column(String(255), nullable=True)
    
    # Action details
    action = Column(String(50), nullable=False, index=True)  # CREATE, UPDATE, DELETE, etc.
    action_status = Column(String(20), default="success")  # success, failed, pending
    
    # Entity information
    entity_type = Column(String(100), nullable=False, index=True)  # client, project, invoice, etc.
    entity_id = Column(Integer, nullable=True, index=True)  # ID of affected record
    entity_name = Column(String(255), nullable=True)  # Name/title of affected entity
    
    # Change tracking
    description = Column(Text, nullable=True)  # Human-readable description of action
    old_values = Column(JSON, nullable=True)  # Previous values (for updates)
    new_values = Column(JSON, nullable=True)  # New values (for updates/creates)
    changes_summary = Column(Text, nullable=True)  # Comma-separated list of changed fields
    
    # Additional context
    ip_address = Column(String(50), nullable=True)
    user_agent = Column(String(500), nullable=True)
    request_method = Column(String(10), nullable=True)  # GET, POST, PUT, DELETE
    request_path = Column(String(500), nullable=True)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    
    def __repr__(self):
        return f"<ActivityLog(id={self.id}, action={self.action}, entity={self.entity_type}, user={self.user_email})>"
