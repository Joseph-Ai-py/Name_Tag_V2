from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.asset import Asset


def create_asset(db: Session, brand_id: str, user_id: str, **values) -> Asset:
	values["metadata_json"] = values.pop("metadata", {})
	asset = Asset(brand_id=brand_id, created_by=user_id, **values)
	db.add(asset)
	db.commit()
	db.refresh(asset)
	return asset


def get_brand_assets(db: Session, brand_id: str) -> list[Asset]:
	result = db.execute(
		select(Asset).where(Asset.brand_id == brand_id).order_by(Asset.created_at.desc())
	)
	return list(result.scalars())


def get_asset(db: Session, brand_id: str, asset_id: str) -> Asset | None:
	return db.scalar(select(Asset).where(Asset.brand_id == brand_id, Asset.id == asset_id))


def delete_asset(db: Session, asset: Asset) -> None:
	db.delete(asset)
	db.commit()
