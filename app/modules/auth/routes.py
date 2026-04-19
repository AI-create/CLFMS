from fastapi import APIRouter, Request, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.response import api_error, api_success
from app.core.security import get_current_user
from app.modules.auth.schemas import LoginRequest, LoginResponse, UserOut
from app.modules.auth import services as auth_services


router = APIRouter()


@router.post("/auth/login")
def login(payload: LoginRequest, db: Session = Depends(get_db)):
    try:
        token, user = auth_services.login_and_issue_token(db, email=payload.email, password=payload.password)
    except Exception:
        # Avoid leaking whether email exists.
        return api_error("INVALID_CREDENTIALS", "Invalid credentials", http_status=401)

    return api_success(
        {"token": token, "user": UserOut(id=user.id, email=user.email, role=user.role)},
        message=None,
    )


@router.get("/auth/me")
def me(request: Request, db: Session = Depends(get_db)):
    user_ctx = get_current_user(request)
    user = auth_services.get_user_by_email(db, user_ctx["email"])
    if not user:
        return api_error("NOT_FOUND", "User not found", http_status=404)

    return api_success(UserOut(id=user.id, email=user.email, role=user.role))

