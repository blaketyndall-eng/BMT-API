from pydantic import BaseModel, Field


class SourceRecrawlRequest(BaseModel):
    reason: str = "manual"
    priority: int = Field(default=90, ge=0, le=100)
    force: bool = False


class SourceRecrawlResponse(BaseModel):
    source_id: str
    crawl_job_id: str
    status: str
    deduped: bool


class CrawlJobReplayRequest(BaseModel):
    priority: int = Field(default=90, ge=0, le=100)
    reason: str = "manual_replay"


class CrawlJobReplayResponse(BaseModel):
    original_crawl_job_id: str
    replay_crawl_job_id: str
    status: str
    deduped: bool
