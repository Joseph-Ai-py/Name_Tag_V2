from datetime import datetime, timezone
from uuid import uuid4

from sqlalchemy import DateTime, ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class ResearchEvent(Base):
	__tablename__ = "research_events"

	id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid4()))
	job_id: Mapped[str] = mapped_column(String(36), ForeignKey("research_jobs.id", ondelete="CASCADE"), index=True, nullable=False)
	type: Mapped[str] = mapped_column(String(50), nullable=False)
	stage: Mapped[str] = mapped_column(String(50), nullable=False)
	message: Mapped[str] = mapped_column(Text, nullable=False)
	created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)
