# MarsResume 接口契约文档 v3.0

> 本文档定义所有模块的接口契约，包括 HTTP API、MCP 协议、事件总线、异常结构。
> 所有模块开发必须严格对齐本文档定义的 Schema，不允许自定义数据结构。

---

## 1. 通用规范

### 1.1 HTTP 统一响应格式

```json
{
  "success": true,
  "data": { ... },
  "error": null,
  "meta": {
    "request_id": "uuid",
    "timestamp": "2026-08-13T10:00:00Z",
    "rate_limit_remaining": 28
  }
}
```

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| success | boolean | 是 | 请求是否成功 |
| data | object/null | 是 | 成功时返回的数据 |
| error | object/null | 是 | 失败时的错误信息 |
| meta | object | 是 | 元数据 |

### 1.2 统一错误结构

```json
{
  "code": "RATE_LIMITED",
  "message": "请求过于频繁，请稍后重试",
  "detail": {
    "retry_after": 30,
    "limit": 15,
    "window": 60
  }
}
```

### 1.3 全局错误码表

| 错误码 | HTTP 状态码 | 说明 | 触发条件 |
|--------|-------------|------|----------|
| `UNAUTHORIZED` | 401 | 未认证 | JWT 缺失或无效 |
| `FORBIDDEN` | 403 | 无权限 | 套餐不满足要求 |
| `NOT_FOUND` | 404 | 资源不存在 | 记录/文件不存在 |
| `RATE_LIMITED` | 429 | 请求超限 | 超过速率限制 |
| `QUOTA_EXCEEDED` | 429 | 配额超限 | 月度使用次数用完 |
| `VALIDATION_ERROR` | 422 | 参数校验失败 | 请求参数不符合 Schema |
| `INJECTION_DETECTED` | 400 | 注入攻击 | 检测到 prompt 注入 |
| `FILE_TOO_LARGE` | 413 | 文件过大 | 超过 10MB |
| `UNSUPPORTED_FORMAT` | 400 | 格式不支持 | 文件格式不在允许列表 |
| `LLM_ERROR` | 502 | LLM 调用失败 | 上游 LLM API 异常 |
| `RAG_ERROR` | 500 | RAG 服务异常 | 向量检索失败 |
| `INTERNAL_ERROR` | 500 | 内部错误 | 未预期的异常 |

### 1.4 SSE 事件格式

```
event: {event_type}
data: {json_payload}
```

| 事件类型 | 方向 | 说明 |
|----------|------|------|
| `step1` | 服务端→客户端 | 深挖分析完成 |
| `step2` | 服务端→客户端 | 亮点识别完成 |
| `step3_start` | 服务端→客户端 | 开始生成 |
| `step3_chunk` | 服务端→客户端 | 生成过程 token |
| `step4` | 服务端→客户端 | 指标检查完成 |
| `step5` | 服务端→客户端 | 自检完成 |
| `done` | 服务端→客户端 | 全部完成 |
| `error` | 服务端→客户端 | 错误发生 |
| `progress` | 服务端→客户端 | 进度更新 |

---

## 2. HTTP API 接口清单

### 2.1 健康检查

```
GET /api/status
```

**Response `data`:**
```json
{
  "status": "ok",
  "message": "服务运行正常",
  "api_configured": true,
  "version": "3.0.0",
  "auth_enabled": true,
  "rag_enabled": true
}
```

### 2.2 简历上传

```
POST /api/resume/upload
Content-Type: multipart/form-data

Body: file (UploadFile)
```

**Response `data`:**
```json
{
  "file_id": "a1b2c3d4e5f6",
  "filename": "resume.pdf",
  "ext": ".pdf",
  "text": "提取的文本内容...",
  "text_length": 2048
}
```

**Error:** `UNSUPPORTED_FORMAT`, `FILE_TOO_LARGE`

### 2.3 简历-JD 对齐分析

```
POST /api/resume/analyze
Content-Type: multipart/form-data

Body:
  resume_text: string (required)
  jd_text: string (required)
```

**Response `data`:**
```json
{
  "suggestions": [
    {
      "id": "sug_001",
      "section": "综合优势",
      "original": "熟悉项目管理",
      "suggested": "主导过3个跨部门项目，使用Jira管理迭代，交付周期缩短30%",
      "reason": "JD要求'具备项目管理经验'，建议用量化数据展示",
      "severity": "high"
    }
  ],
  "summary": {
    "match_score": 65,
    "strengths": ["技术背景匹配", "行业经验丰富"],
    "gaps": ["缺少量化成果", "项目管理表述笼统"],
    "key_improvements": "重点补充量化数据和项目成果"
  }
}
```

### 2.4 简历优化（完整流程）

