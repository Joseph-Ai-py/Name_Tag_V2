from copy import deepcopy
from typing import Any

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.brand_state import BrandState
from app.models.history import History
from app.models.snapshot import Snapshot
from app.services.mutation_service import validate_brand_state_change_paths
from app.core.exceptions import BrandStateVersionConflictError


def create_initial_brand_state(
    db: Session,
    brand_id: str,
) -> BrandState:
    initial_state = {
        "business": {
            "industry": None,
            "service": None,
            "problem": None,
            "solution": None,
            "business_model": None,
            "pricing": None,
        },
        "market": {
            "tam": None,
            "sam": None,
            "som": None,
            "competitors": [],
            "swot": None,
            "trends": [],
        },
        "customer": {
            "target": None,
            "segments": [],
            "persona": None,
            "needs": [],
            "pain_points": [],
            "journey": None,
            "jtbd": None,
        },
        "brand": {
            "name": None,
            "mission": None,
            "vision": None,
            "values": [],
            "positioning": None,
            "story": None,
            "personality": [],
            "tone": None,
            "key_message": None,
            "tagline": None,
        },
        "visual": {
            "colors": [],
            "typography": None,
            "mood": None,
            "logo": None,
            "character": None,
        },
        "assets": [],
        "research": [],
        "feedback": [],
        "decisions": [],
    }

    brand_state = BrandState(
        brand_id=brand_id,
        state=initial_state,
        version=1,
    )

    db.add(brand_state)

    return brand_state


def get_brand_state(
    db: Session,
    brand_id: str,
) -> BrandState | None:
    result = db.execute(
        select(BrandState).where(
            BrandState.brand_id == brand_id,
        )
    )

    return result.scalar_one_or_none()


def merge_state(current: dict[str, Any], changes: dict[str, Any]) -> dict[str, Any]:
    merged = deepcopy(current)

    for key, value in changes.items():
        if isinstance(value, dict) and isinstance(merged.get(key), dict):
            merged[key] = merge_state(merged[key], value)
        else:
            merged[key] = deepcopy(value)

    return merged


def update_brand_state(
    db: Session,
    brand_state: BrandState,
    changes: dict[str, Any],
    expected_version: int | None = None,
    user_id: str | None = None,
) -> BrandState:
    if (
        expected_version is not None
        and brand_state.version != expected_version
    ):
        raise BrandStateVersionConflictError(
            brand_state.brand_id,
            expected_version,
            brand_state.version,
        )

    validate_brand_state_change_paths(changes)
    previous_state = deepcopy(brand_state.state)
    previous_version = brand_state.version
    if user_id:
        db.add(Snapshot(
            brand_id=brand_state.brand_id,
            version=previous_version,
            state=previous_state,
            created_by=user_id,
        ))
    brand_state.state = merge_state(brand_state.state, changes)
    brand_state.version += 1
    if user_id:
        db.add(History(
            brand_id=brand_state.brand_id,
            user_id=user_id,
            action="direct_brand_state_edit",
            details={
                "from_version": previous_version,
                "to_version": brand_state.version,
                "changes": changes,
            },
        ))
    db.commit()
    db.refresh(brand_state)
    return brand_state