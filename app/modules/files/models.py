from sqlalchemy import Column, Integer, String, DateTime, Float, Text, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
import enum

from app.core.database import Base


class FileTypeEnum(str, enum.Enum):
    DOCUMENT = "document"
    AGREEMENT = "agreement"
    KYC = "kyc"
    INVOICE = "invoice"
    PROPOSAL = "proposal"
    QUOTATION = "quotation"
    SOW = "statement_of_work"
    REPORT = "report"
    OTHER = "other"


class FileUpload(Base):
    __tablename__ = "file_uploads"

    id = Column(Integer, primary_key=True, index=True)
    file_name = Column(String(255), nullable=False)
    file_path = Column(String(500), nullable=False, unique=True)
    file_type = Column(String(50), default="other")  # Store as string
    mime_type = Column(String(100), nullable=False)
    file_size = Column(Float, nullable=False)  # in bytes
    uploaded_by = Column(Integer, nullable=False)  # user_id
    uploaded_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Reference to entity (client_id, project_id, etc.)
    entity_type = Column(String(50), nullable=True)  # e.g., 'client', 'project', 'onboarding'
    entity_id = Column(Integer, nullable=True)
    
    # Metadata
    description = Column(Text, nullable=True)
    is_deleted = Column(Integer, default=0)  # soft delete
    
    # Security
    virus_scan_status = Column(String(50), default="pending")  # pending, passed, failed
    
    # Relationships
    versions = relationship("FileVersion", back_populates="file", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<FileUpload(id={self.id}, name={self.file_name}, type={self.file_type})>"


class FileVersion(Base):
    __tablename__ = "file_versions"

    id = Column(Integer, primary_key=True, index=True)
    file_id = Column(Integer, ForeignKey("file_uploads.id"), nullable=False)
    version_number = Column(Integer, nullable=False)
    file_path = Column(String(500), nullable=False)  # Previous version path
    file_size = Column(Float, nullable=False)
    mime_type = Column(String(100), nullable=False)
    uploaded_at = Column(DateTime, default=datetime.utcnow)
    updated_by = Column(Integer, nullable=False)  # user_id
    change_notes = Column(Text, nullable=True)
    
    # Relationships
    file = relationship("FileUpload", back_populates="versions")

    def __repr__(self):
        return f"<FileVersion(file_id={self.file_id}, version={self.version_number})>"
