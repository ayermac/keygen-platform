from datetime import datetime

from pydantic import BaseModel


class CategoryCreate(BaseModel):
    name: str
    code: str
    score_per_key: int
    score_label: str = "积分"
    max_activations: int = 1
    expiry_days: int | None = None


class CategoryUpdate(BaseModel):
    name: str | None = None
    score_per_key: int | None = None
    score_label: str | None = None
    max_activations: int | None = None
    expiry_days: int | None = None


class CategoryItem(BaseModel):
    id: int
    name: str
    code: str
    score_per_key: int
    score_label: str
    max_activations: int
    expiry_days: int | None
    api_key: str
    created_at: datetime

    class Config:
        from_attributes = True


class CategoryListResponse(BaseModel):
    items: list[CategoryItem]
