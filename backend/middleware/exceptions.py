"""
全局异常定义
"""

from typing import Any, Dict, Optional


class AppError(Exception):
    """应用异常基类"""

    def __init__(
        self,
        code: str,
        message: str,
        status_code: int = 500,
        detail: Optional[Dict[str, Any]] = None,
    ):
        self.code = code
        self.message = message
        self.status_code = status_code
        self.detail = detail or {}
        super().__init__(self.message)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "code": self.code,
            "message": self.message,
            "detail": self.detail,
        }


class UnauthorizedError(AppError):
    def __init__(self, message="未认证，请先登录"):
        super().__init__(code="UNAUTHORIZED", message=message, status_code=401)


class ForbiddenError(AppError):
    def __init__(self, message="无权限执行此操作"):
        super().__init__(code="FORBIDDEN", message=message, status_code=403)


class QuotaExceededError(AppError):
    def __init__(self, plan: str = "free", limit: int = 3):
        super().__init__(
            code="QUOTA_EXCEEDED",
            message=f"月度使用次数已用完（{plan} 版上限 {limit} 次）",
            status_code=429,
            detail={"plan": plan, "limit": limit},
        )


class ValidationError(AppError):
    def __init__(self, message="参数校验失败", detail: Optional[dict] = None):
        super().__init__(code="VALIDATION_ERROR", message=message, status_code=422, detail=detail)
