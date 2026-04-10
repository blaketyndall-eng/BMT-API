"""initial core schema

Revision ID: 20260410_0001
Revises: None
Create Date: 2026-04-10 00:00:00
"""
from __future__ import annotations

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


revision = "20260410_0001"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "vendors",
        sa.Column("vendor_id", postgresql.UUID(as_uuid=True), primary_key=True, nullable=False),
        sa.Column("canonical_name", sa.String(length=255), nullable=False),
        sa.Column("canonical_slug", sa.String(length=255), nullable=False),
        sa.Column("primary_domain", sa.String(length=255), nullable=True),
        sa.Column("summary_short", sa.Text(), nullable=True),
        sa.Column("status", sa.String(length=50), nullable=False, server_default="active"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.UniqueConstraint("canonical_slug", name="uq_vendors_canonical_slug"),
    )

    op.create_table(
        "products",
        sa.Column("product_id", postgresql.UUID(as_uuid=True), primary_key=True, nullable=False),
        sa.Column("vendor_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("vendors.vendor_id"), nullable=False),
        sa.Column("canonical_name", sa.String(length=255), nullable=False),
        sa.Column("canonical_slug", sa.String(length=255), nullable=False),
        sa.Column("product_type", sa.String(length=100), nullable=False, server_default="core_platform"),
        sa.Column("summary_short", sa.Text(), nullable=True),
        sa.Column("status", sa.String(length=50), nullable=False, server_default="active"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
    )

    op.create_table(
        "sources",
        sa.Column("source_id", postgresql.UUID(as_uuid=True), primary_key=True, nullable=False),
        sa.Column("vendor_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("vendors.vendor_id"), nullable=True),
        sa.Column("product_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("products.product_id"), nullable=True),
        sa.Column("source_family", sa.String(length=100), nullable=False),
        sa.Column("source_type", sa.String(length=100), nullable=False),
        sa.Column("root_url", sa.String(length=2048), nullable=False),
        sa.Column("connector_type", sa.String(length=100), nullable=False),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.text("true")),
        sa.Column("source_metadata", postgresql.JSONB(astext_type=sa.Text()), nullable=False, server_default=sa.text("'{}'::jsonb")),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
    )

    op.create_table(
        "pages",
        sa.Column("page_id", postgresql.UUID(as_uuid=True), primary_key=True, nullable=False),
        sa.Column("source_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("sources.source_id"), nullable=False),
        sa.Column("canonical_url", sa.String(length=2048), nullable=False),
        sa.Column("page_type", sa.String(length=100), nullable=True),
        sa.Column("title", sa.String(length=500), nullable=True),
        sa.Column("http_status", sa.Integer(), nullable=True),
        sa.Column("content_sha256", sa.String(length=64), nullable=True),
        sa.Column("raw_object_key", sa.String(length=500), nullable=True),
        sa.Column("text_object_key", sa.String(length=500), nullable=True),
        sa.Column("parser_metadata", postgresql.JSONB(astext_type=sa.Text()), nullable=False, server_default=sa.text("'{}'::jsonb")),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.UniqueConstraint("canonical_url", name="uq_pages_canonical_url"),
    )

    op.create_table(
        "crawl_jobs",
        sa.Column("crawl_job_id", postgresql.UUID(as_uuid=True), primary_key=True, nullable=False),
        sa.Column("vendor_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("vendors.vendor_id"), nullable=True),
        sa.Column("product_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("products.product_id"), nullable=True),
        sa.Column("source_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("sources.source_id"), nullable=True),
        sa.Column("job_type", sa.String(length=100), nullable=False),
        sa.Column("worker_queue", sa.String(length=100), nullable=False),
        sa.Column("status", sa.String(length=50), nullable=False, server_default="queued"),
        sa.Column("priority", sa.Integer(), nullable=False, server_default="50"),
        sa.Column("payload", postgresql.JSONB(astext_type=sa.Text()), nullable=False, server_default=sa.text("'{}'::jsonb")),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
    )

    op.create_index("ix_vendors_primary_domain", "vendors", ["primary_domain"], unique=False)
    op.create_index("ix_products_vendor_id", "products", ["vendor_id"], unique=False)
    op.create_index("ix_sources_vendor_id", "sources", ["vendor_id"], unique=False)
    op.create_index("ix_sources_product_id", "sources", ["product_id"], unique=False)
    op.create_index("ix_pages_source_id", "pages", ["source_id"], unique=False)
    op.create_index("ix_crawl_jobs_status_priority", "crawl_jobs", ["status", "priority"], unique=False)


def downgrade() -> None:
    op.drop_index("ix_crawl_jobs_status_priority", table_name="crawl_jobs")
    op.drop_index("ix_pages_source_id", table_name="pages")
    op.drop_index("ix_sources_product_id", table_name="sources")
    op.drop_index("ix_sources_vendor_id", table_name="sources")
    op.drop_index("ix_products_vendor_id", table_name="products")
    op.drop_index("ix_vendors_primary_domain", table_name="vendors")

    op.drop_table("crawl_jobs")
    op.drop_table("pages")
    op.drop_table("sources")
    op.drop_table("products")
    op.drop_table("vendors")
