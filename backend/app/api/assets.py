from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.permissions import require_editor_role
from app.dependencies import get_current_user, get_database
from app.models.user import User
from app.schemas.asset import AssetCreateRequest, AssetResponse
from app.services.asset_service import create_asset, delete_asset, get_asset, get_brand_assets
from app.services.brand_service import get_brand_membership

router = APIRouter(prefix="/api/brands/{brand_id}/assets", tags=["assets"])


def asset_response(asset) -> AssetResponse:
	return AssetResponse(
		id=asset.id,
		brand_id=asset.brand_id,
		created_by=asset.created_by,
		type=asset.type,
		filename=asset.filename,
		mime_type=asset.mime_type,
		storage_path=asset.storage_path,
		metadata=asset.metadata_json,
		created_at=asset.created_at,
	)


def membership_or_404(db: Session, brand_id: str, user_id: str):
	membership = get_brand_membership(db, brand_id, user_id)
	if membership is None:
		raise HTTPException(status_code=404, detail="Brand not found")
	return membership


@router.post("", response_model=AssetResponse, status_code=status.HTTP_201_CREATED)
def create_asset_endpoint(brand_id: str, payload: AssetCreateRequest, current_user: User = Depends(get_current_user), db: Session = Depends(get_database)):
	membership = membership_or_404(db, brand_id, current_user.id)
	require_editor_role(membership.role)
	asset = create_asset(db, brand_id, current_user.id, **payload.model_dump())
	return asset_response(asset)


@router.get("", response_model=list[AssetResponse])
def list_assets(brand_id: str, current_user: User = Depends(get_current_user), db: Session = Depends(get_database)):
	membership_or_404(db, brand_id, current_user.id)
	return [asset_response(asset) for asset in get_brand_assets(db, brand_id)]


@router.delete("/{asset_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_asset_endpoint(brand_id: str, asset_id: str, current_user: User = Depends(get_current_user), db: Session = Depends(get_database)):
	membership = membership_or_404(db, brand_id, current_user.id)
	require_editor_role(membership.role)
	asset = get_asset(db, brand_id, asset_id)
	if asset is None:
		raise HTTPException(status_code=404, detail="Asset not found")
	delete_asset(db, asset)
