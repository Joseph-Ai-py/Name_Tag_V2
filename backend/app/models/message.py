from datetime import datetime, timezone
from uuid import uuid4

from sqlalchemy import DateTime, ForeignKey, JSON, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class Message(Base):
	__tablename__ = "messages"

	id: Mapped[str] = mapped_column(
		String(36),
		primary_key=True,
		default=lambda: str(uuid4()),
	)

	conversation_id: Mapped[str] = mapped_column(
		String(36),
		ForeignKey("conversations.id", ondelete="CASCADE"),
		index=True,
		nullable=False,
	)

	role: Mapped[str] = mapped_column(
		String(20),
		nullable=False,
	)

	content: Mapped[str] = mapped_column(
		Text,
		nullable=False,
	)

	artifact: Mapped[dict | None] = mapped_column(
		JSON,
		nullable=True,
	)

	created_at: Mapped[datetime] = mapped_column(
		DateTime(timezone=True),
		default=lambda: datetime.now(timezone.utc),
		nullable=False,
	)
