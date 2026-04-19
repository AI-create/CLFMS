from datetime import datetime
from typing import Optional, List
from sqlalchemy.orm import Session

from app.modules.closure.models import (
    ProjectClosure,
    ClosureChecklist,
    ClosureStatus,
)
from app.modules.closure.schemas import (
    ClosureChecklistItemCreate,
    ClosureChecklistItemUpdate,
    ProjectClosureCreate,
    ProjectClosureUpdate,
)


class ClosureService:
    @staticmethod
    def initiate_project_closure(
        db: Session, project_id: int, payload: ProjectClosureCreate
    ) -> ProjectClosure:
        """Initiate closure for a project with default checklist items."""
        # Check if closure already exists
        existing = db.query(ProjectClosure).filter(ProjectClosure.project_id == project_id).first()
        if existing:
            return existing
        
        closure = ProjectClosure(
            project_id=project_id,
            deliverables_description=payload.deliverables_description,
            closure_notes=payload.closure_notes,
        )
        db.add(closure)
        db.flush()

        # Create default closure checklist items
        default_items = [
            {"title": "Verify Deliverables", "description": "Confirm all deliverables match scope"},
            {"title": "Final Invoice Generated", "description": "Ensure final invoice has been issued"},
            {"title": "Payment Received", "description": "Confirm receipt of final payment"},
            {"title": "Client Sign-Off", "description": "Obtain client acceptance and sign-off"},
            {"title": "Knowledge Transfer Complete", "description": "Complete any required knowledge transfer"},
            {"title": "Documentation Updated", "description": "Finalize all project documentation"},
        ]

        for item_data in default_items:
            item = ClosureChecklist(
                closure_id=closure.id,
                project_id=project_id,
                title=item_data["title"],
                description=item_data["description"],
            )
            db.add(item)

        db.commit()
        db.refresh(closure)
        return closure

    @staticmethod
    def get_project_closure(db: Session, project_id: int) -> Optional[ProjectClosure]:
        """Get closure record for a project."""
        return db.query(ProjectClosure).filter(ProjectClosure.project_id == project_id).first()

    @staticmethod
    def get_closure_by_id(db: Session, closure_id: int) -> Optional[ProjectClosure]:
        """Get closure record by ID."""
        return db.query(ProjectClosure).filter(ProjectClosure.id == closure_id).first()

    @staticmethod
    def update_project_closure(
        db: Session, project_id: int, payload: ProjectClosureUpdate
    ) -> Optional[ProjectClosure]:
        """Update closure record."""
        closure = db.query(ProjectClosure).filter(ProjectClosure.project_id == project_id).first()
        if not closure:
            return None

        update_data = payload.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(closure, field, value)

        db.commit()
        db.refresh(closure)
        return closure

    @staticmethod
    def mark_deliverables_complete(
        db: Session, project_id: int, notes: Optional[str] = None
    ) -> Optional[ProjectClosure]:
        """Mark deliverables as completed."""
        closure = db.query(ProjectClosure).filter(ProjectClosure.project_id == project_id).first()
        if not closure:
            return None

        closure.deliverables_completed = True
        closure.deliverables_completed_at = datetime.utcnow()
        if notes:
            closure.deliverables_notes = notes

        db.commit()
        db.refresh(closure)
        return closure

    @staticmethod
    def mark_final_payment_received(
        db: Session, project_id: int, amount: float, notes: Optional[str] = None
    ) -> Optional[ProjectClosure]:
        """Record receipt of final payment."""
        closure = db.query(ProjectClosure).filter(ProjectClosure.project_id == project_id).first()
        if not closure:
            return None

        closure.final_payment_received = True
        closure.final_payment_date = datetime.utcnow()
        closure.final_payment_amount = amount
        if notes:
            closure_notes = (closure.closure_notes or "") + f"\nPayment: {notes}"
            closure.closure_notes = closure_notes.strip()

        db.commit()
        db.refresh(closure)
        return closure

    @staticmethod
    def add_closure_checklist_item(
        db: Session, project_id: int, payload: ClosureChecklistItemCreate
    ) -> ClosureChecklist:
        """Add a custom closure checklist item."""
        closure = db.query(ProjectClosure).filter(ProjectClosure.project_id == project_id).first()
        if not closure:
            raise ValueError(f"No closure record found for project {project_id}")

        item = ClosureChecklist(
            closure_id=closure.id,
            project_id=project_id,
            title=payload.title,
            description=payload.description,
            notes=payload.notes,
        )
        db.add(item)
        db.commit()
        db.refresh(item)
        return item

    @staticmethod
    def get_closure_checklist_items(db: Session, project_id: int) -> List[ClosureChecklist]:
        """Get all closure checklist items for a project."""
        return db.query(ClosureChecklist).filter(ClosureChecklist.project_id == project_id).all()

    @staticmethod
    def get_closure_checklist_item(db: Session, item_id: int) -> Optional[ClosureChecklist]:
        """Get a specific closure checklist item."""
        return db.query(ClosureChecklist).filter(ClosureChecklist.id == item_id).first()

    @staticmethod
    def update_closure_checklist_item(
        db: Session, item_id: int, payload: ClosureChecklistItemUpdate
    ) -> Optional[ClosureChecklist]:
        """Update a closure checklist item."""
        item = db.query(ClosureChecklist).filter(ClosureChecklist.id == item_id).first()
        if not item:
            return None

        update_data = payload.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(item, field, value)
            if field == "is_completed" and value:
                item.completed_at = datetime.utcnow()

        db.commit()
        db.refresh(item)
        return item

    @staticmethod
    def mark_closure_item_complete(
        db: Session, item_id: int, notes: Optional[str] = None
    ) -> Optional[ClosureChecklist]:
        """Mark a closure checklist item as complete."""
        item = db.query(ClosureChecklist).filter(ClosureChecklist.id == item_id).first()
        if not item:
            return None

        item.is_completed = True
        item.completed_at = datetime.utcnow()
        if notes:
            item.notes = notes

        db.commit()
        db.refresh(item)
        return item

    @staticmethod
    def delete_closure_checklist_item(db: Session, item_id: int) -> bool:
        """Delete a closure checklist item."""
        item = db.query(ClosureChecklist).filter(ClosureChecklist.id == item_id).first()
        if not item:
            return False

        db.delete(item)
        db.commit()
        return True

    @staticmethod
    def get_closure_progress(db: Session, project_id: int) -> dict:
        """Get closure progress metrics."""
        items = db.query(ClosureChecklist).filter(ClosureChecklist.project_id == project_id).all()

        if not items:
            return {
                "total_items": 0,
                "completed_items": 0,
                "progress_percentage": 0.0,
            }

        total = len(items)
        completed = sum(1 for item in items if item.is_completed)
        percentage = (completed / total * 100) if total > 0 else 0.0

        return {
            "total_items": total,
            "completed_items": completed,
            "progress_percentage": round(percentage, 2),
        }

    @staticmethod
    def mark_closure_completed(db: Session, project_id: int) -> Optional[ProjectClosure]:
        """Mark project closure as completed."""
        closure = db.query(ProjectClosure).filter(ProjectClosure.project_id == project_id).first()
        if not closure:
            return None

        closure.status = ClosureStatus.COMPLETED
        closure.closure_completed_at = datetime.utcnow()
        db.commit()
        db.refresh(closure)
        return closure

    @staticmethod
    def archive_project(
        db: Session, project_id: int, reason: Optional[str] = None
    ) -> Optional[ProjectClosure]:
        """Archive a completed project."""
        closure = db.query(ProjectClosure).filter(ProjectClosure.project_id == project_id).first()
        if not closure:
            return None

        closure.status = ClosureStatus.ARCHIVED
        closure.archived_at = datetime.utcnow()
        if reason:
            closure.archival_reason = reason

        db.commit()
        db.refresh(closure)
        return closure
