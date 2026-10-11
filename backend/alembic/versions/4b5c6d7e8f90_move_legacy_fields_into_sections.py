"""move Legacy A-to-DE data into existing BrandState sections

Revision ID: 4b5c6d7e8f90
Revises: 3a4b5c6d7e8f
"""
from typing import Sequence, Union

from alembic import op
from sqlalchemy import select, update

from app.core.legacy_template import canonical_section_extensions
from app.models.brand_state import BrandState


revision: str = "4b5c6d7e8f90"
down_revision: Union[str, Sequence[str], None] = "3a4b5c6d7e8f"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def _has_content(value) -> bool:
    if value is None or value == "":
        return False
    if isinstance(value, list):
        return any(_has_content(item) for item in value)
    if isinstance(value, dict):
        return any(_has_content(item) for item in value.values())
    return True


def upgrade() -> None:
    connection = op.get_bind()
    defaults = canonical_section_extensions()
    rows = connection.execute(select(BrandState.id, BrandState.state)).all()
    for brand_state_id, state in rows:
        next_state = dict(state or {})
        legacy = next_state.pop("legacy", {}) or {}
        for section_name, extensions in defaults.items():
            section = dict(next_state.get(section_name) or {})
            section.update({key: value for key, value in extensions.items() if key not in section})
            next_state[section_name] = section

        if legacy:
            brand_info = legacy.get("brand_info", {})
            data_a = legacy.get("data_a", {})
            data_b = legacy.get("data_b", {})
            data_c = legacy.get("data_c", {})
            data_de = legacy.get("data_de", {})
            brand = next_state["brand"]
            for source, target in {
                "brand_name": "name",
                "brand_name_en": "name_en",
                "name_meaning": "name_meaning",
                "slogan": "tagline",
                "story_summary": "story",
                "seed_color": "seed_color",
                "seed_color_reason": "seed_color_reason",
            }.items():
                if not _has_content(brand.get(target)) and _has_content(brand_info.get(source)):
                    brand[target] = brand_info[source]
            for source, target in {
                "brand_philosophy": "brand_philosophy",
                "brand_essence": "brand_essence",
                "core_identity": "core_identity",
                "naming_expansion": "naming_expansion",
                "slogan_expansion": "slogan_expansion",
                "positioning": "positioning_detail",
                "unbreakable_brand_promise": "unbreakable_brand_promise",
            }.items():
                if not _has_content(brand.get(target)) and _has_content(data_a.get(source)):
                    brand[target] = data_a[source]
            if not _has_content(brand.get("interview_data")) and _has_content(legacy.get("interview_data")):
                brand["interview_data"] = legacy["interview_data"]

            customer = next_state["customer"]
            for source, target in {"persona_strategy": "persona_strategy", "customer_journey": "journey_detail"}.items():
                if not _has_content(customer.get(target)) and _has_content(data_b.get(source)):
                    customer[target] = data_b[source]
            visual = next_state["visual"]
            for source, target in {
                "color_palette": "colors",
                "typography": "typography",
                "visual_mood_guide": "visual_mood_guide",
                "design_principles": "design_principles",
                "logo_identity": "logo",
                "character_guide": "character",
                "logo_path": "logo_path",
                "char_path": "char_path",
            }.items():
                if not _has_content(visual.get(target)) and _has_content(data_c.get(source) or data_de.get(source)):
                    visual[target] = data_c.get(source) or data_de.get(source)

        connection.execute(
            update(BrandState).where(BrandState.id == brand_state_id).values(state=next_state)
        )


def downgrade() -> None:
    # The canonical section values remain authoritative after migration.
    pass
