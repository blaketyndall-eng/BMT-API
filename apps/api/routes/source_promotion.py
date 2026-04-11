from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from packages.contracts.api_common import ApiEnvelope
from packages.contracts.source_promotion import (
    PromoteSourceProposalRequest,
    PromoteSourceProposalResponse,
    RejectSourceProposalRequest,
    RejectSourceProposalResponse,
)
from packages.core.deps import get_db
from packages.services.source_promotion import SourcePromotionService

router = APIRouter(prefix="/v1/admin/source-proposals", tags=["admin"])


@router.post("/promote", response_model=ApiEnvelope)
def promote_source_proposal(payload: PromoteSourceProposalRequest, db: Session = Depends(get_db)) -> ApiEnvelope:
    result: PromoteSourceProposalResponse = SourcePromotionService(db).promote(payload)
    return ApiEnvelope(data=result.model_dump())


@router.post("/reject", response_model=ApiEnvelope)
def reject_source_proposal(payload: RejectSourceProposalRequest, db: Session = Depends(get_db)) -> ApiEnvelope:
    result: RejectSourceProposalResponse = SourcePromotionService(db).reject(payload)
    return ApiEnvelope(data=result.model_dump())
