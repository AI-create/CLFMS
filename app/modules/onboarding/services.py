from datetime import datetime
from typing import Optional, List
from sqlalchemy.orm import Session

from app.modules.onboarding.models import (
    ClientOnboarding,
    OnboardingChecklistItem,
    OnboardingChecklistItemType,
)
from app.modules.onboarding.schemas import (
    OnboardingChecklistItemCreate,
    OnboardingChecklistItemUpdate,
    ClientOnboardingCreate,
    ClientOnboardingUpdate,
)


class OnboardingService:
    @staticmethod
    def create_client_onboarding(
        db: Session, client_id: int, payload: ClientOnboardingCreate
    ) -> ClientOnboarding:
        """Create onboarding record for a client with default checklist items."""
        # Create the main onboarding record
        onboarding = ClientOnboarding(
            client_id=client_id,
            assigned_to=payload.assigned_to,
            notes=payload.notes,
        )
        db.add(onboarding)
        db.flush()  # Get the ID without committing yet

        # Create default checklist items
        default_items = [
            OnboardingChecklistItemType.NDA_SIGNED,
            OnboardingChecklistItemType.AGREEMENT_SIGNED,
            OnboardingChecklistItemType.ADVANCE_PAYMENT_RECEIVED,
            OnboardingChecklistItemType.KYC_DOCUMENTS_UPLOADED,
        ]

        for item_type in default_items:
            item = OnboardingChecklistItem(
                onboarding_id=onboarding.id,
                client_id=client_id,
                item_type=item_type,
                title=item_type.value.replace("_", " ").title(),
                is_completed=False,
            )
            db.add(item)

        db.commit()
        db.refresh(onboarding)
        return onboarding

    @staticmethod
    def get_client_onboarding(db: Session, client_id: int) -> Optional[ClientOnboarding]:
        """Get onboarding record for a client."""
        return db.query(ClientOnboarding).filter(ClientOnboarding.client_id == client_id).first()

    @staticmethod
    def get_onboarding_by_id(db: Session, onboarding_id: int) -> Optional[ClientOnboarding]:
        """Get onboarding record by ID."""
        return db.query(ClientOnboarding).filter(ClientOnboarding.id == onboarding_id).first()

    @staticmethod
    def update_client_onboarding(
        db: Session, client_id: int, payload: ClientOnboardingUpdate
    ) -> Optional[ClientOnboarding]:
        """Update onboarding record."""
        onboarding = db.query(ClientOnboarding).filter(ClientOnboarding.client_id == client_id).first()
        if not onboarding:
            return None

        update_data = payload.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(onboarding, field, value)

        db.commit()
        db.refresh(onboarding)
        return onboarding

    @staticmethod
    def add_checklist_item(
        db: Session, client_id: int, payload: OnboardingChecklistItemCreate
    ) -> OnboardingChecklistItem:
        """Add a new checklist item for a client."""
        # Get the onboarding record for this client
        onboarding = db.query(ClientOnboarding).filter(ClientOnboarding.client_id == client_id).first()
        if not onboarding:
            raise ValueError(f"No onboarding record found for client {client_id}")
        
        item = OnboardingChecklistItem(
            onboarding_id=onboarding.id,
            client_id=client_id,
            item_type=payload.item_type,
            title=payload.title,
            description=payload.description,
            notes=payload.notes,
        )
        db.add(item)
        db.commit()
        db.refresh(item)
        return item

    @staticmethod
    def get_checklist_items(db: Session, client_id: int) -> List[OnboardingChecklistItem]:
        """Get all checklist items for a client."""
        return db.query(OnboardingChecklistItem).filter(
            OnboardingChecklistItem.client_id == client_id
        ).all()

    @staticmethod
    def get_checklist_item(db: Session, item_id: int) -> Optional[OnboardingChecklistItem]:
        """Get a specific checklist item."""
        return db.query(OnboardingChecklistItem).filter(OnboardingChecklistItem.id == item_id).first()

    @staticmethod
    def update_checklist_item(
        db: Session, item_id: int, payload: OnboardingChecklistItemUpdate
    ) -> Optional[OnboardingChecklistItem]:
        """Update a checklist item."""
        item = db.query(OnboardingChecklistItem).filter(OnboardingChecklistItem.id == item_id).first()
        if not item:
            return None

        update_data = payload.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(item, field, value)

        db.commit()
        db.refresh(item)
        return item

    @staticmethod
    def mark_checklist_item_complete(
        db: Session, item_id: int, user_email: Optional[str] = None, notes: Optional[str] = None
    ) -> Optional[OnboardingChecklistItem]:
        """Mark a checklist item as complete."""
        item = db.query(OnboardingChecklistItem).filter(OnboardingChecklistItem.id == item_id).first()
        if not item:
            return None

        item.is_completed = True
        item.completed_at = datetime.utcnow()
        if notes:
            item.notes = notes

        db.commit()
        db.refresh(item)

        # Check if all items are completed and update onboarding status
        onboarding = db.query(ClientOnboarding).filter(
            ClientOnboarding.client_id == item.client_id
        ).first()
        if onboarding:
            all_items = db.query(OnboardingChecklistItem).filter(
                OnboardingChecklistItem.client_id == item.client_id
            ).all()
            if all(i.is_completed for i in all_items):
                onboarding.status = "completed"
                onboarding.completed_at = datetime.utcnow()
                db.commit()
                db.refresh(onboarding)

        return item

    @staticmethod
    def delete_checklist_item(db: Session, item_id: int) -> bool:
        """Delete a checklist item."""
        item = db.query(OnboardingChecklistItem).filter(OnboardingChecklistItem.id == item_id).first()
        if not item:
            return False

        db.delete(item)
        db.commit()
        return True

    @staticmethod
    def get_onboarding_progress(db: Session, client_id: int) -> dict:
        """Get onboarding progress metrics."""
        items = db.query(OnboardingChecklistItem).filter(
            OnboardingChecklistItem.client_id == client_id
        ).all()

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
