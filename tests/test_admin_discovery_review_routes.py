from datetime import datetime, timezone

from fastapi.testclient import TestClient

from apps.api.main import app
from packages.core.deps import get_db


class DummyDiscoveryReviewService:
    def __init__(self, _db: object) -> None:
        pass

    def list_candidates(self, **kwargs):
        now = datetime.now(timezone.utc)
        return type(
            "Resp",
            (),
            {
                "model_dump": lambda self: {
                    "items": [
                        {
                            "discovery_run_id": "11111111-1111-1111-1111-111111111111",
                            "vendor_domain": "example.com",
                            "root_url": "https://docs.example.com",
                            "source_family": "vendor_owned",
                            "source_type": "docs_subdomain",
                            "source_group": "developer_shipped_truth",
                            "policy_zone": "green",
                            "connector_type": "browser",
                            "machine_readable": False,
                            "crawler_mode": "browser_fetch",
                            "parser_chain": ["docs_nav_parser", "html_claim_extractor"],
                            "base_confidence_weight": 0.92,
                            "provenance_required": True,
                            "terms_review_required": False,
                            "notes": "Docs subdomain if present.",
                            "trace_id": "trace-1",
                            "created_at": now.isoformat(),
                        }
                    ]
                }
            },
        )()


def override_get_db():
    yield object()


def test_admin_discovery_candidates_endpoint_returns_payload(monkeypatch) -> None:
    monkeypatch.setattr("apps.api.routes.admin_discovery_review.DiscoveryReviewService", DummyDiscoveryReviewService)
    app.dependency_overrides[get_db] = override_get_db
    client = TestClient(app)

    response = client.get("/v1/admin/discovery-candidates?vendor_domain=example.com&limit=10")

    assert response.status_code == 200
    body = response.json()["data"]
    assert body["items"][0]["vendor_domain"] == "example.com"
    assert body["items"][0]["source_group"] == "developer_shipped_truth"
    assert body["items"][0]["root_url"] == "https://docs.example.com"

    app.dependency_overrides.clear()
