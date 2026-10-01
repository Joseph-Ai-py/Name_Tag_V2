from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.dependencies import get_current_user, get_database
from app.models.user import User
from app.schemas.export import ExportRequest, ExportResponse
from app.services.brand_service import get_brand, get_brand_membership
from app.services.export_service import build_json_export

router = APIRouter(prefix="/api/brands/{brand_id}/export", tags=["export"])


@router.post("", response_model=ExportResponse, status_code=status.HTTP_200_OK)
def export_brand(
    brand_id: str,
    payload: ExportRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_database),
):
    if get_brand_membership(db, brand_id, current_user.id) is None:
        raise HTTPException(status_code=404, detail="Brand not found")
    brand = get_brand(db, brand_id)
    if brand is None:
        raise HTTPException(status_code=404, detail="Brand not found")
    return build_json_export(db, brand)