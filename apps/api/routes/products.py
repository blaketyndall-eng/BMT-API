import uuid

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from packages.contracts.api_common import ApiEnvelope
from packages.contracts.claims import ProductClaimsResponse
from packages.contracts.products import ProductCapabilitiesResponse, ProductEvidenceResponse
from packages.core.deps import get_db
from packages.services.product_intelligence import ProductIntelligenceService
from packages.services.product_queries import ProductQueryService

router = APIRouter(prefix="/v1/products", tags=["products"])


@router.get("/{product_id}/claims", response_model=ApiEnvelope)
def get_product_claims(
    product_id: uuid.UUID,
    min_confidence: float = Query(default=0.0, ge=0.0, le=1.0),
    include_stale: bool = Query(default=False),
    include_evidence: bool = Query(default=False),
    db: Session = Depends(get_db),
) -> ApiEnvelope:
    result: ProductClaimsResponse = ProductIntelligenceService(db).get_product_claims(
        product_id,
        min_confidence=min_confidence,
        include_stale=include_stale,
        include_evidence=include_evidence,
    )
    return ApiEnvelope(data=result.model_dump())


@router.get("/{product_id}/capabilities", response_model=ApiEnvelope)
def get_product_capabilities(product_id: uuid.UUID, db: Session = Depends(get_db)) -> ApiEnvelope:
    result: ProductCapabilitiesResponse = ProductQueryService(db).get_product_capabilities(product_id)
    return ApiEnvelope(data=result.model_dump())


@router.get("/{product_id}/evidence", response_model=ApiEnvelope)
def get_product_evidence(product_id: uuid.UUID, db: Session = Depends(get_db)) -> ApiEnvelope:
    result: ProductEvidenceResponse = ProductQueryService(db).get_product_evidence(product_id)
    return ApiEnvelope(data=result.model_dump())
