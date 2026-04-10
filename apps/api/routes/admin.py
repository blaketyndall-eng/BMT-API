from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from packages.contracts.admin import CrawlJobListResponse, EvidenceListResponse, PageListResponse
from packages.contracts.api_common import ApiEnvelope
from packages.core.deps import get_db
from packages.services.admin_queries import AdminQueryService

router = APIRouter(prefix="/v1/admin", tags=["admin"])


@router.get("/crawl-jobs", response_model=ApiEnvelope)
def list_crawl_jobs(
    status: str | None = Query(default=None),
    limit: int = Query(default=50, ge=1, le=200),
    db: Session = Depends(get_db),
) -> ApiEnvelope:
    result: CrawlJobListResponse = AdminQueryService(db).list_crawl_jobs(status=status, limit=limit)
    return ApiEnvelope(data=result.model_dump())


@router.get("/pages", response_model=ApiEnvelope)
def list_pages(
    source_id: str | None = Query(default=None),
    limit: int = Query(default=50, ge=1, le=200),
    db: Session = Depends(get_db),
) -> ApiEnvelope:
    result: PageListResponse = AdminQueryService(db).list_pages(source_id=source_id, limit=limit)
    return ApiEnvelope(data=result.model_dump())


@router.get("/evidence", response_model=ApiEnvelope)
def list_evidence(
    evidence_type: str | None = Query(default=None),
    product_id: str | None = Query(default=None),
    vendor_id: str | None = Query(default=None),
    limit: int = Query(default=50, ge=1, le=200),
    db: Session = Depends(get_db),
) -> ApiEnvelope:
    result: EvidenceListResponse = AdminQueryService(db).list_evidence(
        evidence_type=evidence_type,
        product_id=product_id,
        vendor_id=vendor_id,
        limit=limit,
    )
    return ApiEnvelope(data=result.model_dump())
