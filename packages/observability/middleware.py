from __future__ import annotations

import time

from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response

from packages.observability.tracing import clear_trace_context, generate_trace_id, log_event, set_trace_context


class RequestTracingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next) -> Response:
        request_id = request.headers.get("x-request-id") or generate_trace_id()
        trace_id = request.headers.get("x-trace-id") or generate_trace_id()
        set_trace_context(trace_id=trace_id, request_id=request_id)

        started_at = time.perf_counter()
        log_event(
            "http.server.request.started",
            http_method=request.method,
            http_route=str(request.url.path),
        )
        try:
            response = await call_next(request)
        except Exception:
            duration_ms = round((time.perf_counter() - started_at) * 1000, 3)
            log_event(
                "http.server.request.failed",
                http_method=request.method,
                http_route=str(request.url.path),
                duration_ms=duration_ms,
            )
            clear_trace_context()
            raise

        duration_ms = round((time.perf_counter() - started_at) * 1000, 3)
        response.headers["x-request-id"] = request_id
        response.headers["x-trace-id"] = trace_id
        log_event(
            "http.server.request.completed",
            http_method=request.method,
            http_route=str(request.url.path),
            http_status_code=response.status_code,
            duration_ms=duration_ms,
        )
        clear_trace_context()
        return response
