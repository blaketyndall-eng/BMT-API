from __future__ import annotations

from collections import OrderedDict

from sqlalchemy.orm import Session

from packages.contracts.discovery import DiscoveredSourceCandidate, DiscoveryRequest, DiscoveryResponse
from packages.services.agent_run_store import AgentRunStore
from packages.services.discovery.ecosystem_finder import EcosystemFinderService
from packages.services.discovery.machine_readable_finder import MachineReadableFinderService
from packages.services.discovery.surface_mapper import SurfaceMapperService

DISCOVERY_AGENT_NAME = "registry_manager_discovery"
DISCOVERY_STRATEGY_VERSION = "discovery_v1"


class RegistryManagerService:
    def __init__(self, db: Session) -> None:
        self.db = db
        self.agent_run_store = AgentRunStore(db)
        self.surface_mapper = SurfaceMapperService()
        self.machine_readable_finder = MachineReadableFinderService()
        self.ecosystem_finder = EcosystemFinderService()

    def run_discovery(self, request: DiscoveryRequest) -> DiscoveryResponse:
        groups_run: list[str] = []
        candidates: list[DiscoveredSourceCandidate] = []

        candidates.extend(self.surface_mapper.map_vendor_surfaces(request.vendor_domain))
        groups_run.append("surface_mapper")

        if request.include_machine_readable:
            candidates.extend(self.machine_readable_finder.find(request.vendor_domain))
            groups_run.append("machine_readable_finder")

        if request.include_ecosystem:
            candidates.extend(self.ecosystem_finder.find(request.vendor_domain))
            groups_run.append("ecosystem_finder")

        deduped: OrderedDict[str, DiscoveredSourceCandidate] = OrderedDict()
        for candidate in candidates:
            deduped[candidate.root_url] = candidate

        response = DiscoveryResponse(
            vendor_domain=request.vendor_domain,
            candidates=list(deduped.values()),
            discovery_groups_run=groups_run,
        )
        self.agent_run_store.create_agent_run(
            agent_name=DISCOVERY_AGENT_NAME,
            strategy_version=DISCOVERY_STRATEGY_VERSION,
            mode="manager_orchestrated_discovery",
            product_id=request.product_id,
            vendor_id=None,
            request_payload=request.model_dump(),
            response_payload=response.model_dump(),
        )
        self.db.commit()
        return response
