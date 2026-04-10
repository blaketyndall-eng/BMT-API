from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from packages.contracts.admin import CrawlJobListResponse, PageListResponse
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
