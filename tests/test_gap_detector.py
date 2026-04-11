from datetime import datetime, timezone

from packages.contracts.claims import NormalizedClaim
from packages.services.gap_detector import detect_product_gaps


def _claim(*, claim_type: str, normalized_key: str, confidence: float, source_count: int, flags: list[str]) -> NormalizedClaim:
    return NormalizedClaim(
        claim_id=f"{claim_type}:{normalized_key}",
        claim_type=claim_type,
        normalized_key=normalized_key,
        display_label=normalized_key.replace("_", " ").title(),
        confidence=confidence,
        support_count=1,
        source_count=source_count,
        page_count=1,
        freshness_score=1.0,
        latest_evidence_at=datetime.now(timezone.utc),
        flags=flags,
        evidence=[],
    )


def test_detect_product_gaps_finds_missing_surfaces_and_thin_support() -> None:
    claims = [
        _claim(
            claim_type="integration",
            normalized_key="salesforce",
            confidence=0.72,
            source_count=1,
            flags=[],
        )
    ]

    gaps = detect_product_gaps(page_types={"homepage"}, claims=claims)
    gap_codes = {gap.gap_code for gap in gaps}

    assert "missing_pricing_page" in gap_codes
    assert "missing_docs_surface" in gap_codes
    assert "missing_change_surface" in gap_codes
    assert "no_high_confidence_capabilities" in gap_codes
    assert "integrations_thin_support" in gap_codes
