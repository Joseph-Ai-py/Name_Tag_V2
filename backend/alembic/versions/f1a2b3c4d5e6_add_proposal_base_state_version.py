"""add proposal base state version

Revision ID: f1a2b3c4d5e6
Revises: c2d3e4f5a6b7
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "f1a2b3c4d5e6"
down_revision: Union[str, Sequence[str], None] = "c2d3e4f5a6b7"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column("proposals", sa.Column("base_state_version", sa.Integer(), nullable=True))
    op.execute(
        sa.text(
            "UPDATE proposals "
            "SET base_state_version = ("
            "SELECT version FROM brand_states "
            "WHERE brand_states.brand_id = proposals.brand_id"
            ") WHERE base_state_version IS NULL"
        )
    )
    with op.batch_alter_table("proposals") as batch_op:
        batch_op.alter_column("base_state_version", existing_type=sa.Integer(), nullable=False)


def downgrade() -> None:
    op.drop_column("proposals", "base_state_version")