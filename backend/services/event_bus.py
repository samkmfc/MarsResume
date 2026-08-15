"""
事件总线 — 模块间异步通信中间件
所有模块通过事件总线通信，禁止直接调用其他模块的内部方法
"""

import asyncio
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Callable, Coroutine, Dict, List, Optional
from uuid import uuid4


class EventPriority(Enum):
    """事件优先级"""
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


class EventType(Enum):
    """事件类型枚举"""
    OPTIMIZATION_STARTED = "optimization.started"
    OPTIMIZATION_COMPLETED = "optimization.completed"
    OPTIMIZATION_FAILED = "optimization.failed"

    AGENT_TASK_ASSIGNED = "agent.task_assigned"
    AGENT_TASK_COMPLETED = "agent.task_completed"
    AGENT_TASK_FAILED = "agent.task_failed"

    RAG_CONTEXT_READY = "rag.context_ready"
    RAG_INDEX_UPDATED = "rag.index_updated"

    RATE_LIMIT_TRIGGERED = "rate_limit.triggered"
    RATE_LIMIT_RECOVERED = "rate_limit.recovered"
    AGENT_SUSPENDED = "agent.suspended"
    AGENT_RESUMED = "agent.resumed"

    AUTH_TOKEN_REFRESHED = "auth.token_refreshed"
    AUTH_USER_REGISTERED = "auth.user_registered"
    AUTH_QUOTA_EXCEEDED = "auth.quota_exceeded"


@dataclass
class Event:
    """事件数据结构"""
    event_type: str
    source: str
    target: str
    payload: Dict[str, Any]
    priority: EventPriority = EventPriority.MEDIUM
    event_id: str = field(default_factory=lambda: uuid4().hex[:12])
    timestamp: str = field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
    )
    correlation_id: Optional[str] = None
    retry_count: int = 0
    max_retries: int = 3
    ttl: int = 300


class EventBus:
    """
    异步事件总线

    使用方式:
        bus = EventBus()
        await bus.subscribe("rag.service", my_handler)
        await bus.publish(Event(event_type="...", source="...", target="...", payload={...}))
    """

    def __init__(self):
        self._subscribers: Dict[str, List[Callable[[Event], Coroutine]]] = {}
        self._queues: Dict[str, asyncio.Queue] = {}
        self._lock = asyncio.Lock()

    async def subscribe(self, module_name: str, handler: Callable[[Event], Coroutine]):
        """订阅事件"""
        async with self._lock:
            if module_name not in self._subscribers:
                self._subscribers[module_name] = []
            self._subscribers[module_name].append(handler)

    async def unsubscribe(self, module_name: str, handler: Callable[[Event], Coroutine]):
        """取消订阅"""
        async with self._lock:
            if module_name in self._subscribers:
                self._subscribers[module_name].remove(handler)

    async def publish(self, event: Event):
        """发布事件到目标模块"""
        async with self._lock:
            if event.target in self._subscribers:
                for handler in self._subscribers[event.target]:
                    asyncio.create_task(self._safe_dispatch(handler, event))

    async def publish_all(self, event: Event):
        """广播事件到所有订阅者"""
        async with self._lock:
            for module, handlers in self._subscribers.items():
                for handler in handlers:
                    asyncio.create_task(self._safe_dispatch(handler, event))

    async def _safe_dispatch(self, handler: Callable[[Event], Coroutine], event: Event):
        try:
            await handler(event)
        except Exception as e:
            print(f"[EventBus] 事件处理失败: {event.event_type} 目标={event.target} 错误={e}")

    def get_queue(self, module_name: str) -> asyncio.Queue:
        """获取模块的队列（用于 await 模式）"""
        if module_name not in self._queues:
            self._queues[module_name] = asyncio.Queue()
        return self._queues[module_name]

    async def enqueue(self, event: Event):
        """将事件放入目标模块的队列"""
        queue = self.get_queue(event.target)
        await queue.put(event)

    async def dequeue(self, module_name: str) -> Event:
        """从队列中取出事件（阻塞）"""
        queue = self.get_queue(module_name)
        event = await queue.get()
        return event


# 全局单例
event_bus = EventBus()