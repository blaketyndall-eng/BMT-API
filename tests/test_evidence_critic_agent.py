from datetime import datetime, timezone

from packages.contracts.claims import ClaimEvidenceRef, NormalizedClaim
from packages.services.evidence_critic_agent import EvidenceCriticAgentService


class DummyStore:
    def __init__(self):
        self.calls = []

    def create_agent_run(self, **kwargs):
        self.calls.append(kwargs)
        return object()


class DummySession:
    def commit(self):
        return None


class DummyClaimsResponse:
    def __init__(self, items):
        self.items = items


class DummyProductIntelligence:
    def __init__(self, items):
        self.items = items

    def get_product_claims(self, product_id, min_confidence, include_stale, include_evidence):
        return DummyClaimsResponse(self.items)


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
        normalized_key="single_sign_on" if claim_id == "c1" else "api_access",
        display_label="Single Sign-On" if claim_id == "c1" else "API Access",
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
    service = EvidenceCriticAgentService(DummySession())  # type: ignore[arg-type]
    service.agent_run_store = DummyStore()

    thin_claim = _claim(claim_id="c1", flags=[], source_count=1, include_evidence=True)
    stale_claim = _claim(claim_id="c2", flags=["stale"], source_count=2, include_evidence=False)

    thin_result = service._critique_claim(thin_claim)
    stale_result = service._critique_claim(stale_claim)

    assert thin_result.support_quality == "thin"
    assert "one source" in thin_result.reason.lower()
    assert stale_result.support_quality == "weak"
    assert any("include_evidence" in recommendation for recommendation in stale_result.recommendations)


def test_critique_returns_claim_verification_summary() -> None:
    items = [
        _claim(claim_id="c1", flags=[], source_count=1, include_evidence=True),
        _claim(claim_id="c2", flags=["stale"], source_count=2, include_evidence=False),
    ]
    service = EvidenceCriticAgentService(DummySession())  # type: ignore[arg-type]
    service.product_intelligence = DummyProductIntelligence(items)
    service.agent_run_store = DummyStore()

    response = service.critique(type("Req", (), {"product_id": "00000000-0000-0000-0000-000000000001", "min_confidence": 0.6, "limit": 5, "model_dump": lambda self: {"product_id": "00000000-0000-0000-0000-000000000001", "min_confidence": 0.6, "limit": 5}})())

    assert response.claim_verification is not None
    assert response.claim_verification.thin_claim_count == 1
    assert response.claim_verification.stale_supported_claim_count == 1
    assert len(service.agent_run_store.calls) == 1
