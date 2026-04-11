from fastapi.testclient import TestClient

from apps.api.main import app
from packages.contracts.source_promotion import (
    PromoteSourceProposalResponse,
    RejectSourceProposalResponse,
)
from packages.core.deps import get_db


class DummySourcePromotionService:
    def __init__(self, _db: object) -> None:
        pass

    def promote(self, payload):
        return PromoteSourceProposalResponse(
            product_id=payload.product_id,
            source_id="11111111-1111-1111-1111-111111111111",
            crawl_job_id="22222222-2222-2222-2222-222222222222",
            created_source=True,
            created_crawl_job=True,
            deduped_existing_source=False,
        )

    def reject(self, payload):
        return RejectSourceProposalResponse(
            product_id=payload.product_id,
            rejected=True,
            reason=payload.reason,
            proposal_root_url=payload.proposal.root_url,
        )


def override_get_db():
    yield object()


def test_promote_source_proposal_endpoint_returns_payload(monkeypatch) -> None:
    monkeypatch.setattr("apps.api.routes.source_promotion.SourcePromotionService", DummySourcePromotionService)
    app.dependency_overrides[get_db] = override_get_db
    client = TestClient(app)

    response = client.post(
        "/v1/admin/source-proposals/promote",
        json={
            "product_id": "00000000-0000-0000-0000-000000000001",
            "proposal": {
                "root_url": "https://docs.example.com",
                "source_type": "docs_subdomain",
                "source_family": "vendor_owned",
                "connector_type": "browser",
                "reason": "Docs coverage is missing.",
                "target_gap_codes": ["missing_docs_surface"],
                "confidence": 0.9,
            },
            "create_crawl_job": True,
            "crawl_priority": 90,
        },
    )

    assert response.status_code == 200
    body = response.json()["data"]
    assert body["created_source"] is True
    assert body["created_crawl_job"] is True
    assert body["deduped_existing_source"] is False

    app.dependency_overrides.clear()


def test_reject_source_proposal_endpoint_returns_payload(monkeypatch) -> None:
    monkeypatch.setattr("apps.api.routes.source_promotion.SourcePromotionService", DummySourcePromotionService)
    app.dependency_overrides[get_db] = override_get_db
    client = TestClient(app)

    response = client.post(
        "/v1/admin/source-proposals/reject",
        json={
            "product_id": "00000000-0000-0000-0000-000000000001",
            "proposal": {
                "root_url": "https://docs.example.com",
                "source_type": "docs_subdomain",
                "source_family": "vendor_owned",
                "connector_type": "browser",
                "reason": "Docs coverage is missing.",
                "target_gap_codes": ["missing_docs_surface"],
                "confidence": 0.9,
            },
            "reason": "Low-confidence guess.",
        },
    )

    assert response.status_code == 200
    body = response.json()["data"]
    assert body["rejected"] is True
    assert body["proposal_root_url"] == "https://docs.example.com"

    app.dependency_overrides.clear()
