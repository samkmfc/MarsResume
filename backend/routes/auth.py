"""
Authentication routes — register, login, profile.
"""

from fastapi import APIRouter, Depends
from pydantic import BaseModel, EmailStr, Field
from sqlalchemy.ext.asyncio import AsyncSession
import bcrypt

from auth.jwt import create_access_token
from auth.middleware import get_current_user
from database.engine import get_db, get_user_by_email, get_user_by_id, create_user, increment_usage
from middleware.exceptions import UnauthorizedError, ValidationError

router = APIRouter(prefix="/api/auth", tags=["auth"])


class RegisterRequest(BaseModel):
    email: str = Field(..., max_length=255)
    username: str = Field(..., min_length=1, max_length=100)
    password: str = Field(..., min_length=6, max_length=128)


class LoginRequest(BaseModel):
    email: str = Field(..., max_length=255)
    password: str = Field(..., max_length=128)


@router.post("/register")
async def register(req: RegisterRequest, db: AsyncSession = Depends(get_db)):
    """Register a new user."""
    existing = await get_user_by_email(db, req.email)
    if existing:
        raise ValidationError("该邮箱已被注册")

    hashed = bcrypt.hashpw(req.password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")
    user = await create_user(db, req.email, req.username, hashed)

    return {
        "success": True,
        "data": {
            "id": user.id,
            "email": user.email,
            "username": user.username,
            "plan": user.plan,
        },
        "error": None,
        "meta": {},
    }


@router.post("/login")
async def login(req: LoginRequest, db: AsyncSession = Depends(get_db)):
    """Login and return JWT token."""
    user = await get_user_by_email(db, req.email)
    if not user or not bcrypt.checkpw(req.password.encode("utf-8"), user.hashed_password.encode("utf-8")):
        raise UnauthorizedError("邮箱或密码错误")

    access_token = create_access_token(
        data={
            "sub": user.id,
            "email": user.email,
            "username": user.username,
            "plan": user.plan,
        }
    )

    return {
        "success": True,
        "data": {
            "access_token": access_token,
            "token_type": "bearer",
            "expires_in": 86400,
            "user": user.to_dict(),
        },
        "error": None,
        "meta": {},
    }


@router.get("/me")
async def get_me(
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get current user profile."""
    if not current_user:
        return {"success": True, "data": None, "error": None, "meta": {}}

    user = await get_user_by_id(db, current_user.get("sub"))
    if not user:
        raise UnauthorizedError("用户不存在")

    return {
        "success": True,
        "data": user.to_dict(),
        "error": None,
        "meta": {},
    }