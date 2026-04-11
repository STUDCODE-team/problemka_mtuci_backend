from __future__ import annotations

from contextvars import ContextVar, Token
from uuid import uuid4

from fastapi import Request


_TRACE_ID: ContextVar[str] = ContextVar("trace_id", default="")


def set_current_trace_id(trace_id: str) -> Token[str]:
    return _TRACE_ID.set(trace_id)


def reset_current_trace_id(token: Token[str]) -> None:
    _TRACE_ID.reset(token)


def current_trace_id() -> str:
    return _TRACE_ID.get()


def get_or_create_trace_id(request: Request) -> str:
    trace_id = getattr(request.state, "trace_id", "") or ""
    if trace_id:
        _TRACE_ID.set(trace_id)
        return trace_id

    trace_id = (
        request.headers.get("x-trace-id")
        or request.headers.get("x-request-id")
        or str(uuid4())
    )
    request.state.trace_id = trace_id
    _TRACE_ID.set(trace_id)
    return trace_id
