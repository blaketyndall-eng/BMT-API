"""add browser fetch leasing fields

Revision ID: 20260410_0002
Revises: 20260410_0001
Create Date: 2026-04-10 00:30:00
"""
from __future__ import annotations

from alembic import op
import sqlalchemy as sa


revision = "20260410_0002"
down_revision = "20260410_0001"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("pages", sa.Column("content_type", sa.String(length=255), nullable=True))
    op.add_column("pages", sa.Column("page_text", sa.Text(), nullable=True))
    op.add_column(
        "pages",
        sa.Column(
            "fetched_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("now()"),
        ),
    )

    op.add_column(
        "crawl_jobs",
        sa.Column("attempt_count", sa.Integer(), nullable=False, server_default="0"),
    )
    op.add_column("crawl_jobs", sa.Column("lease_owner", sa.String(length=255), nullable=True))
    op.add_column("crawl_jobs", sa.Column("lease_expires_at", sa.DateTime(timezone=True), nullable=True))
    op.add_column("crawl_jobs", sa.Column("last_error", sa.Text(), nullable=True))
    op.create_index(
        "ix_crawl_jobs_worker_queue_status",
        "crawl_jobs",
        ["worker_queue", "status"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index("ix_crawl_jobs_worker_queue_status", table_name="crawl_jobs")
    op.drop_column("crawl_jobs", "last_error")
    op.drop_column("crawl_jobs", "lease_expires_at")
    op.drop_column("crawl_jobs", "lease_owner")
    op.drop_column("crawl_jobs", "attempt_count")
    op.drop_column("pages", "fetched_at")
    op.drop_column("pages", "page_text")
    op.drop_column("pages", "content_type")
