from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from packages.contracts.api_common import ApiEnvelope
from packages.contracts.discovery_review import DiscoveryCandidateReviewListResponse
from packages.core.deps import get_db
from packages.services.discovery_review import DiscoveryReviewService

router = APIRouter(prefix="/v1/admin", tags=["admin"])


@router.get("/discovery-candidates", response_model=ApiEnvelope)
def list_discovery_candidates(
    vendor_domain: str | None = Query(default=None),
    source_group: str | None = Query(default=None),
    policy_zone: str | None = Query(default=None),
    limit: int = Query(default=100, ge=1, le=500),
    db: Session = Depends(get_db),
) -> ApiEnvelope:
    result: DiscoveryCandidateReviewListResponse = DiscoveryReviewService(db).list_candidates(
        vendor_domain=vendor_domain,
        source_group=source_group,
        policy_zone=policy_zone,
        limit=limit,
    )
    return ApiEnvelope(data=result.model_dump())
