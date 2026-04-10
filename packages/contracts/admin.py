from datetime import datetime

from pydantic import BaseModel


class CrawlJobSummary(BaseModel):
    crawl_job_id: str
    vendor_id: str | None
    product_id: str | None
    source_id: str | None
    source_root_url: str | None
    source_type: str | None
    job_type: str
    worker_queue: str
    status: str
    priority: int
    attempt_count: int
    max_attempts: int
    lease_owner: str | None
    lease_expires_at: datetime | None
    next_attempt_at: datetime | None
    completed_at: datetime | None
    last_error: str | None
    created_at: datetime
    updated_at: datetime


class CrawlJobListResponse(BaseModel):
    items: list[CrawlJobSummary]


class PageSummary(BaseModel):
    page_id: str
    source_id: str
    source_root_url: str | None
    source_type: str | None
    canonical_url: str
    page_type: str | None
    title: str | None
    http_status: int | None
    content_type: str | None
    fetched_at: datetime
    created_at: datetime
    updated_at: datetime


class PageListResponse(BaseModel):
    items: list[PageSummary]


class SourceSummary(BaseModel):
    source_id: str
    vendor_id: str | None
    product_id: str | None
    source_family: str
    source_type: str
    root_url: str
    connector_type: str
    is_active: bool
    created_at: datetime
    updated_at: datetime


class VendorSourcesResponse(BaseModel):
    vendor_id: str
    items: list[SourceSummary]
