from datetime import datetime, timedelta, timezone

from packages.core.models import CrawlJob
from packages.workers.job_leasing import mark_job_failed, mark_job_succeeded


def test_mark_job_failed_sets_retryable_until_max_attempts() -> None:
    job = CrawlJob(
        job_type="fetch_source",
        worker_queue="browser_fetch",
        status="leased",
        priority=80,
        attempt_count=1,
        max_attempts=3,
        payload={},
    )

    mark_job_failed(job, "temporary failure", retryable=True, backoff_seconds=30)

    assert job.status == "retryable"
    assert job.next_attempt_at is not None
    assert job.completed_at is None
    assert job.last_error == "temporary failure"


def test_mark_job_failed_sets_failed_after_max_attempts() -> None:
    job = CrawlJob(
        job_type="fetch_source",
        worker_queue="browser_fetch",
        status="leased",
        priority=80,
        attempt_count=3,
        max_attempts=3,
        payload={},
    )

    mark_job_failed(job, "permanent failure", retryable=True, backoff_seconds=30)

    assert job.status == "failed"
    assert job.next_attempt_at is None
    assert job.completed_at is not None
    assert job.last_error == "permanent failure"


def test_mark_job_succeeded_clears_retry_state() -> None:
    job = CrawlJob(
        job_type="fetch_source",
        worker_queue="browser_fetch",
        status="leased",
        priority=80,
        attempt_count=1,
        max_attempts=3,
        payload={},
        next_attempt_at=datetime.now(timezone.utc) + timedelta(seconds=30),
        last_error="temporary failure",
    )

    mark_job_succeeded(job)

    assert job.status == "succeeded"
    assert job.next_attempt_at is None
    assert job.completed_at is not None
    assert job.last_error is None
