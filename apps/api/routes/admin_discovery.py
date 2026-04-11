from fastapi import APIRouter

from packages.contracts.api_common import ApiEnvelope
from packages.contracts.discovery import DiscoveryRequest, DiscoveryResponse
from packages.services.registry_manager import RegistryManagerService

router = APIRouter(prefix="/v1/admin", tags=["admin"])


@router.post("/discovery/run", response_model=ApiEnvelope)
def run_discovery(payload: DiscoveryRequest) -> ApiEnvelope:
    result: DiscoveryResponse = RegistryManagerService().run_discovery(payload)
    return ApiEnvelope(data=result.model_dump())
