import uuid
from datetime import datetime, timezone

from fastapi.testclient import TestClient

from apps.api.main import app
from packages.contracts.admin import (
    CrawlJobListResponse,
    CrawlJobSummary,
    VendorSourcesResponse,
    SourceSummary,
)
from packages.core.deps import get_db


class DummyService:
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


def override_get_db():
    yield object()


def test_admin_crawl_jobs_endpoint_returns_payload(monkeypatch) -> None:
    monkeypatch.setattr("apps.api.routes.admin.AdminQueryService", DummyService)
    app.dependency_overrides[get_db] = override_get_db
    client = TestClient(app)

    response = client.get("/v1/admin/crawl-jobs?status=queued&limit=10")

    assert response.status_code == 200
    payload = response.json()["data"]["items"][0]
    assert payload["status"] == "queued"
    assert payload["worker_queue"] == "browser_fetch"

    app.dependency_overrides.clear()


def test_vendor_sources_endpoint_returns_payload(monkeypatch) -> None:
    monkeypatch.setattr("apps.api.routes.vendors.AdminQueryService", DummyService)
    app.dependency_overrides[get_db] = override_get_db
    client = TestClient(app)
    vendor_id = uuid.uuid4()

    response = client.get(f"/v1/vendors/{vendor_id}/sources")

    assert response.status_code == 200
    body = response.json()["data"]
    assert body["vendor_id"] == str(vendor_id)
    assert body["items"][0]["root_url"] == "https://example.com"

    app.dependency_overrides.clear()
