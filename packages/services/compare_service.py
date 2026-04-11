from __future__ import annotations

import uuid
from datetime import datetime, timezone

from sqlalchemy.orm import Session

from packages.contracts.claims import NormalizedClaim
from packages.contracts.compare import (
    CompareRequest,
    CompareResponse,
    CompareSideSummary,
    ComparedClaim,
)
from packages.observability.tracing import log_event, traced_span
from packages.services.product_intelligence import ProductIntelligenceService


def _claim_key(claim: NormalizedClaim) -> tuple[str, str]:
    return (claim.claim_type, claim.normalized_key)


def _compare_claim_sets(
    *,
    left_claims: list[NormalizedClaim],
    right_claims: list[NormalizedClaim],
) -> tuple[list[ComparedClaim], list[ComparedClaim], list[ComparedClaim]]:
    left_index = {_claim_key(claim): claim for claim in left_claims}
    right_index = {_claim_key(claim): claim for claim in right_claims}
    all_keys = sorted(set(left_index) | set(right_index), key=lambda item: (item[0], item[1]))

    shared: list[ComparedClaim] = []
    left_only: list[ComparedClaim] = []
    right_only: list[ComparedClaim] = []

    for key in all_keys:
        left = left_index.get(key)
        right = right_index.get(key)
        claim_type, normalized_key = key
        display_label = left.display_label if left else right.display_label  # type: ignore[union-attr]

        if left and right:
            delta = left.confidence - right.confidence
            if abs(delta) < 0.1:
                verdict = "shared"
            elif delta > 0:
                verdict = "shared_but_left_stronger"
            else:
                verdict = "shared_but_right_stronger"
            shared.append(
                ComparedClaim(
                    normalized_key=normalized_key,
                    display_label=display_label,
                    claim_type=claim_type,
                    left=left,
                    right=right,
                    verdict=verdict,
                )
            )
            continue

        if left:
            left_only.append(
                ComparedClaim(
                    normalized_key=normalized_key,
                    display_label=display_label,
                    claim_type=claim_type,
                    left=left,
                    right=None,
                    verdict="left_only",
                )
            )
            continue

        if right:
            right_only.append(
                ComparedClaim(
                    normalized_key=normalized_key,
                    display_label=display_label,
                    claim_type=claim_type,
                    left=None,
                    right=right,
                    verdict="right_only",
                )
            )

    return shared, left_only, right_only


class CompareService:
    def __init__(self, db: Session) -> None:
        self.db = db
        self.product_intelligence = ProductIntelligenceService(db)

    def compare_products(self, request: CompareRequest) -> CompareResponse:
        left_product_id = uuid.UUID(request.left_product_id)
        right_product_id = uuid.UUID(request.right_product_id)

        with traced_span(
            "compare.products",
            left_product_id=str(left_product_id),
            right_product_id=str(right_product_id),
        ):
            left_claims_response = self.product_intelligence.get_product_claims(
                left_product_id,
                min_confidence=request.filters.min_confidence,
                include_stale=request.filters.include_stale,
                include_evidence=request.filters.include_evidence,
            )
            right_claims_response = self.product_intelligence.get_product_claims(
                right_product_id,
                min_confidence=request.filters.min_confidence,
                include_stale=request.filters.include_stale,
                include_evidence=request.filters.include_evidence,
            )

            allowed_claim_types = set(request.filters.claim_types)
            left_claims = [claim for claim in left_claims_response.items if claim.claim_type in allowed_claim_types]
            right_claims = [claim for claim in right_claims_response.items if claim.claim_type in allowed_claim_types]

            left_summary = self.product_intelligence.get_product_summary(
                left_product_id,
                min_confidence=request.filters.min_confidence,
                include_evidence=False,
            )
            right_summary = self.product_intelligence.get_product_summary(
                right_product_id,
                min_confidence=request.filters.min_confidence,
                include_evidence=False,
            )

            shared, left_only, right_only = _compare_claim_sets(
                left_claims=left_claims,
                right_claims=right_claims,
            )
            log_event(
                "compare.products.completed",
                shared_count=len(shared),
                left_only_count=len(left_only),
                right_only_count=len(right_only),
            )

            return CompareResponse(
                generated_at=datetime.now(timezone.utc),
                left=CompareSideSummary(
                    product_id=left_claims_response.product_id,
                    product_name=left_claims_response.product_name,
                    vendor_name=left_claims_response.vendor_name,
                    claim_count=len(left_claims),
                    high_confidence_claim_count=len([claim for claim in left_claims if claim.confidence >= 0.75]),
                    stale_claim_count=len([claim for claim in left_claims if "stale" in claim.flags]),
                    gap_count=len(left_summary.gaps),
                    last_crawled_at=left_summary.stats.last_crawled_at,
                ),
                right=CompareSideSummary(
                    product_id=right_claims_response.product_id,
                    product_name=right_claims_response.product_name,
                    vendor_name=right_claims_response.vendor_name,
                    claim_count=len(right_claims),
                    high_confidence_claim_count=len([claim for claim in right_claims if claim.confidence >= 0.75]),
                    stale_claim_count=len([claim for claim in right_claims if "stale" in claim.flags]),
                    gap_count=len(right_summary.gaps),
                    last_crawled_at=right_summary.stats.last_crawled_at,
                ),
                shared=shared,
                left_only=left_only,
                right_only=right_only,
                left_gaps=left_summary.gaps,
                right_gaps=right_summary.gaps,
            )
