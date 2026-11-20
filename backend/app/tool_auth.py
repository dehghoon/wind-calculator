"""Authenticate each protected API call against the canonical server policy."""
import json
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen
from fastapi import Request as ApiRequest
from fastapi.responses import JSONResponse

TOOL_KEY = "wind_load"
AUTHORITY = "https://www.linkoteq.com/api/entitlements/execution?tool=" + TOOL_KEY

def verify_access(authorization: str | None) -> tuple[int, str]:
    if not authorization or not authorization.startswith("Bearer ") or not authorization[7:].strip():
        return 401, "authentication_required"
    try:
        request = Request(AUTHORITY, headers={"Authorization": authorization, "Accept": "application/json"})
        with urlopen(request, timeout=10) as response:
            result = json.load(response)
        if isinstance(result, dict) and result.get("active") is True and result.get("tool") == TOOL_KEY:
            return 200, "authorized"
        return 403, "tool_access_required"
    except HTTPError as error:
        return (error.code if error.code in (401, 403) else 503), "tool_access_denied"
    except (URLError, TimeoutError, ValueError, OSError):
        return 503, "authorization_unavailable"

async def protect_api(request: ApiRequest, call_next):
    if request.method != "OPTIONS" and request.url.path.startswith("/api/"):
        from starlette.concurrency import run_in_threadpool
        status, error = await run_in_threadpool(verify_access, request.headers.get("authorization"))
        if status != 200:
            return JSONResponse({"detail": {"code": error, "message": "Sign in to Linkoteq with approved tool access."}},
                                status_code=status, headers={"Cache-Control": "no-store"})
    response = await call_next(request)
    if request.url.path.startswith("/api/"):
        response.headers["Cache-Control"] = "private, no-store"
    return response
