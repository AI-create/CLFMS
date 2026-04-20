import secrets

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.security import create_access_token, get_password_hash, verify_password
from app.core.config import settings
from app.modules.auth.models import User


def get_user_by_email(db: Session, email: str) -> User | None:
    stmt = select(User).where(User.email == email)
    return db.execute(stmt).scalar_one_or_none()


def get_user_by_id(db: Session, user_id: int) -> User | None:
    stmt = select(User).where(User.id == user_id)
    return db.execute(stmt).scalar_one_or_none()


def list_users(db: Session) -> list[User]:
    return db.execute(select(User).order_by(User.id)).scalars().all()


def authenticate_user(db: Session, *, email: str, password: str) -> User:
    user = get_user_by_email(db, email)
    if not user or not user.is_active:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")

    if not verify_password(password, user.password_hash):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")

    if not user.is_approved:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Account pending admin approval")

    return user


def create_user(db: Session, *, email: str, password: str, role: str = "admin", full_name: str | None = None) -> User:
    existing = get_user_by_email(db, email)
    if existing:
        return existing

    user = User(
        email=email,
        password_hash=get_password_hash(password),
        role=role,
        full_name=full_name,
        is_active=True,
        is_approved=True,  # Admin-created accounts are pre-approved
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def signup_user(db: Session, *, email: str, password: str, role: str = "researcher", full_name: str | None = None) -> User:
    """Public registration — creates account pending admin approval."""
    existing = get_user_by_email(db, email.lower().strip())
    if existing:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Email already registered")

    token = secrets.token_urlsafe(32)
    user = User(
        email=email.lower().strip(),
        password_hash=get_password_hash(password),
        role=role,
        full_name=full_name,
        is_active=True,
        is_approved=False,
        approval_token=token,
    )
    db.add(user)
    db.commit()
    db.refresh(user)

    # Send approval email to admin (non-blocking — failure is logged, not raised)
    try:
        from app.services.email_service import send_approval_request_email
        send_approval_request_email(user.email, user.full_name or "", token)
    except Exception as exc:  # noqa: BLE001
        import logging
        logging.getLogger("clfms").error("Approval email failed: %s", exc)

    return user


def update_profile(db: Session, *, user: User, full_name: str | None, email: str | None,
                   current_password: str | None, new_password: str | None) -> User:
    if full_name is not None:
        user.full_name = full_name

    if email and email != user.email:
        conflict = get_user_by_email(db, email)
        if conflict and conflict.id != user.id:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Email already in use")
        user.email = email

    if new_password:
        if not current_password:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Current password required to set a new password")
        if not verify_password(current_password, user.password_hash):
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Current password is incorrect")
        user.password_hash = get_password_hash(new_password)

    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def admin_update_user(db: Session, *, user_id: int, full_name: str | None, role: str | None, is_active: bool | None) -> User:
    user = get_user_by_id(db, user_id)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    if full_name is not None:
        user.full_name = full_name
    if role is not None:
        user.role = role
    if is_active is not None:
        user.is_active = is_active

    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def delete_user(db: Session, *, user_id: int, requester_id: int) -> None:
    if user_id == requester_id:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Cannot delete your own account")
    user = get_user_by_id(db, user_id)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    db.delete(user)
    db.commit()


def approve_user_by_token(db: Session, token: str) -> User:
    """Approve a user account via the one-time approval token."""
    stmt = select(User).where(User.approval_token == token)
    user = db.execute(stmt).scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Invalid or expired approval link")
    if user.is_approved:
        return user  # already approved — idempotent
    user.is_approved = True
    user.approval_token = None  # consume the token
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def login_and_issue_token(db: Session, *, email: str, password: str) -> tuple[str, User]:
    user = authenticate_user(db, email=email, password=password)
    token = create_access_token(subject=user.email, role=user.role)
    return token, user


def ensure_default_admin(db: Session) -> None:
    # Create a default admin account to make local development usable.
    # If the user already exists but has a non-bcrypt hash (e.g. legacy sha256_crypt),
    # re-hash their password so logins continue to work after the bcrypt migration.
    existing = get_user_by_email(db, settings.default_admin_email)
    if existing:
        if not existing.password_hash.startswith(("$2b$", "$2a$")):
            existing.password_hash = get_password_hash(settings.default_admin_password)
            db.commit()
        return

    create_user(
        db,
        email=settings.default_admin_email,
        password=settings.default_admin_password,
        role=settings.default_admin_role,
        full_name="System Admin",
    )

