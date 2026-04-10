from __future__ import annotations

import uuid

from sqlalchemy import select
from sqlalchemy.orm import Session

from packages.contracts.products import (
    CapabilityClaim,
    ClaimEvidenceRef,
    ProductCapabilitiesResponse,
    ProductEvidenceItem,
    ProductEvidenceResponse,
)
from packages.core.models import Evidence, Page
from packages.extraction.claim_synthesizer import ClaimEvidenceInput, synthesize_claims


class ProductQueryService:
    def __init__(self, db: Session) -> None:
        self.db = db

    def get_product_capabilities(self, product_id: uuid.UUID) -> ProductCapabilitiesResponse:
        rows = self.db.execute(
            select(Evidence, Page)
            .outerjoin(Page, Evidence.page_id == Page.page_id)
            .where(
                Evidence.product_id == product_id,
                Evidence.evidence_type.in_(["capability", "integration"]),
            )
            .order_by(Evidence.created_at.desc())
        ).all()

        inputs = [
            ClaimEvidenceInput(
                evidence_id=str(evidence.evidence_id),
                evidence_type=evidence.evidence_type,
                label=evidence.label,
                snippet=evidence.snippet,
                confidence=evidence.confidence,
                page_id=str(evidence.page_id) if evidence.page_id else None,
                canonical_url=page.canonical_url if page else None,
                created_at=evidence.created_at,
            )
            for evidence, page in rows
        ]
        claims = synthesize_claims(inputs)

        items = [
            CapabilityClaim(
                claim_type=claim.claim_type,
                label=claim.label,
                confidence=claim.confidence,
                support_count=claim.support_count,
                latest_evidence_at=claim.latest_evidence_at,
                evidence=[
                    ClaimEvidenceRef(
                        evidence_id=evidence.evidence_id,
                        page_id=evidence.page_id,
                        canonical_url=evidence.canonical_url,
                        snippet=evidence.snippet,
                        confidence=evidence.confidence,
                        created_at=evidence.created_at,
                    )
                    for evidence in claim.evidence
                ],
            )
            for claim in claims
        ]
        return ProductCapabilitiesResponse(product_id=str(product_id), items=items)

    def get_product_evidence(self, product_id: uuid.UUID) -> ProductEvidenceResponse:
        rows = self.db.execute(
            select(Evidence, Page)
            .outerjoin(Page, Evidence.page_id == Page.page_id)
            .where(Evidence.product_id == product_id)
            .order_by(Evidence.created_at.desc())
        ).all()

        items = [
            ProductEvidenceItem(
                evidence_id=str(evidence.evidence_id),
                evidence_type=evidence.evidence_type,
                label=evidence.label,
                snippet=evidence.snippet,
                confidence=evidence.confidence,
                canonical_url=page.canonical_url if page else None,
                page_id=str(evidence.page_id) if evidence.page_id else None,
                created_at=evidence.created_at,
                updated_at=evidence.updated_at,
            )
            for evidence, page in rows
        ]
        return ProductEvidenceResponse(product_id=str(product_id), items=items)
