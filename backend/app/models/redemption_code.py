from datetime import datetime
from typing import Optional

from sqlalchemy import BigInteger, String, Integer, DateTime, Enum, JSON, ForeignKey, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class RedemptionCode(Base):
    __tablename__ = "activation_key"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    key_code: Mapped[str] = mapped_column(String(19), unique=True, nullable=False)
    category_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("category.id"), nullable=False)
    status: Mapped[str] = mapped_column(
        Enum("unused", "activated", "expired", "disabled", name="key_status"),
        nullable=False,
        default="unused",
    )
    batch_id: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    card_type_name: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    total_score: Mapped[int] = mapped_column(Integer, nullable=False)
    remaining_score: Mapped[int] = mapped_column(Integer, nullable=False)
    expiry_days: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    activated_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    expires_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, server_default=func.now()
    )
    metadata_: Mapped[Optional[dict]] = mapped_column("metadata", JSON, nullable=True)

    product = relationship("Product", back_populates="redemption_codes")
    logs = relationship("UsageLog", back_populates="redemption_code")
