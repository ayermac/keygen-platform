from __future__ import annotations

from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field, field_validator


class RedeemRequest(BaseModel):
    code: str
    metadata: dict[str, Any] | None = None


class RedeemResponse(BaseModel):
    code: str
    credit_unit: str
    total_credits: int
    remaining_credits: int
    expires_at: datetime | None


class ConsumeRequest(BaseModel):
    code: str
    amount: int = Field(gt=0, description="消耗数量，必须大于 0")
    metadata: dict[str, Any] | None = None
    request_id: str | None = Field(default=None, max_length=128, description="幂等请求 ID，相同 ID 只扣减一次")

    @field_validator("request_id")
    @classmethod
    def strip_request_id(cls, v: str | None) -> str | None:
        if v is not None:
            v = v.strip()
            return v if v else None
        return v


class ConsumeResponse(BaseModel):
    remaining_credits: int


class BalanceRequest(BaseModel):
    code: str
    metadata: dict[str, Any] | None = None


class BalanceResponse(BaseModel):
    code: str
    credit_unit: str
    total_credits: int
    remaining_credits: int
    status: str
    expires_at: datetime | None


class CodeGenerateRequest(BaseModel):
    product_id: int
    count: int
    batch_id: str | None = None
    card_type: str | None = None


class CodeGenerateResponse(BaseModel):
    batch_id: str
    count: int
    codes: list[str]


class CodeSearchRequest(BaseModel):
    product_id: int | None = None
    status: str | None = None
    batch_id: str | None = None
    code: str | None = None
    page: int = 1
    page_size: int = 20


class CodeItem(BaseModel):
    id: int
    code: str
    product_name: str
    status: str
    total_credits: int
    remaining_credits: int
    batch_id: str | None
    activated_at: datetime | None
    expires_at: datetime | None
    created_at: datetime


class CodeSearchResponse(BaseModel):
    total: int
    page: int
    page_size: int
    items: list[CodeItem]


class UsageLogSearchRequest(BaseModel):
    code: str | None = None
    product_id: int | None = None
    action: str | None = None
    start_time: datetime | None = None
    end_time: datetime | None = None
    page: int = 1
    page_size: int = 20


class UsageLogItem(BaseModel):
    id: int
    code: str
    product_name: str
    action: str
    amount: int
    remaining_after: int
    metadata: dict[str, Any] | None
    client_ip: str | None
    request_id: str | None = None
    created_at: datetime


class UsageLogSearchResponse(BaseModel):
    total: int
    page: int
    page_size: int
    items: list[UsageLogItem]
