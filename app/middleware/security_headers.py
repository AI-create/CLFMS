from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware

from app.core.config import settings


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

        # Enforce HTTPS in browsers for production deployments.
        if not settings.debug:
            response.headers["Strict-Transport-Security"] = (
                "max-age=31536000; includeSubDomains"
            )

        # Content Security Policy — tight for an SPA served from the same origin
        response.headers["Content-Security-Policy"] = (
            "default-src 'self'; "
            "script-src 'self'; "
            "style-src 'self' 'unsafe-inline'; "
            "img-src 'self' data:; "
            "font-src 'self'; "
            "connect-src 'self'; "
            "object-src 'none'; "
            "base-uri 'self'; "
            "frame-ancestors 'none';"
        )

        # Remove server fingerprinting header added by uvicorn/starlette
        if "server" in response.headers:
            del response.headers["server"]

        return response
