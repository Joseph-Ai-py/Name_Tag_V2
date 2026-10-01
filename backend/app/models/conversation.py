from datetime import datetime, timezone
from uuid import uuid4

from sqlalchemy import DateTime, ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class Conversation(Base):
	__tablename__ = "conversations"

	id: Mapped[str] = mapped_column(
		String(36),
		primary_key=True,
		default=lambda: str(uuid4()),
	)

	brand_id: Mapped[str] = mapped_column(
		String(36),
		ForeignKey("brands.id", ondelete="CASCADE"),
		index=True,
		nullable=False,
	)

	created_by: Mapped[str] = mapped_column(
		String(36),
		ForeignKey("users.id", ondelete="CASCADE"),
		index=True,
		nullable=False,
	)

	title: Mapped[str | None] = mapped_column(
		Text,
		nullable=True,
	)

	created_at: Mapped[datetime] = mapped_column(
		DateTime(timezone=True),
		default=lambda: datetime.now(timezone.utc),
		nullable=False,
	)

	updated_at: Mapped[datetime] = mapped_column(
		DateTime(timezone=True),
		default=lambda: datetime.now(timezone.utc),
		onupdate=lambda: datetime.now(timezone.utc),
		nullable=False,
	)
