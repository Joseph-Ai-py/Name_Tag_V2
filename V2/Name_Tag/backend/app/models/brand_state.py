from datetime import datetime, timezone
from uuid import uuid4

from sqlalchemy import DateTime, ForeignKey, JSON, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class BrandState(Base):
    __tablename__ = "brand_states"

    __table_args__ = (
        UniqueConstraint(
            "brand_id",
            name="uq_brand_states_brand",
        ),
    )

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

    state: Mapped[dict] = mapped_column(
        JSON,
        nullable=False,
    )

    version: Mapped[int] = mapped_column(
        default=1,
        nullable=False,
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