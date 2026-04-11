from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field

from packages.contracts.claims import NormalizedClaim


class GapItem(BaseModel):
    gap_code: str
    category: Literal["docs", "pricing", "security", "freshness", "integration", "capability"]
    severity: Literal["high", "medium", "low"]
    message: str
    evidence_count: int = 0
    suggested_source_types: list[str] = Field(default_factory=list)


class ProductGapsResponse(BaseModel):
    product_id: str
    product_name: str
    items: list[GapItem]


class ProductSummaryStats(BaseModel):
    source_count: int
    page_count: int
    evidence_count: int
    claim_count: int
    high_confidence_claim_count: int
    stale_claim_count: int
    last_crawled_at: datetime | None


class ProductSummaryResponse(BaseModel):
    product_id: str
    product_name: str
    vendor_id: str
    vendor_name: str
    primary_domain: str | None
    generated_at: datetime
    stats: ProductSummaryStats
    top_capabilities: list[NormalizedClaim]
    top_integrations: list[NormalizedClaim]
    top_changes: list[NormalizedClaim]
    gaps: list[GapItem]
