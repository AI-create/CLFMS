import logging
import random
import secrets
import hashlib
import hmac
from datetime import datetime, timedelta, timezone

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.security import create_access_token, get_password_hash, verify_password
from app.core.config import settings
from app.modules.auth.models import User

logger = logging.getLogger("clfms")

OTP_EXPIRY_MINUTES = 10


def _generate_otp() -> str:
    return f"{random.SystemRandom().randint(0, 999999):06d}"


def _hash_otp(email: str, otp: str) -> str:
    normalized_email = email.lower().strip()
    normalized_otp = otp.strip()
    material = f"{normalized_email}:{normalized_otp}".encode("utf-8")
    return hmac.new(settings.secret_key.encode("utf-8"), material, hashlib.sha256).hexdigest()


def _otp_matches(user: User, otp: str) -> bool:
    if not user.otp_code:
        return False

    submitted_otp = otp.strip()
    expected_hash = _hash_otp(user.email, submitted_otp)

    return hmac.compare_digest(user.otp_code, expected_hash) or hmac.compare_digest(user.otp_code, submitted_otp)


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

    if not user.is_verified:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Email not verified. Please check your inbox for the OTP.")

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
        is_verified=True,  # Admin-created accounts skip OTP
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def signup_user(db: Session, *, email: str, password: str, role: str = "researcher", full_name: str | None = None) -> User:
    """Public registration — creates unverified account and emails an OTP."""
    existing = get_user_by_email(db, email.lower().strip())
    if existing:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Email already registered")

    normalized_email = email.lower().strip()
    otp = _generate_otp()
    user = User(
        email=normalized_email,
        password_hash=get_password_hash(password),
        role=role,
        full_name=full_name,
        is_active=True,
        is_verified=False,
        otp_code=_hash_otp(normalized_email, otp),
        otp_expires_at=datetime.now(timezone.utc) + timedelta(minutes=OTP_EXPIRY_MINUTES),
    )
    db.add(user)
    db.commit()
    db.refresh(user)

    _send_otp_email(user.email, user.full_name or "", otp)
    return user


def verify_otp(db: Session, *, email: str, otp: str) -> User:
    """Verify OTP — marks user as verified and clears the OTP."""
    user = get_user_by_email(db, email.lower().strip())
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Account not found")

    if user.is_verified:
        return user  # Already verified — idempotent

    if not _otp_matches(user, otp):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid OTP")

    if user.otp_expires_at and datetime.now(timezone.utc) > user.otp_expires_at:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="OTP has expired. Please request a new one.")

    user.is_verified = True
    user.otp_code = None
    user.otp_expires_at = None
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def resend_otp(db: Session, *, email: str) -> None:
    """Generate a fresh OTP and resend it."""
    user = get_user_by_email(db, email.lower().strip())
    if not user:
        # Don't reveal whether the email exists
        return

    if user.is_verified:
        return  # Already verified — nothing to do

    otp = _generate_otp()
    user.otp_code = _hash_otp(user.email, otp)
    user.otp_expires_at = datetime.now(timezone.utc) + timedelta(minutes=OTP_EXPIRY_MINUTES)
    db.add(user)
    db.commit()

    _send_otp_email(user.email, user.full_name or "", otp)


def _send_otp_email(email: str, name: str, otp: str) -> None:
    try:
        from app.services.email_service import send_otp_email
        send_otp_email(email, name, otp)
    except Exception as exc:
        logger.error("OTP email failed for %s: %s", email, exc)


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


def login_and_issue_token(db: Session, *, email: str, password: str | None) -> tuple[str, User]:
    """Issue a JWT. If password is None (OTP-verified path), skip password check."""
    if password is None:
        user = get_user_by_email(db, email)
        if not user:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    else:
        user = authenticate_user(db, email=email, password=password)
    token = create_access_token(subject=user.email, role=user.role)
    return token, user


def ensure_default_admin(db: Session) -> None:
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

