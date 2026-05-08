from datetime import datetime

from sqlalchemy import BigInteger, String, Integer, DateTime, Enum, JSON, ForeignKey, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class ActivationLog(Base):
    __tablename__ = "activation_log"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    key_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("activation_key.id"), nullable=False)
    category_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("category.id"), nullable=False)
    action: Mapped[str] = mapped_column(
        Enum("activate", "deduct", name="log_action"), nullable=False
    )
    amount: Mapped[int] = mapped_column(Integer, nullable=False)
    remaining_after: Mapped[int] = mapped_column(Integer, nullable=False)
    metadata_: Mapped[dict | None] = mapped_column("metadata", JSON, nullable=True)
    client_ip: Mapped[str | None] = mapped_column(String(45), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, server_default=func.now()
    )

    activation_key = relationship("ActivationKey", back_populates="logs")
