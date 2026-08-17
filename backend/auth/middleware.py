"""
Auth middleware — FastAPI dependency injection for current user.
"""

from typing import Any, Dict, Optional

from fastapi import Depends, HTTPException, Request, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.ext.asyncio import AsyncSession

from auth.jwt import verify_token, get_token_from_header
from database.engine import get_db, get_user_by_id
from middleware.exceptions import UnauthorizedError, ForbiddenError, QuotaExceededError

security = HTTPBearer(auto_error=False)


async def get_current_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security),
) -> Optional[Dict[str, Any]]:
    """
    Get current user from JWT token.

    Returns:
        User dict if authenticated, None if anonymous
    """
    if credentials is None:
        return None

    payload = verify_token(credentials.credentials)
    if payload is None:
        raise UnauthorizedError("令牌无效或已过期")

    return payload


async def require_user(
    current_user: Optional[Dict[str, Any]] = Depends(get_current_user),
) -> Dict[str, Any]:
    """
    Require authenticated user.

    Raises:
        UnauthorizedError: If not authenticated
    """
    if current_user is None:
        raise UnauthorizedError("请先登录")
    return current_user


def require_plan(min_plan: str = "pro"):
    """
    Require user to have a minimum plan level.

    Args:
        min_plan: Minimum plan required ("free", "pro", "enterprise")

    Usage:
        @app.get("/api/pro-only")
        async def pro_endpoint(user=Depends(require_plan("pro"))):
            ...
    """
    async def _check_plan(
        current_user: Dict[str, Any] = Depends(require_user),
    ) -> Dict[str, Any]:
        plan_rank = {"free": 0, "pro": 1, "enterprise": 2}
        required_rank = plan_rank.get(min_plan, 0)
        user_rank = plan_rank.get(current_user.get("plan", "free"), 0)
        if user_rank < required_rank:
            raise ForbiddenError(f"需要 {min_plan} 版以上套餐")
        return current_user

    return _check_plan


async def check_usage_limit(
    current_user: Dict[str, Any] = Depends(require_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Require an authenticated user and enforce their plan's usage quota.

    JWT 里的 plan/usage_count 在签发后就过时了，这里以 DB 为准读取实时值，
    超额则抛 QuotaExceededError。返回最新的 User 对象，供路由在成功后调用
    increment_usage。
    """
    from config import settings

    user = await get_user_by_id(db, current_user["sub"])
    if user is None:
        raise UnauthorizedError("用户不存在")
    if not user.is_active:
        raise UnauthorizedError("账户已被禁用")

    usage_limit = (
        settings.FREE_USAGE_LIMIT if user.plan == "free"
        else settings.PRO_USAGE_LIMIT if user.plan == "pro"
        else 999999
    )
    if user.usage_count >= usage_limit:
        raise QuotaExceededError(plan=user.plan, limit=usage_limit)
    return user


async def require_admin(
    current_user: Dict[str, Any] = Depends(require_user),
    db: AsyncSession = Depends(get_db),
) -> Dict[str, Any]:
    """
    要求管理员权限。登录 token 从不带 is_admin，因此以 DB 中的字段为准，
    避免"JWT 里没有该字段 → 永远 403"或"可被伪造"两个极端。
    """
    user = await get_user_by_id(db, current_user["sub"])
    if user is None or not user.is_admin:
        raise ForbiddenError("需要管理员权限")
    return current_user