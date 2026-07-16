"""
统一响应包装器 — 所有 API 响应遵循 {success, data?, error?, meta?} 格式
"""

from typing import Any, Optional
from pydantic import BaseModel, Field


class ApiResponse(BaseModel):
    """统一 API 响应"""
    success: bool = Field(..., description="是否成功")
    data: Optional[Any] = Field(None, description="响应数据")
    error: Optional[str] = Field(None, description="错误信息")
    meta: Optional[dict] = Field(None, description="元信息（如速率限制剩余次数）")

    @staticmethod
    def ok(data: Any = None, meta: Optional[dict] = None) -> dict:
        return ApiResponse(success=True, data=data, meta=meta).model_dump(exclude_none=True)

    @staticmethod
    def fail(error: str, meta: Optional[dict] = None, status_code: int = 400) -> dict:
        return ApiResponse(success=False, error=error, meta=meta).model_dump(exclude_none=True)