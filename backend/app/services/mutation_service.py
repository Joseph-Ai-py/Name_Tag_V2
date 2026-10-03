from copy import deepcopy
from typing import Any

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


def flatten_state_paths(prefix: str, value: Any) -> list[str]:
    if not isinstance(value, dict):
        return [prefix] if prefix else []

    paths: list[str] = []
    for key, nested in value.items():
        path = f"{prefix}.{key}" if prefix else key
        if isinstance(nested, dict):
            paths.extend(flatten_state_paths(path, nested))
        else:
            paths.append(path)
    return paths


def validate_brand_state_change_paths(changes: Any) -> None:
    if not isinstance(changes, dict):
        raise ValueError("BrandState changes must be an object")
    if not changes:
        raise ValueError("BrandState changes cannot be empty")

    def validate_path(path: str, value: Any) -> None:
        if path in ALLOWED_PATHS:
            return
        if not isinstance(value, dict):
            raise ValueError(f"Unsupported BrandState path: {path}")
        for key, nested in value.items():
            validate_path(f"{path}.{key}" if path else key, nested)

    for path, value in changes.items():
        validate_path(path, value)


def apply_changes(
    brand_state: BrandState,
    changes: dict,
) -> tuple[dict, dict]:
    current_state = deepcopy(brand_state.state)
    next_state = deepcopy(current_state)

    validate_brand_state_change_paths(changes)

    for path, value in changes.items():
        if "." in path:
            section, field = path.split(".", 1)
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Unsupported BrandState path: {path}",
            )

        if section not in next_state:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid BrandState section: {section}",
            )

        next_state[section][field] = value

    return current_state, next_state