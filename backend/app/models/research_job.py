from datetime import datetime, timezone
from uuid import uuid4

from sqlalchemy import DateTime, ForeignKey, JSON, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class ResearchJob(Base):
	__tablename__ = "research_jobs"

	id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid4()))
	brand_id: Mapped[str] = mapped_column(String(36), ForeignKey("brands.id", ondelete="CASCADE"), index=True, nullable=False)
	created_by: Mapped[str] = mapped_column(String(36), ForeignKey("users.id", ondelete="CASCADE"), index=True, nullable=False)
	mode: Mapped[str] = mapped_column(String(20), nullable=False, default="quick")
	status: Mapped[str] = mapped_column(String(20), nullable=False, default="planning")
	query: Mapped[str] = mapped_column(Text, nullable=False)
	plan: Mapped[dict] = mapped_column(JSON, nullable=False, default=dict)
	progress: Mapped[dict] = mapped_column(JSON, nullable=False, default=dict)
	created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)
	updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc), nullable=False)
