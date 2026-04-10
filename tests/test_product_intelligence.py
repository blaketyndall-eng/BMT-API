from datetime import datetime, timedelta, timezone

from packages.services.product_intelligence import (
    ClaimEvidenceRow,
    ProductContext,
    build_product_claims_response,
)


def test_build_product_claims_response_groups_and_scores_normalized_claims() -> None:
    now = datetime.now(timezone.utc)
    context = ProductContext(
        product_id="product-1",
        product_name="Example",
        vendor_id="vendor-1",
        vendor_name="Example Inc",
    )
    rows = [
        ClaimEvidenceRow(
            evidence_id="e1",
            claim_type="capability",
            label="single_sign_on",
            snippet="Supports SSO in docs.",
            confidence=0.74,
            source_id="source-1",
            page_id="page-1",
            page_type="docs",
            canonical_url="https://docs.example.com/sso",
            created_at=now - timedelta(days=7),
        ),
        ClaimEvidenceRow(
            evidence_id="e2",
            claim_type="capability",
            label="sso",
            snippet="SSO supported in API reference.",
            confidence=0.78,
            source_id="source-2",
            page_id="page-2",
            page_type="api_reference",
            canonical_url="https://developers.example.com/api/auth",
            created_at=now - timedelta(days=3),
        ),
        ClaimEvidenceRow(
            evidence_id="e3",
            claim_type="integration",
            label="salesforce",
            snippet="Integrates with Salesforce.",
            confidence=0.76,
            source_id="source-3",
            page_id="page-3",
            page_type="docs",
            canonical_url="https://docs.example.com/integrations/salesforce",
            created_at=now - timedelta(days=2),
        ),
    ]

    response = build_product_claims_response(
        context=context,
        rows=rows,
        min_confidence=0.0,
        include_stale=False,
        include_evidence=True,
        now=now,
    )

    assert response.product_id == "product-1"
    assert len(response.items) == 2
    sso_claim = next(claim for claim in response.items if claim.normalized_key == "single_sign_on")
    assert sso_claim.support_count == 2
    assert sso_claim.source_count == 2
    assert sso_claim.display_label == "Single Sign-On"
    assert len(sso_claim.evidence) == 2
