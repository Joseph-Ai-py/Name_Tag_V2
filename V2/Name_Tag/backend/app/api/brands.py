from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.dependencies import get_current_user, get_database
from app.models.user import User
from app.schemas.brand import (
    BrandCreateRequest,
    BrandListItem,
    BrandResponse,
)
from app.services.brand_service import (
    create_brand,
    get_user_brands,
)

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