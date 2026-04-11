from datetime import datetime, timezone

from packages.contracts.claims import NormalizedClaim
from packages.services.compare_service import _compare_claim_sets


def _claim(*, claim_type: str, normalized_key: str, confidence: float) -> NormalizedClaim:
    return NormalizedClaim(
        claim_id=f"{claim_type}:{normalized_key}",
        claim_type=claim_type,
        normalized_key=normalized_key,
        display_label=normalized_key.replace("_", " ").title(),
        confidence=confidence,
        support_count=1,
        source_count=1,
        page_count=1,
        freshness_score=1.0,
        latest_evidence_at=datetime.now(timezone.utc),
        flags=[],
        evidence=[],
    )


def test_compare_claim_sets_marks_stronger_and_unique_claims() -> None:
    left_claims = [
        _claim(claim_type="capability", normalized_key="single_sign_on", confidence=0.88),
        _claim(claim_type="integration", normalized_key="salesforce", confidence=0.77),
    ]
    right_claims = [
        _claim(claim_type="capability", normalized_key="single_sign_on", confidence=0.72),
        _claim(claim_type="integration", normalized_key="slack", confidence=0.76),
    ]

    shared, left_only, right_only = _compare_claim_sets(left_claims=left_claims, right_claims=right_claims)

    assert len(shared) == 1
    assert shared[0].verdict == "shared_but_left_stronger"
    assert len(left_only) == 1
    assert left_only[0].normalized_key == "salesforce"
    assert len(right_only) == 1
    assert right_only[0].normalized_key == "slack"
