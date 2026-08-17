"""
速率限制 — 基于内存的滑动窗口实现
"""

import asyncio
import time
import threading
from typing import Any, Optional

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

    # 全局 AI 速率限制实例
ai_rate_limiter = RateLimiter(
    max_requests=settings.AI_RATE_LIMIT,
    window_sec=settings.AI_RATE_WINDOW_SEC,
)


# ── 异步并发控制（用于 LangGraph 工作流） ──


class ConcurrencyLimiter:
    """全局并发控制信号量，限制同时最多 N 个 LLM 调用"""

    def __init__(self, max_concurrent: int = 2):
        self._semaphore = asyncio.Semaphore(max_concurrent)

    async def __aenter__(self):
        await self._semaphore.acquire()
        return self

    async def __aexit__(self, *args):
        self._semaphore.release()


class RetryHandler:
    """指数退避重试处理器，仅在 429 限流错误时重试"""

    BASE_DELAY = 2
    MAX_RETRIES = 5
    MAX_DELAY = 16

    @staticmethod
    def get_delay(attempt: int) -> int:
        delay = RetryHandler.BASE_DELAY * (2 ** attempt)
        return min(delay, RetryHandler.MAX_DELAY)

    @staticmethod
    async def execute_with_retry(
        func, *args, max_retries: int = MAX_RETRIES, **kwargs,
    ) -> Any:
        last_error = None
        for attempt in range(max_retries + 1):
            try:
                return await func(*args, **kwargs)
            except Exception as e:
                last_error = e
                status = getattr(e, 'status_code', None) or getattr(e, 'status', None)
                if status == 429:
                    if attempt < max_retries:
                        delay = RetryHandler.get_delay(attempt)
                        print(f"[Retry] 429 限流，第 {attempt + 1}/{max_retries} 次重试，等待 {delay}s")
                        await asyncio.sleep(delay)
                        continue
                else:
                    raise
        raise last_error


# 全局并发控制实例
concurrency_limiter = ConcurrencyLimiter(max_concurrent=2)