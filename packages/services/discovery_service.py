from __future__ import annotations

from collections import OrderedDict

from packages.contracts.discovery import DiscoveredSourceCandidate, DiscoveryRequest, DiscoveryResponse
from packages.services.discovery.machine_readable_finder import MachineReadableFinderService
from packages.services.discovery.surface_mapper import SurfaceMapperService


class DiscoveryService:
    def __init__(self) -> None:
        self.surface_mapper = SurfaceMapperService()
        self.machine_readable_finder = MachineReadableFinderService()

    def discover(self, request: DiscoveryRequest) -> DiscoveryResponse:
        candidates: list[DiscoveredSourceCandidate] = []
        candidates.extend(self.surface_mapper.map_vendor_surfaces(request.vendor_domain))
        if request.include_machine_readable:
            candidates.extend(self.machine_readable_finder.find(request.vendor_domain))

        deduped: OrderedDict[str, DiscoveredSourceCandidate] = OrderedDict()
        for candidate in candidates:
            deduped[candidate.root_url] = candidate

        return DiscoveryResponse(vendor_domain=request.vendor_domain, candidates=list(deduped.values()))
