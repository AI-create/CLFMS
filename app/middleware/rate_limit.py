from collections import defaultdict, deque
from threading import Lock
from time import time

from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse


class RateLimitMiddleware(BaseHTTPMiddleware):
    """Simple in-memory rate limiting for high-risk auth endpoints."""

    # path -> (max_requests, window_seconds)
    _RULES = {
        "/api/v1/auth/login": (10, 60),
        "/api/v1/auth/signup": (5, 3600),
        "/api/v1/auth/verify-otp": (10, 600),
        "/api/v1/auth/resend-otp": (5, 600),
    }

    def __init__(self, app):
        super().__init__(app)
        self._hits = defaultdict(deque)
        self._lock = Lock()

    def _client_ip(self, request: Request) -> str:
        forwarded = request.headers.get("x-forwarded-for", "")
        if forwarded:
            return forwarded.split(",", 1)[0].strip()
        return request.client.host if request.client else "unknown"

    async def dispatch(self, request: Request, call_next):
        if request.method != "POST":
            return await call_next(request)

        rule = self._RULES.get(request.url.path)
        if not rule:
            return await call_next(request)

        limit, window = rule
        now = time()
        key = f"{request.url.path}:{self._client_ip(request)}"

        with self._lock:
            q = self._hits[key]
            while q and q[0] <= now - window:
                q.popleft()

            if len(q) >= limit:
                return JSONResponse(
                    status_code=429,
                    content={
                        "success": False,
                        "error": {
                            "code": "RATE_LIMITED",
                            "message": "Too many requests. Please try again later.",
                        },
                    },
                )

            q.append(now)

        return await call_next(request)
