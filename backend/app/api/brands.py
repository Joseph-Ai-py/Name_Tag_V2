from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.dependencies import get_current_user, get_database
from app.models.user import User
from app.schemas.brand import (
    BrandCreateRequest,
    BrandListItem,
    BrandResponse,
    BrandUpdateRequest,
)
from app.services.brand_service import (
    create_brand,
    delete_brand,
    get_brand,
    get_brand_membership,
    get_user_brands,
    update_brand,
)
from app.core.permissions import require_editor_role, require_owner_role

router = APIRouter(
    prefix="/api/brands",
    tags=["brands"],
)


@router.post(
    "",
    response_model=BrandResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_brand_endpoint(
    payload: BrandCreateRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_database),
):
    brand = create_brand(
        db=db,
        user_id=current_user.id,
        name=payload.name,
        description=payload.description,
    )

    return BrandResponse(
        id=brand.id,
        name=brand.name,
        description=brand.description,
        created_at=brand.created_at,
        updated_at=brand.updated_at,
    )


@router.get(
    "",
    response_model=list[BrandListItem],
)
def list_brands(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_database),
):
    brands = get_user_brands(
        db=db,
        user_id=current_user.id,
    )

    return [
        BrandListItem(
            id=brand.id,
            name=brand.name,
            description=brand.description,
            role=role,
            created_at=brand.created_at,
            updated_at=brand.updated_at,
        )
        for brand, role in brands
    ]


@router.get(
    "/{brand_id}",
    response_model=BrandResponse,
)
def get_brand_endpoint(
    brand_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_database),
):
    membership = get_brand_membership(db, brand_id, current_user.id)
    if membership is None:
        raise HTTPException(status_code=404, detail="Brand not found")

    brand = get_brand(db, brand_id)
    if brand is None:
        raise HTTPException(status_code=404, detail="Brand not found")

    return BrandResponse.model_validate(brand, from_attributes=True)


@router.patch(
    "/{brand_id}",
    response_model=BrandResponse,
)
def update_brand_endpoint(
    brand_id: str,
    payload: BrandUpdateRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_database),
):
    membership = get_brand_membership(db, brand_id, current_user.id)
    if membership is None:
        raise HTTPException(status_code=404, detail="Brand not found")
    require_editor_role(membership.role)

    brand = get_brand(db, brand_id)
    if brand is None:
        raise HTTPException(status_code=404, detail="Brand not found")

    updated = update_brand(
        db,
        brand,
        payload.name,
        payload.description,
    )
    return BrandResponse.model_validate(updated, from_attributes=True)


@router.delete(
    "/{brand_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_brand_endpoint(
    brand_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_database),
):
    membership = get_brand_membership(db, brand_id, current_user.id)
    if membership is None:
        raise HTTPException(status_code=404, detail="Brand not found")
    require_owner_role(membership.role)

    brand = get_brand(db, brand_id)
    if brand is None:
        raise HTTPException(status_code=404, detail="Brand not found")

    delete_brand(db, brand)