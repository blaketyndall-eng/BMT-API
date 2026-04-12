from __future__ import annotations

import uuid

from sqlalchemy import select
from sqlalchemy.orm import Session

from packages.core.models import Source
from packages.services.gap_detector import detect_product_gaps
from packages.services.product_intelligence import ProductIntelligenceService, build_normalized_claims


class GapClosureService:
    def __init__(self, db: Session) -> None:
        self.db = db
        self.product_intelligence = ProductIntelligenceService(db)

    def compute(self, product_id: str | uuid.UUID, source_id: str | uuid.UUID) -> float:
        product_uuid = uuid.UUID(str(product_id))
        source_uuid = uuid.UUID(str(source_id))
        source = self.db.execute(select(Source).where(Source.source_id == source_uuid)).scalar_one_or_none()
        if source is None:
            return 0.0

        rows = self.product_intelligence._get_claim_rows(product_uuid)
        claims = build_normalized_claims(rows=rows, min_confidence=0.0, include_stale=True, include_evidence=False)
        page_types = self.product_intelligence._get_page_types(product_uuid)
        gaps = detect_product_gaps(page_types=page_types, claims=claims)
        gap_codes = {gap.gap_code for gap in gaps}

        score = 0.0
        if source.source_type == "pricing" and "missing_pricing_page" not in gap_codes:
            score += 0.35
        if source.source_type in {"docs_subdomain", "docs_path", "developers_subdomain"} and "missing_docs_surface" not in gap_codes:
            score += 0.35
        if source.source_type in {"changelog", "release_notes"} and "missing_change_surface" not in gap_codes:
            score += 0.2
        if source.source_type == "integrations_directory" and "integrations_thin_support" not in gap_codes:
            score += 0.2
        if source.source_type == "homepage" and "claims_stale" not in gap_codes:
            score += 0.1
        if "no_high_confidence_capabilities" not in gap_codes:
            score += 0.15

        return round(min(score, 1.0), 3)
