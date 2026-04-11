from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from packages.contracts.agents import (
    EvidenceCriticRequest,
    EvidenceCriticResponse,
    SourcePlannerRequest,
    SourcePlannerResponse,
)
from packages.contracts.api_common import ApiEnvelope
from packages.core.deps import get_db
from packages.services.evidence_critic_agent import EvidenceCriticAgentService
from packages.services.source_planner_agent import SourcePlannerAgentService

router = APIRouter(prefix="/v1/agents", tags=["agents"])


@router.post("/source-planner/plan", response_model=ApiEnvelope)
def plan_sources(payload: SourcePlannerRequest, db: Session = Depends(get_db)) -> ApiEnvelope:
    result: SourcePlannerResponse = SourcePlannerAgentService(db).plan(payload)
    return ApiEnvelope(data=result.model_dump())


@router.post("/evidence-critic/critique", response_model=ApiEnvelope)
def critique_evidence(payload: EvidenceCriticRequest, db: Session = Depends(get_db)) -> ApiEnvelope:
    result: EvidenceCriticResponse = EvidenceCriticAgentService(db).critique(payload)
    return ApiEnvelope(data=result.model_dump())
