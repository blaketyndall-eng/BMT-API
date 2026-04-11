from datetime import datetime

from pydantic import BaseModel


class CrawlJobSummary(BaseModel):
    crawl_job_id: str
    vendor_id: str | None
    product_id: str | None
    source_id: str | None
    source_root_url: str | None
    source_type: str | None
    job_type: str
    worker_queue: str
    status: str
    priority: int
    attempt_count: int
    max_attempts: int
    lease_owner: str | None
    lease_expires_at: datetime | None
    next_attempt_at: datetime | None
    completed_at: datetime | None
    last_error: str | None
    created_at: datetime
    updated_at: datetime


class CrawlJobListResponse(BaseModel):
    items: list[CrawlJobSummary]


class PageSummary(BaseModel):
    page_id: str
    source_id: str
    source_root_url: str | None
    source_type: str | None
    canonical_url: str
    page_type: str | None
    title: str | None
    http_status: int | None
    content_type: str | None
    classifier_version: str | None
    classifier_confidence: float | None
    fetched_at: datetime
    created_at: datetime
    updated_at: datetime


class PageListResponse(BaseModel):
    items: list[PageSummary]


class EvidenceSummary(BaseModel):
    evidence_id: str
    vendor_id: str | None
    product_id: str | None
    source_id: str | None
    page_id: str | None
    canonical_url: str | None
    page_type: str | None
    evidence_type: str
    label: str
    snippet: str
    confidence: float
    extractor_name: str
    extractor_version: str
    created_at: datetime
    updated_at: datetime


class EvidenceListResponse(BaseModel):
    items: list[EvidenceSummary]


class SourceSummary(BaseModel):
    source_id: str
    vendor_id: str | None
    product_id: str | None
    source_family: str
    source_type: str
    root_url: str
    connector_type: str
    is_active: bool
    created_at: datetime
    updated_at: datetime


class VendorSourcesResponse(BaseModel):
    vendor_id: str
    items: list[SourceSummary]


class AgentRunSummary(BaseModel):
    agent_run_id: str
    agent_name: str
    strategy_version: str | None
    mode: str | None
    status: str
    trace_id: str | None
    request_id: str | None
    product_id: str | None
    vendor_id: str | None
    created_at: datetime
    updated_at: datetime


class AgentRunListResponse(BaseModel):
    items: list[AgentRunSummary]


class AgentEvalRunSummary(BaseModel):
    agent_eval_run_id: str
    agent_name: str
    evaluator_version: str
    status: str
    trace_id: str | None
    score: float | None
    overall_passed: bool | None
    created_at: datetime
    updated_at: datetime


class AgentEvalRunListResponse(BaseModel):
    items: list[AgentEvalRunSummary]


class SourceProposalDecisionSummary(BaseModel):
    source_proposal_decision_id: str
    decision_type: str
    agent_name: str | None
    trace_id: str | None
    product_id: str | None
    vendor_id: str | None
    source_id: str | None
    crawl_job_id: str | None
    proposal_root_url: str | None
    note: str | None
    created_at: datetime
    updated_at: datetime


class SourceProposalDecisionListResponse(BaseModel):
    items: list[SourceProposalDecisionSummary]
