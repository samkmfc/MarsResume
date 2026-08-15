"""
配置管理 — 统一加载环境变量
"""

import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()


class Settings:
    # ── LLM ──
    LLM_API_KEY: str = os.getenv("LLM_API_KEY", "")
    LLM_BASE_URL: str = os.getenv("LLM_BASE_URL", "https://api.openai.com/v1")
    LLM_MODEL: str = os.getenv("LLM_MODEL", "gpt-4o")

    # ── Server ──
    SERVER_PORT: int = int(os.getenv("SERVER_PORT", "8000"))
    CORS_ORIGINS: list[str] = os.getenv("CORS_ORIGINS", "http://localhost:5173,http://localhost:3000").split(",")

    # ── Rate Limit (AI generation) ──
    AI_RATE_LIMIT: int = int(os.getenv("AI_RATE_LIMIT", "30"))
    AI_RATE_WINDOW_SEC: int = int(os.getenv("AI_RATE_WINDOW_SEC", "3600"))

    # ── Data ──
    _default_db = str(Path(__file__).resolve().parent / "data" / "storage.json")
    DB_PATH: str = os.getenv("DB_PATH", _default_db)

    # ── RAG ──
    RAG_ENABLED: bool = os.getenv("RAG_ENABLED", "true").lower() == "true"
    _default_chroma = str(Path(__file__).resolve().parent / "data" / "chroma_db")
    RAG_CHROMA_PATH: str = os.getenv("RAG_CHROMA_PATH", _default_chroma)
    RAG_TOP_K: int = int(os.getenv("RAG_TOP_K", "5"))

    # ── Auth / JWT ──
    JWT_SECRET_KEY: str = os.getenv("JWT_SECRET_KEY", "mars-resume-dev-secret-change-in-production")
    JWT_ALGORITHM: str = "HS256"
    JWT_EXPIRE_MINUTES: int = int(os.getenv("JWT_EXPIRE_MINUTES", "1440"))  # 24h

    # ── Database ──
    _default_sqlite = str(Path(__file__).resolve().parent / "data" / "marsresume.db")
    DATABASE_URL: str = os.getenv("DATABASE_URL", f"sqlite+aiosqlite:///{_default_sqlite}")

    # ── Plan limits ──
    FREE_USAGE_LIMIT: int = int(os.getenv("FREE_USAGE_LIMIT", "3"))
    PRO_USAGE_LIMIT: int = int(os.getenv("PRO_USAGE_LIMIT", "100"))


settings = Settings()