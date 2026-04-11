import uuid
from datetime import datetime, timezone

from fastapi.testclient import TestClient

from apps.api.main import app
from packages.contracts.claims import ClaimEvidenceRef as NormalizedClaimEvidenceRef
from packages.contracts.claims import NormalizedClaim, ProductClaimsResponse
from packages.contracts.product_intelligence import (
    GapItem,
    ProductGapsResponse,
    ProductSummaryResponse,
    ProductSummaryStats,
)
from packages.contracts.products import (
    CapabilityClaim,
    ClaimEvidenceRef,
    ProductCapabilitiesResponse,
    ProductEvidenceItem,
    ProductEvidenceResponse,
)
from packages.core.deps import get_db


class DummyProductService:
    def __init__(self, _db: object) -> None:
        pass

    def get_product_capabilities(self, product_id: uuid.UUID) -> ProductCapabilitiesResponse:
        now = datetime.now(timezone.utc)
        return ProductCapabilitiesResponse(
            product_id=str(product_id),
            items=[
                CapabilityClaim(
                    claim_type="capability",
                    label="single_sign_on",
                    confidence=0.88,
                    support_count=2,
                    latest_evidence_at=now,
                    evidence=[
                        ClaimEvidenceRef(
                            evidence_id=str(uuid.uuid4()),
                            page_id=str(uuid.uuid4()),
                            canonical_url="https://example.com/docs/sso",
                            snippet="Supports SSO.",
                            confidence=0.78,
                            created_at=now,
                        )
                    ],
                )
            ],
        )

    def get_product_evidence(self, product_id: uuid.UUID) -> ProductEvidenceResponse:
        now = datetime.now(timezone.utc)
        return ProductEvidenceResponse(
            product_id=str(product_id),
            items=[
                ProductEvidenceItem(
                    evidence_id=str(uuid.uuid4()),
                    evidence_type="capability",
                    label="single_sign_on",
                    snippet="Supports SSO.",
                    confidence=0.78,
                    canonical_url="https://example.com/docs/sso",
                    page_id=str(uuid.uuid4()),
                    created_at=now,
                    updated_at=now,
                )
            ],
        )


class DummyProductIntelligenceService:
    def __init__(self, _db: object) -> None:
        pass

    def get_product_claims(
        self,
        product_id: uuid.UUID,
        *,
        min_confidence: float = 0.0,
        include_stale: bool = False,
        include_evidence: bool = False,
    ) -> ProductClaimsResponse:
        now = datetime.now(timezone.utc)
        return ProductClaimsResponse(
            product_id=str(product_id),
            product_name="Example",
            vendor_id=str(uuid.uuid4()),
            vendor_name="Example Inc",
            items=[
                NormalizedClaim(
                    claim_id="capability:single_sign_on",
                    claim_type="capability",
                    normalized_key="single_sign_on",
                    display_label="Single Sign-On",
                    confidence=max(0.88, min_confidence),
                    support_count=2,
                    source_count=2,
                    page_count=2,
                    freshness_score=1.0,
                    latest_evidence_at=now,
                    flags=[] if include_stale else ["multi_source", "docs_backed"],
                    evidence=[
                        NormalizedClaimEvidenceRef(
                            evidence_id=str(uuid.uuid4()),
                            page_id=str(uuid.uuid4()),
                            source_id=str(uuid.uuid4()),
                            canonical_url="https://example.com/docs/sso",
                            page_type="docs",
                            snippet="Supports SSO.",
                            confidence=0.78,
                            created_at=now,
                        )
                    ]
                    if include_evidence
                    else [],
                )
            ],
            next_cursor=None,
        )

    def get_product_summary(
        self,
        product_id: uuid.UUID,
        *,
        min_confidence: float = 0.6,
        include_evidence: bool = False,
    ) -> ProductSummaryResponse:
        now = datetime.now(timezone.utc)
        claim = NormalizedClaim(
            claim_id="capability:single_sign_on",
            claim_type="capability",
            normalized_key="single_sign_on",
            display_label="Single Sign-On",
            confidence=max(0.88, min_confidence),
            support_count=2,
            source_count=2,
            page_count=2,
            freshness_score=1.0,
            latest_evidence_at=now,
            flags=["multi_source", "docs_backed"],
            evidence=[] if not include_evidence else [
                NormalizedClaimEvidenceRef(
                    evidence_id=str(uuid.uuid4()),
                    page_id=str(uuid.uuid4()),
                    source_id=str(uuid.uuid4()),
                    canonical_url="https://example.com/docs/sso",
                    page_type="docs",
                    snippet="Supports SSO.",
                    confidence=0.78,
                    created_at=now,
                )
            ],
        )
        return ProductSummaryResponse(
            product_id=str(product_id),
            product_name="Example",
            vendor_id=str(uuid.uuid4()),
            vendor_name="Example Inc",
            primary_domain="example.com",
            generated_at=now,
            stats=ProductSummaryStats(
                source_count=3,
                page_count=4,
                evidence_count=6,
                claim_count=1,
                high_confidence_claim_count=1,
                stale_claim_count=0,
                last_crawled_at=now,
            ),
            top_capabilities=[claim],
            top_integrations=[],
            top_changes=[],
            gaps=[
                GapItem(
                    gap_code="missing_pricing_page",
                    category="pricing",
                    severity="high",
                    message="No pricing page has been discovered for this product yet.",
                    evidence_count=0,
                    suggested_source_types=["pricing"],
                )
            ],
        )

    def get_product_gaps(
        self,
        product_id: uuid.UUID,
        *,
        severity: str | None = None,
        category: str | None = None,
    ) -> ProductGapsResponse:
        gap = GapItem(
            gap_code="missing_pricing_page",
            category="pricing",
            severity=severity or "high",
            message="No pricing page has been discovered for this product yet.",
            evidence_count=0,
            suggested_source_types=["pricing"],
        )
        items = [gap]
        if category and category != gap.category:
            items = []
        return ProductGapsResponse(product_id=str(product_id), product_name="Example", items=items)


