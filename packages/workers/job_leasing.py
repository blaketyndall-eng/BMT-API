from __future__ import annotations

from datetime import datetime, timedelta, timezone

from sqlalchemy import and_, or_, select
from sqlalchemy.orm import Session

from packages.core.models import CrawlJob


DEFAULT_RETRY_BACKOFF_SECONDS = 60


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
                or_(
                    and_(CrawlJob.status == "queued"),
                    and_(
                        CrawlJob.status == "retryable",
                        or_(
                            CrawlJob.next_attempt_at.is_(None),
                            CrawlJob.next_attempt_at <= now,
                        ),
                    ),
                    and_(
                        CrawlJob.status == "leased",
                        CrawlJob.lease_expires_at.is_not(None),
                        CrawlJob.lease_expires_at <= now,
                    ),
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
    job.next_attempt_at = None
    job.completed_at = None
    job.attempt_count += 1
    db.flush()
    return job


def mark_job_succeeded(job: CrawlJob) -> None:
    job.status = "succeeded"
    job.lease_owner = None
    job.lease_expires_at = None
    job.next_attempt_at = None
    job.completed_at = datetime.now(timezone.utc)
    job.last_error = None


def mark_job_failed(
    job: CrawlJob,
    message: str,
    *,
    retryable: bool = True,
    backoff_seconds: int = DEFAULT_RETRY_BACKOFF_SECONDS,
) -> None:
    now = datetime.now(timezone.utc)
    job.lease_owner = None
    job.lease_expires_at = None
    job.last_error = message[:5000]

    should_retry = retryable and job.attempt_count < job.max_attempts
    if should_retry:
        job.status = "retryable"
        job.next_attempt_at = now + timedelta(seconds=backoff_seconds)
        job.completed_at = None
    else:
        job.status = "failed"
        job.next_attempt_at = None
        job.completed_at = now
