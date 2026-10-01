from datetime import datetime, timezone
from uuid import uuid4

from sqlalchemy import Boolean, DateTime, ForeignKey, JSON, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class ResearchFinding(Base):
	__tablename__ = "research_findings"

	id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid4()))
	report_id: Mapped[str] = mapped_column(String(36), ForeignKey("research_reports.id", ondelete="CASCADE"), index=True, nullable=False)
	statement: Mapped[str] = mapped_column(Text, nullable=False)
	evidence: Mapped[str] = mapped_column(Text, nullable=False)
	source_ids: Mapped[list] = mapped_column(JSON, nullable=False, default=list)
	confidence: Mapped[str] = mapped_column(String(30), nullable=False, default="insufficient_evidence")
	suggested_fields: Mapped[list] = mapped_column(JSON, nullable=False, default=list)
	applied: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
	created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)
