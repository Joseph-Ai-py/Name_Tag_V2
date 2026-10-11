"""remove duplicated canonical BrandState fields

Revision ID: 5c6d7e8f9012
Revises: 4b5c6d7e8f90
"""
from typing import Sequence, Union

from alembic import op
from sqlalchemy import select, update

from app.models.brand_state import BrandState


revision: str = "5c6d7e8f9012"
down_revision: Union[str, Sequence[str], None] = "4b5c6d7e8f90"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    connection = op.get_bind()
    rows = connection.execute(select(BrandState.id, BrandState.state)).all()
    for brand_state_id, state in rows:
        next_state = dict(state or {})
        brand = dict(next_state.get("brand") or {})
        core_identity = brand.pop("core_identity", None)
        if core_identity and "value_details" not in brand:
            brand["value_details"] = core_identity.get("core_values", []) if isinstance(core_identity, dict) else core_identity
        positioning_detail = brand.get("positioning_detail")
        if isinstance(positioning_detail, dict):
            positioning_detail.pop("statement", None)
            brand["positioning_detail"] = positioning_detail
        next_state["brand"] = brand
        connection.execute(update(BrandState).where(BrandState.id == brand_state_id).values(state=next_state))


def downgrade() -> None:
    pass
