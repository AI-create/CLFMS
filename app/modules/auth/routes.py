from fastapi import APIRouter, Request, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.response import api_error, api_success
from app.core.security import get_current_user, require_roles
from app.modules.auth.schemas import (
    LoginRequest,
    LoginResponse,
    SignupRequest,
    UpdateProfileRequest,
    AdminUpdateUserRequest,
    OtpVerifyRequest,
    ResendOtpRequest,
    UserOut,
)
from app.modules.auth import services as auth_services


router = APIRouter()


@router.post("/auth/login")
def login(payload: LoginRequest, db: Session = Depends(get_db)):
    try:
        token, user = auth_services.login_and_issue_token(db, email=payload.email, password=payload.password)
    except Exception as exc:
        detail = str(exc.detail) if hasattr(exc, "detail") else ""
        if "Email not verified" in detail:
            return api_error("EMAIL_NOT_VERIFIED", "Please verify your email before logging in.", http_status=403)
        return api_error("INVALID_CREDENTIALS", "Invalid credentials", http_status=401)

    return api_success(
        {"token": token, "user": UserOut.model_validate(user)},
        message=None,
    )


@router.post("/auth/signup")
def signup(payload: SignupRequest, db: Session = Depends(get_db)):
    """Public self-registration. Sends OTP to user's email for verification."""
    try:
        user = auth_services.signup_user(
            db,
            email=payload.email,
            password=payload.password,
            role=payload.role or "researcher",
            full_name=payload.full_name,
        )
    except Exception as exc:
        detail = str(exc.detail) if hasattr(exc, "detail") else "Signup failed"
        return api_error("SIGNUP_ERROR", detail, http_status=400)

    return api_success(
        {"email": user.email},
        message="Account created. A 6-digit OTP has been sent to your email.",
    )


@router.post("/auth/verify-otp")
def verify_otp(payload: OtpVerifyRequest, db: Session = Depends(get_db)):
    """Verify the OTP sent to the user's email and return a login token."""
    try:
        user = auth_services.verify_otp(db, email=payload.email, otp=payload.otp)
    except Exception as exc:
        detail = str(exc.detail) if hasattr(exc, "detail") else "Verification failed"
        return api_error("OTP_ERROR", detail, http_status=400)

    token, _ = auth_services.login_and_issue_token(db, email=user.email, password=None)
    return api_success({"token": token, "user": UserOut.model_validate(user)}, message="Email verified. Welcome!")


@router.post("/auth/resend-otp")
def resend_otp(payload: ResendOtpRequest, db: Session = Depends(get_db)):
    """Resend OTP to the given email (always returns success to prevent enumeration)."""
    auth_services.resend_otp(db, email=payload.email)
    return api_success({}, message="If that email is registered and unverified, a new OTP has been sent.")


@router.get("/auth/me")
def me(request: Request, db: Session = Depends(get_db)):
    user_ctx = get_current_user(request)
    user = auth_services.get_user_by_email(db, user_ctx["email"])
    if not user:
        return api_error("NOT_FOUND", "User not found", http_status=404)

    return api_success(UserOut.model_validate(user))


@router.put("/auth/profile")
def update_profile(
    payload: UpdateProfileRequest,
    request: Request,
    db: Session = Depends(get_db),
    _user=Depends(get_current_user),
):
    """Update own profile (name, email, password)."""
    user = auth_services.get_user_by_email(db, _user["email"])
    if not user:
        return api_error("NOT_FOUND", "User not found", http_status=404)

    try:
        updated = auth_services.update_profile(
            db,
            user=user,
            full_name=payload.full_name,
            email=payload.email,
            current_password=payload.current_password,
            new_password=payload.new_password,
        )
    except Exception as exc:
        detail = str(exc.detail) if hasattr(exc, "detail") else "Update failed"
        return api_error("UPDATE_ERROR", detail, http_status=400)

    return api_success(UserOut.model_validate(updated))


# ── Admin: User Management ──────────────────────────────────────────────────

@router.get("/users")
def list_users(
    db: Session = Depends(get_db),
    _user=Depends(require_roles(["admin", "founder"])),
):
    users = auth_services.list_users(db)
    return api_success([UserOut.model_validate(u) for u in users])


@router.put("/users/{user_id}")
def update_user(
    user_id: int,
    payload: AdminUpdateUserRequest,
    db: Session = Depends(get_db),
    _user=Depends(require_roles(["admin", "founder"])),
):
    try:
        updated = auth_services.admin_update_user(
            db,
            user_id=user_id,
            full_name=payload.full_name,
            role=payload.role,
            is_active=payload.is_active,
        )
    except Exception as exc:
        detail = str(exc.detail) if hasattr(exc, "detail") else "Update failed"
        return api_error("UPDATE_ERROR", detail, http_status=400)

    return api_success(UserOut.model_validate(updated))


@router.delete("/users/{user_id}")
def delete_user(
    user_id: int,
    request: Request,
    db: Session = Depends(get_db),
    _user=Depends(require_roles(["admin"])),
):
    current_user = auth_services.get_user_by_email(db, _user["email"])
    try:
        auth_services.delete_user(db, user_id=user_id, requester_id=current_user.id)
    except Exception as exc:
        detail = str(exc.detail) if hasattr(exc, "detail") else "Delete failed"
        return api_error("DELETE_ERROR", detail, http_status=400)

    return api_success({"deleted": True})



router = APIRouter()


