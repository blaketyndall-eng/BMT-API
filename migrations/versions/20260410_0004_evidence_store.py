"""add evidence table for extracted signals

Revision ID: 20260410_0004
Revises: 20260410_0003
Create Date: 2026-04-10 23:05:00
"""
from __future__ import annotations

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


revision = "20260410_0004"
down_revision = "20260410_0003"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "evidence",
        sa.Column("evidence_id", postgresql.UUID(as_uuid=True), primary_key=True, nullable=False),
        sa.Column("vendor_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("vendors.vendor_id"), nullable=True),
        sa.Column("product_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("products.product_id"), nullable=True),
        sa.Column("source_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("sources.source_id"), nullable=True),
        sa.Column("page_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("pages.page_id"), nullable=True),
        sa.Column("evidence_type", sa.String(length=100), nullable=False),
        sa.Column("label", sa.String(length=255), nullable=False),
        sa.Column("snippet", sa.Text(), nullable=False),
        sa.Column("confidence", sa.Float(), nullable=False, server_default="0.5"),
        sa.Column("extractor_name", sa.String(length=100), nullable=False),
        sa.Column("extractor_version", sa.String(length=100), nullable=False),
        sa.Column("evidence_metadata", postgresql.JSONB(astext_type=sa.Text()), nullable=False, server_default=sa.text("'{}'::jsonb")),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
    )
    op.create_index("ix_evidence_page_id", "evidence", ["page_id"], unique=False)
    op.create_index("ix_evidence_product_type", "evidence", ["product_id", "evidence_type"], unique=False)
    op.create_index("ix_evidence_vendor_type", "evidence", ["vendor_id", "evidence_type"], unique=False)


def downgrade() -> None:
    op.drop_index("ix_evidence_vendor_type", table_name="evidence")
    op.drop_index("ix_evidence_product_type", table_name="evidence")
    op.drop_index("ix_evidence_page_id", table_name="evidence")
    op.drop_table("evidence")
