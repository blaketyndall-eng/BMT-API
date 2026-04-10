from __future__ import annotations

from sqlalchemy import select

from packages.connectors.browser_fetcher import fetch_page
from packages.core.db import SessionLocal
from packages.core.models import Page, Source
from packages.extraction.page_classifier import CLASSIFIER_VERSION, classify_page
from packages.workers.job_leasing import lease_next_job, mark_job_failed, mark_job_succeeded


async def process_one_browser_fetch_job(*, worker_id: str) -> bool:
    db = SessionLocal()
    try:
        job = lease_next_job(db, worker_queue="browser_fetch", worker_id=worker_id)
        if job is None:
            db.commit()
            return False

        source = db.get(Source, job.source_id)
        if source is None:
            mark_job_failed(job, f"Source not found for job {job.crawl_job_id}", retryable=False)
            db.commit()
            return True

        try:
            result = await fetch_page(source.root_url)
            classification = classify_page(
                requested_url=result.requested_url,
                final_url=result.final_url,
                title=result.title,
                page_text=result.page_text,
                source_type=source.source_type,
            )

            page = db.execute(
                select(Page).where(Page.canonical_url == result.final_url)
            ).scalar_one_or_none()
            if page is None:
                page = Page(
                    source_id=source.source_id,
                    canonical_url=result.final_url,
                )
                db.add(page)

            page.page_type = classification.page_type
            page.title = result.title
            page.http_status = result.status_code
            page.content_type = result.content_type
            page.content_sha256 = result.content_sha256
            page.page_text = result.page_text
            page.fetched_at = result.fetched_at
            page.parser_metadata = {
                "requested_url": result.requested_url,
                "final_url": result.final_url,
                "source_type": source.source_type,
                "content_type": result.content_type,
                "classifier_version": CLASSIFIER_VERSION,
                "classifier_confidence": classification.confidence,
                "classifier_reasons": classification.reasons,
            }

            mark_job_succeeded(job)
            db.commit()
            return True
        except Exception as exc:
            mark_job_failed(job, str(exc), retryable=True)
            db.commit()
            return True
    finally:
        db.close()
