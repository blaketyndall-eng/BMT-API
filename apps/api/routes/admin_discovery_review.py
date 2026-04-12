from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from packages.contracts.api_common import ApiEnvelope
from packages.contracts.discovery_review import (
    DiscoveryCandidateDecisionRequest,
    DiscoveryCandidateDecisionResponse,
    DiscoveryCandidateReviewListResponse,
)
from packages.core.deps import get_db
from packages.services.discovery_review import DiscoveryReviewService

router = APIRouter(prefix="/v1/admin", tags=["admin"])


@router.get("/discovery-candidates", response_model=ApiEnvelope)
def list_discovery_candidates(
    vendor_domain: str | None = Query(default=None),
    source_group: str | None = Query(default=None),
    policy_zone: str | None = Query(default=None),
    review_status: str | None = Query(default=None),
    limit: int = Query(default=100, ge=1, le=500),
    db: Session = Depends(get_db),
) -> ApiEnvelope:
    result: DiscoveryCandidateReviewListResponse = DiscoveryReviewService(db).list_candidates(
        vendor_domain=vendor_domain,
        source_group=source_group,
        policy_zone=policy_zone,
        review_status=review_status,
        limit=limit,
    )
    return ApiEnvelope(data=result.model_dump())


@router.post("/discovery-candidates/{discovery_candidate_id}/approve", response_model=ApiEnvelope)
def approve_discovery_candidate(
    discovery_candidate_id: str,
    payload: DiscoveryCandidateDecisionRequest,
    db: Session = Depends(get_db),
) -> ApiEnvelope:
    result: DiscoveryCandidateDecisionResponse = DiscoveryReviewService(db).approve_candidate(
        discovery_candidate_id=discovery_candidate_id,
        reviewer_note=payload.reviewer_note,
    )
    return ApiEnvelope(data=result.model_dump())


@router.post("/discovery-candidates/{discovery_candidate_id}/reject", response_model=ApiEnvelope)
def reject_discovery_candidate(
    discovery_candidate_id: str,
    payload: DiscoveryCandidateDecisionRequest,
    db: Session = Depends(get_db),
) -> ApiEnvelope:
    result: DiscoveryCandidateDecisionResponse = DiscoveryReviewService(db).reject_candidate(
        discovery_candidate_id=discovery_candidate_id,
        reviewer_note=payload.reviewer_note,
    )
    return ApiEnvelope(data=result.model_dump())
