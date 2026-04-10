from __future__ import annotations

import uuid
from datetime import datetime

from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, String, Text, func
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
