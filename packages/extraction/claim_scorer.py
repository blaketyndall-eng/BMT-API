from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone

_DOCS_PAGE_TYPES = {"docs", "api_reference"}
_LOW_TRUST_PAGE_TYPES = {"homepage", "generic", None}


@dataclass(frozen=True)
class ScorableClaimEvidence:
    source_id: str | None
    page_id: str | None
    page_type: str | None
    confidence: float
    created_at: datetime


@dataclass(frozen=True)
class ClaimScore:
    confidence: float
    freshness_score: float
    latest_evidence_at: datetime | None
    source_count: int
    page_count: int
    flags: tuple[str, ...]


def freshness_score_for_timestamp(
    latest_evidence_at: datetime | None,
    *,
    now: datetime | None = None,
) -> float:
    if latest_evidence_at is None:
        return 0.0

    current_time = now or datetime.now(timezone.utc)
    age_days = max(0, (current_time - latest_evidence_at).days)
    if age_days <= 30:
        return 1.0
    if age_days <= 90:
        return 0.7
    if age_days <= 180:
        return 0.4
    return 0.2


def score_claim(
    evidence_items: list[ScorableClaimEvidence],
    *,
    now: datetime | None = None,
) -> ClaimScore:
    if not evidence_items:
        return ClaimScore(
            confidence=0.0,
            freshness_score=0.0,
            latest_evidence_at=None,
            source_count=0,
            page_count=0,
            flags=("empty",),
        )

    latest_evidence_at = max(item.created_at for item in evidence_items)
    freshness_score = freshness_score_for_timestamp(latest_evidence_at, now=now)
    source_count = len({item.source_id for item in evidence_items if item.source_id})
    page_count = len({item.page_id for item in evidence_items if item.page_id})
    base_confidence = sum(item.confidence for item in evidence_items) / len(evidence_items)
    source_bonus = min(0.10, 0.05 * max(0, source_count - 1))
    page_bonus = min(0.05, 0.02 * max(0, page_count - 1))
    has_docs_backing = any(item.page_type in _DOCS_PAGE_TYPES for item in evidence_items)
    docs_bonus = 0.05 if has_docs_backing else 0.0
    has_only_low_trust_pages = all(item.page_type in _LOW_TRUST_PAGE_TYPES for item in evidence_items)
    homepage_penalty = 0.05 if has_only_low_trust_pages else 0.0
    stale_penalty = 0.10 if freshness_score <= 0.4 else 0.0
    final_confidence = max(
        0.0,
        min(
            0.99,
            round(
                base_confidence + source_bonus + page_bonus + docs_bonus - homepage_penalty - stale_penalty,
                3,
            ),
        ),
    )

    flags: list[str] = []
    if source_count <= 1:
        flags.append("thin_support")
    if source_count > 1:
        flags.append("multi_source")
    if has_docs_backing:
        flags.append("docs_backed")
    if freshness_score <= 0.4:
        flags.append("stale")

    return ClaimScore(
        confidence=final_confidence,
        freshness_score=freshness_score,
        latest_evidence_at=latest_evidence_at,
        source_count=source_count,
        page_count=page_count,
        flags=tuple(flags),
    )
