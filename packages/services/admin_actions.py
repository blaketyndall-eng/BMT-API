from __future__ import annotations

import uuid

from sqlalchemy import select
from sqlalchemy.orm import Session

from packages.contracts.admin_actions import (
    CrawlJobReplayRequest,
    CrawlJobReplayResponse,
    SourceRecrawlRequest,
    SourceRecrawlResponse,
)
from packages.core.models import CrawlJob, Source

_ACTIVE_JOB_STATUSES = {"queued", "leased", "retryable"}


class AdminActionService:
    def __init__(self, db: Session) -> None:
        self.db = db

    def recrawl_source(self, source_id: uuid.UUID, request: SourceRecrawlRequest) -> SourceRecrawlResponse:
        source = self.db.get(Source, source_id)
        if source is None:
            raise ValueError(f"Source not found: {source_id}")

        existing_job = self.db.execute(
            select(CrawlJob).where(
                CrawlJob.source_id == source_id,
                CrawlJob.job_type == "fetch_source",
                CrawlJob.status.in_(_ACTIVE_JOB_STATUSES),
            )
        ).scalar_one_or_none()
        if existing_job is not None and not request.force:
            return SourceRecrawlResponse(
                source_id=str(source_id),
                crawl_job_id=str(existing_job.crawl_job_id),
                status="deduped",
                deduped=True,
            )

        worker_queue = "browser_fetch" if source.connector_type == "browser" else "api_fetch"
        job = CrawlJob(
            vendor_id=source.vendor_id,
            product_id=source.product_id,
            source_id=source.source_id,
            job_type="fetch_source",
            worker_queue=worker_queue,
            status="queued",
            priority=request.priority,
            max_attempts=3,
            payload={
                "source_id": str(source.source_id),
                "product_id": str(source.product_id) if source.product_id else None,
                "vendor_id": str(source.vendor_id) if source.vendor_id else None,
                "root_url": source.root_url,
                "source_type": source.source_type,
                "reason": request.reason,
                "trigger": "admin_recrawl",
                "force": request.force,
            },
        )
        self.db.add(job)
        self.db.commit()
        self.db.refresh(job)
        return SourceRecrawlResponse(
            source_id=str(source_id),
            crawl_job_id=str(job.crawl_job_id),
            status="queued",
            deduped=False,
        )

    def replay_crawl_job(self, crawl_job_id: uuid.UUID, request: CrawlJobReplayRequest) -> CrawlJobReplayResponse:
        original_job = self.db.get(CrawlJob, crawl_job_id)
        if original_job is None:
            raise ValueError(f"Crawl job not found: {crawl_job_id}")

        existing_job = self.db.execute(
            select(CrawlJob).where(
                CrawlJob.source_id == original_job.source_id,
                CrawlJob.job_type == original_job.job_type,
                CrawlJob.status.in_(_ACTIVE_JOB_STATUSES),
            )
        ).scalar_one_or_none()
        if existing_job is not None:
            return CrawlJobReplayResponse(
                original_crawl_job_id=str(crawl_job_id),
                replay_crawl_job_id=str(existing_job.crawl_job_id),
                status="deduped",
                deduped=True,
            )

        replay_job = CrawlJob(
            vendor_id=original_job.vendor_id,
            product_id=original_job.product_id,
            source_id=original_job.source_id,
            job_type=original_job.job_type,
            worker_queue=original_job.worker_queue,
            status="queued",
            priority=request.priority,
            max_attempts=original_job.max_attempts,
            payload={
                **original_job.payload,
                "reason": request.reason,
                "trigger": "admin_replay",
                "replayed_from": str(original_job.crawl_job_id),
            },
        )
        self.db.add(replay_job)
        self.db.commit()
        self.db.refresh(replay_job)
        return CrawlJobReplayResponse(
            original_crawl_job_id=str(crawl_job_id),
            replay_crawl_job_id=str(replay_job.crawl_job_id),
            status="queued",
            deduped=False,
        )
