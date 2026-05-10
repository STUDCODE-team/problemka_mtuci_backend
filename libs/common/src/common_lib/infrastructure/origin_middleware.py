import re

from fastapi import Request
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware

_ALLOWED_ORIGIN_RE = re.compile(r"^https://[a-zA-Z0-9-]+\.problemka-mtuci\.tech$")
_SAFE_METHODS = frozenset({"GET", "HEAD", "OPTIONS"})


class OriginCheckMiddleware(BaseHTTPMiddleware):
    """Reject state-changing requests whose Origin header doesn't match the allowed domain.

    Requests without an Origin header (mobile clients, server-to-server) are allowed through.
    Requests with X-Internal-Secret are treated as internal and skipped.
    """

    async def dispatch(self, request: Request, call_next):
        if request.method in _SAFE_METHODS:
            return await call_next(request)
        if request.headers.get("x-internal-secret"):
            return await call_next(request)
        origin = request.headers.get("origin")
        if origin and not _ALLOWED_ORIGIN_RE.match(origin):
            return JSONResponse(
                status_code=403,
                content={"detail": "Forbidden origin"},
            )
        return await call_next(request)
