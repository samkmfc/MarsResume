"""
全局共享缓存层 — 减少重复 LLM 调用
复用 RAG 向量、会话数据、测试结果
"""

import time
from typing import Any, Dict, Optional, Tuple


class MemoryCache:
    """
    内存缓存，支持 TTL 过期自动清理
    """

    def __init__(self, default_ttl: int = 300):
        self._cache: Dict[str, Tuple[Any, float]] = {}
        self._default_ttl = default_ttl

    def get(self, key: str) -> Optional[Any]:
        if key in self._cache:
            value, expire_at = self._cache[key]
            if time.time() < expire_at:
                return value
            del self._cache[key]
        return None

    def set(self, key: str, value: Any, ttl: Optional[int] = None):
        expire_at = time.time() + (ttl or self._default_ttl)
        self._cache[key] = (value, expire_at)

    def delete(self, key: str):
        self._cache.pop(key, None)

    def clear(self):
        self._cache.clear()

    def cleanup(self):
        """清理过期缓存"""
        now = time.time()
        expired = [k for k, (_, t) in self._cache.items() if now >= t]
        for k in expired:
            del self._cache[k]


# 全局缓存实例
cache = MemoryCache()