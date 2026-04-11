from pydantic import BaseModel, Field


class SourcePlannerRequest(BaseModel):
    product_id: str
    max_candidates: int = Field(default=5, ge=1, le=20)
    include_existing_sources: bool = False


class SourceProposal(BaseModel):
    root_url: str
    source_type: str
    source_family: str = "vendor_owned"
    connector_type: str = "browser"
    reason: str
    target_gap_codes: list[str] = Field(default_factory=list)
    confidence: float = Field(ge=0.0, le=1.0)


class AgentRunSummary(BaseModel):
    agent_name: str
    strategy_version: str
    mode: str


class SourcePlannerResponse(BaseModel):
    product_id: str
    agent: AgentRunSummary
    considered_gap_codes: list[str] = Field(default_factory=list)
    proposals: list[SourceProposal] = Field(default_factory=list)
