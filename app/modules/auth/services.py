from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.security import create_access_token, get_password_hash, verify_password
from app.core.config import settings
from app.modules.auth.models import User


def get_user_by_email(db: Session, email: str) -> User | None:
    stmt = select(User).where(User.email == email)
    return db.execute(stmt).scalar_one_or_none()


def authenticate_user(db: Session, *, email: str, password: str) -> User:
    user = get_user_by_email(db, email)
    if not user or not user.is_active:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")

    if not verify_password(password, user.password_hash):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")

    return user


def create_user(db: Session, *, email: str, password: str, role: str = "admin") -> User:
    existing = get_user_by_email(db, email)
    if existing:
        return existing

    user = User(
        email=email,
        password_hash=get_password_hash(password),
        role=role,
        is_active=True,
    )
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
    create_user(
        db,
        email=settings.default_admin_email,
        password=settings.default_admin_password,
        role=settings.default_admin_role,
    )

