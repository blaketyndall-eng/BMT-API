from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from packages.contracts.api_common import ApiEnvelope
from packages.contracts.discovery import DiscoveryRequest, DiscoveryResponse
from packages.core.deps import get_db
from packages.services.registry_manager import RegistryManagerService

router = APIRouter(prefix="/v1/admin", tags=["admin"])


@router.post("/discovery/run", response_model=ApiEnvelope)
def run_discovery(payload: DiscoveryRequest, db: Session = Depends(get_db)) -> ApiEnvelope:
    result: DiscoveryResponse = RegistryManagerService(db).run_discovery(payload)
    return ApiEnvelope(data=result.model_dump())