```
POST /api/optimize
Content-Type: application/json

Body:
{
  "resume_text": "string (required, 1-10000)",
  "section_type": "string (required)",
  "section_content": "string (required)",
  "user_answers": "string (optional, 0-5000)",
  "jd_text": "string (optional)",
  "use_rag": true
}
```

**Response `data`（need_answers=true）:**
```json
{
  "need_answers": true,
  "questions": ["这个项目你的角色是什么？", "用的什么工具？"],
  "known_info": "已有信息总结",
  "step1_result": { ... }
}
```

**Response `data`（need_answers=false）:**
```json
{
  "need_answers": false,
  "final_text": "优化后的简历文本...",
  "changes_summary": ["改动1", "改动2", "改动3"],
  "results": {
    "step1": { ... },
    "step2": { ... },
    "step3": "生成文本...",
    "step4": { ... },
    "step5": { ... }
  }
}
```

### 2.5 简历优化（流式）

```
POST /api/optimize/stream
Content-Type: application/json

Body: 同上 /api/optimize
```

**SSE 事件流：** 按 `step1 → step2 → step3_start → step3_chunk* → step4 → step5 → done` 顺序推送

### 2.6 PDF 导出

```
POST /api/resume/export-pdf
Content-Type: multipart/form-data

Body:
  file_id: string (required)
  ext: string (required)
  replacements_json: string (required, JSON array)
  title: string (optional, default "简历")
```

**Response:** `application/pdf` 二进制流

### 2.7 获取模块类型

```
GET /api/section-types
```

**Response `data`:**
```json
{
  "sections": [
    {"id": "comprehensive_advantage", "name": "综合优势", "description": "个人简介/综合优势/核心能力模块"},
    {"id": "work_experience", "name": "工作经历", "description": "工作经历/职业经历模块"},
    {"id": "project_experience", "name": "项目经验", "description": "项目经验/项目案例模块"},
    {"id": "skills", "name": "技能", "description": "专业技能/技术栈模块"}
  ]
}
```

### 2.8 配置查询

```
GET /api/config
```

**Response `data`:**
```json
{
  "api_configured": true,
  "model": "deepseek-v4-flash",
  "base_url": "https://api.openai.com/v1",
  "rate_limit": 30,
  "rag_enabled": true,
  "auth_enabled": true
}
```

### 2.9 用户认证

```
POST /api/auth/register
Body: { "email": "string", "username": "string", "password": "string" }

POST /api/auth/login
Body: { "email": "string", "password": "string" }
Response: { "access_token": "jwt...", "token_type": "bearer", "expires_in": 86400 }

GET /api/auth/me
Header: Authorization: Bearer {token}
Response: { "id": "uuid", "email": "string", "username": "string", "plan": "free", "usage_count": 2, "usage_limit": 3 }
```

### 2.10 优化历史

```
GET /api/history?limit=20
Response: { "records": [{ "id": "uuid", "section_type": "string", "created_at": "iso8601", "match_score": 65 }] }

GET /api/history/{id}
Response: { "id": "uuid", "section_type": "string", "original_text": "string", "optimized_text": "string", "changes_summary": [], "created_at": "iso8601" }
```

### 2.11 RAG 管理

```
POST /api/rag/add-example
Body: { "text": "string", "metadata": { "industry": "AI", "position": "产品经理", "tags": ["亮点", "量化"] } }

POST /api/rag/add-jd-template
Body: { "jd_text": "string", "metadata": { "industry": "AI", "position": "产品经理" } }

GET /api/rag/search?q=关键词&type=examples&top_k=5
Response: { "results": [{ "text": "string", "metadata": {}, "score": 0.95 }] }

GET /api/rag/stats
Response: { "total_examples": 100, "total_jd_templates": 50, "collections": ["resume_examples", "jd_templates"] }
```

### 2.12 管理接口

```
GET /api/admin/users?page=1&page_size=20
Header: Authorization: Bearer {admin_token}
Response: { "items": [...], "total": 100, "page": 1, "page_size": 20 }

PUT /api/admin/users/{id}/plan
Body: { "plan": "pro" }
```

---

## 3. MCP 协议契约

### 3.1 传输协议

| 传输方式 | 适用场景 | 协议 |
|----------|----------|------|
| stdio | Claude Desktop 集成 | 标准输入输出 |
| SSE | 远程访问 / HTTP 代理 | Server-Sent Events |

### 3.2 MCP 工具定义

#### Tool: `parse_resume`

```json
{
  "name": "parse_resume",
  "description": "解析简历文件，提取文本内容",
  "inputSchema": {
    "type": "object",
    "properties": {
      "file_path": {
        "type": "string",
        "description": "简历文件路径（支持 .pdf, .docx, .png, .jpg）"
      }
    },
    "required": ["file_path"]
  }
}
```