@router.post("/auth/login")
def login(payload: LoginRequest, db: Session = Depends(get_db)):
    try:
        token, user = auth_services.login_and_issue_token(db, email=payload.email, password=payload.password)
    except Exception as exc:
        detail = str(exc.detail) if hasattr(exc, "detail") else ""
        if "pending admin approval" in detail:
            return api_error("PENDING_APPROVAL", "Your account is pending admin approval.", http_status=403)
        # Generic — avoid leaking whether email exists
        return api_error("INVALID_CREDENTIALS", "Invalid credentials", http_status=401)

    return api_success(
        {"token": token, "user": UserOut.model_validate(user)},
        message=None,
    )


@router.post("/auth/signup")
def signup(payload: SignupRequest, db: Session = Depends(get_db)):
    """Public self-registration. Account requires admin approval before login."""
    try:
        user = auth_services.signup_user(
            db,
            email=payload.email,
            password=payload.password,
            role=payload.role or "researcher",
            full_name=payload.full_name,
        )
    except Exception as exc:
        detail = str(exc.detail) if hasattr(exc, "detail") else "Signup failed"
        return api_error("SIGNUP_ERROR", detail, http_status=400)

    return api_success({"user": UserOut.model_validate(user)}, message="Account created — awaiting admin approval")


@router.get("/auth/approve/{token}", response_class=HTMLResponse)
def approve_account(token: str, db: Session = Depends(get_db)):
    """One-click approval link sent to admin via email."""
    try:
        user = auth_services.approve_user_by_token(db, token)
    except Exception:
        return HTMLResponse(
            content=_approval_html(
                success=False,
                message="Invalid or expired approval link. The account may have already been approved.",
            ),
            status_code=404,
        )
    return HTMLResponse(
        content=_approval_html(
            success=True,
            message=f"Account for <strong>{user.email}</strong> has been approved. They can now log in.",
        ),
        status_code=200,
    )


def _approval_html(success: bool, message: str) -> str:
    color = "#22c55e" if success else "#ef4444"
    icon = "&#10003;" if success else "&#10007;"
    title = "Account Approved" if success else "Approval Failed"
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>{title} — CLFMS</title>
  <style>
    body {{ font-family: Arial, sans-serif; background: #0f172a; color: #e2e8f0;
           display: flex; align-items: center; justify-content: center;
           min-height: 100vh; margin: 0; }}
    .card {{ background: #1e293b; border-radius: 16px; padding: 48px 40px;
             text-align: center; max-width: 420px; width: 90%; }}
    .icon {{ width: 64px; height: 64px; border-radius: 50%;
             background: {color}22; display: flex; align-items: center;
             justify-content: center; margin: 0 auto 20px; font-size: 32px;
             color: {color}; }}
    h1 {{ color: #fff; margin: 0 0 12px; font-size: 22px; }}
    p {{ color: #94a3b8; line-height: 1.6; margin: 0 0 28px; }}
    a {{ display: inline-block; background: #2563eb; color: #fff; padding: 12px 28px;
         border-radius: 8px; text-decoration: none; font-weight: bold; }}
  </style>
</head>
<body>
  <div class="card">
    <div class="icon">{icon}</div>
    <h1>{title}</h1>
    <p>{message}</p>
    <a href="https://magnetarai.online/businesstools">Go to CLFMS</a>
  </div>
</body>
</html>"""


@router.get("/auth/me")
def me(request: Request, db: Session = Depends(get_db)):
    user_ctx = get_current_user(request)
    user = auth_services.get_user_by_email(db, user_ctx["email"])
    if not user:
        return api_error("NOT_FOUND", "User not found", http_status=404)

    return api_success(UserOut.model_validate(user))


@router.put("/auth/profile")
def update_profile(
    payload: UpdateProfileRequest,
    request: Request,
    db: Session = Depends(get_db),
    _user=Depends(get_current_user),
):
    """Update own profile (name, email, password)."""
    user = auth_services.get_user_by_email(db, _user["email"])
    if not user:
        return api_error("NOT_FOUND", "User not found", http_status=404)

    try:
        updated = auth_services.update_profile(
            db,
            user=user,
            full_name=payload.full_name,
            email=payload.email,
            current_password=payload.current_password,
            new_password=payload.new_password,
        )
    except Exception as exc:
        detail = str(exc.detail) if hasattr(exc, "detail") else "Update failed"
        return api_error("UPDATE_ERROR", detail, http_status=400)

    return api_success(UserOut.model_validate(updated))


# ── Admin: User Management ──────────────────────────────────────────────────

@router.get("/users")
def list_users(
    db: Session = Depends(get_db),
    _user=Depends(require_roles(["admin", "founder"])),
):
    users = auth_services.list_users(db)
    return api_success([UserOut.model_validate(u) for u in users])


@router.put("/users/{user_id}")
def update_user(
    user_id: int,
    payload: AdminUpdateUserRequest,
    db: Session = Depends(get_db),
    _user=Depends(require_roles(["admin", "founder"])),
):
    try:
        updated = auth_services.admin_update_user(
            db,
            user_id=user_id,
            full_name=payload.full_name,
            role=payload.role,
            is_active=payload.is_active,
        )
    except Exception as exc:
        detail = str(exc.detail) if hasattr(exc, "detail") else "Update failed"
        return api_error("UPDATE_ERROR", detail, http_status=400)

    return api_success(UserOut.model_validate(updated))


@router.delete("/users/{user_id}")
def delete_user(
    user_id: int,
    request: Request,
    db: Session = Depends(get_db),
    _user=Depends(require_roles(["admin"])),
):
    current_user = auth_services.get_user_by_email(db, _user["email"])
    try:
        auth_services.delete_user(db, user_id=user_id, requester_id=current_user.id)
    except Exception as exc:
        detail = str(exc.detail) if hasattr(exc, "detail") else "Delete failed"
        return api_error("DELETE_ERROR", detail, http_status=400)

    return api_success({"deleted": True})

