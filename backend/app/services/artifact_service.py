from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.artifact import Artifact
from app.services.mutation_service import ALLOWED_PATHS
from app.services.proposal_service import apply_proposal, create_proposal


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


def artifact_brand_changes(artifact: Artifact) -> dict[str, object]:
	changes: dict[str, object] = {}
	content = artifact.content
	for section in ("business", "market", "customer", "brand", "visual"):
		section_values = content.get(section)
		if isinstance(section_values, dict):
			for field, value in section_values.items():
				if f"{section}.{field}" in ALLOWED_PATHS:
					changes[f"{section}.{field}"] = value

	section_by_type = {
		"brand_strategy": "brand",
		"brand_identity": "brand",
		"business_discovery": "business",
		"customer_analysis": "customer",
		"visual_direction": "visual",
	}
	section = section_by_type.get(artifact.type)
	if section:
		for field, value in content.items():
			if f"{section}.{field}" in ALLOWED_PATHS:
				changes[f"{section}.{field}"] = value
	return changes


def apply_artifact(db: Session, artifact: Artifact, user_id: str) -> Artifact:
	if artifact.status not in {"draft", "approved"}:
		raise ValueError("Only draft or approved artifacts can be applied")
	changes = artifact_brand_changes(artifact)
	if not changes:
		raise ValueError("Artifact does not contain applicable BrandState changes")
	proposal = create_proposal(
		db=db,
		brand_id=artifact.brand_id,
		user_id=user_id,
		title=artifact.title,
		summary=f"Artifact {artifact.id} approved for BrandState application",
		changes=changes,
	)
	proposal.status = "approved"
	db.commit()
	apply_proposal(db, proposal, user_id)
	artifact.status = "applied"
	db.commit()
	db.refresh(artifact)
	return artifact
