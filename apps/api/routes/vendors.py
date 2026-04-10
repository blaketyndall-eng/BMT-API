import uuid

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from packages.contracts.api_common import ApiEnvelope
from packages.contracts.admin import VendorSourcesResponse
from packages.contracts.vendor import VendorResolveRequest
from packages.core.deps import get_db
from packages.services.admin_queries import AdminQueryService
from packages.services.vendor_resolution import VendorResolutionService

router = APIRouter(prefix="/v1/vendors", tags=["vendors"])


@router.post("/resolve", response_model=ApiEnvelope)
def resolve_vendor(payload: VendorResolveRequest, db: Session = Depends(get_db)) -> ApiEnvelope:
    result = VendorResolutionService(db).resolve(payload)
    return ApiEnvelope(data=result.model_dump())


@router.get("/{vendor_id}/sources", response_model=ApiEnvelope)
def list_vendor_sources(vendor_id: uuid.UUID, db: Session = Depends(get_db)) -> ApiEnvelope:
    result = AdminQueryService(db).list_vendor_sources(vendor_id)
    return ApiEnvelope(data=result.model_dump())
