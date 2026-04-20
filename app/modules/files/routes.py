from fastapi import APIRouter, Depends, UploadFile, File, Query, HTTPException
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from typing import Optional
import logging
import os
import re

from app.core.database import get_db
from app.core.response import api_success, api_error
from app.core.security import require_roles
from app.modules.auth.models import User
from app.modules.files.schemas import (
    FileUploadCreate,
    FileUploadUpdate,
    FileUploadResponse,
    FileUploadMetadata,
    FileListResponse,
    FileVersionResponse,
    FileVersionRestoreRequest,
)
from app.modules.files.services import FileService

logger = logging.getLogger("clfms")

router = APIRouter(prefix="/files", tags=["Files"])

# Constants
MAX_FILE_SIZE = 50 * 1024 * 1024  # 50MB
ALLOWED_EXTENSIONS = {
    "pdf", "doc", "docx", "xls", "xlsx", "ppt", "pptx",
    "txt", "jpg", "jpeg", "png", "gif", "zip", "rar", "7z"
}


def _sanitize_filename(filename: str) -> str:
    """Strip path components and dangerous characters from filenames."""
    # Take only the basename (prevent path traversal via filename)
    filename = os.path.basename(filename)
    # Remove any character that isn't alphanumeric, dot, hyphen, or underscore
    filename = re.sub(r"[^\w.\-]", "_", filename)
    # Collapse multiple consecutive dots (prevent extension spoofing like .exe.pdf)
    filename = re.sub(r"\.{2,}", ".", filename)
    return filename or "upload"


def validate_file(file: UploadFile) -> tuple:
    """Validate uploaded file."""
    if not file.filename:
        raise HTTPException(status_code=400, detail="Invalid filename")

    # Check file size (UploadFile doesn't expose size directly, so we check during read)
    ext = file.filename.split(".")[-1].lower() if "." in file.filename else ""

    if ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail=f"File type .{ext} not allowed. Allowed: {', '.join(ALLOWED_EXTENSIONS)}"
        )

    safe_filename = _sanitize_filename(file.filename)
    return safe_filename, file.content_type or "application/octet-stream"


@router.post("/upload", response_model=dict)
async def upload_file(
    file: UploadFile = File(...),
    file_type: str = Query("other"),
    entity_type: Optional[str] = Query(None),
    entity_id: Optional[int] = Query(None),
    description: Optional[str] = Query(None),
    db: Session = Depends(get_db),
    current_user=Depends(require_roles(["admin", "sales", "project_manager", "pm", "finance"])),
):
    """Upload a file."""
    filename, mime_type = validate_file(file)

    # Read file data
    file_data = await file.read()

    if len(file_data) > MAX_FILE_SIZE:
        return api_error("FILE_TOO_LARGE", f"File exceeds {MAX_FILE_SIZE / 1024 / 1024}MB limit", 400)

    # Get user ID from database using email
    user_email = current_user.get("email")
    user = db.query(User).filter(User.email == user_email).first()
    if not user:
        return api_error("USER_NOT_FOUND", "User not found", 404)
    user_id = user.id

    try:
        file_upload = FileService.upload_file(
            db=db,
            file_data=file_data,
            original_filename=filename,
            mime_type=mime_type,
            file_type=file_type,
            uploaded_by=user_id,
            entity_type=entity_type,
            entity_id=entity_id,
            description=description,
        )

        return api_success(FileUploadResponse.from_orm(file_upload).model_dump())
    except Exception as e:
        logger.error("File upload failed: %s", e, exc_info=True)
        return api_error("UPLOAD_FAILED", "File upload failed", 500)


@router.get("", response_model=dict)
def list_files(
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    file_type: Optional[str] = Query(None),
    entity_type: Optional[str] = Query(None),
    entity_id: Optional[int] = Query(None),
    db: Session = Depends(get_db),
    _user=Depends(require_roles(["admin", "sales", "project_manager", "pm", "finance"])),
):
    """List files with optional filtering."""
    files, total = FileService.list_files(
        db=db,
        skip=skip,
        limit=limit,
        file_type=file_type,
        entity_type=entity_type,
        entity_id=entity_id,
    )

    response = FileListResponse(
        total=total,
        skip=skip,
        limit=limit,
        files=[FileUploadResponse.from_orm(f).model_dump() for f in files]
    )

    return api_success(response.model_dump())


@router.get("/{file_id}/metadata", response_model=dict)
def get_file_metadata(
    file_id: int,
    db: Session = Depends(get_db),
    _user=Depends(require_roles(["admin", "sales", "project_manager", "pm", "finance"])),
):
    """Get file metadata."""
    file = FileService.get_file(db, file_id)
    if not file:
        return api_error("NOT_FOUND", "File not found", 404)

    metadata = FileUploadMetadata(
        id=file.id,
        file_name=file.file_name,
        file_type=file.file_type,
        file_size=file.file_size,
        uploaded_by=file.uploaded_by,
        uploaded_at=file.uploaded_at,
        entity_type=file.entity_type,
        entity_id=file.entity_id,
        description=file.description,
        version_count=len(file.versions)
    )

    return api_success(metadata.model_dump())