**Response:**
```json
{
  "content": [
    {
      "type": "text",
      "text": "{\"file_id\": \"a1b2c3d4e5f6\", \"ext\": \".pdf\", \"text\": \"解析后的文本...\", \"text_length\": 2048}"
    }
  ]
}
```

#### Tool: `analyze_resume_jd`

```json
{
  "name": "analyze_resume_jd",
  "description": "分析简历与职位描述(JD)的匹配度，返回逐条修改建议",
  "inputSchema": {
    "type": "object",
    "properties": {
      "resume_text": { "type": "string", "description": "简历文本" },
      "jd_text": { "type": "string", "description": "职位描述文本" }
    },
    "required": ["resume_text", "jd_text"]
  }
}
```

#### Tool: `optimize_resume_section`

```json
{
  "name": "optimize_resume_section",
  "description": "优化简历的指定模块（综合优势/工作经历/项目经验/技能）",
  "inputSchema": {
    "type": "object",
    "properties": {
      "resume_text": { "type": "string", "description": "完整简历文本" },
      "section_type": { "type": "string", "description": "模块类型：综合优势/工作经历/项目经验/技能" },
      "section_content": { "type": "string", "description": "该模块当前内容" },
      "user_answers": { "type": "string", "description": "用户补充信息（可选）" }
    },
    "required": ["resume_text", "section_type", "section_content"]
  }
}
```

#### Tool: `export_resume_pdf`

```json
{
  "name": "export_resume_pdf",
  "description": "导出优化后的简历为 PDF 文件",
  "inputSchema": {
    "type": "object",
    "properties": {
      "file_id": { "type": "string", "description": "上传时返回的文件ID" },
      "ext": { "type": "string", "description": "文件扩展名" },
      "replacements": {
        "type": "array",
        "items": {
          "type": "object",
          "properties": {
            "original": { "type": "string" },
            "suggested": { "type": "string" }
          }
        }
      }
    },
    "required": ["file_id", "ext", "replacements"]
  }
}
```

#### Resource: `resume://history`

```json
{
  "uri": "resume://history",
  "name": "优化历史记录",
  "description": "获取简历优化历史记录",
  "mimeType": "application/json"
}
```

### 3.3 MCP 启动配置

```json
{
  "mcpServers": {
    "mars-resume": {
      "command": "python",
      "args": ["backend/mcp/run.py"],
      "env": {
        "MCP_TRANSPORT": "stdio"
      }
    }
  }
}
```

---

## 4. 事件总线格式

### 4.1 内部事件总线（模块间通信）

所有模块通过事件总线通信，事件格式如下：

```json
{
  "event_id": "evt_001",
  "event_type": "optimization.completed",
  "source": "langgraph.workflow",
  "target": "rag.service",
  "timestamp": "2026-08-13T10:00:00Z",
  "correlation_id": "corr_001",
  "payload": { ... },
  "metadata": {
    "priority": "high",
    "retry_count": 0,
    "ttl": 300
  }
}
```

### 4.2 事件类型清单

| 事件类型 | 源模块 | 目标模块 | 说明 |
|----------|--------|----------|------|
| `optimization.started` | FastAPI | LangGraph | 开始优化流程 |
| `optimization.completed` | LangGraph | RAG | 优化完成，存入知识库 |
| `rag.context_ready` | RAG | Agent | RAG 增强上下文就绪 |
| `agent.task_assigned` | Coordinator | Agent | 分配任务给 Agent |
| `agent.task_completed` | Agent | Coordinator | Agent 任务完成 |
| `auth.token_refreshed` | Auth | FastAPI | 令牌刷新成功 |
| `rate_limit.triggered` | RateLimit | Agent | 限流触发，挂起 Agent |

### 4.3 内部事件总线实现

使用 Python 的 `asyncio.Queue` 实现异步事件总线：

```python
# event_bus.py
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Dict, Optional
from uuid import uuid4

class EventPriority(Enum):
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"

@dataclass
class Event:
    event_type: str
    source: str
    target: str
    payload: Dict[str, Any]
    priority: EventPriority = EventPriority.MEDIUM
    event_id: str = field(default_factory=lambda: uuid4().hex[:12])
    timestamp: str = field(default_factory=lambda: datetime.utcnow().isoformat() + "Z")
    correlation_id: Optional[str] = None
    retry_count: int = 0
    ttl: int = 300

class EventBus:
    """异步事件总线"""
    def __init__(self):
        self._queues: Dict[str, asyncio.Queue] = {}
    
    def subscribe(self, module_name: str):
        if module_name not in self._queues:
            self._queues[module_name] = asyncio.Queue()
        return self._queues[module_name]
    
    async def publish(self, event: Event):
        if event.target in self._queues:
            await self._queues[event.target].put(event)
    
    async def consume(self, module_name: str) -> Event:
        queue = self.subscribe(module_name)
        return await queue.get()
```

