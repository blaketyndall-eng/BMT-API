from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field

ClaimType = Literal["capability", "integration", "change_event"]


class ClaimEvidenceRef(BaseModel):
    evidence_id: str
    page_id: str | None
    source_id: str | None
    canonical_url: str | None
    page_type: str | None
    snippet: str
    confidence: float
    created_at: datetime


class NormalizedClaim(BaseModel):
    claim_id: str
    claim_type: ClaimType
    normalized_key: str
    display_label: str
    confidence: float
    support_count: int
    source_count: int
    page_count: int
    freshness_score: float
    latest_evidence_at: datetime | None
    flags: list[str] = Field(default_factory=list)
    evidence: list[ClaimEvidenceRef] = Field(default_factory=list)


class ProductClaimsResponse(BaseModel):
    product_id: str
    product_name: str
    vendor_id: str
    vendor_name: str
    items: list[NormalizedClaim]
    next_cursor: str | None = None
