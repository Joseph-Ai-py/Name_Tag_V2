from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.brand_state import BrandState


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