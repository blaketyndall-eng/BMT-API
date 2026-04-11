from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from packages.contracts.api_common import ApiEnvelope
from packages.contracts.compare import CompareRequest, CompareResponse
from packages.core.deps import get_db
from packages.services.compare_service import CompareService

router = APIRouter(prefix="/v1", tags=["compare"])


@router.post("/compare", response_model=ApiEnvelope)
def compare_products(payload: CompareRequest, db: Session = Depends(get_db)) -> ApiEnvelope:
    result: CompareResponse = CompareService(db).compare_products(payload)
    return ApiEnvelope(data=result.model_dump())
