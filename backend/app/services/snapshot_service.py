from copy import deepcopy

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.brand_state import BrandState
from app.models.history import History
from app.models.snapshot import Snapshot


def get_brand_snapshots(db: Session, brand_id: str) -> list[Snapshot]:
    result = db.execute(
        select(Snapshot)
        .where(Snapshot.brand_id == brand_id)
        .order_by(Snapshot.version.desc(), Snapshot.created_at.desc())
    )
    return list(result.scalars().all())


def get_snapshot(db: Session, brand_id: str, snapshot_id: str) -> Snapshot | None:
    result = db.execute(
        select(Snapshot).where(
            Snapshot.id == snapshot_id,
            Snapshot.brand_id == brand_id,
        )
    )
    return result.scalar_one_or_none()


def restore_snapshot(db: Session, snapshot: Snapshot, user_id: str) -> BrandState:
    brand_state = db.scalar(
        select(BrandState).where(BrandState.brand_id == snapshot.brand_id)
    )
    if brand_state is None:
        raise ValueError("Brand state not found")

    current_version = brand_state.version
    db.add(
        Snapshot(
            brand_id=snapshot.brand_id,
            version=current_version,
            state=deepcopy(brand_state.state),
            created_by=user_id,
        )
    )
    brand_state.state = deepcopy(snapshot.state)
    brand_state.version = current_version + 1
    db.add(
        History(
            brand_id=snapshot.brand_id,
            user_id=user_id,
            action="snapshot_restored",
            proposal_id=None,
            details={
                "from_version": current_version,
                "to_version": brand_state.version,
                "snapshot_id": snapshot.id,
                "snapshot_version": snapshot.version,
            },
        )
    )
    db.commit()
    db.refresh(brand_state)
    return brand_state
