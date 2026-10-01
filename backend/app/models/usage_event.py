from datetime import datetime, timezone
from uuid import uuid4

from sqlalchemy import DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class UsageEvent(Base):
	__tablename__ = "usage_events"

	id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid4()))
	user_id: Mapped[str] = mapped_column(String(36), ForeignKey("users.id", ondelete="CASCADE"), index=True, nullable=False)
	brand_id: Mapped[str] = mapped_column(String(36), ForeignKey("brands.id", ondelete="CASCADE"), index=True, nullable=False)
	feature: Mapped[str] = mapped_column(String(50), nullable=False)
	model: Mapped[str] = mapped_column(String(100), nullable=False)
	request_id: Mapped[str] = mapped_column(String(36), unique=True, nullable=False)
	input_tokens: Mapped[int | None] = mapped_column(Integer, nullable=True)
	output_tokens: Mapped[int | None] = mapped_column(Integer, nullable=True)
	duration_ms: Mapped[int | None] = mapped_column(Integer, nullable=True)
	status: Mapped[str] = mapped_column(String(20), nullable=False)
	created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)
