from datetime import datetime

from sqlalchemy import BigInteger, String, Integer, DateTime, Enum, JSON, ForeignKey, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class ActivationKey(Base):
    __tablename__ = "activation_key"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    key_code: Mapped[str] = mapped_column(String(19), unique=True, nullable=False)
    category_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("category.id"), nullable=False)
    status: Mapped[str] = mapped_column(
        Enum("unused", "activated", "expired", "disabled", name="key_status"),
        nullable=False,
        default="unused",
    )
    batch_id: Mapped[str | None] = mapped_column(String(50), nullable=True)
    total_score: Mapped[int] = mapped_column(Integer, nullable=False)
    remaining_score: Mapped[int] = mapped_column(Integer, nullable=False)
    activated_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    expires_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, server_default=func.now()
    )
    metadata_: Mapped[dict | None] = mapped_column("metadata", JSON, nullable=True)

    category = relationship("Category", back_populates="activation_keys")
    logs = relationship("ActivationLog", back_populates="activation_key")
