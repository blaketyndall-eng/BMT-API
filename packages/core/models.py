from __future__ import annotations

import uuid
from datetime import datetime

from sqlalchemy import Boolean, DateTime, Float, ForeignKey, Integer, String, Text, func
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from packages.core.db import Base


class TimestampMixin:
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
    )


class Vendor(TimestampMixin, Base):
    __tablename__ = "vendors"

    vendor_id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    canonical_name: Mapped[str] = mapped_column(String(255), nullable=False)
    canonical_slug: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    primary_domain: Mapped[str | None] = mapped_column(String(255))
    summary_short: Mapped[str | None] = mapped_column(Text)
    status: Mapped[str] = mapped_column(String(50), default="active", nullable=False)

    products: Mapped[list[Product]] = relationship(back_populates="vendor", cascade="all, delete-orphan")
    sources: Mapped[list[Source]] = relationship(back_populates="vendor", cascade="all, delete-orphan")
    evidence_items: Mapped[list[Evidence]] = relationship(back_populates="vendor")


class Product(TimestampMixin, Base):
    __tablename__ = "products"

    product_id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    vendor_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("vendors.vendor_id"), nullable=False)
    canonical_name: Mapped[str] = mapped_column(String(255), nullable=False)
    canonical_slug: Mapped[str] = mapped_column(String(255), nullable=False)
    product_type: Mapped[str] = mapped_column(String(100), default="core_platform", nullable=False)
    summary_short: Mapped[str | None] = mapped_column(Text)
    status: Mapped[str] = mapped_column(String(50), default="active", nullable=False)

    vendor: Mapped[Vendor] = relationship(back_populates="products")
    sources: Mapped[list[Source]] = relationship(back_populates="product")
    evidence_items: Mapped[list[Evidence]] = relationship(back_populates="product")


class Source(TimestampMixin, Base):
    __tablename__ = "sources"

    source_id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    vendor_id: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("vendors.vendor_id"))
    product_id: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("products.product_id"))
    source_family: Mapped[str] = mapped_column(String(100), nullable=False)
    source_type: Mapped[str] = mapped_column(String(100), nullable=False)
    root_url: Mapped[str] = mapped_column(String(2048), nullable=False)
    connector_type: Mapped[str] = mapped_column(String(100), nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    source_metadata: Mapped[dict] = mapped_column(JSONB, default=dict, nullable=False)

    vendor: Mapped[Vendor | None] = relationship(back_populates="sources")
    product: Mapped[Product | None] = relationship(back_populates="sources")
    pages: Mapped[list[Page]] = relationship(back_populates="source", cascade="all, delete-orphan")
    evidence_items: Mapped[list[Evidence]] = relationship(back_populates="source")


class Page(TimestampMixin, Base):
    __tablename__ = "pages"

    page_id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    source_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("sources.source_id"), nullable=False)
    canonical_url: Mapped[str] = mapped_column(String(2048), unique=True, nullable=False)
    page_type: Mapped[str | None] = mapped_column(String(100))
    title: Mapped[str | None] = mapped_column(String(500))
    http_status: Mapped[int | None] = mapped_column(Integer)
    content_type: Mapped[str | None] = mapped_column(String(255))
    content_sha256: Mapped[str | None] = mapped_column(String(64))
    raw_object_key: Mapped[str | None] = mapped_column(String(500))
    text_object_key: Mapped[str | None] = mapped_column(String(500))
    page_text: Mapped[str | None] = mapped_column(Text)
    fetched_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    parser_metadata: Mapped[dict] = mapped_column(JSONB, default=dict, nullable=False)

    source: Mapped[Source] = relationship(back_populates="pages")
    evidence_items: Mapped[list[Evidence]] = relationship(back_populates="page", cascade="all, delete-orphan")


class Evidence(TimestampMixin, Base):
    __tablename__ = "evidence"

    evidence_id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    vendor_id: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("vendors.vendor_id"))
    product_id: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("products.product_id"))
    source_id: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("sources.source_id"))
    page_id: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("pages.page_id"))
    evidence_type: Mapped[str] = mapped_column(String(100), nullable=False)
    label: Mapped[str] = mapped_column(String(255), nullable=False)
    snippet: Mapped[str] = mapped_column(Text, nullable=False)
    confidence: Mapped[float] = mapped_column(Float, nullable=False, default=0.5)
    extractor_name: Mapped[str] = mapped_column(String(100), nullable=False)
    extractor_version: Mapped[str] = mapped_column(String(100), nullable=False)
    evidence_metadata: Mapped[dict] = mapped_column(JSONB, default=dict, nullable=False)

    vendor: Mapped[Vendor | None] = relationship(back_populates="evidence_items")
    product: Mapped[Product | None] = relationship(back_populates="evidence_items")
    source: Mapped[Source | None] = relationship(back_populates="evidence_items")
    page: Mapped[Page | None] = relationship(back_populates="evidence_items")


