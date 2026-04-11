from uuid import uuid4

from packages.contracts.admin_actions import CrawlJobReplayRequest, SourceRecrawlRequest
from packages.services.admin_actions import AdminActionService


class DummySource:
    def __init__(self) -> None:
        self.source_id = uuid4()
        self.vendor_id = uuid4()
        self.product_id = uuid4()
        self.root_url = "https://example.com"
        self.source_type = "homepage"
        self.connector_type = "browser"


class DummyJob:
    def __init__(self) -> None:
        self.crawl_job_id = uuid4()
        self.source_id = uuid4()
        self.vendor_id = uuid4()
        self.product_id = uuid4()
        self.job_type = "fetch_source"
        self.worker_queue = "browser_fetch"
        self.max_attempts = 3
        self.payload = {"root_url": "https://example.com"}


class DummyScalarResult:
    def __init__(self, value) -> None:
        self._value = value

    def scalar_one_or_none(self):
        return self._value


class DummySession:
    def __init__(self, source=None, existing_job=None, original_job=None) -> None:
        self.source = source
        self.existing_job = existing_job
        self.original_job = original_job
        self.added = []

    def get(self, model, object_id):
        model_name = getattr(model, "__name__", "")
        if model_name == "Source":
            return self.source
        if model_name == "CrawlJob":
            return self.original_job
        return None

    def execute(self, stmt):
        return DummyScalarResult(self.existing_job)

    def add(self, obj):
        self.added.append(obj)

    def commit(self):
        return None

    def refresh(self, obj):
        return None


def test_recrawl_source_dedupes_existing_active_job() -> None:
    source = DummySource()
    existing_job = DummyJob()
    session = DummySession(source=source, existing_job=existing_job)

    result = AdminActionService(session).recrawl_source(source.source_id, SourceRecrawlRequest())

    assert result.deduped is True
    assert result.status == "deduped"
    assert result.crawl_job_id == str(existing_job.crawl_job_id)
    assert session.added == []


def test_recrawl_source_creates_new_job_when_forced() -> None:
    source = DummySource()
    existing_job = DummyJob()
    session = DummySession(source=source, existing_job=existing_job)

    result = AdminActionService(session).recrawl_source(
        source.source_id,
        SourceRecrawlRequest(force=True, priority=95, reason="manual"),
    )

    assert result.deduped is False
    assert result.status == "queued"
    assert len(session.added) == 1
    assert session.added[0].priority == 95


def test_replay_crawl_job_dedupes_existing_active_job() -> None:
    original_job = DummyJob()
    existing_job = DummyJob()
    session = DummySession(existing_job=existing_job, original_job=original_job)

    result = AdminActionService(session).replay_crawl_job(original_job.crawl_job_id, CrawlJobReplayRequest())

    assert result.deduped is True
    assert result.status == "deduped"
    assert result.replay_crawl_job_id == str(existing_job.crawl_job_id)


def test_replay_crawl_job_creates_new_job_when_no_active_job_exists() -> None:
    original_job = DummyJob()
    session = DummySession(existing_job=None, original_job=original_job)

    result = AdminActionService(session).replay_crawl_job(
        original_job.crawl_job_id,
        CrawlJobReplayRequest(priority=91, reason="manual_replay"),
    )

    assert result.deduped is False
    assert result.status == "queued"
    assert len(session.added) == 1
    assert session.added[0].priority == 91
