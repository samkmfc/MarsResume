# MarsResume 模块通信契约 v3.0

> 本文档定义 worktree 同步规则、事件总线实现、全局异常结构体。
> 所有模块必须遵守此文档定义的通信规范。

---

## 1. worktree 跨分支同步规则

### 1.1 worktree 命名规范

```
worktree-{module_name}
```

| 模块 | worktree 名称 | 分支名称 |
|------|---------------|----------|
| LangGraph + 多Agent | `worktree-langgraph` | `feat/langgraph-workflow` |
| MCP Server | `worktree-mcp` | `feat/mcp-server` |
| RAG 知识库 | `worktree-rag` | `feat/rag-knowledge-base` |
| SaaS 鉴权 | `worktree-saas` | `feat/saas-auth` |
| 前端升级 | `worktree-frontend` | `feat/frontend-upgrade` |

### 1.2 创建 worktree 命令

```bash
# 从 master 创建 worktree（每个模块独立分支）
git worktree add ../worktree-langgraph feat/langgraph-workflow
git worktree add ../worktree-mcp feat/mcp-server
git worktree add ../worktree-rag feat/rag-knowledge-base
git worktree add ../worktree-saas feat/saas-auth
git worktree add ../worktree-frontend feat/frontend-upgrade
```

### 1.3 只读共享文件

以下文件在各个 worktree 中为**只读引用**，不允许修改：

| 文件 | 说明 | 托管位置 |
|------|------|----------|
| `docs/architecture.md` | 架构设计文档 | 主仓库 master |
| `docs/openapi-schema.md` | 接口契约文档 | 主仓库 master |
| `docs/contracts.md` | 本文件 | 主仓库 master |
| `backend/agents/base.py` | Agent 基类契约 | worktree-langgraph |
| `backend/graph/state.py` | 状态定义契约 | worktree-langgraph |

### 1.4 同步流程

```
master (主分支)
│
├── feat/langgraph-workflow  ← 批次1 (Agent 1)
│   └── 开发完成后 → PR → master
│
├── feat/mcp-server          ← 批次1 (Agent 2)
│   └── 开发完成后 → PR → master
│
├── feat/rag-knowledge-base  ← 批次2 (Agent 3)
│   └── 依赖 master 合并批次1后 → PR → master
│
├── feat/saas-auth           ← 批次2 (Agent 4)
│   └── 依赖 master 合并批次1后 → PR → master
│
└── feat/frontend-upgrade    ← 批次3 (Agent 5)
    └── 依赖 master 合并批次1/2后 → PR → master
```

### 1.5 合并前检查清单

每个 worktree 合并到 master 前必须通过：

```bash
# 1. 契约校验
python scripts/check-contracts.py --module {module_name}

# 2. 语法检查
cd backend && python -m py_compile main.py && python -m py_compile services/*.py

# 3. 导入检查
python -c "from main import app; print('OK')"

# 4. 确保不破坏现有 API
grep -r "def _" backend/main.py | sort
```

### 1.6 冲突解决规则

| 冲突类型 | 解决策略 | 优先级 |
|----------|----------|--------|
| 同一文件不冲突行 | 自动合并 | 高 |
| 同一文件同一行冲突 | 以先合并的模块为准，后合并的模块适配 | 中 |
| 契约文件冲突 | 以 master 文档为准 | 最高 |
| 依赖冲突 (requirements.txt) | 合并所有依赖，统一版本 | 中 |

---

## 2. 事件总线实现

### 2.1 代码位置

`backend/services/event_bus.py`

### 2.2 完整实现

