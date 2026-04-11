from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field

from packages.contracts.claims import NormalizedClaim
from packages.contracts.product_intelligence import GapItem


class CompareFilters(BaseModel):
    claim_types: list[Literal["capability", "integration", "change_event"]] = Field(
        default_factory=lambda: ["capability", "integration"]
    )
    min_confidence: float = Field(default=0.6, ge=0.0, le=1.0)
    include_stale: bool = False
    include_evidence: bool = False


class CompareRequest(BaseModel):
    left_product_id: str
    right_product_id: str
    filters: CompareFilters = Field(default_factory=CompareFilters)


class ComparedClaim(BaseModel):
    normalized_key: str
    display_label: str
    claim_type: str
    left: NormalizedClaim | None
    right: NormalizedClaim | None
    verdict: Literal[
        "shared",
        "left_only",
        "right_only",
        "advantage_left",
        "advantage_right",
        "shared_but_left_stronger",
        "shared_but_right_stronger",
    ]


class CompareSideSummary(BaseModel):
    product_id: str
    product_name: str
    vendor_name: str
    claim_count: int
    high_confidence_claim_count: int
    stale_claim_count: int
    gap_count: int
    last_crawled_at: datetime | None


class CompareResponse(BaseModel):
    generated_at: datetime
    left: CompareSideSummary
    right: CompareSideSummary
    shared: list[ComparedClaim]
    left_only: list[ComparedClaim]
    right_only: list[ComparedClaim]
    left_gaps: list[GapItem]
    right_gaps: list[GapItem]