class CrawlJob(TimestampMixin, Base):
    __tablename__ = "crawl_jobs"

    crawl_job_id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    vendor_id: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("vendors.vendor_id"))
    product_id: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("products.product_id"))
    source_id: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("sources.source_id"))
    job_type: Mapped[str] = mapped_column(String(100), nullable=False)
    worker_queue: Mapped[str] = mapped_column(String(100), nullable=False)
    status: Mapped[str] = mapped_column(String(50), default="queued", nullable=False)
    priority: Mapped[int] = mapped_column(Integer, default=50, nullable=False)
    attempt_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    max_attempts: Mapped[int] = mapped_column(Integer, default=3, nullable=False)
    lease_owner: Mapped[str | None] = mapped_column(String(255))
    lease_expires_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    next_attempt_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    last_error: Mapped[str | None] = mapped_column(Text)
    payload: Mapped[dict] = mapped_column(JSONB, default=dict, nullable=False)


class AgentRun(TimestampMixin, Base):
    __tablename__ = "agent_runs"

    agent_run_id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    agent_name: Mapped[str] = mapped_column(String(100), nullable=False)
    strategy_version: Mapped[str | None] = mapped_column(String(100))
    mode: Mapped[str | None] = mapped_column(String(100))
    status: Mapped[str] = mapped_column(String(50), default="completed", nullable=False)
    trace_id: Mapped[str | None] = mapped_column(String(64))
    request_id: Mapped[str | None] = mapped_column(String(64))
    product_id: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("products.product_id"))
    vendor_id: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("vendors.vendor_id"))
    request_payload: Mapped[dict] = mapped_column(JSONB, default=dict, nullable=False)
    response_payload: Mapped[dict] = mapped_column(JSONB, default=dict, nullable=False)
    error_message: Mapped[str | None] = mapped_column(Text)


class DiscoveryCandidate(TimestampMixin, Base):
    __tablename__ = "discovery_candidates"

    discovery_candidate_id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    discovery_run_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("agent_runs.agent_run_id"), nullable=False)
    product_id: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("products.product_id"))
    promoted_source_id: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("sources.source_id"))
    vendor_domain: Mapped[str] = mapped_column(String(255), nullable=False)
    root_url: Mapped[str] = mapped_column(String(2048), nullable=False)
    source_family: Mapped[str] = mapped_column(String(100), nullable=False)
    source_type: Mapped[str] = mapped_column(String(100), nullable=False)
    source_group: Mapped[str] = mapped_column(String(100), nullable=False)
    policy_zone: Mapped[str] = mapped_column(String(50), nullable=False)
    connector_type: Mapped[str] = mapped_column(String(100), nullable=False)
    machine_readable: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    crawler_mode: Mapped[str] = mapped_column(String(100), nullable=False)
    parser_chain: Mapped[list] = mapped_column(JSONB, default=list, nullable=False)
    base_confidence_weight: Mapped[float] = mapped_column(Float, default=0.5, nullable=False)
    provenance_required: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    terms_review_required: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    review_status: Mapped[str] = mapped_column(String(50), default="pending", nullable=False)
    reviewer_note: Mapped[str | None] = mapped_column(Text)
    notes: Mapped[str | None] = mapped_column(Text)
    approved_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    rejected_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    candidate_metadata: Mapped[dict] = mapped_column(JSONB, default=dict, nullable=False)


class AgentEvalRun(TimestampMixin, Base):
    __tablename__ = "agent_eval_runs"

    agent_eval_run_id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    agent_name: Mapped[str] = mapped_column(String(100), nullable=False)
    evaluator_version: Mapped[str] = mapped_column(String(100), nullable=False)
    status: Mapped[str] = mapped_column(String(50), default="completed", nullable=False)
    trace_id: Mapped[str | None] = mapped_column(String(64))
    request_payload: Mapped[dict] = mapped_column(JSONB, default=dict, nullable=False)
    response_payload: Mapped[dict] = mapped_column(JSONB, default=dict, nullable=False)
    score: Mapped[float | None] = mapped_column(Float)
    overall_passed: Mapped[bool | None] = mapped_column(Boolean)
    error_message: Mapped[str | None] = mapped_column(Text)


class SourceProposalDecision(TimestampMixin, Base):
    __tablename__ = "source_proposal_decisions"

    source_proposal_decision_id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    decision_type: Mapped[str] = mapped_column(String(50), nullable=False)
    agent_name: Mapped[str | None] = mapped_column(String(100))
    trace_id: Mapped[str | None] = mapped_column(String(64))
    product_id: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("products.product_id"))
    vendor_id: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("vendors.vendor_id"))
    source_id: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("sources.source_id"))
    crawl_job_id: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("crawl_jobs.crawl_job_id"))
    proposal_payload: Mapped[dict] = mapped_column(JSONB, default=dict, nullable=False)
    decision_payload: Mapped[dict] = mapped_column(JSONB, default=dict, nullable=False)
    note: Mapped[str | None] = mapped_column(Text)
