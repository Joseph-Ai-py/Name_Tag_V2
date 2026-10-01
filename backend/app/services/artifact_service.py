from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.artifact import Artifact


def create_artifact(db: Session, brand_id: str, user_id: str, artifact_type: str, title: str, content: dict) -> Artifact:
	artifact = Artifact(brand_id=brand_id, created_by=user_id, type=artifact_type.strip(), title=title.strip(), content=content, status="draft")
	db.add(artifact)
	db.commit()
	db.refresh(artifact)
	return artifact


def get_artifact(db: Session, brand_id: str, artifact_id: str) -> Artifact | None:
	result = db.execute(select(Artifact).where(Artifact.id == artifact_id, Artifact.brand_id == brand_id))
	return result.scalar_one_or_none()


def get_brand_artifacts(db: Session, brand_id: str) -> list[Artifact]:
	result = db.execute(select(Artifact).where(Artifact.brand_id == brand_id).order_by(Artifact.created_at.desc()))
	return list(result.scalars().all())


def change_artifact_status(db: Session, artifact: Artifact, status: str) -> Artifact:
	artifact.status = status
	db.commit()
	db.refresh(artifact)
	return artifact
