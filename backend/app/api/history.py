from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.dependencies import get_current_user, get_database
from app.models.user import User
from app.schemas.history import HistoryResponse
from app.services.brand_service import get_brand_membership
from app.services.history_service import get_brand_history


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