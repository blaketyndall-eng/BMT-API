from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from packages.contracts.api_common import ApiEnvelope
from packages.contracts.entity_resolution import EntityResolutionRequest, EntityResolutionResponse
from packages.core.deps import get_db
from packages.services.entity_resolution import EntityResolutionService

router = APIRouter(prefix="/v1/admin", tags=["admin"])


@router.post("/entity-resolution/resolve", response_model=ApiEnvelope)
def resolve_entities(payload: EntityResolutionRequest, db: Session = Depends(get_db)) -> ApiEnvelope:
    result: EntityResolutionResponse = EntityResolutionService(db).resolve(payload)
    return ApiEnvelope(data=result.model_dump())
