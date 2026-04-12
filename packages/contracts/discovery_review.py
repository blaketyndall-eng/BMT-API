from datetime import datetime

from pydantic import BaseModel, Field


class DiscoveryCandidateReviewItem(BaseModel):
    discovery_candidate_id: str
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
    review_status: str
    reviewer_note: str | None = None
    notes: str | None = None
    promoted_source_id: str | None = None
    trace_id: str | None = None
    approved_at: datetime | None = None
    rejected_at: datetime | None = None
    created_at: datetime
    updated_at: datetime


class DiscoveryCandidateReviewListResponse(BaseModel):
    items: list[DiscoveryCandidateReviewItem] = Field(default_factory=list)


class DiscoveryCandidateDecisionResponse(BaseModel):
    discovery_candidate_id: str
    review_status: str
    reviewer_note: str | None = None
    approved_at: datetime | None = None
    rejected_at: datetime | None = None


class DiscoveryCandidateDecisionRequest(BaseModel):
    reviewer_note: str | None = None
