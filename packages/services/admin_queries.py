from __future__ import annotations

import uuid

from sqlalchemy import Select, select
from sqlalchemy.orm import Session

from packages.contracts.admin import (
    AgentEvalRunListResponse,
    AgentEvalRunSummary,
    AgentRunListResponse,
    AgentRunSummary,
    CrawlJobListResponse,
    CrawlJobSummary,
    EvidenceListResponse,
    EvidenceSummary,
    PageListResponse,
    PageSummary,
    SourceProposalDecisionListResponse,
    SourceProposalDecisionSummary,
    SourceSummary,
    VendorSourcesResponse,
)
from packages.core.models import AgentEvalRun, AgentRun, CrawlJob, Evidence, Page, Source, SourceProposalDecision


class AdminQueryService:
    def __init__(self, db: Session) -> None:
        self.db = db

    def list_crawl_jobs(self, *, status: str | None, limit: int) -> CrawlJobListResponse:
        stmt: Select = (
            select(CrawlJob, Source)
            .outerjoin(Source, CrawlJob.source_id == Source.source_id)
            .order_by(CrawlJob.created_at.desc())
            .limit(limit)
        )
        if status:
            stmt = stmt.where(CrawlJob.status == status)

        rows = self.db.execute(stmt).all()
        items = [
            CrawlJobSummary(
                crawl_job_id=str(job.crawl_job_id),
                vendor_id=str(job.vendor_id) if job.vendor_id else None,
                product_id=str(job.product_id) if job.product_id else None,
                source_id=str(job.source_id) if job.source_id else None,
                source_root_url=source.root_url if source else None,
                source_type=source.source_type if source else None,
                job_type=job.job_type,
                worker_queue=job.worker_queue,
                status=job.status,
                priority=job.priority,
                attempt_count=job.attempt_count,
                max_attempts=job.max_attempts,
                lease_owner=job.lease_owner,
                lease_expires_at=job.lease_expires_at,
                next_attempt_at=job.next_attempt_at,
                completed_at=job.completed_at,
                last_error=job.last_error,
                created_at=job.created_at,
                updated_at=job.updated_at,
            )
            for job, source in rows
        ]
        return CrawlJobListResponse(items=items)

    def list_pages(self, *, source_id: str | None, limit: int) -> PageListResponse:
        stmt: Select = (
            select(Page, Source)
            .join(Source, Page.source_id == Source.source_id)
            .order_by(Page.fetched_at.desc(), Page.created_at.desc())
            .limit(limit)
        )
        if source_id:
            stmt = stmt.where(Page.source_id == uuid.UUID(source_id))

        rows = self.db.execute(stmt).all()
        items = [
            PageSummary(
                page_id=str(page.page_id),
                source_id=str(page.source_id),
                source_root_url=source.root_url,
                source_type=source.source_type,
                canonical_url=page.canonical_url,
                page_type=page.page_type,
                title=page.title,
                http_status=page.http_status,
                content_type=page.content_type,
                classifier_version=page.parser_metadata.get("classifier_version"),
                classifier_confidence=page.parser_metadata.get("classifier_confidence"),
                fetched_at=page.fetched_at,
                created_at=page.created_at,
                updated_at=page.updated_at,
            )
            for page, source in rows
        ]
        return PageListResponse(items=items)

    def list_evidence(
        self,
        *,
        evidence_type: str | None,
        product_id: str | None,
        vendor_id: str | None,
        limit: int,
    ) -> EvidenceListResponse:
        stmt: Select = (
            select(Evidence, Page)
            .outerjoin(Page, Evidence.page_id == Page.page_id)
            .order_by(Evidence.created_at.desc())
            .limit(limit)
        )
        if evidence_type:
            stmt = stmt.where(Evidence.evidence_type == evidence_type)
        if product_id:
            stmt = stmt.where(Evidence.product_id == uuid.UUID(product_id))
        if vendor_id:
            stmt = stmt.where(Evidence.vendor_id == uuid.UUID(vendor_id))

        rows = self.db.execute(stmt).all()
        items = [
            EvidenceSummary(
                evidence_id=str(evidence.evidence_id),
                vendor_id=str(evidence.vendor_id) if evidence.vendor_id else None,
                product_id=str(evidence.product_id) if evidence.product_id else None,
                source_id=str(evidence.source_id) if evidence.source_id else None,
                page_id=str(evidence.page_id) if evidence.page_id else None,
                canonical_url=page.canonical_url if page else None,
                page_type=page.page_type if page else None,
                evidence_type=evidence.evidence_type,
                label=evidence.label,
                snippet=evidence.snippet,
                confidence=evidence.confidence,
                extractor_name=evidence.extractor_name,
                extractor_version=evidence.extractor_version,
                created_at=evidence.created_at,
                updated_at=evidence.updated_at,
            )
            for evidence, page in rows
        ]
        return EvidenceListResponse(items=items)

    def list_vendor_sources(self, vendor_id: uuid.UUID) -> VendorSourcesResponse:
        rows = self.db.execute(
            select(Source)
            .where(Source.vendor_id == vendor_id)
            .order_by(Source.created_at.desc())
        ).scalars()

        items = [
            SourceSummary(
                source_id=str(source.source_id),
                vendor_id=str(source.vendor_id) if source.vendor_id else None,
                product_id=str(source.product_id) if source.product_id else None,
                source_family=source.source_family,
                source_type=source.source_type,
                root_url=source.root_url,
                connector_type=source.connector_type,
                is_active=source.is_active,
                created_at=source.created_at,
                updated_at=source.updated_at,
            )
            for source in rows
        ]
        return VendorSourcesResponse(vendor_id=str(vendor_id), items=items)

    def list_agent_runs(self, *, agent_name: str | None, product_id: str | None, status: str | None, trace_id: str | None, limit: int) -> AgentRunListResponse:
        stmt: Select = select(AgentRun).order_by(AgentRun.created_at.desc()).limit(limit)
        if agent_name:
            stmt = stmt.where(AgentRun.agent_name == agent_name)
        if product_id:
            stmt = stmt.where(AgentRun.product_id == uuid.UUID(product_id))
        if status:
            stmt = stmt.where(AgentRun.status == status)
        if trace_id:
            stmt = stmt.where(AgentRun.trace_id == trace_id)

        rows = self.db.execute(stmt).scalars()
        items = [
            AgentRunSummary(
                agent_run_id=str(run.agent_run_id),
                agent_name=run.agent_name,
                strategy_version=run.strategy_version,
                mode=run.mode,
                status=run.status,
                trace_id=run.trace_id,
                request_id=run.request_id,
                product_id=str(run.product_id) if run.product_id else None,
                vendor_id=str(run.vendor_id) if run.vendor_id else None,
                created_at=run.created_at,
                updated_at=run.updated_at,
            )
            for run in rows
        ]
        return AgentRunListResponse(items=items)

    def list_agent_eval_runs(self, *, agent_name: str | None, status: str | None, trace_id: str | None, limit: int) -> AgentEvalRunListResponse:
        stmt: Select = select(AgentEvalRun).order_by(AgentEvalRun.created_at.desc()).limit(limit)
        if agent_name:
            stmt = stmt.where(AgentEvalRun.agent_name == agent_name)
        if status:
            stmt = stmt.where(AgentEvalRun.status == status)
        if trace_id:
            stmt = stmt.where(AgentEvalRun.trace_id == trace_id)

        rows = self.db.execute(stmt).scalars()
        items = [
            AgentEvalRunSummary(
                agent_eval_run_id=str(run.agent_eval_run_id),
                agent_name=run.agent_name,
                evaluator_version=run.evaluator_version,
                status=run.status,
                trace_id=run.trace_id,
                score=run.score,
                overall_passed=run.overall_passed,
                created_at=run.created_at,
                updated_at=run.updated_at,
            )
            for run in rows
        ]
        return AgentEvalRunListResponse(items=items)

    def list_source_proposal_decisions(self, *, decision_type: str | None, product_id: str | None, trace_id: str | None, limit: int) -> SourceProposalDecisionListResponse:
        stmt: Select = select(SourceProposalDecision).order_by(SourceProposalDecision.created_at.desc()).limit(limit)
        if decision_type:
            stmt = stmt.where(SourceProposalDecision.decision_type == decision_type)
        if product_id:
            stmt = stmt.where(SourceProposalDecision.product_id == uuid.UUID(product_id))
        if trace_id:
            stmt = stmt.where(SourceProposalDecision.trace_id == trace_id)

        rows = self.db.execute(stmt).scalars()
        items = [
            SourceProposalDecisionSummary(
                source_proposal_decision_id=str(decision.source_proposal_decision_id),
                decision_type=decision.decision_type,
                agent_name=decision.agent_name,
                trace_id=decision.trace_id,
                product_id=str(decision.product_id) if decision.product_id else None,
                vendor_id=str(decision.vendor_id) if decision.vendor_id else None,
                source_id=str(decision.source_id) if decision.source_id else None,
                crawl_job_id=str(decision.crawl_job_id) if decision.crawl_job_id else None,
                proposal_root_url=decision.proposal_payload.get("root_url"),
                note=decision.note,
                created_at=decision.created_at,
                updated_at=decision.updated_at,
            )
            for decision in rows
        ]
        return SourceProposalDecisionListResponse(items=items)
