from datetime import datetime, timedelta, timezone

from packages.extraction.claim_scorer import ScorableClaimEvidence, score_claim


def test_score_claim_rewards_docs_backed_multi_source_evidence() -> None:
    now = datetime.now(timezone.utc)
    items = [
        ScorableClaimEvidence(
            source_id="source-1",
            page_id="page-1",
            page_type="docs",
            confidence=0.74,
            created_at=now - timedelta(days=5),
        ),
        ScorableClaimEvidence(
            source_id="source-2",
            page_id="page-2",
            page_type="api_reference",
            confidence=0.78,
            created_at=now - timedelta(days=2),
        ),
    ]

    score = score_claim(items, now=now)

    assert score.confidence > 0.82
    assert score.freshness_score == 1.0
    assert score.source_count == 2
    assert "docs_backed" in score.flags
    assert "multi_source" in score.flags


def test_score_claim_penalizes_old_homepage_only_evidence() -> None:
    now = datetime.now(timezone.utc)
    items = [
        ScorableClaimEvidence(
            source_id="source-1",
            page_id="page-1",
            page_type="homepage",
            confidence=0.72,
            created_at=now - timedelta(days=210),
        )
    ]

    score = score_claim(items, now=now)

    assert score.confidence < 0.6
    assert score.freshness_score == 0.2
    assert "thin_support" in score.flags
    assert "stale" in score.flags
