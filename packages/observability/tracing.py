from __future__ import annotations

import time
import uuid
from contextlib import contextmanager
from contextvars import ContextVar
from typing import Any, Iterator

import structlog

_TRACE_ID: ContextVar[str | None] = ContextVar("trace_id", default=None)
_REQUEST_ID: ContextVar[str | None] = ContextVar("request_id", default=None)
_SPAN_STACK: ContextVar[list[str]] = ContextVar("span_stack", default=[])

logger = structlog.get_logger("bmt_api.tracing")


def generate_trace_id() -> str:
    return uuid.uuid4().hex


def generate_span_id() -> str:
    return uuid.uuid4().hex[:16]


def set_trace_context(*, trace_id: str, request_id: str | None = None) -> None:
    _TRACE_ID.set(trace_id)
    if request_id is not None:
        _REQUEST_ID.set(request_id)


def clear_trace_context() -> None:
    _TRACE_ID.set(None)
    _REQUEST_ID.set(None)
    _SPAN_STACK.set([])


def get_trace_context() -> dict[str, str | None]:
    span_stack = _SPAN_STACK.get()
    active_span_id = span_stack[-1] if span_stack else None
    return {
        "trace_id": _TRACE_ID.get(),
        "request_id": _REQUEST_ID.get(),
        "span_id": active_span_id,
    }


def log_event(event_name: str, **attributes: Any) -> None:
    logger.info(event_name, **get_trace_context(), **attributes)


@contextmanager
def traced_span(name: str, **attributes: Any) -> Iterator[str]:
    span_id = generate_span_id()
    parent_context = get_trace_context()
    parent_span_id = parent_context.get("span_id")
    span_stack = list(_SPAN_STACK.get())
    span_stack.append(span_id)
    token = _SPAN_STACK.set(span_stack)
    started_at = time.perf_counter()
    logger.info(
        "span.started",
        **get_trace_context(),
        span_name=name,
        parent_span_id=parent_span_id,
        **attributes,
    )
    try:
        yield span_id
    except Exception as exc:
        duration_ms = round((time.perf_counter() - started_at) * 1000, 3)
        logger.exception(
            "span.failed",
            **get_trace_context(),
            span_name=name,
            parent_span_id=parent_span_id,
            duration_ms=duration_ms,
            error_type=type(exc).__name__,
            error_message=str(exc),
            **attributes,
        )
        raise
    else:
        duration_ms = round((time.perf_counter() - started_at) * 1000, 3)
        logger.info(
            "span.completed",
            **get_trace_context(),
            span_name=name,
            parent_span_id=parent_span_id,
            duration_ms=duration_ms,
            **attributes,
        )
    finally:
        _SPAN_STACK.reset(token)
