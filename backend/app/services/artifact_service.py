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
	field_aliases = {
		("customer", "target_segment"): "customer.target",
		("customer", "target"): "customer.target",
		("customer", "persona"): "customer.persona",
		("customer", "needs"): "customer.needs",
		("customer", "pain_points"): "customer.pain_points",
		("customer", "jtbd"): "customer.jtbd",
		("brand", "positioning"): "brand.positioning",
		("brand", "key_message"): "brand.key_message",
		("brand", "core_value"): "brand.values",
		("brand", "value_proposition"): "brand.key_message",
		("brand", "brand_essence"): "brand.positioning",
		("brand", "key_elements"): "brand.story",
		("brand", "target_slogan"): "brand.tagline",
	}
	brand_aliases = {
		"core_value": "brand.values",
		"value_proposition": "brand.key_message",
		"brand_essence": "brand.positioning",
		"key_elements": "brand.story",
		"target_slogan": "brand.tagline",
	}
	for section in ("business", "market", "customer", "brand", "visual"):
		section_values = content.get(section)
		if isinstance(section_values, dict):
			for field, value in section_values.items():
				candidate = field_aliases.get((section, field), f"{section}.{field}")
				if candidate in ALLOWED_PATHS:
					changes[candidate] = value

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
			normalized_field = str(field).strip().lower().replace(" ", "_")
			candidate = brand_aliases.get(normalized_field) if section == "brand" else None
			candidate = candidate or field_aliases.get((section, field), f"{section}.{field}")
			if candidate in ALLOWED_PATHS:
				changes[candidate] = value
	for nested in content.values():
		if not isinstance(nested, dict):
			continue
		for field, value in nested.items():
			normalized_field = str(field).strip().lower().replace(" ", "_")
			candidate = brand_aliases.get(normalized_field)
			if candidate is None:
				for section_name in ("business", "market", "customer", "brand", "visual"):
					candidate = field_aliases.get((section_name, normalized_field))
					if candidate:
						break
			if candidate in ALLOWED_PATHS:
				changes[candidate] = value
	if artifact.type == "brand_identity":
		for nested in content.values():
			if not isinstance(nested, dict):
				continue
			for field, value in nested.items():
				candidate = brand_aliases.get(str(field).strip().lower().replace(" ", "_"))
				if candidate in ALLOWED_PATHS:
					changes[candidate] = value
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
