from __future__ import annotations

from typing import Callable
from uuid import uuid4

from opentelemetry import trace as otel_trace
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response

from common_lib.utils.trace import reset_current_trace_id, set_current_trace_id


class TraceIdMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next: Callable[[Request], Response]) -> Response:
        span = otel_trace.get_current_span()
        ctx = span.get_span_context()
        if ctx.is_valid:
            trace_id = format(ctx.trace_id, "032x")
        else:
            trace_id = (
                request.headers.get("x-trace-id")
                or request.headers.get("x-request-id")
                or str(uuid4())
            )

        token = set_current_trace_id(trace_id)
        request.state.trace_id = trace_id
        try:
            response = await call_next(request)
        finally:
            reset_current_trace_id(token)

        response.headers.setdefault("X-Trace-Id", trace_id)
        return response
