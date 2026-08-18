"""
Admin routes — user management, plan management.
"""

from fastapi import APIRouter, Depends, Query
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from auth.deps import require_admin
from database.engine import get_db
from models.user import User

router = APIRouter(prefix="/api/admin", tags=["admin"])


@router.get("/users")
async def list_users(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    _admin: dict = Depends(require_admin),
):
    """List all users (admin only)."""
    offset = (page - 1) * page_size
    result = await db.execute(select(User).offset(offset).limit(page_size))
    users = result.scalars().all()
    total_result = await db.execute(select(User))
    total = len(total_result.scalars().all())

    return {
        "success": True,
        "data": {
            "items": [u.to_dict() for u in users],
            "total": total,
            "page": page,
            "page_size": page_size,
        },
        "error": None,
        "meta": {},
    }


@router.put("/users/{user_id}/plan")
async def update_user_plan(
    user_id: str,
    plan: str,
    db: AsyncSession = Depends(get_db),
    _admin: dict = Depends(require_admin),
):
    """Update user's plan (admin only)."""
    if plan not in ("free", "pro", "enterprise"):
        return {"success": False, "data": None, "error": {"code": "VALIDATION_ERROR", "message": "无效的套餐类型"}, "meta": {}}

    await db.execute(
        update(User).where(User.id == user_id).values(plan=plan)
    )

    return {"success": True, "data": {"user_id": user_id, "plan": plan}, "error": None, "meta": {}}