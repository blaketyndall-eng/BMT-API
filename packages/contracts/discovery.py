from pydantic import BaseModel, Field


class DiscoveryRequest(BaseModel):
    vendor_domain: str
    product_id: str | None = None
    include_machine_readable: bool = True


class DiscoveredSourceCandidate(BaseModel):
    root_url: str
    source_family: str
    source_type: str
    source_group: str
    policy_zone: str
    connector_type: str
    machine_readable: bool
    crawler_mode: str
    parser_chain: list[str] = Field(default_factory=list)
    base_confidence_weight: float = Field(ge=0.0, le=1.0)
    provenance_required: bool = True
    terms_review_required: bool = False
    notes: str | None = None


class DiscoveryResponse(BaseModel):
    vendor_domain: str
    candidates: list[DiscoveredSourceCandidate] = Field(default_factory=list)
