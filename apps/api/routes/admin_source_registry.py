from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from packages.contracts.api_common import ApiEnvelope
from packages.contracts.source_registry import SourceRegistryListResponse
from packages.core.deps import get_db
from packages.services.source_registry import SourceRegistryService

router = APIRouter(prefix="/v1/admin", tags=["admin"])


@router.get("/source-registry", response_model=ApiEnvelope)
def list_source_registry(
    product_id: str | None = Query(default=None),
    source_group: str | None = Query(default=None),
    policy_zone: str | None = Query(default=None),
    limit: int = Query(default=100, ge=1, le=500),
    db: Session = Depends(get_db),
) -> ApiEnvelope:
    result: SourceRegistryListResponse = SourceRegistryService(db).list_registry_entries(
        product_id=product_id,
        source_group=source_group,
        policy_zone=policy_zone,
        limit=limit,
    )
    return ApiEnvelope(data=result.model_dump())
