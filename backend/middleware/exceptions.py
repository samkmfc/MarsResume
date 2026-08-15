"""
全局异常定义 — 所有模块必须使用此处的异常类
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


# ── 认证异常 ──

class UnauthorizedError(AppError):
    def __init__(self, message="未认证，请先登录"):
        super().__init__(code="UNAUTHORIZED", message=message, status_code=401)


class ForbiddenError(AppError):
    def __init__(self, message="无权限执行此操作"):
        super().__init__(code="FORBIDDEN", message=message, status_code=403)


# ── 限流异常 ──

class RateLimitedError(AppError):
    def __init__(self, retry_after: int = 30, limit: int = 15, window: int = 60):
        super().__init__(
            code="RATE_LIMITED",
            message=f"请求过于频繁，请在 {retry_after} 秒后重试",
            status_code=429,
            detail={"retry_after": retry_after, "limit": limit, "window": window},
        )


class QuotaExceededError(AppError):
    def __init__(self, plan: str = "free", limit: int = 3):
        super().__init__(
            code="QUOTA_EXCEEDED",
            message=f"月度使用次数已用完（{plan} 版上限 {limit} 次）",
            status_code=429,
            detail={"plan": plan, "limit": limit},
        )


# ── 参数异常 ──

class ValidationError(AppError):
    def __init__(self, message="参数校验失败", detail: Optional[dict] = None):
        super().__init__(code="VALIDATION_ERROR", message=message, status_code=422, detail=detail)


class FileTooLargeError(AppError):
    def __init__(self, max_size_mb: int = 10):
        super().__init__(
            code="FILE_TOO_LARGE",
            message=f"文件过大，最大支持 {max_size_mb}MB",
            status_code=413,
            detail={"max_size_mb": max_size_mb},
        )


class UnsupportedFormatError(AppError):
    def __init__(self, ext: str, allowed: list = None):
        super().__init__(
            code="UNSUPPORTED_FORMAT",
            message=f"不支持的文件格式: {ext}",
            status_code=400,
            detail={"ext": ext, "allowed_formats": allowed or []},
        )


# ── 业务异常 ──

class ResourceNotFoundError(AppError):
    def __init__(self, resource: str, resource_id: str):
        super().__init__(
            code="NOT_FOUND",
            message=f"{resource} 不存在: {resource_id}",
            status_code=404,
            detail={"resource": resource, "id": resource_id},
        )


class InjectionDetectedError(AppError):
    def __init__(self):
        super().__init__(
            code="INJECTION_DETECTED",
            message="检测到潜在的注入攻击，请求已被拦截",
            status_code=400,
        )


# ── 服务异常 ──

class LLMError(AppError):
    def __init__(self, message="LLM 调用失败", detail: Optional[dict] = None):
        super().__init__(code="LLM_ERROR", message=message, status_code=502, detail=detail)


class RAGError(AppError):
    def __init__(self, message="RAG 服务异常", detail: Optional[dict] = None):
        super().__init__(code="RAG_ERROR", message=message, status_code=500, detail=detail)


class InternalError(AppError):
    def __init__(self, message="内部服务器错误"):
        super().__init__(code="INTERNAL_ERROR", message=message, status_code=500)