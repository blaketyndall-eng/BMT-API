from __future__ import annotations

import uuid

from sqlalchemy import Select, select
from sqlalchemy.orm import Session

from packages.contracts.admin import (
    CrawlJobListResponse,
    CrawlJobSummary,
    PageListResponse,
    PageSummary,
    SourceSummary,
    VendorSourcesResponse,
)
from packages.core.models import CrawlJob, Page, Source


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
                fetched_at=page.fetched_at,
                created_at=page.created_at,
                updated_at=page.updated_at,
            )
            for page, source in rows
        ]
        return PageListResponse(items=items)

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
