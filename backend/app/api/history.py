from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.permissions import require_editor_role
from app.dependencies import get_current_user, get_database
from app.models.user import User
from app.schemas.history import HistoryResponse
from app.schemas.snapshot import SnapshotResponse
from app.services.brand_service import get_brand_membership
from app.services.history_service import get_brand_history
from app.services.snapshot_service import get_brand_snapshots, get_snapshot, restore_snapshot


router = APIRouter(
    prefix="/api/brands",
    tags=["history"],
)


@router.get(
    "/{brand_id}/history",
    response_model=list[HistoryResponse],
)
def list_history(
    brand_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_database),
):
    membership = get_brand_membership(
        db=db,
        brand_id=brand_id,
        user_id=current_user.id,
    )

    if membership is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Brand not found",
        )

    history = get_brand_history(
        db=db,
        brand_id=brand_id,
    )

    return [
        HistoryResponse(
            id=item.id,
            brand_id=item.brand_id,
            user_id=item.user_id,
            action=item.action,
            proposal_id=item.proposal_id,
            details=item.details,
            created_at=item.created_at,
        )
        for item in history
    ]


@router.get(
    "/{brand_id}/snapshots",
    response_model=list[SnapshotResponse],
)
def list_snapshots(
    brand_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_database),
):
    if get_brand_membership(db, brand_id, current_user.id) is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Brand not found")
    return get_brand_snapshots(db, brand_id)


@router.post(
    "/{brand_id}/snapshots/{snapshot_id}/restore",
    response_model=SnapshotResponse,
)
def restore_snapshot_endpoint(
    brand_id: str,
    snapshot_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_database),
):
    membership = get_brand_membership(db, brand_id, current_user.id)
    if membership is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Brand not found")
    require_editor_role(membership.role)
    snapshot = get_snapshot(db, brand_id, snapshot_id)
    if snapshot is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Snapshot not found")
    try:
        brand_state = restore_snapshot(db, snapshot, current_user.id)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc)) from exc
    return SnapshotResponse(
        id=snapshot.id,
        brand_id=brand_id,
        version=brand_state.version,
        state=brand_state.state,
        created_by=current_user.id,
        created_at=snapshot.created_at,
    )