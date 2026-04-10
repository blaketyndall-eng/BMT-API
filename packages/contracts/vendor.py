from typing import Literal

from pydantic import BaseModel, Field


class VendorResolveInput(BaseModel):
    type: Literal["domain"] = "domain"
    value: str


class VendorResolveOptions(BaseModel):
    discover_sources: bool = True
    seed_crawl: bool = True


class VendorResolveRequest(BaseModel):
    input: VendorResolveInput
    options: VendorResolveOptions = Field(default_factory=VendorResolveOptions)


class DiscoveredSourceResponse(BaseModel):
    source_id: str
    source_type: str
    source_family: str
    root_url: str
    connector_type: str


class VendorResolveResponse(BaseModel):
    vendor_id: str
    primary_product_id: str
    canonical_name: str
    primary_domain: str
    match_confidence: float
    discovered_sources: list[DiscoveredSourceResponse]
    seeded_job_ids: list[str]
