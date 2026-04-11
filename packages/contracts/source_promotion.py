from pydantic import BaseModel, Field

from packages.contracts.agents import SourceProposal


class PromoteSourceProposalRequest(BaseModel):
    product_id: str
    proposal: SourceProposal
    create_crawl_job: bool = True
    crawl_priority: int = Field(default=90, ge=0, le=100)
    note: str | None = None


class PromoteSourceProposalResponse(BaseModel):
    product_id: str
    source_id: str
    crawl_job_id: str | None = None
    created_source: bool
    created_crawl_job: bool
    deduped_existing_source: bool


class RejectSourceProposalRequest(BaseModel):
    product_id: str
    proposal: SourceProposal
    reason: str


class RejectSourceProposalResponse(BaseModel):
    product_id: str
    rejected: bool
    reason: str
    proposal_root_url: str
