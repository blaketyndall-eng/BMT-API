from __future__ import annotations

import uuid
from dataclasses import dataclass
from datetime import datetime, timezone

from sqlalchemy import select
from sqlalchemy.orm import Session

from packages.contracts.claims import ClaimEvidenceRef, NormalizedClaim, ProductClaimsResponse
from packages.core.models import Evidence, Page, Product, Vendor
from packages.extraction.claim_normalizer import normalize_claim
from packages.extraction.claim_scorer import ScorableClaimEvidence, score_claim


@dataclass(frozen=True)
class ProductContext:
    product_id: str
    product_name: str
    vendor_id: str
    vendor_name: str


@dataclass(frozen=True)
class ClaimEvidenceRow:
    evidence_id: str
    claim_type: str
    label: str
    snippet: str
    confidence: float
    source_id: str | None
    page_id: str | None
    page_type: str | None
    canonical_url: str | None
    created_at: datetime


_CLAIM_TYPE_ORDER = {"capability": 0, "integration": 1, "change_event": 2}


def build_product_claims_response(
    *,
    context: ProductContext,
    rows: list[ClaimEvidenceRow],
    min_confidence: float = 0.0,
    include_stale: bool = False,
    include_evidence: bool = False,
    now: datetime | None = None,
) -> ProductClaimsResponse:
    grouped_rows: dict[tuple[str, str], list[ClaimEvidenceRow]] = {}
    display_labels: dict[tuple[str, str], str] = {}

    for row in rows:
        normalized = normalize_claim(claim_type=row.claim_type, label=row.label)
        key = (normalized.claim_type, normalized.normalized_key)
        grouped_rows.setdefault(key, []).append(row)
        display_labels[key] = normalized.display_label

    claims: list[NormalizedClaim] = []
    current_time = now or datetime.now(timezone.utc)

    for (claim_type, normalized_key), claim_rows in grouped_rows.items():
        ordered_rows = sorted(
            claim_rows,
            key=lambda row: (row.confidence, row.created_at),
            reverse=True,
        )
        score = score_claim(
            [
                ScorableClaimEvidence(
                    source_id=row.source_id,
                    page_id=row.page_id,
                    page_type=row.page_type,
                    confidence=row.confidence,
                    created_at=row.created_at,
                )
                for row in ordered_rows
            ],
            now=current_time,
        )
        if score.confidence < min_confidence:
            continue
        if not include_stale and "stale" in score.flags:
            continue

        evidence_refs: list[ClaimEvidenceRef] = []
        if include_evidence:
            evidence_refs = [
                ClaimEvidenceRef(
                    evidence_id=row.evidence_id,
                    page_id=row.page_id,
                    source_id=row.source_id,
                    canonical_url=row.canonical_url,
                    page_type=row.page_type,
                    snippet=row.snippet,
                    confidence=row.confidence,
                    created_at=row.created_at,
                )
                for row in ordered_rows[:5]
            ]

        claims.append(
            NormalizedClaim(
                claim_id=f"{claim_type}:{normalized_key}",
                claim_type=claim_type,
                normalized_key=normalized_key,
                display_label=display_labels[(claim_type, normalized_key)],
                confidence=score.confidence,
                support_count=len(ordered_rows),
                source_count=score.source_count,
                page_count=score.page_count,
                freshness_score=score.freshness_score,
                latest_evidence_at=score.latest_evidence_at,
                flags=list(score.flags),
                evidence=evidence_refs,
            )
        )

    items = sorted(
        claims,
        key=lambda claim: (
            _CLAIM_TYPE_ORDER.get(claim.claim_type, 99),
            -claim.confidence,
            -claim.source_count,
            -claim.support_count,
            claim.display_label.lower(),
        ),
    )
    return ProductClaimsResponse(
        product_id=context.product_id,
        product_name=context.product_name,
        vendor_id=context.vendor_id,
        vendor_name=context.vendor_name,
        items=items,
        next_cursor=None,
    )


class ProductIntelligenceService:
    def __init__(self, db: Session) -> None:
        self.db = db

    def get_product_claims(
        self,
        product_id: uuid.UUID,
        *,
        min_confidence: float = 0.0,
        include_stale: bool = False,
        include_evidence: bool = False,
    ) -> ProductClaimsResponse:
        context = self._get_product_context(product_id)
        rows = self._get_claim_rows(product_id)
        return build_product_claims_response(
            context=context,
            rows=rows,
            min_confidence=min_confidence,
            include_stale=include_stale,
            include_evidence=include_evidence,
        )

    def _get_product_context(self, product_id: uuid.UUID) -> ProductContext:
        row = self.db.execute(
            select(Product, Vendor)
            .join(Vendor, Product.vendor_id == Vendor.vendor_id)
            .where(Product.product_id == product_id)
        ).one_or_none()
        if row is None:
            raise ValueError(f"Product not found: {product_id}")

        product, vendor = row
        return ProductContext(
            product_id=str(product.product_id),
            product_name=product.canonical_name,
            vendor_id=str(vendor.vendor_id),
            vendor_name=vendor.canonical_name,
        )

    def _get_claim_rows(self, product_id: uuid.UUID) -> list[ClaimEvidenceRow]:
        rows = self.db.execute(
            select(Evidence, Page)
            .outerjoin(Page, Evidence.page_id == Page.page_id)
            .where(Evidence.product_id == product_id)
            .order_by(Evidence.created_at.desc())
        ).all()
        return [
            ClaimEvidenceRow(
                evidence_id=str(evidence.evidence_id),
                claim_type=evidence.evidence_type,
                label=evidence.label,
                snippet=evidence.snippet,
                confidence=evidence.confidence,
                source_id=str(evidence.source_id) if evidence.source_id else None,
                page_id=str(evidence.page_id) if evidence.page_id else None,
                page_type=page.page_type if page else None,
                canonical_url=page.canonical_url if page else None,
                created_at=evidence.created_at,
            )
            for evidence, page in rows
        ]
