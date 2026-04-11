from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from packages.contracts.admin import (
    AgentEvalRunListResponse,
    AgentRunListResponse,
    SourceProposalDecisionListResponse,
)
from packages.contracts.api_common import ApiEnvelope
from packages.core.deps import get_db
from packages.services.admin_queries import AdminQueryService
from packages.services.registry_manager import DISCOVERY_AGENT_NAME

router = APIRouter(prefix="/v1/admin", tags=["admin"])


@router.get("/agent-runs", response_model=ApiEnvelope)
def list_agent_runs(
    agent_name: str | None = Query(default=None),
    product_id: str | None = Query(default=None),
    status: str | None = Query(default=None),
    trace_id: str | None = Query(default=None),
    limit: int = Query(default=50, ge=1, le=200),
    db: Session = Depends(get_db),
) -> ApiEnvelope:
    result: AgentRunListResponse = AdminQueryService(db).list_agent_runs(
        agent_name=agent_name,
        product_id=product_id,
        status=status,
        trace_id=trace_id,
        limit=limit,
    )
    return ApiEnvelope(data=result.model_dump())


@router.get("/discovery-runs", response_model=ApiEnvelope)
def list_discovery_runs(
    product_id: str | None = Query(default=None),
    status: str | None = Query(default=None),
    trace_id: str | None = Query(default=None),
    limit: int = Query(default=50, ge=1, le=200),
    db: Session = Depends(get_db),
) -> ApiEnvelope:
    result: AgentRunListResponse = AdminQueryService(db).list_agent_runs(
        agent_name=DISCOVERY_AGENT_NAME,
        product_id=product_id,
        status=status,
        trace_id=trace_id,
        limit=limit,
    )
    return ApiEnvelope(data=result.model_dump())


@router.get("/agent-evals", response_model=ApiEnvelope)
def list_agent_eval_runs(
    agent_name: str | None = Query(default=None),
    status: str | None = Query(default=None),
    trace_id: str | None = Query(default=None),
    limit: int = Query(default=50, ge=1, le=200),
    db: Session = Depends(get_db),
) -> ApiEnvelope:
    result: AgentEvalRunListResponse = AdminQueryService(db).list_agent_eval_runs(
        agent_name=agent_name,
        status=status,
        trace_id=trace_id,
        limit=limit,
    )
    return ApiEnvelope(data=result.model_dump())


@router.get("/source-proposal-decisions", response_model=ApiEnvelope)
def list_source_proposal_decisions(
    decision_type: str | None = Query(default=None),
    product_id: str | None = Query(default=None),
    trace_id: str | None = Query(default=None),
    limit: int = Query(default=50, ge=1, le=200),
    db: Session = Depends(get_db),
) -> ApiEnvelope:
    result: SourceProposalDecisionListResponse = AdminQueryService(db).list_source_proposal_decisions(
        decision_type=decision_type,
        product_id=product_id,
        trace_id=trace_id,
        limit=limit,
    )
    return ApiEnvelope(data=result.model_dump())
