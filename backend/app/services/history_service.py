from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.history import History


def get_brand_history(
    db: Session,
    brand_id: str,
) -> list[History]:
    result = db.execute(
        select(History)
        .where(
            History.brand_id == brand_id,
        )
        .order_by(
            History.created_at.desc(),
        )
    )

    return list(result.scalars().all())