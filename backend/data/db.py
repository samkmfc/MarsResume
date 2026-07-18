"""
简易文件数据库 — 使用 JSON 文件持久化优化历史

提供基本的 CRUD 操作，支持优化记录存储和历史查询。
生产环境应迁移到 SQLite/PostgreSQL。
"""

import json
import os
import threading
from datetime import datetime
from pathlib import Path
from typing import Optional
from uuid import uuid4

from config import settings


class Storage:
    """基于 JSON 文件的持久化存储（线程安全）"""

    def __init__(self, path: str = None):
        self.path = path or settings.DB_PATH
        # 安全兜底：如果路径为空，使用默认值
        if not self.path:
            self.path = str(Path(__file__).resolve().parent / "storage.json")
        self._lock = threading.Lock()
        self._ensure_file()

    def _ensure_file(self):
        os.makedirs(os.path.dirname(self.path), exist_ok=True)
        if not os.path.exists(self.path):
            with open(self.path, "w", encoding="utf-8") as f:
                json.dump({"optimizations": []}, f)

    def _read(self) -> dict:
        with open(self.path, "r", encoding="utf-8") as f:
            return json.load(f)

    def _write(self, data: dict):
        with open(self.path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

    def save_optimization(
        self,
        section_type: str,
        original_text: str,
        optimized_text: str,
        changes_summary: list[str],
    ) -> dict:
        """保存一条优化记录"""
        record = {
            "id": uuid4().hex[:12],
            "section_type": section_type,
            "original_text": original_text[:500],
            "optimized_text": optimized_text,
            "changes_summary": changes_summary,
            "created_at": datetime.now().isoformat(),
        }
        with self._lock:
            data = self._read()
            data["optimizations"].insert(0, record)
            # 最多保留 100 条
            data["optimizations"] = data["optimizations"][:100]
            self._write(data)
        return record

    def get_history(self, limit: int = 20) -> list[dict]:
        """获取优化历史"""
        with self._lock:
            data = self._read()
            return data["optimizations"][:limit]

    def get_optimization(self, opt_id: str) -> Optional[dict]:
        """获取单条优化记录"""
        with self._lock:
            data = self._read()
            for record in data["optimizations"]:
                if record["id"] == opt_id:
                    return record
        return None


# 全局存储实例
storage = Storage()