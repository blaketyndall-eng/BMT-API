from datetime import datetime, timezone

from packages.contracts.claims import ClaimEvidenceRef, NormalizedClaim
from packages.services.evidence_critic_agent import EvidenceCriticAgentService


def _claim(*, claim_id: str, flags: list[str], source_count: int, include_evidence: bool) -> NormalizedClaim:
    evidence = []
    if include_evidence:
        evidence = [
            ClaimEvidenceRef(
                evidence_id="e1",
                page_id="p1",
                source_id="s1",
                canonical_url="https://docs.example.com",
                page_type="docs",
                snippet="Supports SSO.",
                confidence=0.82,
                created_at=datetime.now(timezone.utc),
            )
        ]
    return NormalizedClaim(
        claim_id=claim_id,
        claim_type="capability",
        normalized_key="single_sign_on",
        display_label="Single Sign-On",
        confidence=0.82,
        support_count=1,
        source_count=source_count,
        page_count=1,
        freshness_score=1.0,
        latest_evidence_at=datetime.now(timezone.utc),
        flags=flags,
        evidence=evidence,
    )


def test_critique_claim_marks_thin_or_stale_support() -> None:
    service = EvidenceCriticAgentService(db=None)  # type: ignore[arg-type]

    thin_claim = _claim(claim_id="c1", flags=[], source_count=1, include_evidence=True)
    stale_claim = _claim(claim_id="c2", flags=["stale"], source_count=2, include_evidence=False)

    thin_result = service._critique_claim(thin_claim)
    stale_result = service._critique_claim(stale_claim)

    assert thin_result.support_quality == "thin"
    assert "one source" in thin_result.reason.lower()
    assert stale_result.support_quality == "weak"
    assert any("include_evidence" in recommendation for recommendation in stale_result.recommendations)
