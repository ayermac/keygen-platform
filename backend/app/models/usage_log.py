from datetime import datetime
from typing import Optional

from sqlalchemy import BigInteger, String, Integer, DateTime, Enum, JSON, ForeignKey, UniqueConstraint, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class UsageLog(Base):
    __tablename__ = "activation_log"
    __table_args__ = (
        UniqueConstraint("category_id", "key_id", "action", "request_id", name="uq_log_idempotency"),
    )

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    key_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("activation_key.id"), nullable=False)
    category_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("category.id"), nullable=False)
    action: Mapped[str] = mapped_column(
        Enum("activate", "deduct", name="log_action"), nullable=False
    )
    amount: Mapped[int] = mapped_column(Integer, nullable=False)
    remaining_after: Mapped[int] = mapped_column(Integer, nullable=False)
    metadata_: Mapped[Optional[dict]] = mapped_column("metadata", JSON, nullable=True)
    client_ip: Mapped[Optional[str]] = mapped_column(String(45), nullable=True)
    request_id: Mapped[Optional[str]] = mapped_column(String(128), nullable=True, index=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, server_default=func.now()
    )

    redemption_code = relationship("RedemptionCode", back_populates="logs")
