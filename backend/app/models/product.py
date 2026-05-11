from datetime import datetime
from typing import List, Optional

from sqlalchemy import BigInteger, String, Integer, DateTime, JSON, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class Product(Base):
    __tablename__ = "category"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    code: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    score_per_key: Mapped[int] = mapped_column(Integer, nullable=False)
    score_label: Mapped[str] = mapped_column(String(50), nullable=False, default="积分")
    max_activations: Mapped[int] = mapped_column(Integer, nullable=False, default=1)
    expiry_days: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    api_key: Mapped[str] = mapped_column(String(80), unique=True, nullable=False)
    card_types: Mapped[Optional[List]] = mapped_column(JSON, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, server_default=func.now(), onupdate=func.now()
    )

    redemption_codes = relationship("RedemptionCode", back_populates="product")
