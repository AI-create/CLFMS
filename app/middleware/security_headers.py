from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware


class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """Add security-hardening HTTP response headers to every response."""

    async def dispatch(self, request: Request, call_next):
        response = await call_next(request)

        # Prevent MIME-type sniffing
        response.headers["X-Content-Type-Options"] = "nosniff"

        # Block page from being framed (clickjacking protection)
        response.headers["X-Frame-Options"] = "DENY"

        # Enable browser XSS filter (legacy browsers)
        response.headers["X-XSS-Protection"] = "1; mode=block"

        # Only allow HTTPS in production (referrer leakage)
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"

        # Restrict powerful features
        response.headers["Permissions-Policy"] = (
            "geolocation=(), camera=(), microphone=(), payment=()"
        )

        # Content Security Policy — tight for an SPA served from the same origin
        response.headers["Content-Security-Policy"] = (
            "default-src 'self'; "
            "script-src 'self' 'unsafe-inline'; "
            "style-src 'self' 'unsafe-inline'; "
            "img-src 'self' data:; "
            "font-src 'self'; "
            "connect-src 'self'; "
            "frame-ancestors 'none';"
        )

        # Remove server fingerprinting header added by uvicorn/starlette
        if "server" in response.headers:
            del response.headers["server"]

        return response
