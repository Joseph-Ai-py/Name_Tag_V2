from time import perf_counter
from uuid import uuid4

from sqlalchemy.orm import Session

from app.config import get_settings
from app.models.usage_event import UsageEvent


def start_usage() -> float:
    return perf_counter()


def record_usage(
    db: Session,
    user_id: str,
    brand_id: str,
    feature: str,
    started_at: float,
    status: str = "completed",
) -> UsageEvent:
    settings = get_settings()
    event = UsageEvent(
        user_id=user_id,
        brand_id=brand_id,
        feature=feature,
        model=settings.gemini_model if settings.llm_provider == "gemini" else "mock",
        request_id=str(uuid4()),
        duration_ms=int((perf_counter() - started_at) * 1000),
        status=status,
    )
    db.add(event)
    db.commit()
    db.refresh(event)
    return event