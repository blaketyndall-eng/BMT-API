from datetime import datetime

from pydantic import BaseModel, Field


class DiscoveryCandidateReviewItem(BaseModel):
    discovery_run_id: str
    vendor_domain: str
    root_url: str
    source_family: str
    source_type: str
    source_group: str
    policy_zone: str
    connector_type: str
    machine_readable: bool
    crawler_mode: str
    parser_chain: list[str] = Field(default_factory=list)
    base_confidence_weight: float
    provenance_required: bool = True
    terms_review_required: bool = False
    notes: str | None = None
    trace_id: str | None = None
    created_at: datetime


class DiscoveryCandidateReviewListResponse(BaseModel):
    items: list[DiscoveryCandidateReviewItem] = Field(default_factory=list)
