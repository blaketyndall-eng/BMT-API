from pydantic import BaseModel, Field


class SourceRegistryEntry(BaseModel):
    source_id: str
    vendor_id: str | None
    product_id: str | None
    root_url: str
    source_family: str
    source_group: str
    source_type: str
    policy_zone: str
    connector_type: str
    machine_readable: bool
    crawler_mode: str
    parser_chain: list[str] = Field(default_factory=list)
    base_confidence_weight: float = Field(ge=0.0, le=1.0)
    freshness_profile: str
    refresh_cadence: str
    provenance_required: bool = True
    terms_review_required: bool = False
    notes: str | None = None


class SourceRegistryListResponse(BaseModel):
    items: list[SourceRegistryEntry] = Field(default_factory=list)
