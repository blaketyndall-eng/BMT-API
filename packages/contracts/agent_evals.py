from pydantic import BaseModel, Field


class AgentEvalRequest(BaseModel):
    agent_name: str
    payload: dict = Field(default_factory=dict)


class AgentEvalCheck(BaseModel):
    check_name: str
    passed: bool
    severity: str
    message: str


class AgentEvalScorecard(BaseModel):
    overall_passed: bool
    passed_checks: int
    failed_checks: int
    score: float = Field(ge=0.0, le=1.0)


class AgentEvalResponse(BaseModel):
    agent_name: str
    evaluator_version: str
    scorecard: AgentEvalScorecard
    checks: list[AgentEvalCheck] = Field(default_factory=list)
