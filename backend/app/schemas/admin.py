from pydantic import BaseModel


class LoginRequest(BaseModel):
    username: str
    password: str


class LoginResponse(BaseModel):
    token: str


class AuditLogItem(BaseModel):
    id: int
    admin_username: str
    action: str
    target_type: str
    target_id: int | None
    detail: dict | None
    created_at: str


class AuditLogListResponse(BaseModel):
    total: int
    page: int
    page_size: int
    items: list[AuditLogItem]


class StatsOverview(BaseModel):
    total_keys: int
    activated_keys: int
    total_score_consumed: int
    today_activations: int


class CategoryStats(BaseModel):
    category_id: int
    category_name: str
    total_keys: int
    activated_keys: int
    total_score: int
    consumed_score: int
    activation_trend: list[dict]
