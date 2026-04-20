from datetime import datetime, timedelta, timezone
from typing import Any, Callable

import bcrypt
from fastapi import HTTPException, Request, status
from jose import JWTError, jwt

from .config import settings

# Use bcrypt directly — passlib 1.7.4 is incompatible with bcrypt ≥ 4.0.
_BCRYPT_ROUNDS = 12

# Roles that always pass any require_roles() check (super-roles).
_SUPER_ROLES = {"admin", "founder"}


def get_password_hash(password: str) -> str:
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt(rounds=_BCRYPT_ROUNDS)).decode()


def verify_password(password: str, password_hash: str) -> bool:
    try:
        return bcrypt.checkpw(password.encode(), password_hash.encode())
    except Exception:
        return False


def create_access_token(*, subject: str, role: str) -> str:
    now = datetime.now(timezone.utc)
    expire = now + timedelta(minutes=settings.jwt_expire_minutes)
    payload = {
        "sub": subject,
        "role": role,
        "iat": int(now.timestamp()),
        "exp": int(expire.timestamp()),
    }
    return jwt.encode(payload, settings.secret_key, algorithm=settings.jwt_algorithm)


def decode_access_token(token: str) -> dict[str, Any]:
    try:
        return jwt.decode(token, settings.secret_key, algorithms=[settings.jwt_algorithm])
    except JWTError as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid or expired token") from e


def get_current_user(request: Request) -> dict[str, Any]:
    user = getattr(request.state, "user", None)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authenticated")
    return user


def require_roles(allowed_roles: list[str]) -> Callable[[Request], dict[str, Any]]:
    """Return a FastAPI dependency that checks the current user's role.
    Super-roles (admin, founder) always pass regardless of allowed_roles.
    """
    def _guard(request: Request) -> dict[str, Any]:
        user = get_current_user(request)
        role = user.get("role")
        if role in _SUPER_ROLES or role in allowed_roles:
            return user
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied")

    return _guard
