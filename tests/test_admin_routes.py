import uuid
from datetime import datetime, timezone

from fastapi.testclient import TestClient

from apps.api.main import app
from packages.contracts.admin import (
    CrawlJobListResponse,
    CrawlJobSummary,
    SourceSummary,
    VendorSourcesResponse,
)
from packages.contracts.admin_actions import CrawlJobReplayResponse, SourceRecrawlResponse
from packages.core.deps import get_db


class DummyQueryService:
    def __init__(self, _db: object) -> None:
        pass

    def list_crawl_jobs(self, *, status: str | None, limit: int) -> CrawlJobListResponse:
        now = datetime.now(timezone.utc)
        return CrawlJobListResponse(
            items=[
                CrawlJobSummary(
                    crawl_job_id=str(uuid.uuid4()),
                    vendor_id=None,
                    product_id=None,
                    source_id=None,
                    source_root_url="https://example.com",
                    source_type="homepage",
                    job_type="fetch_source",
                    worker_queue="browser_fetch",
                    status=status or "queued",
                    priority=80,
                    attempt_count=1,
                    lease_owner=None,
                    lease_expires_at=None,
                    last_error=None,
                    created_at=now,
                    updated_at=now,
                )
            ]
        )

    def list_vendor_sources(self, vendor_id: uuid.UUID) -> VendorSourcesResponse:
        now = datetime.now(timezone.utc)
        return VendorSourcesResponse(
            vendor_id=str(vendor_id),
            items=[
                SourceSummary(
                    source_id=str(uuid.uuid4()),
                    vendor_id=str(vendor_id),
                    product_id=None,
                    source_family="vendor_owned",
                    source_type="homepage",
                    root_url="https://example.com",
                    connector_type="browser",
                    is_active=True,
                    created_at=now,
                    updated_at=now,
                )
            ],
        )


class DummyActionService:
    def __init__(self, _db: object) -> None:
        pass

    def recrawl_source(self, source_id, request):
        return SourceRecrawlResponse(
            source_id=str(source_id),
            crawl_job_id=str(uuid.uuid4()),
            status="queued",
            deduped=False,
        )

    def replay_crawl_job(self, crawl_job_id, request):
        return CrawlJobReplayResponse(
            original_crawl_job_id=str(crawl_job_id),
            replay_crawl_job_id=str(uuid.uuid4()),
            status="queued",
            deduped=False,
        )


def override_get_db():
    yield object()


def test_admin_crawl_jobs_endpoint_returns_payload(monkeypatch) -> None:
    monkeypatch.setattr("apps.api.routes.admin.AdminQueryService", DummyQueryService)
    app.dependency_overrides[get_db] = override_get_db
    client = TestClient(app)

    response = client.get("/v1/admin/crawl-jobs?status=queued&limit=10")

    assert response.status_code == 200
    payload = response.json()["data"]["items"][0]
    assert payload["status"] == "queued"
    assert payload["worker_queue"] == "browser_fetch"

    app.dependency_overrides.clear()


def test_admin_recrawl_source_endpoint_returns_payload(monkeypatch) -> None:
    monkeypatch.setattr("apps.api.routes.admin.AdminActionService", DummyActionService)
    app.dependency_overrides[get_db] = override_get_db
    client = TestClient(app)
    source_id = uuid.uuid4()

    response = client.post(
        f"/v1/admin/sources/{source_id}/recrawl",
        json={"reason": "manual", "priority": 95, "force": False},
    )

    assert response.status_code == 200
    body = response.json()["data"]
    assert body["source_id"] == str(source_id)
    assert body["status"] == "queued"

    app.dependency_overrides.clear()


def test_admin_replay_crawl_job_endpoint_returns_payload(monkeypatch) -> None:
    monkeypatch.setattr("apps.api.routes.admin.AdminActionService", DummyActionService)
    app.dependency_overrides[get_db] = override_get_db
    client = TestClient(app)
    crawl_job_id = uuid.uuid4()

    response = client.post(
        f"/v1/admin/crawl-jobs/{crawl_job_id}/replay",
        json={"priority": 91, "reason": "manual_replay"},
    )

    assert response.status_code == 200
    body = response.json()["data"]
    assert body["original_crawl_job_id"] == str(crawl_job_id)
    assert body["status"] == "queued"

    app.dependency_overrides.clear()


def test_vendor_sources_endpoint_returns_payload(monkeypatch) -> None:
    monkeypatch.setattr("apps.api.routes.vendors.AdminQueryService", DummyQueryService)
    app.dependency_overrides[get_db] = override_get_db
    client = TestClient(app)
    vendor_id = uuid.uuid4()

    response = client.get(f"/v1/vendors/{vendor_id}/sources")

    assert response.status_code == 200
    body = response.json()["data"]
    assert body["vendor_id"] == str(vendor_id)
    assert body["items"][0]["root_url"] == "https://example.com"

    app.dependency_overrides.clear()
