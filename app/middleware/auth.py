from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware

from app.core.security import decode_access_token


class AuthMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        request.state.user = None

        auth_header = request.headers.get("Authorization")
        if auth_header and auth_header.startswith("Bearer "):
            token = auth_header.split(" ", 1)[1].strip()
            if token:
                try:
                    payload = decode_access_token(token)
                    # Minimal user context for RBAC.
                    request.state.user = {"email": payload.get("sub"), "role": payload.get("role")}
                except Exception:
                    request.state.user = None

        response = await call_next(request)
        return response
