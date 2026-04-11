from __future__ import annotations

import uuid

from sqlalchemy.orm import Session

from packages.core.models import AgentEvalRun, AgentRun, SourceProposalDecision
from packages.observability.tracing import get_trace_context


class AgentRunStore:
    def __init__(self, db: Session) -> None:
        self.db = db

    def create_agent_run(
        self,
        *,
        agent_name: str,
        strategy_version: str | None,
        mode: str | None,
        product_id: str | None,
        vendor_id: str | None,
        request_payload: dict,
        response_payload: dict,
        status: str = "completed",
        error_message: str | None = None,
    ) -> AgentRun:
        trace_context = get_trace_context()
        record = AgentRun(
            agent_name=agent_name,
            strategy_version=strategy_version,
            mode=mode,
            status=status,
            trace_id=trace_context.get("trace_id"),
            request_id=trace_context.get("request_id"),
            product_id=uuid.UUID(product_id) if product_id else None,
            vendor_id=uuid.UUID(vendor_id) if vendor_id else None,
            request_payload=request_payload,
            response_payload=response_payload,
            error_message=error_message,
        )
        self.db.add(record)
        self.db.flush()
        return record

    def create_agent_eval_run(
        self,
        *,
        agent_name: str,
        evaluator_version: str,
        request_payload: dict,
        response_payload: dict,
        score: float | None,
        overall_passed: bool | None,
        status: str = "completed",
        error_message: str | None = None,
    ) -> AgentEvalRun:
        trace_context = get_trace_context()
        record = AgentEvalRun(
            agent_name=agent_name,
            evaluator_version=evaluator_version,
            status=status,
            trace_id=trace_context.get("trace_id"),
            request_payload=request_payload,
            response_payload=response_payload,
            score=score,
            overall_passed=overall_passed,
            error_message=error_message,
        )
        self.db.add(record)
        self.db.flush()
        return record

    def create_source_proposal_decision(
        self,
        *,
        decision_type: str,
        agent_name: str | None,
        product_id: str | None,
        vendor_id: str | None,
        source_id: str | None,
        crawl_job_id: str | None,
        proposal_payload: dict,
        decision_payload: dict,
        note: str | None = None,
    ) -> SourceProposalDecision:
        trace_context = get_trace_context()
        record = SourceProposalDecision(
            decision_type=decision_type,
            agent_name=agent_name,
            trace_id=trace_context.get("trace_id"),
            product_id=uuid.UUID(product_id) if product_id else None,
            vendor_id=uuid.UUID(vendor_id) if vendor_id else None,
            source_id=uuid.UUID(source_id) if source_id else None,
            crawl_job_id=uuid.UUID(crawl_job_id) if crawl_job_id else None,
            proposal_payload=proposal_payload,
            decision_payload=decision_payload,
            note=note,
        )
        self.db.add(record)
        self.db.flush()
        return record
