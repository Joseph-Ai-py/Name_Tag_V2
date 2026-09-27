from copy import deepcopy

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models.brand_state import BrandState


ALLOWED_PATHS = {
    "business.industry",
    "business.service",
    "business.problem",
    "business.solution",
    "business.business_model",
    "business.pricing",

    "market.tam",
    "market.sam",
    "market.som",
    "market.competitors",
    "market.swot",
    "market.trends",

    "customer.target",
    "customer.segments",
    "customer.persona",
    "customer.needs",
    "customer.pain_points",
    "customer.journey",
    "customer.jtbd",

    "brand.name",
    "brand.mission",
    "brand.vision",
    "brand.values",
    "brand.positioning",
    "brand.story",
    "brand.personality",
    "brand.tone",
    "brand.key_message",
    "brand.tagline",

    "visual.colors",
    "visual.typography",
    "visual.mood",
    "visual.logo",
    "visual.character",
}


def apply_changes(
    brand_state: BrandState,
    changes: dict,
) -> tuple[dict, dict]:
    current_state = deepcopy(brand_state.state)
    next_state = deepcopy(current_state)

    for path, value in changes.items():
        if path not in ALLOWED_PATHS:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Unsupported BrandState path: {path}",
            )

        section, field = path.split(".", 1)

        if section not in next_state:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid BrandState section: {section}",
            )

        next_state[section][field] = value

    return current_state, next_state