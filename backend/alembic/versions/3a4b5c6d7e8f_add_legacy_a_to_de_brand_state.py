"""add legacy A-to-DE compatibility data to BrandState

Revision ID: 3a4b5c6d7e8f
Revises: f1a2b3c4d5e6
"""
from typing import Sequence, Union

from alembic import op
from sqlalchemy import select, update

from app.core.legacy_template import legacy_state_template
from app.models.brand_state import BrandState


revision: str = "3a4b5c6d7e8f"
down_revision: Union[str, Sequence[str], None] = "f1a2b3c4d5e6"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    connection = op.get_bind()
    rows = connection.execute(select(BrandState.id, BrandState.state)).all()
    for brand_state_id, state in rows:
        next_state = dict(state or {})
        if "legacy" not in next_state:
            next_state["legacy"] = legacy_state_template()
            connection.execute(
                update(BrandState)
                .where(BrandState.id == brand_state_id)
                .values(state=next_state)
            )


def downgrade() -> None:
    connection = op.get_bind()
    rows = connection.execute(select(BrandState.id, BrandState.state)).all()
    for brand_state_id, state in rows:
        next_state = dict(state or {})
        next_state.pop("legacy", None)
        connection.execute(
            update(BrandState)
            .where(BrandState.id == brand_state_id)
            .values(state=next_state)
        )
