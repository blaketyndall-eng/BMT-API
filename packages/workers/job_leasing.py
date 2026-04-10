from __future__ import annotations

from datetime import datetime, timedelta, timezone

from sqlalchemy import or_, select
from sqlalchemy.orm import Session

from packages.core.models import CrawlJob


def lease_next_job(
    db: Session,
    *,
    worker_queue: str,
    worker_id: str,
    lease_seconds: int = 300,
) -> CrawlJob | None:
    now = datetime.now(timezone.utc)
    job = (
        db.execute(
            select(CrawlJob)
            .where(
                CrawlJob.worker_queue == worker_queue,
                CrawlJob.status == "queued",
                or_(
                    CrawlJob.lease_expires_at.is_(None),
                    CrawlJob.lease_expires_at <= now,
                ),
            )
            .order_by(CrawlJob.priority.desc(), CrawlJob.created_at.asc())
            .limit(1)
            .with_for_update(skip_locked=True)
        )
        .scalars()
        .first()
    )

    if job is None:
        return None

    job.status = "leased"
    job.lease_owner = worker_id
    job.lease_expires_at = now + timedelta(seconds=lease_seconds)
    job.attempt_count += 1
    db.flush()
    return job


def mark_job_succeeded(job: CrawlJob) -> None:
    job.status = "succeeded"
    job.lease_owner = None
    job.lease_expires_at = None
    job.last_error = None


def mark_job_failed(job: CrawlJob, message: str) -> None:
    job.status = "failed"
    job.lease_owner = None
    job.lease_expires_at = None
    job.last_error = message[:5000]
