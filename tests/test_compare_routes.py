from datetime import datetime, timezone
from uuid import uuid4

from fastapi.testclient import TestClient

from apps.api.main import app
from packages.contracts.claims import NormalizedClaim
from packages.contracts.compare import CompareRequest, CompareResponse, CompareSideSummary, ComparedClaim
from packages.contracts.product_intelligence import GapItem
from packages.core.deps import get_db


class DummyCompareService:
    def __init__(self, _db: object) -> None:
        pass

    def compare_products(self, request: CompareRequest) -> CompareResponse:
        now = datetime.now(timezone.utc)
        left_claim = NormalizedClaim(
            claim_id="capability:single_sign_on",
            claim_type="capability",
            normalized_key="single_sign_on",
            display_label="Single Sign-On",
            confidence=0.88,
            support_count=2,
            source_count=2,
            page_count=2,
            freshness_score=1.0,
            latest_evidence_at=now,
            flags=["multi_source", "docs_backed"],
            evidence=[],
        )
        right_claim = NormalizedClaim(
            claim_id="capability:single_sign_on",
            claim_type="capability",
            normalized_key="single_sign_on",
            display_label="Single Sign-On",
            confidence=0.74,
            support_count=1,
            source_count=1,
            page_count=1,
            freshness_score=1.0,
            latest_evidence_at=now,
            flags=["thin_support"],
            evidence=[],
        )
        return CompareResponse(
            generated_at=now,
            left=CompareSideSummary(
                product_id=request.left_product_id,
                product_name="Left Product",
                vendor_name="Left Vendor",
                claim_count=1,
                high_confidence_claim_count=1,
                stale_claim_count=0,
                gap_count=1,
                last_crawled_at=now,
            ),
            right=CompareSideSummary(
                product_id=request.right_product_id,
                product_name="Right Product",
                vendor_name="Right Vendor",
                claim_count=1,
                high_confidence_claim_count=0,
                stale_claim_count=0,
                gap_count=2,
                last_crawled_at=now,
            ),
            shared=[
                ComparedClaim(
                    normalized_key="single_sign_on",
                    display_label="Single Sign-On",
                    claim_type="capability",
                    left=left_claim,
                    right=right_claim,
                    verdict="shared_but_left_stronger",
                )
            ],
            left_only=[],
            right_only=[],
            left_gaps=[
                GapItem(
                    gap_code="missing_pricing_page",
                    category="pricing",
                    severity="high",
                    message="Missing pricing page.",
                    evidence_count=0,
                    suggested_source_types=["pricing"],
                )
            ],
            right_gaps=[
                GapItem(
                    gap_code="missing_docs_surface",
                    category="docs",
                    severity="high",
                    message="Missing docs surface.",
                    evidence_count=0,
                    suggested_source_types=["docs_subdomain"],
                )
            ],
        )


def override_get_db():
    yield object()


def test_compare_endpoint_returns_payload(monkeypatch) -> None:
    monkeypatch.setattr("apps.api.routes.compare.CompareService", DummyCompareService)
    app.dependency_overrides[get_db] = override_get_db
    client = TestClient(app)
    left_product_id = str(uuid4())
    right_product_id = str(uuid4())

    response = client.post(
        "/v1/compare",
        json={
            "left_product_id": left_product_id,
            "right_product_id": right_product_id,
            "filters": {
                "claim_types": ["capability", "integration"],
                "min_confidence": 0.6,
                "include_stale": False,
                "include_evidence": False,
            },
        },
    )

    assert response.status_code == 200
    body = response.json()["data"]
    assert body["left"]["product_id"] == left_product_id
    assert body["right"]["product_id"] == right_product_id
    assert body["shared"][0]["verdict"] == "shared_but_left_stronger"
    assert body["shared"][0]["normalized_key"] == "single_sign_on"

    app.dependency_overrides.clear()
