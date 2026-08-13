"""
限流调度器 — 全局并发控制 + 令牌桶 + 指数退避重试
"""

import asyncio
import time
from dataclasses import dataclass
from typing import Any, Callable, Dict, Optional


@dataclass
class RateLimitResult:
    allowed: bool
    remaining: int
    retry_after: int  # 秒


class ConcurrencyLimiter:
    """
    全局并发控制信号量

    限制同时最多 N 个 LLM 调用
    超出时阻塞等待，直到某个调用释放许可
    """

    def __init__(self, max_concurrent: int = 2):
        self._semaphore = asyncio.Semaphore(max_concurrent)
        self._max = max_concurrent
        self._waiting = 0

    async def acquire(self) -> bool:
        """获取执行许可（阻塞直到可用）"""
        self._waiting += 1
        await self._semaphore.acquire()
        self._waiting -= 1
        return True

    def release(self):
        """释放执行许可"""
        self._semaphore.release()

    @property
    def waiting_count(self) -> int:
        return self._waiting

    @property
    def available(self) -> int:
        return self._max - (self._max - self._semaphore._value)


class TokenBucketLimiter:
    """
    令牌桶限流器 — 单 Agent 级别

    每个 Agent 独立配额，超过自动休眠
    """

    def __init__(self, max_calls: int = 15, window: int = 60):
        self.max_calls = max_calls
        self.window = window  # 秒
        self._buckets: Dict[str, list] = {}

    async def check(self, agent_id: str) -> RateLimitResult:
        now = time.time()
        if agent_id not in self._buckets:
            self._buckets[agent_id] = []

        # 清理过期记录
        self._buckets[agent_id] = [t for t in self._buckets[agent_id] if now - t < self.window]

        used = len(self._buckets[agent_id])
        remaining = self.max_calls - used

        if remaining <= 0:
            oldest = min(self._buckets[agent_id])
            retry_after = int(self.window - (now - oldest))
            return RateLimitResult(allowed=False, remaining=0, retry_after=max(retry_after, 1))

        self._buckets[agent_id].append(now)
        return RateLimitResult(allowed=True, remaining=remaining, retry_after=0)


class RetryHandler:
    """
    指数退避重试处理器

    重试策略: 2s → 4s → 8s → 16s, 最大 5 次
    仅在 429 限流错误时重试
    """

    BASE_DELAY = 2
    MAX_RETRIES = 5
    MAX_DELAY = 16

    @staticmethod
    def get_delay(attempt: int) -> int:
        delay = RetryHandler.BASE_DELAY * (2 ** attempt)
        return min(delay, RetryHandler.MAX_DELAY)

    @staticmethod
    async def execute_with_retry(
        func: Callable,
        *args: Any,
        max_retries: int = MAX_RETRIES,
        **kwargs: Any,
    ) -> Any:
        """
        带指数退避的异步重试执行

        429 错误触发重试，其他错误直接抛出
        """
        last_error = None

        for attempt in range(max_retries + 1):
            try:
                return await func(*args, **kwargs)
            except Exception as e:
                last_error = e

                # 只有 429 限流错误才重试
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


# 全局单例
concurrency_limiter = ConcurrencyLimiter(max_concurrent=2)