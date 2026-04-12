from __future__ import annotations

import uuid
from datetime import datetime, timezone

from sqlalchemy import select
from sqlalchemy.orm import Session

from packages.contracts.discovery import DiscoveredSourceCandidate
from packages.contracts.discovery_review import (
    DiscoveryCandidateDecisionResponse,
    DiscoveryCandidateReviewItem,
    DiscoveryCandidateReviewListResponse,
)
from packages.core.models import DiscoveryCandidate


class DiscoveryReviewService:
    def __init__(self, db: Session) -> None:
        self.db = db

    def create_candidates(
        self,
        *,
        discovery_run_id: str,
        product_id: str | None,
        vendor_domain: str,
        candidates: list[DiscoveredSourceCandidate],
    ) -> list[DiscoveryCandidate]:
        created: list[DiscoveryCandidate] = []
        for candidate in candidates:
            record = DiscoveryCandidate(
                discovery_run_id=uuid.UUID(discovery_run_id),
                product_id=uuid.UUID(product_id) if product_id else None,
                vendor_domain=vendor_domain,
                root_url=candidate.root_url,
                source_family=candidate.source_family,
                source_type=candidate.source_type,
                source_group=candidate.source_group,
                policy_zone=candidate.policy_zone,
                connector_type=candidate.connector_type,
                machine_readable=candidate.machine_readable,
                crawler_mode=candidate.crawler_mode,
                parser_chain=candidate.parser_chain,
                base_confidence_weight=candidate.base_confidence_weight,
                provenance_required=candidate.provenance_required,
                terms_review_required=candidate.terms_review_required,
                notes=candidate.notes,
                review_status="pending",
                candidate_metadata={},
            )
            self.db.add(record)
            created.append(record)
        self.db.flush()
        return created

    def list_candidates(
        self,
        *,
        vendor_domain: str | None,
        source_group: str | None,
        policy_zone: str | None,
        review_status: str | None,
        limit: int,
    ) -> DiscoveryCandidateReviewListResponse:
        stmt = select(DiscoveryCandidate).order_by(DiscoveryCandidate.created_at.desc()).limit(limit)
        if vendor_domain:
            stmt = stmt.where(DiscoveryCandidate.vendor_domain == vendor_domain)
        if source_group:
            stmt = stmt.where(DiscoveryCandidate.source_group == source_group)
        if policy_zone:
            stmt = stmt.where(DiscoveryCandidate.policy_zone == policy_zone)
        if review_status:
            stmt = stmt.where(DiscoveryCandidate.review_status == review_status)

        rows = self.db.execute(stmt).scalars()
        items = [self._to_item(candidate) for candidate in rows]
        return DiscoveryCandidateReviewListResponse(items=items)

    def approve_candidate(self, discovery_candidate_id: str, reviewer_note: str | None) -> DiscoveryCandidateDecisionResponse:
        candidate = self._get_candidate(discovery_candidate_id)
        candidate.review_status = "approved"
        candidate.reviewer_note = reviewer_note
        candidate.approved_at = datetime.now(timezone.utc)
        candidate.rejected_at = None
        self.db.commit()
        return self._decision_response(candidate)

    def reject_candidate(self, discovery_candidate_id: str, reviewer_note: str | None) -> DiscoveryCandidateDecisionResponse:
        candidate = self._get_candidate(discovery_candidate_id)
        candidate.review_status = "rejected"
        candidate.reviewer_note = reviewer_note
        candidate.rejected_at = datetime.now(timezone.utc)
        candidate.approved_at = None
        self.db.commit()
        return self._decision_response(candidate)

    def _get_candidate(self, discovery_candidate_id: str) -> DiscoveryCandidate:
        candidate = self.db.execute(
            select(DiscoveryCandidate).where(DiscoveryCandidate.discovery_candidate_id == uuid.UUID(discovery_candidate_id))
        ).scalar_one()
        return candidate

    def _decision_response(self, candidate: DiscoveryCandidate) -> DiscoveryCandidateDecisionResponse:
        return DiscoveryCandidateDecisionResponse(
            discovery_candidate_id=str(candidate.discovery_candidate_id),
            review_status=candidate.review_status,
            reviewer_note=candidate.reviewer_note,
            approved_at=candidate.approved_at,
            rejected_at=candidate.rejected_at,
        )

    def _to_item(self, candidate: DiscoveryCandidate) -> DiscoveryCandidateReviewItem:
        return DiscoveryCandidateReviewItem(
            discovery_candidate_id=str(candidate.discovery_candidate_id),
            discovery_run_id=str(candidate.discovery_run_id),
            vendor_domain=candidate.vendor_domain,
            root_url=candidate.root_url,
            source_family=candidate.source_family,
            source_type=candidate.source_type,
            source_group=candidate.source_group,
            policy_zone=candidate.policy_zone,
            connector_type=candidate.connector_type,
            machine_readable=candidate.machine_readable,
            crawler_mode=candidate.crawler_mode,
            parser_chain=list(candidate.parser_chain or []),
            base_confidence_weight=candidate.base_confidence_weight,
            provenance_required=candidate.provenance_required,
            terms_review_required=candidate.terms_review_required,
            review_status=candidate.review_status,
            reviewer_note=candidate.reviewer_note,
            notes=candidate.notes,
            promoted_source_id=str(candidate.promoted_source_id) if candidate.promoted_source_id else None,
            trace_id=None,
            approved_at=candidate.approved_at,
            rejected_at=candidate.rejected_at,
            created_at=candidate.created_at,
            updated_at=candidate.updated_at,
        )
