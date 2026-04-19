from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional, List
from enum import Enum


class FileTypeEnum(str, Enum):
    DOCUMENT = "document"
    AGREEMENT = "agreement"
    KYC = "kyc"
    INVOICE = "invoice"
    PROPOSAL = "proposal"
    QUOTATION = "quotation"
    SOW = "statement_of_work"
    REPORT = "report"
    OTHER = "other"


class FileVersionResponse(BaseModel):
    id: int
    file_id: int
    version_number: int
    file_size: float
    mime_type: str
    uploaded_at: datetime
    updated_by: int
    change_notes: Optional[str] = None

    class Config:
        from_attributes = True


class FileUploadResponse(BaseModel):
    id: int
    file_name: str
    file_type: str
    mime_type: str
    file_size: float
    uploaded_by: int
    uploaded_at: datetime
    updated_at: datetime
    entity_type: Optional[str] = None
    entity_id: Optional[int] = None
    description: Optional[str] = None
    virus_scan_status: str
    versions: List[FileVersionResponse] = []

    class Config:
        from_attributes = True


class FileUploadCreate(BaseModel):
    file_type: FileTypeEnum = FileTypeEnum.OTHER
    description: Optional[str] = None
    entity_type: Optional[str] = None
    entity_id: Optional[int] = None


class FileUploadUpdate(BaseModel):
    description: Optional[str] = None
    file_type: Optional[FileTypeEnum] = None


class FileUploadMetadata(BaseModel):
    id: int
    file_name: str
    file_type: str
    file_size: float
    uploaded_by: int
    uploaded_at: datetime
    entity_type: Optional[str] = None
    entity_id: Optional[int] = None
    description: Optional[str] = None
    version_count: int = 0

    class Config:
        from_attributes = True


class FileListResponse(BaseModel):
    total: int
    skip: int
    limit: int
    files: List[FileUploadResponse]


class FileVersionRestoreRequest(BaseModel):
    version_number: int = Field(..., gt=0)
    restore_notes: Optional[str] = None
