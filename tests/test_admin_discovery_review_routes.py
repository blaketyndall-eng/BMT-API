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
                            "discovery_candidate_id": "22222222-2222-2222-2222-222222222222",
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
                            "review_status": "pending",
                            "reviewer_note": None,
                            "notes": "Docs subdomain if present.",
                            "promoted_source_id": None,
                            "trace_id": "trace-1",
                            "approved_at": None,
                            "rejected_at": None,
                            "created_at": now.isoformat(),
                            "updated_at": now.isoformat(),
                        }
                    ]
                }
            },
        )()

    def approve_candidate(self, discovery_candidate_id: str, reviewer_note: str | None):
        now = datetime.now(timezone.utc)
        return type(
            "Resp",
            (),
            {
                "model_dump": lambda self: {
                    "discovery_candidate_id": discovery_candidate_id,
                    "review_status": "approved",
                    "reviewer_note": reviewer_note,
                    "approved_at": now.isoformat(),
                    "rejected_at": None,
                }
            },
        )()

    def reject_candidate(self, discovery_candidate_id: str, reviewer_note: str | None):
        now = datetime.now(timezone.utc)
        return type(
            "Resp",
            (),
            {
                "model_dump": lambda self: {
                    "discovery_candidate_id": discovery_candidate_id,
                    "review_status": "rejected",
                    "reviewer_note": reviewer_note,
                    "approved_at": None,
                    "rejected_at": now.isoformat(),
                }
            },
        )()


def override_get_db():
    yield object()


def test_admin_discovery_candidates_endpoint_returns_payload(monkeypatch) -> None:
    monkeypatch.setattr("apps.api.routes.admin_discovery_review.DiscoveryReviewService", DummyDiscoveryReviewService)
    app.dependency_overrides[get_db] = override_get_db
    client = TestClient(app)

    response = client.get("/v1/admin/discovery-candidates?vendor_domain=example.com&review_status=pending&limit=10")

    assert response.status_code == 200
    body = response.json()["data"]
    assert body["items"][0]["vendor_domain"] == "example.com"
    assert body["items"][0]["source_group"] == "developer_shipped_truth"
    assert body["items"][0]["review_status"] == "pending"

    app.dependency_overrides.clear()


def test_admin_discovery_candidate_approve_endpoint_returns_payload(monkeypatch) -> None:
    monkeypatch.setattr("apps.api.routes.admin_discovery_review.DiscoveryReviewService", DummyDiscoveryReviewService)
    app.dependency_overrides[get_db] = override_get_db
    client = TestClient(app)

    response = client.post(
        "/v1/admin/discovery-candidates/22222222-2222-2222-2222-222222222222/approve",
        json={"reviewer_note": "High-signal docs surface."},
    )

    assert response.status_code == 200
    body = response.json()["data"]
    assert body["review_status"] == "approved"
    assert body["reviewer_note"] == "High-signal docs surface."

    app.dependency_overrides.clear()


def test_admin_discovery_candidate_reject_endpoint_returns_payload(monkeypatch) -> None:
    monkeypatch.setattr("apps.api.routes.admin_discovery_review.DiscoveryReviewService", DummyDiscoveryReviewService)
    app.dependency_overrides[get_db] = override_get_db
    client = TestClient(app)

    response = client.post(
        "/v1/admin/discovery-candidates/22222222-2222-2222-2222-222222222222/reject",
        json={"reviewer_note": "Duplicate or low-value candidate."},
    )

    assert response.status_code == 200
    body = response.json()["data"]
    assert body["review_status"] == "rejected"
    assert body["reviewer_note"] == "Duplicate or low-value candidate."

    app.dependency_overrides.clear()