---

## 5. 模块间调用契约

### 5.1 Agent 调用契约

每个 Agent 统一实现以下接口：

```python
class BaseAgent(ABC):
    """Agent 基类契约"""
    
    @abstractmethod
    async def run(self, context: AgentContext) -> AgentResult:
        """
        执行 Agent 任务
        
        Args:
            context: AgentContext
                - task_id: str
                - input_data: Dict[str, Any]
                - rag_context: Optional[str]
                - config: Dict[str, Any]
        
        Returns:
            AgentResult
                - task_id: str
                - success: bool
                - output_data: Dict[str, Any]
                - error: Optional[AgentError]
                - metrics: Dict[str, Any]  # token用量, 耗时等
        """
        pass
```

### 5.2 LangGraph 节点契约

```python
# 每个 LangGraph 节点的签名
async def node_name(state: OptimizationState) -> dict:
    """
    输入: OptimizationState (完整图状态)
    输出: dict (要更新的状态字段)
    """
    pass
```

### 5.3 RAG 服务契约

```python
class RAGService:
    async def search_similar(
        self, 
        query: str, 
        collection: str, 
        top_k: int = 5,
        filter: Optional[dict] = None
    ) -> list[SearchResult]:
        """语义搜索"""
        pass
    
    async def get_optimization_context(
        self,
        resume_text: str,
        jd_text: Optional[str] = None
    ) -> str:
        """
        获取优化增强上下文（注入到 prompt 的 few-shot 示例）
        返回格式化后的字符串
        """
        pass
```

### 5.4 限流器契约

```python
class RateLimiter:
    async def check(
        self, 
        client_id: str,
        quota: int = 15,
        window: int = 60
    ) -> RateLimitResult:
        """
        检查是否超过限流
        
        Returns:
            RateLimitResult
                - allowed: bool
                - remaining: int
                - retry_after: int  # 秒
        """
        pass
    
    async def acquire(self) -> bool:
        """
        获取 LLM 调用许可（阻塞直到可用）
        全局并发控制，最多同时 2 个 LLM 调用
        """
        pass
    
    async def release(self):
        """释放 LLM 调用许可"""
        pass
```

---

## 6. 数据结构体

### 6.1 用户模型

```json
{
  "id": "uuid",
  "email": "user@example.com",
  "username": "用户名",
  "hashed_password": "bcrypt_hash",
  "plan": "free | pro | enterprise",
  "usage_count": 5,
  "usage_limit": 3,
  "is_active": true,
  "is_admin": false,
  "created_at": "2026-08-13T10:00:00Z",
  "updated_at": "2026-08-13T10:00:00Z"
}
```

### 6.2 优化记录模型

```json
{
  "id": "uuid",
  "user_id": "uuid (nullable)",
  "resume_text": "简历文本",
  "jd_text": "JD文本 (nullable)",
  "section_type": "综合优势",
  "section_content": "模块内容",
  "optimized_text": "优化后文本",
  "changes_summary": ["改动1", "改动2"],
  "match_score": 65,
  "suggestions": [
    {"id": "sug_001", "original": "...", "suggested": "...", "severity": "high"}
  ],
  "model_used": "deepseek-v4-flash",
  "tokens_used": 2048,
  "created_at": "2026-08-13T10:00:00Z"
}
```

### 6.3 RAG 知识库条目

```json
{
  "id": "uuid",
  "text": "简历片段或JD模板内容",
  "metadata": {
    "industry": "AI",
    "position": "产品经理",
    "tags": ["量化", "亮点"],
    "source": "user_upload | admin_add | auto_collect"
  },
  "embedding": [0.123, 0.456, ...],
  "created_at": "2026-08-13T10:00:00Z"
}
```

---

## 7. 契约校验规则

### 7.1 校验内容

每个模块开发完成后，必须通过以下校验：

1. **接口签名校验**：路由路径、方法、参数名与 OpenAPI 文档一致
2. **响应格式校验**：response 的 `data` 字段结构与文档一致
3. **错误码校验**：所有错误使用统一的错误码和结构
4. **类型校验**：Python 类型注解与实际返回类型一致

### 7.2 校验脚本

```bash
# 运行方式
python scripts/check-contracts.py --module langgraph
python scripts/check-contracts.py --module mcp
python scripts/check-contracts.py --module rag
```