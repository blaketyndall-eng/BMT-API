"""add crawl job retry lifecycle fields

Revision ID: 20260410_0003
Revises: 20260410_0002
Create Date: 2026-04-10 22:40:00
"""
from __future__ import annotations

from alembic import op
import sqlalchemy as sa


revision = "20260410_0003"
down_revision = "20260410_0002"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "crawl_jobs",
        sa.Column("max_attempts", sa.Integer(), nullable=False, server_default="3"),
    )
    op.add_column("crawl_jobs", sa.Column("next_attempt_at", sa.DateTime(timezone=True), nullable=True))
    op.add_column("crawl_jobs", sa.Column("completed_at", sa.DateTime(timezone=True), nullable=True))
    op.create_index(
        "ix_crawl_jobs_worker_queue_status_retry",
        "crawl_jobs",
        ["worker_queue", "status", "next_attempt_at"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index("ix_crawl_jobs_worker_queue_status_retry", table_name="crawl_jobs")
    op.drop_column("crawl_jobs", "completed_at")
    op.drop_column("crawl_jobs", "next_attempt_at")
    op.drop_column("crawl_jobs", "max_attempts")
