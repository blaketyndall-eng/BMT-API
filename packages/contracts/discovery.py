from pydantic import BaseModel, Field

from packages.contracts.source_registry import SourceRegistryEntry


class DiscoveryRunRequest(BaseModel):
    product_id: str
    include_machine_readable: bool = True
    include_ecosystem: bool = False
    limit: int = Field(default=50, ge=1, le=200)


class DiscoveryAgentSummary(BaseModel):
    agent_name: str
    strategy_version: str
    mode: str


class DiscoveryRunResponse(BaseModel):
    product_id: str
    vendor_id: str | None
    domain: str | None
    agent: DiscoveryAgentSummary
    candidates: list[SourceRegistryEntry] = Field(default_factory=list)
