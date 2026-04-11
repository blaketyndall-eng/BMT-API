from fastapi.testclient import TestClient

from apps.api.main import app
from packages.observability.tracing import clear_trace_context, get_trace_context, set_trace_context


def test_request_tracing_middleware_sets_response_headers() -> None:
    client = TestClient(app)

    response = client.get("/healthz")

    assert response.status_code == 200
    assert response.headers.get("x-request-id")
    assert response.headers.get("x-trace-id")


def test_request_tracing_middleware_preserves_incoming_headers() -> None:
    client = TestClient(app)

    response = client.get(
        "/healthz",
        headers={"x-request-id": "req-123", "x-trace-id": "trace-123"},
    )

    assert response.status_code == 200
    assert response.headers["x-request-id"] == "req-123"
    assert response.headers["x-trace-id"] == "trace-123"


def test_trace_context_round_trip() -> None:
    clear_trace_context()
    set_trace_context(trace_id="trace-a", request_id="request-a")

    context = get_trace_context()

    assert context["trace_id"] == "trace-a"
    assert context["request_id"] == "request-a"
    assert context["span_id"] is None

    clear_trace_context()
