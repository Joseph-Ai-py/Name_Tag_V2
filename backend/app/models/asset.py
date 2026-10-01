from datetime import datetime, timezone
from uuid import uuid4

from sqlalchemy import DateTime, ForeignKey, JSON, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class Asset(Base):
	__tablename__ = "assets"

	id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid4()))
	brand_id: Mapped[str] = mapped_column(String(36), ForeignKey("brands.id", ondelete="CASCADE"), index=True, nullable=False)
	created_by: Mapped[str] = mapped_column(String(36), ForeignKey("users.id", ondelete="CASCADE"), index=True, nullable=False)
	type: Mapped[str] = mapped_column(String(50), nullable=False)
	filename: Mapped[str] = mapped_column(String(300), nullable=False)
	mime_type: Mapped[str] = mapped_column(String(100), nullable=False)
	storage_path: Mapped[str] = mapped_column(Text, nullable=False)
	metadata_json: Mapped[dict] = mapped_column("metadata", JSON, nullable=False, default=dict)
	created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)
