"""create research tables

Revision ID: 9d0f6a1b2c3d
Revises: 8c9d5e2f4a1b
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "9d0f6a1b2c3d"
down_revision: Union[str, Sequence[str], None] = "8c9d5e2f4a1b"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "research_jobs",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("brand_id", sa.String(length=36), nullable=False),
        sa.Column("created_by", sa.String(length=36), nullable=False),
        sa.Column("mode", sa.String(length=20), nullable=False),
        sa.Column("status", sa.String(length=20), nullable=False),
        sa.Column("query", sa.Text(), nullable=False),
        sa.Column("plan", sa.JSON(), nullable=False),
        sa.Column("progress", sa.JSON(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["brand_id"], ["brands.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["created_by"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_research_jobs_brand_id", "research_jobs", ["brand_id"])
    op.create_index("ix_research_jobs_created_by", "research_jobs", ["created_by"])

    op.create_table(
        "research_reports",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("research_job_id", sa.String(length=36), nullable=False),
        sa.Column("brand_id", sa.String(length=36), nullable=False),
        sa.Column("title", sa.String(length=300), nullable=False),
        sa.Column("executive_summary", sa.Text(), nullable=False),
        sa.Column("sections", sa.JSON(), nullable=False),
        sa.Column("status", sa.String(length=20), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["research_job_id"], ["research_jobs.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["brand_id"], ["brands.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_research_reports_research_job_id", "research_reports", ["research_job_id"])
    op.create_index("ix_research_reports_brand_id", "research_reports", ["brand_id"])

    op.create_table(
        "research_sources",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("report_id", sa.String(length=36), nullable=False),
        sa.Column("url", sa.Text(), nullable=False),
        sa.Column("title", sa.String(length=300), nullable=False),
        sa.Column("publisher", sa.String(length=200), nullable=True),
        sa.Column("summary", sa.Text(), nullable=True),
        sa.Column("source_type", sa.String(length=30), nullable=False),
        sa.Column("accessed_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["report_id"], ["research_reports.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_research_sources_report_id", "research_sources", ["report_id"])

    op.create_table(
        "research_findings",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("report_id", sa.String(length=36), nullable=False),
        sa.Column("statement", sa.Text(), nullable=False),
        sa.Column("evidence", sa.Text(), nullable=False),
        sa.Column("source_ids", sa.JSON(), nullable=False),
        sa.Column("confidence", sa.String(length=30), nullable=False),
        sa.Column("suggested_fields", sa.JSON(), nullable=False),
        sa.Column("applied", sa.Boolean(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["report_id"], ["research_reports.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_research_findings_report_id", "research_findings", ["report_id"])

    op.create_table(
        "research_events",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("job_id", sa.String(length=36), nullable=False),
        sa.Column("type", sa.String(length=50), nullable=False),
        sa.Column("stage", sa.String(length=50), nullable=False),
        sa.Column("message", sa.Text(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["job_id"], ["research_jobs.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_research_events_job_id", "research_events", ["job_id"])


def downgrade() -> None:
    op.drop_index("ix_research_events_job_id", table_name="research_events")
    op.drop_table("research_events")
    op.drop_index("ix_research_findings_report_id", table_name="research_findings")
    op.drop_table("research_findings")
    op.drop_index("ix_research_sources_report_id", table_name="research_sources")
    op.drop_table("research_sources")
    op.drop_index("ix_research_reports_brand_id", table_name="research_reports")
    op.drop_index("ix_research_reports_research_job_id", table_name="research_reports")
    op.drop_table("research_reports")
    op.drop_index("ix_research_jobs_created_by", table_name="research_jobs")
    op.drop_index("ix_research_jobs_brand_id", table_name="research_jobs")
    op.drop_table("research_jobs")