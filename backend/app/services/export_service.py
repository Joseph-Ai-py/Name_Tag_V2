from datetime import datetime, timezone
from typing import Any

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.artifact import Artifact
from app.models.asset import Asset
from app.models.brand import Brand
from app.models.research_report import ResearchReport
from app.services.brand_state_service import get_brand_state


def build_json_export(db: Session, brand: Brand) -> dict[str, Any]:
    brand_state = get_brand_state(db, brand.id)
    artifacts = db.scalars(select(Artifact).where(Artifact.brand_id == brand.id).order_by(Artifact.created_at)).all()
    assets = db.scalars(select(Asset).where(Asset.brand_id == brand.id).order_by(Asset.created_at)).all()
    research = db.scalars(select(ResearchReport).where(ResearchReport.brand_id == brand.id).order_by(ResearchReport.created_at)).all()

    return {
        "format": "json",
        "exported_at": datetime.now(timezone.utc),
        "brand": {
            "id": brand.id,
            "name": brand.name,
            "description": brand.description,
            "created_at": brand.created_at,
            "updated_at": brand.updated_at,
        },
        "brand_state": {
            "state": brand_state.state if brand_state else {},
            "version": brand_state.version if brand_state else None,
        },
        "artifacts": [
            {"id": item.id, "type": item.type, "title": item.title, "content": item.content, "status": item.status}
            for item in artifacts
        ],
        "assets": [
            {"id": item.id, "type": item.type, "filename": item.filename, "mime_type": item.mime_type, "storage_path": item.storage_path, "metadata": item.metadata_json}
            for item in assets
        ],
        "research": [
            {"id": item.id, "title": item.title, "executive_summary": item.executive_summary, "sections": item.sections, "status": item.status}
            for item in research
        ],
    }