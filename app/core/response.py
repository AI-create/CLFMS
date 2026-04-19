from typing import Any, Optional

from fastapi.responses import JSONResponse


def api_success(data: Any = None, message: Optional[str] = None) -> dict[str, Any]:
    return {"success": True, "data": data, "message": message}


def api_error(code: str, message: str, http_status: int = 400) -> dict[str, Any]:
    return JSONResponse(
        status_code=http_status,
        content={
            "success": False,
            "error": {
                "code": code,
                "message": message,
            },
        },
    )

