"""
配置管理 — 统一加载环境变量
"""

import os
import sys
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
    # 无默认值 — 必须在 .env / 环境变量中显式设置，启动时校验（见文件末尾）
    JWT_SECRET_KEY: str = os.getenv("JWT_SECRET_KEY", "")
    JWT_ALGORITHM: str = "HS256"
    JWT_EXPIRE_MINUTES: int = int(os.getenv("JWT_EXPIRE_MINUTES", "1440"))  # 24h

    # ── Database ──
    _default_sqlite = str(Path(__file__).resolve().parent / "data" / "marsresume.db")
    DATABASE_URL: str = os.getenv("DATABASE_URL", f"sqlite+aiosqlite:///{_default_sqlite}")

    # ── Plan limits ──
    FREE_USAGE_LIMIT: int = int(os.getenv("FREE_USAGE_LIMIT", "3"))
    PRO_USAGE_LIMIT: int = int(os.getenv("PRO_USAGE_LIMIT", "100"))


settings = Settings()


# ── JWT 密钥启动校验 ───────────────────────────────────────
# 移除硬编码默认值后，必须在环境变量中显式设置一个随机密钥。
# 空值或沿用源码里的公开占位符都会直接拒绝启动，防止任何人伪造令牌。
# 测试（pytest）下放宽，保留 conftest "无需 .env" 的约定。
_INSECURE_PLACEHOLDER = "mars-resume-dev-secret-change-in-production"
if (
    not settings.JWT_SECRET_KEY
    or settings.JWT_SECRET_KEY == _INSECURE_PLACEHOLDER
) and "pytest" not in sys.modules:
    raise RuntimeError(
        "JWT_SECRET_KEY 未配置或沿用了公开占位符。"
        "请在 .env / 环境变量中设置随机密钥："
        'python -c "import secrets; print(secrets.token_hex(32))"'
    )