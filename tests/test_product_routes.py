import uuid
from datetime import datetime, timezone

from fastapi.testclient import TestClient

from apps.api.main import app
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


def override_get_db():
    yield object()


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
