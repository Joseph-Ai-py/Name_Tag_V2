"""create employee meetings

Revision ID: c2d3e4f5a6b7
Revises: b1c2d3e4f5a6
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "c2d3e4f5a6b7"
down_revision: Union[str, Sequence[str], None] = "b1c2d3e4f5a6"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "employee_meetings",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("brand_id", sa.String(length=36), nullable=False),
        sa.Column("created_by", sa.String(length=36), nullable=False),
        sa.Column("agenda", sa.Text(), nullable=False),
        sa.Column("mode", sa.String(length=20), nullable=False),
        sa.Column("status", sa.String(length=30), nullable=False),
        sa.Column("participants", sa.JSON(), nullable=False),
        sa.Column("shared_context", sa.JSON(), nullable=False),
        sa.Column("critic", sa.JSON(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("completed_at", sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(["brand_id"], ["brands.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["created_by"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_employee_meetings_brand_id", "employee_meetings", ["brand_id"])
    op.create_index("ix_employee_meetings_created_by", "employee_meetings", ["created_by"])

    op.create_table(
        "meeting_opinions",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("meeting_id", sa.String(length=36), nullable=False),
        sa.Column("employee", sa.String(length=50), nullable=False),
        sa.Column("skill", sa.String(length=50), nullable=False),
        sa.Column("opinion", sa.Text(), nullable=False),
        sa.Column("evidence", sa.JSON(), nullable=False),
        sa.Column("agreements", sa.JSON(), nullable=False),
        sa.Column("conflicts", sa.JSON(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["meeting_id"], ["employee_meetings.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_meeting_opinions_meeting_id", "meeting_opinions", ["meeting_id"])

    op.create_table(
        "meeting_decisions",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("meeting_id", sa.String(length=36), nullable=False),
        sa.Column("decision", sa.Text(), nullable=False),
        sa.Column("rationale", sa.Text(), nullable=False),
        sa.Column("changes", sa.JSON(), nullable=False),
        sa.Column("proposal_id", sa.String(length=36), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["meeting_id"], ["employee_meetings.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["proposal_id"], ["proposals.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_meeting_decisions_meeting_id", "meeting_decisions", ["meeting_id"])


def downgrade() -> None:
    op.drop_index("ix_meeting_decisions_meeting_id", table_name="meeting_decisions")
    op.drop_table("meeting_decisions")
    op.drop_index("ix_meeting_opinions_meeting_id", table_name="meeting_opinions")
    op.drop_table("meeting_opinions")
    op.drop_index("ix_employee_meetings_created_by", table_name="employee_meetings")
    op.drop_index("ix_employee_meetings_brand_id", table_name="employee_meetings")
    op.drop_table("employee_meetings")
