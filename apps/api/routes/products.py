import uuid

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from packages.contracts.api_common import ApiEnvelope
from packages.contracts.products import ProductCapabilitiesResponse, ProductEvidenceResponse
from packages.core.deps import get_db
from packages.services.product_queries import ProductQueryService

router = APIRouter(prefix="/v1/products", tags=["products"])


@router.get("/{product_id}/capabilities", response_model=ApiEnvelope)
def get_product_capabilities(product_id: uuid.UUID, db: Session = Depends(get_db)) -> ApiEnvelope:
    result: ProductCapabilitiesResponse = ProductQueryService(db).get_product_capabilities(product_id)
    return ApiEnvelope(data=result.model_dump())


@router.get("/{product_id}/evidence", response_model=ApiEnvelope)
def get_product_evidence(product_id: uuid.UUID, db: Session = Depends(get_db)) -> ApiEnvelope:
    result: ProductEvidenceResponse = ProductQueryService(db).get_product_evidence(product_id)
    return ApiEnvelope(data=result.model_dump())
