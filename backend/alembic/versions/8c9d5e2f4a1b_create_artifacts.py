"""create artifacts

Revision ID: 8c9d5e2f4a1b
Revises: 7b8e4f1c2d3a
Create Date: 2026-10-01
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "8c9d5e2f4a1b"
down_revision: Union[str, Sequence[str], None] = "7b8e4f1c2d3a"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "artifacts",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("brand_id", sa.String(length=36), nullable=False),
        sa.Column("created_by", sa.String(length=36), nullable=False),
        sa.Column("type", sa.String(length=50), nullable=False),
        sa.Column("title", sa.String(length=300), nullable=False),
        sa.Column("content", sa.JSON(), nullable=False),
        sa.Column("status", sa.String(length=20), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["brand_id"], ["brands.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["created_by"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_artifacts_brand_id", "artifacts", ["brand_id"], unique=False)
    op.create_index("ix_artifacts_created_by", "artifacts", ["created_by"], unique=False)


def downgrade() -> None:
    op.drop_index("ix_artifacts_created_by", table_name="artifacts")
    op.drop_index("ix_artifacts_brand_id", table_name="artifacts")
    op.drop_table("artifacts")
