from typing import Any

from pydantic import BaseModel


class ApiResponse(BaseModel):
    code: int = 0
    message: str = "success"
    data: Any = None


def success(data: Any = None) -> dict:
    return ApiResponse(code=0, message="success", data=data).model_dump()


def error(code: int, message: str) -> dict:
    return ApiResponse(code=code, message=message, data=None).model_dump()
