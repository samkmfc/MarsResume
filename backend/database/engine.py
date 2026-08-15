"""
Database engine and session management.
Supports SQLite (dev) and PostgreSQL (production).
"""

import os
from typing import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.pool import NullPool

from config import settings
from models.base import Base


# Create engine
engine = create_async_engine(
    settings.DATABASE_URL,
    poolclass=NullPool if "sqlite" in settings.DATABASE_URL else None,
    echo=False,
)

# Session factory
async_session_factory = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)


async def init_db():
    """Initialize database tables."""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """FastAPI dependency — get database session."""
    async with async_session_factory() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


async def get_user_by_email(db: AsyncSession, email: str):
    """Get user by email."""
    from sqlalchemy import select
    from models.user import User
    result = await db.execute(select(User).where(User.email == email))
    return result.scalar_one_or_none()


async def get_user_by_id(db: AsyncSession, user_id: str):
    """Get user by ID."""
    from sqlalchemy import select
    from models.user import User
    result = await db.execute(select(User).where(User.id == user_id))
    return result.scalar_one_or_none()


async def create_user(db: AsyncSession, email: str, username: str, hashed_password: str) -> object:
    """Create a new user."""
    from models.user import User
    from datetime import datetime, timezone
    user = User(
        email=email,
        username=username,
        hashed_password=hashed_password,
        plan="free",
        usage_count=0,
        usage_limit=3,
        is_active=True,
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc),
    )
    db.add(user)
    await db.flush()
    return user


async def increment_usage(db: AsyncSession, user_id: str):
    """Increment usage counter for a user."""
    from sqlalchemy import update
    from models.user import User
    await db.execute(
        update(User).where(User.id == user_id).values(usage_count=User.usage_count + 1)
    )