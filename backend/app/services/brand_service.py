from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.brand import Brand
from app.models.brand_member import BrandMember
from app.services.brand_state_service import create_initial_brand_state


def create_brand(
    db: Session,
    user_id: str,
    name: str,
    description: str | None,
) -> Brand:
    brand = Brand(
        name=name.strip(),
        description=description,
    )

    db.add(brand)
    db.flush()

    membership = BrandMember(
        brand_id=brand.id,
        user_id=user_id,
        role="owner",
    )

    db.add(membership)

    create_initial_brand_state(
        db=db,
        brand_id=brand.id,
    )

    db.commit()
    db.refresh(brand)

    return brand


def get_user_brands(
    db: Session,
    user_id: str,
) -> list[tuple[Brand, str]]:
    result = db.execute(
        select(Brand, BrandMember.role)
        .join(
            BrandMember,
            BrandMember.brand_id == Brand.id,
        )
        .where(
            BrandMember.user_id == user_id,
        )
        .order_by(Brand.created_at.desc())
    )

    return list(result.all())


def get_brand(
    db: Session,
    brand_id: str,
) -> Brand | None:
    return db.get(Brand, brand_id)


def update_brand(
    db: Session,
    brand: Brand,
    name: str | None,
    description: str | None,
) -> Brand:
    if name is not None:
        brand.name = name.strip()

    if description is not None:
        brand.description = description

    db.commit()
    db.refresh(brand)
    return brand


def delete_brand(
    db: Session,
    brand: Brand,
) -> None:
    db.delete(brand)
    db.commit()


def get_brand_membership(
    db: Session,
    brand_id: str,
    user_id: str,
) -> BrandMember | None:
    result = db.execute(
        select(BrandMember).where(
            BrandMember.brand_id == brand_id,
            BrandMember.user_id == user_id,
        )
    )

    return result.scalar_one_or_none()