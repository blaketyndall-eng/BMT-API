from datetime import datetime, timezone

from fastapi.testclient import TestClient

from apps.api.main import app
from packages.core.deps import get_db


class DummyAdminQueryService:
    def __init__(self, _db: object) -> None:
        pass

    def list_agent_runs(self, **kwargs):
        now = datetime.now(timezone.utc)
        return type(
            "Resp",
            (),
            {
                "model_dump": lambda self: {
                    "items": [
                        {
                            "agent_run_id": "11111111-1111-1111-1111-111111111111",
                            "agent_name": "registry_manager_discovery",
                            "strategy_version": "discovery_v1",
                            "mode": "manager_orchestrated_discovery",
                            "status": "completed",
                            "trace_id": "trace-1",
                            "request_id": "request-1",
                            "product_id": None,
                            "vendor_id": None,
                            "created_at": now.isoformat(),
                            "updated_at": now.isoformat(),
                        }
                    ]
                }
            },
        )()


def override_get_db():
    yield object()


def test_admin_discovery_runs_endpoint_returns_payload(monkeypatch) -> None:
    monkeypatch.setattr("apps.api.routes.admin_agent_ops.AdminQueryService", DummyAdminQueryService)
    app.dependency_overrides[get_db] = override_get_db
    client = TestClient(app)

    response = client.get("/v1/admin/discovery-runs?limit=10")

    assert response.status_code == 200
    body = response.json()["data"]
    assert body["items"][0]["agent_name"] == "registry_manager_discovery"
    assert body["items"][0]["mode"] == "manager_orchestrated_discovery"

    app.dependency_overrides.clear()