```python
"""
事件总线 — 模块间异步通信中间件
所有模块通过事件总线通信，禁止直接调用其他模块的内部方法
"""

import asyncio
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Callable, Coroutine, Dict, List, Optional, Set
from uuid import uuid4


class EventPriority(Enum):
    """事件优先级"""
    HIGH = "high"      # 限流/异常等关键事件
    MEDIUM = "medium"  # 业务事件（优化完成等）
    LOW = "low"        # 日志/指标等非关键事件


class EventType(Enum):
    """事件类型枚举"""
    # 优化流程
    OPTIMIZATION_STARTED = "optimization.started"
    OPTIMIZATION_COMPLETED = "optimization.completed"
    OPTIMIZATION_FAILED = "optimization.failed"
    
    # Agent 任务
    AGENT_TASK_ASSIGNED = "agent.task_assigned"
    AGENT_TASK_COMPLETED = "agent.task_completed"
    AGENT_TASK_FAILED = "agent.task_failed"
    
    # RAG
    RAG_CONTEXT_READY = "rag.context_ready"
    RAG_INDEX_UPDATED = "rag.index_updated"
    
    # 限流与调度
    RATE_LIMIT_TRIGGERED = "rate_limit.triggered"
    RATE_LIMIT_RECOVERED = "rate_limit.recovered"
    AGENT_SUSPENDED = "agent.suspended"
    AGENT_RESUMED = "agent.resumed"
    
    # 认证
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
    ttl: int = 300  # 事件存活时间（秒）


class EventBus:
    """
    异步事件总线
    
    使用方式:
        bus = EventBus()
        
        # 订阅事件
        async def handler(event: Event):
            print(f"收到事件: {event.event_type}")
        
        await bus.subscribe("rag.service", handler)
        
        # 发布事件
        await bus.publish(Event(
            event_type="optimization.completed",
            source="langgraph.workflow",
            target="rag.service",
            payload={"optimized_text": "..."}
        ))
    """
    
    def __init__(self):
        self._subscribers: Dict[str, List[Callable[[Event], Coroutine]]] = {}
        self._queues: Dict[str, asyncio.Queue] = {}
        self._lock = asyncio.Lock()
    
    async def subscribe(
        self, 
        module_name: str, 
        handler: Callable[[Event], Coroutine]
    ):
        """订阅事件"""
        async with self._lock:
            if module_name not in self._subscribers:
                self._subscribers[module_name] = []
            self._subscribers[module_name].append(handler)
    
    async def unsubscribe(
        self, 
        module_name: str, 
        handler: Callable[[Event], Coroutine]
    ):
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
    
    async def _safe_dispatch(
        self, 
        handler: Callable[[Event], Coroutine], 
        event: Event
    ):
        """安全分发，捕获异常"""
        try:
            await handler(event)
        except Exception as e:
            print(f"[EventBus] 事件处理失败: {event.event_type} → {e}")
    
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
```

### 2.3 模块间通信规则

| 规则 | 说明 |
|------|------|
| 禁止直接调用 | 模块 A 不能直接调用模块 B 的内部方法 |
| 必须通过事件总线 | 所有跨模块通信必须通过 `EventBus.publish()` |
| 同模块内部调用 | 允许直接调用 |
| 事件不丢失 | 重要事件使用 Queue 模式，确保消费 |
| 超时处理 | 事件处理超时 30s，超时后记录日志 |

---

## 3. 全局异常结构体

### 3.1 代码位置

`backend/middleware/exceptions.py`（新建，替代原有的 exception_handler.py）

### 3.2 完整实现

