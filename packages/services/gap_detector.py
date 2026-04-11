from __future__ import annotations

from packages.contracts.claims import NormalizedClaim
from packages.contracts.product_intelligence import GapItem

_DOCS_PAGE_TYPES = {"docs", "api_reference"}
_CHANGE_PAGE_TYPES = {"changelog"}
_PRICING_PAGE_TYPES = {"pricing"}


def detect_product_gaps(*, page_types: set[str | None], claims: list[NormalizedClaim]) -> list[GapItem]:
    gaps: list[GapItem] = []

    if not any(page_type in _PRICING_PAGE_TYPES for page_type in page_types):
        gaps.append(
            GapItem(
                gap_code="missing_pricing_page",
                category="pricing",
                severity="high",
                message="No pricing page has been discovered for this product yet.",
                suggested_source_types=["pricing"],
            )
        )

    if not any(page_type in _DOCS_PAGE_TYPES for page_type in page_types):
        gaps.append(
            GapItem(
                gap_code="missing_docs_surface",
                category="docs",
                severity="high",
                message="No docs or API reference surface has been discovered for this product yet.",
                suggested_source_types=["docs_subdomain", "developers_subdomain", "docs_path", "api_reference"],
            )
        )

    if not any(page_type in _CHANGE_PAGE_TYPES for page_type in page_types):
        gaps.append(
            GapItem(
                gap_code="missing_change_surface",
                category="freshness",
                severity="medium",
                message="No changelog or release-notes surface has been discovered for this product yet.",
                suggested_source_types=["changelog", "release_notes"],
            )
        )

    capability_claims = [claim for claim in claims if claim.claim_type == "capability"]
    integration_claims = [claim for claim in claims if claim.claim_type == "integration"]
    stale_claims = [claim for claim in claims if "stale" in claim.flags]
    high_confidence_capabilities = [claim for claim in capability_claims if claim.confidence >= 0.75]

    if not high_confidence_capabilities:
        gaps.append(
            GapItem(
                gap_code="no_high_confidence_capabilities",
                category="capability",
                severity="high",
                message="No high-confidence capability claims are available yet.",
                evidence_count=len(capability_claims),
                suggested_source_types=["docs_subdomain", "developers_subdomain", "docs_path", "api_reference"],
            )
        )

    if integration_claims and all(claim.source_count <= 1 for claim in integration_claims):
        gaps.append(
            GapItem(
                gap_code="integrations_thin_support",
                category="integration",
                severity="medium",
                message="Integration claims exist, but they are only supported by a single source each.",
                evidence_count=sum(claim.support_count for claim in integration_claims),
                suggested_source_types=["docs_subdomain", "docs_path", "api_reference"],
            )
        )

    if stale_claims:
        gaps.append(
            GapItem(
                gap_code="claims_stale",
                category="freshness",
                severity="medium",
                message="Some claims are stale and should be refreshed with a new crawl.",
                evidence_count=len(stale_claims),
                suggested_source_types=["homepage", "docs_subdomain", "api_reference", "changelog"],
            )
        )

    return gaps
