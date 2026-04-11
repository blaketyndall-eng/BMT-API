from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from packages.contracts.agent_evals import AgentEvalRequest, AgentEvalResponse
from packages.contracts.api_common import ApiEnvelope
from packages.core.deps import get_db
from packages.services.agent_evaluator import AgentEvaluatorService

router = APIRouter(prefix="/v1/admin", tags=["admin"])


@router.post("/agent-evals/run", response_model=ApiEnvelope)
def run_agent_eval(payload: AgentEvalRequest, db: Session = Depends(get_db)) -> ApiEnvelope:
    result: AgentEvalResponse = AgentEvaluatorService().evaluate(payload)
    return ApiEnvelope(data=result.model_dump())