```python
"""
全局异常定义 — 所有模块必须使用此处的异常类
"""

from typing import Any, Dict, Optional


class AppError(Exception):
    """应用异常基类"""
    
    def __init__(
        self,
        code: str,
        message: str,
        status_code: int = 500,
        detail: Optional[Dict[str, Any]] = None,
    ):
        self.code = code
        self.message = message
        self.status_code = status_code
        self.detail = detail or {}
        super().__init__(self.message)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "code": self.code,
            "message": self.message,
            "detail": self.detail,
        }


# ── 认证异常 ──

class UnauthorizedError(AppError):
    def __init__(self, message="未认证，请先登录"):
        super().__init__(
            code="UNAUTHORIZED",
            message=message,
            status_code=401,
        )

class ForbiddenError(AppError):
    def __init__(self, message="无权限执行此操作"):
        super().__init__(
            code="FORBIDDEN",
            message=message,
            status_code=403,
        )


# ── 限流异常 ──

class RateLimitedError(AppError):
    def __init__(self, retry_after: int = 30, limit: int = 15, window: int = 60):
        super().__init__(
            code="RATE_LIMITED",
            message=f"请求过于频繁，请在 {retry_after} 秒后重试",
            status_code=429,
            detail={"retry_after": retry_after, "limit": limit, "window": window},
        )

class QuotaExceededError(AppError):
    def __init__(self, plan: str = "free", limit: int = 3):
        super().__init__(
            code="QUOTA_EXCEEDED",
            message=f"月度使用次数已用完（{plan} 版上限 {limit} 次）",
            status_code=429,
            detail={"plan": plan, "limit": limit},
        )


# ── 参数异常 ──

class ValidationError(AppError):
    def __init__(self, message="参数校验失败", detail: Optional[dict] = None):
        super().__init__(
            code="VALIDATION_ERROR",
            message=message,
            status_code=422,
            detail=detail,
        )

class FileTooLargeError(AppError):
    def __init__(self, max_size_mb: int = 10):
        super().__init__(
            code="FILE_TOO_LARGE",
            message=f"文件过大，最大支持 {max_size_mb}MB",
            status_code=413,
            detail={"max_size_mb": max_size_mb},
        )

class UnsupportedFormatError(AppError):
    def __init__(self, ext: str, allowed: list = None):
        super().__init__(
            code="UNSUPPORTED_FORMAT",
            message=f"不支持的文件格式: {ext}",
            status_code=400,
            detail={"ext": ext, "allowed_formats": allowed or []},
        )


# ── 业务异常 ──

class ResourceNotFoundError(AppError):
    def __init__(self, resource: str, resource_id: str):
        super().__init__(
            code="NOT_FOUND",
            message=f"{resource} 不存在: {resource_id}",
            status_code=404,
            detail={"resource": resource, "id": resource_id},
        )

class InjectionDetectedError(AppError):
    def __init__(self):
        super().__init__(
            code="INJECTION_DETECTED",
            message="检测到潜在的注入攻击，请求已被拦截",
            status_code=400,
        )


# ── 服务异常 ──

class LLMError(AppError):
    def __init__(self, message="LLM 调用失败", detail: Optional[dict] = None):
        super().__init__(
            code="LLM_ERROR",
            message=message,
            status_code=502,
            detail=detail,
        )

class RAGError(AppError):
    def __init__(self, message="RAG 服务异常", detail: Optional[dict] = None):
        super().__init__(
            code="RAG_ERROR",
            message=message,
            status_code=500,
            detail=detail,
        )

class InternalError(AppError):
    def __init__(self, message="内部服务器错误"):
        super().__init__(
            code="INTERNAL_ERROR",
            message=message,
            status_code=500,
        )
```

### 3.3 异常处理中间件

```python
# backend/middleware/exception_handler.py（更新）
from fastapi import Request
from fastapi.responses import JSONResponse
from middleware.exceptions import AppError

async def global_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    if isinstance(exc, AppError):
        return JSONResponse(
            status_code=exc.status_code,
            content={
                "success": False,
                "data": None,
                "error": exc.to_dict(),
                "meta": {
                    "request_id": getattr(request.state, "request_id", None),
                    "timestamp": datetime.utcnow().isoformat() + "Z",
                },
            },
        )
    
    # 未知异常 → 包装为 InternalError
    return JSONResponse(
        status_code=500,
        content={
            "success": False,
            "data": None,
            "error": {
                "code": "INTERNAL_ERROR",
                "message": "内部服务器错误",
                "detail": {"type": type(exc).__name__} if isinstance(exc, Exception) else {},
            },
            "meta": {
                "request_id": getattr(request.state, "request_id", None),
                "timestamp": datetime.utcnow().isoformat() + "Z",
            },
        },
    )
```

