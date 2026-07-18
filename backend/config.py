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
    AI_RATE_LIMIT: int = int(os.getenv("AI_RATE_LIMIT", "30"))      # requests per window
    AI_RATE_WINDOW_SEC: int = int(os.getenv("AI_RATE_WINDOW_SEC", "3600"))  # 1 hour

    # ── Data ──
    # 优先使用环境变量，否则使用 __file__ 所在目录的相对路径
    _default_db = str(Path(__file__).resolve().parent / "data" / "storage.json")
    DB_PATH: str = os.getenv("DB_PATH", _default_db)


settings = Settings()