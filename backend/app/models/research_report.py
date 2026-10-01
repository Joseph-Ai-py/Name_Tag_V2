from datetime import datetime, timezone
from uuid import uuid4

from sqlalchemy import DateTime, ForeignKey, JSON, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class ResearchReport(Base):
	__tablename__ = "research_reports"

	id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid4()))
	research_job_id: Mapped[str] = mapped_column(String(36), ForeignKey("research_jobs.id", ondelete="CASCADE"), index=True, nullable=False)
	brand_id: Mapped[str] = mapped_column(String(36), ForeignKey("brands.id", ondelete="CASCADE"), index=True, nullable=False)
	title: Mapped[str] = mapped_column(String(300), nullable=False)
	executive_summary: Mapped[str] = mapped_column(Text, nullable=False)
	sections: Mapped[list] = mapped_column(JSON, nullable=False, default=list)
	status: Mapped[str] = mapped_column(String(20), nullable=False, default="completed")
	created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)
	updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc), nullable=False)
