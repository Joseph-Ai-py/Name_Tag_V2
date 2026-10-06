from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.dependencies import get_current_user, get_database
from app.core.exceptions import BrandStateVersionConflictError
from app.models.user import User
from app.schemas.brand_state import (
    BrandStateResponse,
    BrandStateUpdateRequest,
)
from app.services.brand_service import get_brand_membership
from app.services.brand_state_service import (
    get_brand_state,
    update_brand_state,
)
from app.core.permissions import require_editor_role


router = APIRouter(
    prefix="/api/brands",
    tags=["brand-state"],
)


@router.get(
    "/{brand_id}/state",
    response_model=BrandStateResponse,
)
def get_brand_state_endpoint(
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

    brand_state = get_brand_state(
        db=db,
        brand_id=brand_id,
    )

    if brand_state is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Brand state not found",
        )

    return BrandStateResponse(
        id=brand_state.id,
        brand_id=brand_state.brand_id,
        state=brand_state.state,
        version=brand_state.version,
        created_at=brand_state.created_at,
        updated_at=brand_state.updated_at,
    )


@router.patch(
    "/{brand_id}/state",
    response_model=BrandStateResponse,
)
def update_brand_state_endpoint(
    brand_id: str,
    payload: BrandStateUpdateRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_database),
):
    membership = get_brand_membership(db, brand_id, current_user.id)
    if membership is None:
        raise HTTPException(status_code=404, detail="Brand not found")
    require_editor_role(membership.role)

    brand_state = get_brand_state(db, brand_id)
    if brand_state is None:
        raise HTTPException(status_code=404, detail="Brand state not found")

    try:
        brand_state = update_brand_state(
            db=db,
            brand_state=brand_state,
            changes=payload.state,
            expected_version=payload.expected_version,
        )
    except BrandStateVersionConflictError as exc:
        raise HTTPException(
            status_code=409,
            detail={
                "code": "BRAND_STATE_VERSION_CONFLICT",
                "message": str(exc),
                "expected_version": exc.expected_version,
                "actual_version": exc.actual_version,
            },
        ) from exc
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    return BrandStateResponse(
        id=brand_state.id,
        brand_id=brand_state.brand_id,
        state=brand_state.state,
        version=brand_state.version,
        created_at=brand_state.created_at,
        updated_at=brand_state.updated_at,
    )