from datetime import datetime, timezone
from uuid import uuid4

from sqlalchemy import DateTime, ForeignKey, JSON, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class ResearchSource(Base):
	__tablename__ = "research_sources"

	id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid4()))
	report_id: Mapped[str] = mapped_column(String(36), ForeignKey("research_reports.id", ondelete="CASCADE"), index=True, nullable=False)
	url: Mapped[str] = mapped_column(Text, nullable=False)
	title: Mapped[str] = mapped_column(String(300), nullable=False)
	publisher: Mapped[str | None] = mapped_column(String(200), nullable=True)
	summary: Mapped[str | None] = mapped_column(Text, nullable=True)
	source_type: Mapped[str] = mapped_column(String(30), nullable=False, default="unknown")
	accessed_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)
