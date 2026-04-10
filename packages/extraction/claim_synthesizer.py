from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime


@dataclass(frozen=True)
class ClaimEvidenceInput:
    evidence_id: str
    evidence_type: str
    label: str
    snippet: str
    confidence: float
    page_id: str | None
    canonical_url: str | None
    created_at: datetime


@dataclass(frozen=True)
class SynthesizedClaim:
    claim_type: str
    label: str
    confidence: float
    support_count: int
    latest_evidence_at: datetime | None
    evidence: list[ClaimEvidenceInput]


def synthesize_claims(items: list[ClaimEvidenceInput]) -> list[SynthesizedClaim]:
    grouped: dict[tuple[str, str], list[ClaimEvidenceInput]] = {}
    for item in items:
        key = (item.evidence_type, item.label)
        grouped.setdefault(key, []).append(item)

    claims: list[SynthesizedClaim] = []
    for (claim_type, label), evidence_items in grouped.items():
        ordered = sorted(evidence_items, key=lambda item: (item.confidence, item.created_at), reverse=True)
        avg_confidence = sum(item.confidence for item in ordered) / len(ordered)
        confidence_boost = min(0.12, 0.03 * max(0, len(ordered) - 1))
        claim_confidence = min(0.99, round(avg_confidence + confidence_boost, 3))
        latest_evidence_at = max((item.created_at for item in ordered), default=None)

        claims.append(
            SynthesizedClaim(
                claim_type=claim_type,
                label=label,
                confidence=claim_confidence,
                support_count=len(ordered),
                latest_evidence_at=latest_evidence_at,
                evidence=ordered[:5],
            )
        )

    return sorted(
        claims,
        key=lambda claim: (claim.claim_type, claim.confidence, claim.support_count, claim.label),
        reverse=True,
    )
