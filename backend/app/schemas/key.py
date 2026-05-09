from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field


class ActivateRequest(BaseModel):
    key_code: str
    metadata: dict[str, Any] | None = None


class ActivateResponse(BaseModel):
    key_code: str
    score_label: str
    total_score: int
    remaining_score: int
    expires_at: datetime | None


class DeductRequest(BaseModel):
    key_code: str
    amount: int = Field(gt=0, description="扣减数量，必须大于 0")
    metadata: dict[str, Any] | None = None


class DeductResponse(BaseModel):
    remaining_score: int


class BalanceRequest(BaseModel):
    key_code: str
    metadata: dict[str, Any] | None = None


class BalanceResponse(BaseModel):
    key_code: str
    score_label: str
    total_score: int
    remaining_score: int
    status: str
    expires_at: datetime | None


class KeyGenerateRequest(BaseModel):
    category_id: int
    count: int
    batch_id: str | None = None


class KeyGenerateResponse(BaseModel):
    batch_id: str
    count: int
    keys: list[str]


class KeySearchRequest(BaseModel):
    category_id: int | None = None
    status: str | None = None
    batch_id: str | None = None
    key_code: str | None = None
    page: int = 1
    page_size: int = 20


class KeyItem(BaseModel):
    id: int
    key_code: str
    category_name: str
    status: str
    total_score: int
    remaining_score: int
    batch_id: str | None
    activated_at: datetime | None
    expires_at: datetime | None
    created_at: datetime


class KeySearchResponse(BaseModel):
    total: int
    page: int
    page_size: int
    items: list[KeyItem]


class UsageLogSearchRequest(BaseModel):
    key_code: str | None = None
    category_id: int | None = None
    action: str | None = None
    start_time: datetime | None = None
    end_time: datetime | None = None
    page: int = 1
    page_size: int = 20


class UsageLogItem(BaseModel):
    id: int
    key_code: str
    category_name: str
    action: str
    amount: int
    remaining_after: int
    metadata: dict[str, Any] | None
    client_ip: str | None
    created_at: datetime


class UsageLogSearchResponse(BaseModel):
    total: int
    page: int
    page_size: int
    items: list[UsageLogItem]
