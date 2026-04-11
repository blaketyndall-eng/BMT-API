from __future__ import annotations

import uuid

from sqlalchemy import select
from sqlalchemy.orm import Session

from packages.contracts.source_promotion import (
    PromoteSourceProposalRequest,
    PromoteSourceProposalResponse,
    RejectSourceProposalRequest,
    RejectSourceProposalResponse,
)
from packages.core.models import CrawlJob, Product, Source, Vendor
from packages.observability.tracing import log_event, traced_span

_ACTIVE_JOB_STATUSES = {"queued", "leased", "retryable"}


class SourcePromotionService:
    def __init__(self, db: Session) -> None:
        self.db = db

    def promote(self, request: PromoteSourceProposalRequest) -> PromoteSourceProposalResponse:
        product_id = uuid.UUID(request.product_id)
        with traced_span("source_promotion.promote", product_id=request.product_id):
            product, vendor = self._get_product_vendor(product_id)

            existing_source = self.db.execute(
                select(Source).where(
                    Source.product_id == product_id,
                    Source.root_url == request.proposal.root_url,
                )
            ).scalar_one_or_none()

            created_source = False
            deduped_existing_source = existing_source is not None
            if existing_source is None:
                source = Source(
                    vendor_id=vendor.vendor_id,
                    product_id=product.product_id,
                    source_family=request.proposal.source_family,
                    source_type=request.proposal.source_type,
                    root_url=request.proposal.root_url,
                    connector_type=request.proposal.connector_type,
                    is_active=True,
                    source_metadata={
                        "promotion_reason": request.proposal.reason,
                        "target_gap_codes": request.proposal.target_gap_codes,
                        "proposal_confidence": request.proposal.confidence,
                        "promotion_note": request.note,
                        "trigger": "agent_source_promotion",
                    },
                )
                self.db.add(source)
                self.db.flush()
                existing_source = source
                created_source = True

            crawl_job_id: str | None = None
            created_crawl_job = False
            if request.create_crawl_job:
                existing_job = self.db.execute(
                    select(CrawlJob).where(
                        CrawlJob.source_id == existing_source.source_id,
                        CrawlJob.job_type == "fetch_source",
                        CrawlJob.status.in_(_ACTIVE_JOB_STATUSES),
                    )
                ).scalar_one_or_none()
                if existing_job is None:
                    worker_queue = "browser_fetch" if existing_source.connector_type == "browser" else "api_fetch"
                    job = CrawlJob(
                        vendor_id=existing_source.vendor_id,
                        product_id=existing_source.product_id,
                        source_id=existing_source.source_id,
                        job_type="fetch_source",
                        worker_queue=worker_queue,
                        status="queued",
                        priority=request.crawl_priority,
                        max_attempts=3,
                        payload={
                            "source_id": str(existing_source.source_id),
                            "product_id": str(existing_source.product_id) if existing_source.product_id else None,
                            "vendor_id": str(existing_source.vendor_id) if existing_source.vendor_id else None,
                            "root_url": existing_source.root_url,
                            "source_type": existing_source.source_type,
                            "trigger": "source_promotion",
                            "promotion_note": request.note,
                        },
                    )
                    self.db.add(job)
                    self.db.flush()
                    crawl_job_id = str(job.crawl_job_id)
                    created_crawl_job = True
                else:
                    crawl_job_id = str(existing_job.crawl_job_id)

            self.db.commit()
            log_event(
                "source_promotion.promoted",
                product_id=request.product_id,
                source_id=str(existing_source.source_id),
                created_source=created_source,
                created_crawl_job=created_crawl_job,
                deduped_existing_source=deduped_existing_source,
            )
            return PromoteSourceProposalResponse(
                product_id=request.product_id,
                source_id=str(existing_source.source_id),
                crawl_job_id=crawl_job_id,
                created_source=created_source,
                created_crawl_job=created_crawl_job,
                deduped_existing_source=deduped_existing_source,
            )

    def reject(self, request: RejectSourceProposalRequest) -> RejectSourceProposalResponse:
        with traced_span("source_promotion.reject", product_id=request.product_id):
            log_event(
                "source_promotion.rejected",
                product_id=request.product_id,
                proposal_root_url=request.proposal.root_url,
                reason=request.reason,
            )
            return RejectSourceProposalResponse(
                product_id=request.product_id,
                rejected=True,
                reason=request.reason,
                proposal_root_url=request.proposal.root_url,
            )

    def _get_product_vendor(self, product_id: uuid.UUID) -> tuple[Product, Vendor]:
        row = self.db.execute(
            select(Product, Vendor)
            .join(Vendor, Product.vendor_id == Vendor.vendor_id)
            .where(Product.product_id == product_id)
        ).one_or_none()
        if row is None:
            raise ValueError(f"Product not found: {product_id}")
        return row
