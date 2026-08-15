"""
pytest 共享夹具 — 提供免外部依赖的 TestClient 与 mock 引擎。

策略：
  - 不触碰真实 LLM / 网络：FakeEngine 替换 main.get_engine
  - 不污染磁盘：mock 掉 storage 写入与 SQLAlchemy init_db
  - 无需 .env：config 全部带默认值
"""

import sys
from pathlib import Path

# 让 `from main import app` 可解析（测试文件与 main.py 同级于 backend/）
_BACKEND = Path(__file__).resolve().parent
if str(_BACKEND) not in sys.path:
    sys.path.insert(0, str(_BACKEND))

import pytest
from fastapi.testclient import TestClient


# ── 假 LLM / 假引擎 ──────────────────────────────────────────

class FakeLLM:
    """记录调用、返回预设 JSON 的 LLM 替身。"""

    def __init__(self, json_response: str = '{"questions": [], "known_info": "info", "highlights": [], "fixed_text": "", "final_version": "", "summary": []}'):
        self._json = json_response
        self.calls = []

    def chat(self, **kw):
        self.calls.append(("chat", kw))
        return self._json

    def chat_stream(self, **kw):
        self.calls.append(("chat_stream", kw))
        yield "模拟生成内容"


class FakeEngine:
    """SkillEngine 替身，避免真实 LLM 调用。"""

    def __init__(self, result: dict | None = None):
        self.result = result or {"need_answers": True, "questions": ["示例追问"], "known_info": ""}
        self.llm = FakeLLM()

    async def optimize_async(self, **kw):
        return self.result

    def optimize(self, *a, **kw):
        return self.result


# ── 夹具 ────────────────────────────────────────────────────

@pytest.fixture
def client(monkeypatch):
    """FastAPI TestClient，禁用 DB/RAG 启动副作用。"""
    # init_db 建表到真实 sqlite，测试中禁用
    import database.engine as db_engine
    async def _noop_init():
        return None
    monkeypatch.setattr(db_engine, "init_db", _noop_init)

    from main import app
    with TestClient(app) as c:
        yield c


@pytest.fixture
def fake_engine(monkeypatch):
    """注入 FakeEngine 并拦截历史写入，避免落盘。"""
    import main
    eng = FakeEngine()
    monkeypatch.setattr(main, "get_engine", lambda: eng)
    monkeypatch.setattr(main.storage, "save_optimization", lambda **kw: "test-opt-id")
    return eng