---

## 4. 限流调度器

### 4.1 代码位置

`backend/middleware/rate_limiter.py`

### 4.2 核心实现

```python
"""
限流调度器 — 全局并发控制 + 指数退避重试
"""

import asyncio
import time
from dataclasses import dataclass
from typing import Dict, Optional


@dataclass
class RateLimitResult:
    allowed: bool
    remaining: int
    retry_after: int  # 秒


class ConcurrencyLimiter:
    """
    全局并发控制
    
    限制同时最多 N 个 LLM 调用
    超出时阻塞等待
    """
    
    def __init__(self, max_concurrent: int = 2):
        self._semaphore = asyncio.Semaphore(max_concurrent)
        self._max = max_concurrent
    
    async def acquire(self) -> bool:
        """获取执行许可（阻塞直到可用）"""
        await self._semaphore.acquire()
        return True
    
    def release(self):
        """释放执行许可"""
        self._semaphore.release()
    
    @property
    def available(self) -> int:
        return self._max - self._semaphore._value  # 不精确，仅参考


class TokenBucketLimiter:
    """
    令牌桶限流器 — 单 Agent 级别
    
    每个 Agent 独立配额，超过自动休眠
    """
    
    def __init__(self, max_calls: int = 15, window: int = 60):
        self.max_calls = max_calls
        self.window = window  # 秒
        self._buckets: Dict[str, list] = {}  # agent_id -> [timestamp, ...]
    
    async def check(self, agent_id: str) -> RateLimitResult:
        now = time.time()
        if agent_id not in self._buckets:
            self._buckets[agent_id] = []
        
        # 清理过期记录
        self._buckets[agent_id] = [
            t for t in self._buckets[agent_id] 
            if now - t < self.window
        ]
        
        used = len(self._buckets[agent_id])
        remaining = self.max_calls - used
        
        if remaining <= 0:
            # 计算最早的一条记录什么时候过期
            oldest = min(self._buckets[agent_id])
            retry_after = int(self.window - (now - oldest))
            return RateLimitResult(allowed=False, remaining=0, retry_after=max(retry_after, 1))
        
        self._buckets[agent_id].append(now)
        return RateLimitResult(allowed=True, remaining=remaining, retry_after=0)


class RetryHandler:
    """
    指数退避重试处理器
    
    重试策略: 2s → 4s → 8s → 16s, 最大 5 次
    """
    
    BASE_DELAY = 2  # 秒
    MAX_RETRIES = 5
    MAX_DELAY = 16  # 秒
    
    @staticmethod
    def get_delay(attempt: int) -> int:
        """计算第 attempt 次重试的等待时间"""
        delay = RetryHandler.BASE_DELAY * (2 ** attempt)
        return min(delay, RetryHandler.MAX_DELAY)
    
    @staticmethod
    async def execute_with_retry(
        func,
        *args,
        max_retries: int = MAX_RETRIES,
        **kwargs,
    ):
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
                if hasattr(e, 'status_code') and e.status_code == 429:
                    if attempt < max_retries:
                        delay = RetryHandler.get_delay(attempt)
                        print(f"[Retry] 429 限流，第 {attempt+1} 次重试，等待 {delay}s")
                        await asyncio.sleep(delay)
                        continue
                
                # 非 429 错误直接抛出
                raise
        
        # 重试耗尽
        raise last_error
```

---

## 5. 全局共享缓存层

### 5.1 代码位置

`backend/services/cache.py`

### 5.2 实现

```python
"""
全局共享缓存层 — 减少重复 LLM 调用
复用 RAG 向量、会话数据、测试结果
"""

import time
from typing import Any, Dict, Optional, Tuple


class MemoryCache:
    """
    内存缓存
    
    支持 TTL 过期，自动清理
    """
    
    def __init__(self, default_ttl: int = 300):
        self._cache: Dict[str, Tuple[Any, float]] = {}  # key -> (value, expire_at)
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
```