@router.get("/{file_id}/download")
def download_file(
    file_id: int,
    db: Session = Depends(get_db),
    _user=Depends(require_roles(["admin", "sales", "project_manager", "pm", "finance"])),
):
    """Download a file."""
    file = FileService.get_file(db, file_id)
    if not file:
        return api_error("NOT_FOUND", "File not found", 404)

    # Path traversal protection — ensure resolved path stays inside the uploads directory
    upload_root = os.path.realpath(FileService.get_file_upload_dir())
    file_real = os.path.realpath(file.file_path)
    if not file_real.startswith(upload_root + os.sep) and file_real != upload_root:
        logger.warning("Path traversal attempt detected for file_id=%s: %s", file_id, file.file_path)
        return api_error("FORBIDDEN", "Access denied", 403)

    if not os.path.isfile(file_real):
        return api_error("NOT_FOUND", "File not found on disk", 404)

    try:
        return FileResponse(
            path=file_real,
            filename=file.file_name,
            media_type=file.mime_type
        )
    except Exception as e:
        logger.error("File download failed for file_id=%s: %s", file_id, e, exc_info=True)
        return api_error("DOWNLOAD_FAILED", "File download failed", 500)


@router.put("/{file_id}", response_model=dict)
def update_file(
    file_id: int,
    payload: FileUploadUpdate,
    db: Session = Depends(get_db),
    _user=Depends(require_roles(["admin", "project_manager", "pm"])),
):
    """Update file metadata."""
    file = FileService.update_file(
        db=db,
        file_id=file_id,
        description=payload.description,
        file_type=payload.file_type,
    )

    if not file:
        return api_error("NOT_FOUND", "File not found", 404)

    return api_success(FileUploadResponse.from_orm(file).model_dump())


@router.delete("/{file_id}", response_model=dict)
def delete_file(
    file_id: int,
    db: Session = Depends(get_db),
    _user=Depends(require_roles(["admin", "project_manager", "pm"])),
):
    """Soft delete a file."""
    success = FileService.delete_file(db, file_id)
    if not success:
        return api_error("NOT_FOUND", "File not found", 404)

    return api_success({"message": "File deleted successfully"})


@router.get("/{file_id}/versions", response_model=dict)
def get_file_versions(
    file_id: int,
    db: Session = Depends(get_db),
    _user=Depends(require_roles(["admin", "project_manager", "pm"])),
):
    """Get all versions of a file."""
    versions = FileService.get_file_versions(db, file_id)
    if versions is None:
        return api_error("NOT_FOUND", "File not found", 404)

    return api_success({
        "file_id": file_id,
        "version_count": len(versions),
        "versions": [FileVersionResponse.from_orm(v).model_dump() for v in versions]
    })


@router.post("/{file_id}/restore-version", response_model=dict)
def restore_file_version(
    file_id: int,
    payload: FileVersionRestoreRequest,
    db: Session = Depends(get_db),
    current_user=Depends(require_roles(["admin", "project_manager", "pm"])),
):
    """Restore file to a previous version."""
    # Get user ID from database using email
    user_email = current_user.get("email")
    user = db.query(User).filter(User.email == user_email).first()
    if not user:
        return api_error("USER_NOT_FOUND", "User not found", 404)
    user_id = user.id

    try:
        file = FileService.restore_version(
            db=db,
            file_id=file_id,
            version_number=payload.version_number,
            restored_by=user_id,
            restore_notes=payload.restore_notes,
        )

        if not file:
            return api_error("NOT_FOUND", "File or version not found", 404)

        return api_success(FileUploadResponse.from_orm(file).model_dump())
    except Exception as e:
        logger.error("File restore failed for file_id=%s: %s", file_id, e, exc_info=True)
        return api_error("RESTORE_FAILED", "File restore failed", 500)


@router.post("/{file_id}/new-version", response_model=dict)
async def create_file_version(
    file_id: int,
    file: UploadFile = File(...),
    change_notes: Optional[str] = Query(None),
    db: Session = Depends(get_db),
    current_user=Depends(require_roles(["admin", "project_manager", "pm"])),
):
    """Create a new version of an existing file."""
    filename, mime_type = validate_file(file)

    file_data = await file.read()

    if len(file_data) > MAX_FILE_SIZE:
        return api_error("FILE_TOO_LARGE", f"File exceeds {MAX_FILE_SIZE / 1024 / 1024}MB limit", 400)

    # Get user ID from database using email
    user_email = current_user.get("email")
    user = db.query(User).filter(User.email == user_email).first()
    if not user:
        return api_error("USER_NOT_FOUND", "User not found", 404)
    user_id = user.id

    try:
        result = FileService.create_new_version(
            db=db,
            file_id=file_id,
            file_data=file_data,
            mime_type=mime_type,
            updated_by=user_id,
            change_notes=change_notes,
        )

        if not result:
            return api_error("NOT_FOUND", "File not found", 404)

        file_obj, version = result
        return api_success({
            "file": FileUploadResponse.from_orm(file_obj).model_dump(),
            "new_version": FileVersionResponse.from_orm(version).model_dump()
        })
    except Exception as e:
        logger.error("New version creation failed for file_id=%s: %s", file_id, e, exc_info=True)
        return api_error("VERSION_FAILED", "Version creation failed", 500)


@router.get("/{file_id}", response_model=dict)
def get_file(
    file_id: int,
    db: Session = Depends(get_db),
    _user=Depends(require_roles(["admin", "sales", "project_manager", "pm", "finance"])),
):
    """Get file details."""
    file = FileService.get_file(db, file_id)
    if not file:
        return api_error("NOT_FOUND", "File not found", 404)

    return api_success(FileUploadResponse.from_orm(file).model_dump())