def override_get_db():
    yield object()


def test_product_claims_endpoint_returns_payload(monkeypatch) -> None:
    monkeypatch.setattr("apps.api.routes.products.ProductIntelligenceService", DummyProductIntelligenceService)
    app.dependency_overrides[get_db] = override_get_db
    client = TestClient(app)
    product_id = uuid.uuid4()

    response = client.get(
        f"/v1/products/{product_id}/claims?min_confidence=0.5&include_stale=true&include_evidence=true"
    )

    assert response.status_code == 200
    body = response.json()["data"]
    assert body["product_id"] == str(product_id)
    assert body["items"][0]["normalized_key"] == "single_sign_on"
    assert body["items"][0]["display_label"] == "Single Sign-On"
    assert body["items"][0]["evidence"][0]["page_type"] == "docs"

    app.dependency_overrides.clear()


def test_product_summary_endpoint_returns_payload(monkeypatch) -> None:
    monkeypatch.setattr("apps.api.routes.products.ProductIntelligenceService", DummyProductIntelligenceService)
    app.dependency_overrides[get_db] = override_get_db
    client = TestClient(app)
    product_id = uuid.uuid4()

    response = client.get(f"/v1/products/{product_id}/summary?min_confidence=0.5&include_evidence=true")

    assert response.status_code == 200
    body = response.json()["data"]
    assert body["product_id"] == str(product_id)
    assert body["stats"]["claim_count"] == 1
    assert body["top_capabilities"][0]["normalized_key"] == "single_sign_on"
    assert body["gaps"][0]["gap_code"] == "missing_pricing_page"

    app.dependency_overrides.clear()


def test_product_gaps_endpoint_returns_payload(monkeypatch) -> None:
    monkeypatch.setattr("apps.api.routes.products.ProductIntelligenceService", DummyProductIntelligenceService)
    app.dependency_overrides[get_db] = override_get_db
    client = TestClient(app)
    product_id = uuid.uuid4()

    response = client.get(f"/v1/products/{product_id}/gaps?severity=high&category=pricing")

    assert response.status_code == 200
    body = response.json()["data"]
    assert body["product_id"] == str(product_id)
    assert body["items"][0]["gap_code"] == "missing_pricing_page"
    assert body["items"][0]["category"] == "pricing"

    app.dependency_overrides.clear()


def test_product_capabilities_endpoint_returns_payload(monkeypatch) -> None:
    monkeypatch.setattr("apps.api.routes.products.ProductQueryService", DummyProductService)
    app.dependency_overrides[get_db] = override_get_db
    client = TestClient(app)
    product_id = uuid.uuid4()

    response = client.get(f"/v1/products/{product_id}/capabilities")

    assert response.status_code == 200
    body = response.json()["data"]
    assert body["product_id"] == str(product_id)
    assert body["items"][0]["label"] == "single_sign_on"

    app.dependency_overrides.clear()


def test_product_evidence_endpoint_returns_payload(monkeypatch) -> None:
    monkeypatch.setattr("apps.api.routes.products.ProductQueryService", DummyProductService)
    app.dependency_overrides[get_db] = override_get_db
    client = TestClient(app)
    product_id = uuid.uuid4()

    response = client.get(f"/v1/products/{product_id}/evidence")

    assert response.status_code == 200
    body = response.json()["data"]
    assert body["product_id"] == str(product_id)
    assert body["items"][0]["evidence_type"] == "capability"

    app.dependency_overrides.clear()
