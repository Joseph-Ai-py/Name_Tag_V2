from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.permissions import require_editor_role
from app.core.exceptions import BrandStateVersionConflictError
from app.dependencies import get_current_user, get_database
from app.models.user import User
from app.schemas.artifact import ArtifactCreateRequest, ArtifactResponse
from app.services.artifact_service import apply_artifact, change_artifact_status, create_artifact, get_artifact, get_brand_artifacts
from app.services.brand_service import get_brand_membership

router = APIRouter(tags=["artifacts"])


def to_response(artifact) -> ArtifactResponse:
    return ArtifactResponse(**{field: getattr(artifact, field) for field in ArtifactResponse.model_fields})


def require_brand_editor(db: Session, brand_id: str, user_id: str) -> None:
    membership = get_brand_membership(db, brand_id, user_id)
    if membership is None:
        raise HTTPException(status_code=404, detail="Brand not found")
    require_editor_role(membership.role)


def get_accessible_artifact(db: Session, brand_id: str, artifact_id: str, current_user: User):
    require_brand_editor(db, brand_id, current_user.id)
    artifact = get_artifact(db, brand_id, artifact_id)
    if artifact is None:
        raise HTTPException(status_code=404, detail="Artifact not found")
    return artifact


@router.post("/api/brands/{brand_id}/artifacts", response_model=ArtifactResponse, status_code=status.HTTP_201_CREATED)
def create_artifact_endpoint(brand_id: str, payload: ArtifactCreateRequest, current_user: User = Depends(get_current_user), db: Session = Depends(get_database)):
    require_brand_editor(db, brand_id, current_user.id)
    artifact = create_artifact(db, brand_id, current_user.id, payload.type, payload.title, payload.content)
    return to_response(artifact)


@router.get("/api/brands/{brand_id}/artifacts", response_model=list[ArtifactResponse])
def list_artifacts_endpoint(brand_id: str, current_user: User = Depends(get_current_user), db: Session = Depends(get_database)):
    if get_brand_membership(db, brand_id, current_user.id) is None:
        raise HTTPException(status_code=404, detail="Brand not found")
    return [to_response(item) for item in get_brand_artifacts(db, brand_id)]


@router.get("/api/brands/{brand_id}/artifacts/{artifact_id}", response_model=ArtifactResponse)
def get_artifact_endpoint(brand_id: str, artifact_id: str, current_user: User = Depends(get_current_user), db: Session = Depends(get_database)):
    return to_response(get_accessible_artifact(db, brand_id, artifact_id, current_user))


def set_artifact_status(brand_id: str, artifact_id: str, next_status: str, current_user: User, db: Session):
    artifact = get_accessible_artifact(db, brand_id, artifact_id, current_user)
    if artifact.status != "draft":
        raise HTTPException(status_code=409, detail="Only draft artifacts can change status")
    return to_response(change_artifact_status(db, artifact, next_status))


@router.post("/api/brands/{brand_id}/artifacts/{artifact_id}/approve", response_model=ArtifactResponse)
def approve_artifact_endpoint(brand_id: str, artifact_id: str, current_user: User = Depends(get_current_user), db: Session = Depends(get_database)):
    return set_artifact_status(brand_id, artifact_id, "approved", current_user, db)


@router.post("/api/brands/{brand_id}/artifacts/{artifact_id}/apply", response_model=ArtifactResponse)
def apply_artifact_endpoint(brand_id: str, artifact_id: str, current_user: User = Depends(get_current_user), db: Session = Depends(get_database)):
    artifact = get_accessible_artifact(db, brand_id, artifact_id, current_user)
    try:
        return to_response(apply_artifact(db, artifact, current_user.id))
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


@router.post("/api/brands/{brand_id}/artifacts/{artifact_id}/reject", response_model=ArtifactResponse)
def reject_artifact_endpoint(brand_id: str, artifact_id: str, current_user: User = Depends(get_current_user), db: Session = Depends(get_database)):
    return set_artifact_status(brand_id, artifact_id, "rejected", current_user, db)