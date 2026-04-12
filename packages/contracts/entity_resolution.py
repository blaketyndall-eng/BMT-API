from pydantic import BaseModel, Field


class EntityResolutionRequest(BaseModel):
    vendor_domain: str | None = None
    root_url: str | None = None
    artifact_slug: str | None = None


class VendorResolutionMatch(BaseModel):
    vendor_id: str
    canonical_name: str
    canonical_slug: str
    primary_domain: str | None = None
    match_reason: str
    confidence: float = Field(ge=0.0, le=1.0)


class ProductResolutionMatch(BaseModel):
    product_id: str
    canonical_name: str
    canonical_slug: str
    vendor_id: str
    match_reason: str
    confidence: float = Field(ge=0.0, le=1.0)


class EntityResolutionResponse(BaseModel):
    vendor_domain: str | None = None
    root_url: str | None = None
    artifact_slug: str | None = None
    vendor_matches: list[VendorResolutionMatch] = Field(default_factory=list)
    product_matches: list[ProductResolutionMatch] = Field(default_factory=list)
