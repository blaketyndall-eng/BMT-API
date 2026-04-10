from datetime import datetime, timezone

from packages.extraction.claim_synthesizer import ClaimEvidenceInput, synthesize_claims


def test_synthesize_claims_groups_by_type_and_label() -> None:
    now = datetime.now(timezone.utc)
    items = [
        ClaimEvidenceInput(
            evidence_id="1",
            evidence_type="capability",
            label="single_sign_on",
            snippet="Supports SSO.",
            confidence=0.74,
            page_id="p1",
            canonical_url="https://example.com/docs/sso",
            created_at=now,
        ),
        ClaimEvidenceInput(
            evidence_id="2",
            evidence_type="capability",
            label="single_sign_on",
            snippet="Single sign-on is supported.",
            confidence=0.80,
            page_id="p2",
            canonical_url="https://example.com/security",
            created_at=now,
        ),
        ClaimEvidenceInput(
            evidence_id="3",
            evidence_type="integration",
            label="salesforce",
            snippet="Integrates with Salesforce.",
            confidence=0.78,
            page_id="p3",
            canonical_url="https://example.com/integrations",
            created_at=now,
        ),
    ]

    claims = synthesize_claims(items)

    assert len(claims) == 2
    sso_claim = next(claim for claim in claims if claim.label == "single_sign_on")
    assert sso_claim.support_count == 2
    assert sso_claim.confidence > 0.80
    salesforce_claim = next(claim for claim in claims if claim.label == "salesforce")
    assert salesforce_claim.claim_type == "integration"
