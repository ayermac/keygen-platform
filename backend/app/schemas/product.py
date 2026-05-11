from __future__ import annotations

from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict


class CardType(BaseModel):
    name: str
    total_score: int
    expiry_days: int | None = None


class ProductCreate(BaseModel):
    name: str
    code: str
    default_credits: int
    credit_unit: str = "积分"
    max_activations: int = 1
    expiry_days: int | None = None
    card_types: list[CardType] | None = None


class ProductUpdate(BaseModel):
    name: str | None = None
    default_credits: int | None = None
    credit_unit: str | None = None
    max_activations: int | None = None
    expiry_days: int | None = None
    card_types: list[CardType] | None = None


class ProductItem(BaseModel):
    id: int
    name: str
    code: str
    default_credits: int
    credit_unit: str
    max_activations: int
    expiry_days: int | None
    api_key: str
    card_types: list[dict[str, Any]] | None = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class ProductListResponse(BaseModel):
    items: list[ProductItem]
