import os
import shutil
from datetime import datetime
from typing import Optional, List, Tuple
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_

from app.modules.files.models import FileUpload, FileVersion, FileTypeEnum
from app.core.config import settings


class FileService:
    @staticmethod
    def get_file_upload_dir():
        """Get or create file upload directory."""
        import os
        # Use project root/uploads/files directory
        project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
        upload_dir = os.path.join(project_root, "uploads", "files")
        os.makedirs(upload_dir, exist_ok=True)
        return upload_dir

    @staticmethod
    def get_unique_filename(filename: str) -> str:
        """Generate unique filename with timestamp."""
        name, ext = os.path.splitext(filename)
        timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S_%f")[:-3]
        return f"{name}_{timestamp}{ext}"

    @staticmethod
    def upload_file(
        db: Session,
        file_data: bytes,
        original_filename: str,
        mime_type: str,
        file_type: str,
        uploaded_by: int,
        entity_type: Optional[str] = None,
        entity_id: Optional[int] = None,
        description: Optional[str] = None,
    ) -> Optional[FileUpload]:
        """Upload and store file."""
        file_path = None
        try:
            upload_dir = FileService.get_file_upload_dir()
            unique_filename = FileService.get_unique_filename(original_filename)
            file_path = os.path.join(upload_dir, unique_filename)

            # Save file
            with open(file_path, "wb") as f:
                f.write(file_data)

            file_size = os.path.getsize(file_path)

            # Ensure file_type is a string value
            if file_type is None or file_type == '':
                file_type_str = "other"
            else:
                file_type_str = str(file_type).lower() if isinstance(file_type, str) else "other"

            # Create database record
            file_upload = FileUpload(
                file_name=original_filename,
                file_path=file_path,
                file_type=file_type_str,
                mime_type=mime_type,
                file_size=file_size,
                uploaded_by=uploaded_by,
                entity_type=entity_type,
                entity_id=entity_id,
                description=description,
                virus_scan_status="pending",  # Would integrate with virus scanning API
            )

            db.add(file_upload)
            db.commit()
            db.refresh(file_upload)

            return file_upload
        except Exception as e:
            db.rollback()
            # Clean up partial file if creation failed
            if file_path and os.path.exists(file_path):
                os.remove(file_path)
            raise e

    @staticmethod
    def get_file(db: Session, file_id: int) -> Optional[FileUpload]:
        """Get file by ID."""
        return db.query(FileUpload).filter(
            and_(FileUpload.id == file_id, FileUpload.is_deleted == 0)
        ).first()

    @staticmethod
    def get_file_by_path(db: Session, file_path: str) -> Optional[FileUpload]:
        """Get file by path."""
        return db.query(FileUpload).filter(
            and_(FileUpload.file_path == file_path, FileUpload.is_deleted == 0)
        ).first()

    @staticmethod
    def list_files(
        db: Session,
        skip: int = 0,
        limit: int = 10,
        file_type: Optional[str] = None,
        entity_type: Optional[str] = None,
        entity_id: Optional[int] = None,
    ) -> Tuple[List[FileUpload], int]:
        """List files with optional filtering."""
        query = db.query(FileUpload).filter(FileUpload.is_deleted == 0)

        if file_type:
            query = query.filter(FileUpload.file_type == file_type)

        if entity_type:
            query = query.filter(FileUpload.entity_type == entity_type)

        if entity_id:
            query = query.filter(FileUpload.entity_id == entity_id)

        total = query.count()
        files = query.order_by(FileUpload.uploaded_at.desc()).offset(skip).limit(limit).all()

        return files, total

    @staticmethod
    def update_file(
        db: Session,
        file_id: int,
        description: Optional[str] = None,
        file_type: Optional[str] = None,
    ) -> Optional[FileUpload]:
        """Update file metadata."""
        file = FileService.get_file(db, file_id)
        if not file:
            return None

        if description is not None:
            file.description = description
        if file_type is not None:
            file.file_type = file_type

        db.commit()
        db.refresh(file)
        return file

    @staticmethod
    def delete_file(db: Session, file_id: int) -> bool:
        """Soft delete file."""
        file = FileService.get_file(db, file_id)
        if not file:
            return False

        file.is_deleted = 1
        db.commit()
        return True

    @staticmethod
    def hard_delete_file(db: Session, file_id: int) -> bool:
        """Permanently delete file and its versions."""
        file = FileService.get_file(db, file_id)
        if not file:
            # Try to find soft-deleted file
            file = db.query(FileUpload).filter(FileUpload.id == file_id).first()
            if not file:
                return False

        # Delete physical files
        if os.path.exists(file.file_path):
            os.remove(file.file_path)

        for version in file.versions:
            if os.path.exists(version.file_path):
                os.remove(version.file_path)

        # Delete database records
        db.delete(file)
        db.commit()
        return True

    @staticmethod
    def create_new_version(
        db: Session,
        file_id: int,
        file_data: bytes,
        mime_type: str,
        updated_by: int,
        change_notes: Optional[str] = None,
    ) -> Optional[Tuple[FileUpload, FileVersion]]:
        """Create a new version of existing file."""
        file = FileService.get_file(db, file_id)
        if not file:
            return None

        try:
            # Get next version number
            max_version = db.query(FileVersion).filter(
                FileVersion.file_id == file_id
            ).order_by(FileVersion.version_number.desc()).first()
            next_version = (max_version.version_number + 1) if max_version else 1

            # Save current file as version
            upload_dir = FileService.get_file_upload_dir()
            version_filename = f"v{next_version}_{FileService.get_unique_filename(file.file_name)}"
            version_path = os.path.join(upload_dir, version_filename)

            with open(version_path, "wb") as f:
                f.write(file_data)

            file_size = os.path.getsize(version_path)

            # Create version record
            new_version = FileVersion(
                file_id=file_id,
                version_number=next_version,
                file_path=version_path,
                file_size=file_size,
                mime_type=mime_type,
                updated_by=updated_by,
                change_notes=change_notes,
            )

            db.add(new_version)

            # Update file record
            file.updated_at = datetime.utcnow()

            db.commit()
            db.refresh(file)

            return file, new_version
        except Exception as e:
            db.rollback()
            if os.path.exists(version_path):
                os.remove(version_path)
            raise e

    @staticmethod
    def get_file_versions(db: Session, file_id: int) -> Optional[List[FileVersion]]:
        """Get all versions of a file."""
        file = FileService.get_file(db, file_id)
        if not file:
            return None

        return db.query(FileVersion).filter(
            FileVersion.file_id == file_id
        ).order_by(FileVersion.version_number.desc()).all()

    @staticmethod
    def restore_version(
        db: Session,
        file_id: int,
        version_number: int,
        restored_by: int,
        restore_notes: Optional[str] = None,
    ) -> Optional[FileUpload]:
        """Restore file to a previous version."""
        file = FileService.get_file(db, file_id)
        if not file:
            return None

        version = db.query(FileVersion).filter(
            and_(FileVersion.file_id == file_id, FileVersion.version_number == version_number)
        ).first()

        if not version:
            return None

        try:
            # Read version file
            with open(version.file_path, "rb") as f:
                file_data = f.read()

            # Save current file as new version
            upload_dir = FileService.get_file_upload_dir()
            new_version_num = (
                db.query(FileVersion)
                .filter(FileVersion.file_id == file_id)
                .order_by(FileVersion.version_number.desc())
                .first()
            )
            next_num = (new_version_num.version_number + 1) if new_version_num else 1

            backup_filename = f"v{next_num}_backup_{FileService.get_unique_filename(file.file_name)}"
            backup_path = os.path.join(upload_dir, backup_filename)

            # Backup current file
            with open(file.file_path, "rb") as f:
                current_data = f.read()
            with open(backup_path, "wb") as f:
                f.write(current_data)

            # Create version record for current file
            backup_version = FileVersion(
                file_id=file_id,
                version_number=next_num,
                file_path=backup_path,
                file_size=os.path.getsize(backup_path),
                mime_type=file.mime_type,
                updated_by=restored_by,
                change_notes=f"Auto backup before restoring to v{version_number}. Notes: {restore_notes}",
            )
            db.add(backup_version)

            # Write restored version to current file
            with open(file.file_path, "wb") as f:
                f.write(file_data)

            file.file_size = os.path.getsize(file.file_path)
            file.updated_at = datetime.utcnow()

            db.commit()
            db.refresh(file)

            return file
        except Exception as e:
            db.rollback()
            raise e

    @staticmethod
    def read_file(file_path: str) -> Optional[bytes]:
        """Read file contents."""
        if not os.path.exists(file_path):
            return None

        try:
            with open(file_path, "rb") as f:
                return f.read()
        except Exception as e:
            raise e

    @staticmethod
    def set_virus_scan_status(db: Session, file_id: int, status: str) -> Optional[FileUpload]:
        """Update virus scan status."""
        file = db.query(FileUpload).filter(FileUpload.id == file_id).first()
        if not file:
            return None

        file.virus_scan_status = status
        db.commit()
        db.refresh(file)
        return file
