"""
速率限制 — 基于内存的滑动窗口实现
"""

import time
import threading
from typing import Optional

from config import settings


class RateLimiter:
    """基于内存的固定窗口速率限制（单进程可用，生产环境应迁移到 Redis）"""

    def __init__(self, max_requests: int = 30, window_sec: int = 3600):
        self.max_requests = max_requests
        self.window_sec = window_sec
        self._buckets: dict[str, list[float]] = {}
        self._lock = threading.Lock()

    def check(self, key: str) -> tuple[bool, int]:
        """
        检查 key 是否允许请求。
        返回 (allowed, retry_after_seconds)
        """
        now = time.time()
        cutoff = now - self.window_sec

        with self._lock:
            timestamps = self._buckets.get(key, [])
            # 清理过期时间戳
            timestamps = [t for t in timestamps if t > cutoff]

            if len(timestamps) >= self.max_requests:
                retry_after = int(timestamps[0] + self.window_sec - now)
                return False, max(1, retry_after)

            timestamps.append(now)
            self._buckets[key] = timestamps
            remaining = self.max_requests - len(timestamps)
            return True, remaining

    def get_remaining(self, key: str) -> int:
        """获取 key 剩余的可用请求数"""
        now = time.time()
        cutoff = now - self.window_sec
        with self._lock:
            timestamps = self._buckets.get(key, [])
            timestamps = [t for t in timestamps if t > cutoff]
            self._buckets[key] = timestamps
            return max(0, self.max_requests - len(timestamps))


# 全局 AI 速率限制实例
ai_rate_limiter = RateLimiter(
    max_requests=settings.AI_RATE_LIMIT,
    window_sec=settings.AI_RATE_WINDOW_SEC,
)