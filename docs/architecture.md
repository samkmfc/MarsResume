# MarsResume 整体架构设计 v3.0

> 本文档为项目改造的顶层架构设计，定义所有模块的边界、依赖关系和数据流。
> 所有模块开发必须遵循本文档定义的接口契约和通信标准。

---

## 1. 整体分层架构

```
┌─────────────────────────────────────────────────────────────────────┐
│   PRESENTATION LAYER                                                │
│  ┌─────────────────────┐  ┌──────────────────┐  ┌───────────────┐  │
│  │  React SPA (TS)     │  │  MCP Client       │  │  3rd Party    │  │
│  │  Vite + Tailwind    │  │  (Claude/Cursor)  │  │  (API调用)    │  │
│  └─────────┬───────────┘  └────────┬─────────┘  └───────┬───────┘  │
└────────────┼────────────────────────┼────────────────────┼──────────┘
             │        HTTP/SSE        │       MCP stdio    │   HTTP
┌────────────┼────────────────────────┼────────────────────┼──────────┐
│   INTERFACE LAYER                   │                    │          │
│  ┌────────┴──────────┐  ┌──────────┴──────────┐  ┌──────┴───────┐ │
│  │  FastAPI Server   │  │  MCP Server         │  │  Rate Limit  │ │
│  │  REST + SSE       │  │  Tool/Resource API  │  │  Middleware  │ │
│  └────────┬──────────┘  └──────────┬──────────┘  └──────┬───────┘ │
└────────────┼────────────────────────┼────────────────────┼──────────┘
             │                        │                    │
┌────────────┼────────────────────────┼────────────────────┼──────────┐
│   WORKFLOW LAYER                   │                    │          │
│  ┌────────┴────────────────────────┴────────────────────┴───────┐  │
│  │  LangGraph StateGraph                                         │  │
│  │                                                               │  │
│  │  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐     │  │
│  │  │ DeepDive │─▶│Identify  │─▶│ Generate │─▶│  Check   │     │  │
│  │  │  Node    │  │Highlights│  │  Node    │  │ Metrics  │     │  │
│  │  └──────────┘  └──────────┘  └──────────┘  └────┬─────┘     │  │
│  │       │                                            │         │  │
│  │       ▼                                            ▼         │  │
│  │  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐     │  │
│  │  │  Ask     │  │  Review  │◀─│  Retry   │◀─│  Fail    │     │  │
│  │  │  User    │  │  Node    │  │  Node    │  │  Node    │     │  │
│  │  └──────────┘  └──────────┘  └──────────┘  └──────────┘     │  │
│  └──────────────────────────────────────────────────────────────┘  │
└────────────────────────────────────────────────────────────────────┘
                             │
┌────────────────────────────┼────────────────────────────────────────┐
│   AGENT LAYER             │                                        │
│  ┌──────────────────────────────────────────────────────────────┐  │
│  │  Agent Registry (协调调度)                                    │  │
│  │                                                               │  │
│  │  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐       │  │
│  │  │ Parser Agent │  │ JD Analyzer  │  │ Writer Agent │       │  │
│  │  │ (简历解析)    │  │ Agent (JD分析)│  │ (优化写作)    │       │  │
│  │  └──────────────┘  └──────────────┘  └──────────────┘       │  │
│  │  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐       │  │
│  │  │ Reviewer     │  │ Interview    │  │ Coordinator  │       │  │
│  │  │ Agent (质检)  │  │ Agent (面试)  │  │ Agent (协调)  │       │  │
│  │  └──────────────┘  └──────────────┘  └──────────────┘       │  │
│  └──────────────────────────────────────────────────────────────┘  │
└────────────────────────────────────────────────────────────────────┘
                             │
┌────────────────────────────┼────────────────────────────────────────┐
│   SERVICE LAYER            │                                        │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐              │
│  │  LLM Client  │  │  File Parser │  │  Docx Editor │              │
│  │  (OpenAI SDK)│  │  (PyMuPDF)   │  │  (python-docx)              │
│  └──────────────┘  └──────────────┘  └──────────────┘              │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐              │
│  │  RAG Service │  │  Embedding   │  │  PDF Generator              │
│  │  (向量检索)   │  │  Service     │  │  (ReportLab)  │              │
│  └──────────────┘  └──────────────┘  └──────────────┘              │
└────────────────────────────────────────────────────────────────────┘
                             │
┌────────────────────────────┼────────────────────────────────────────┐
│   DATA LAYER              │                                        │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐              │
│  │  PostgreSQL  │  │  ChromaDB    │  │  Redis Cache │              │
│  │  (业务数据)   │  │  (向量数据)   │  │  (限流/会话)  │              │
│  └──────────────┘  └──────────────┘  └──────────────┘              │
│  ┌──────────────┐  ┌──────────────┐                                │
│  │  SQLAlchemy  │  │  JSON File   │                                │
│  │  ORM         │  │  (兼容层)     │                                │
│  └──────────────┘  └──────────────┘                                │
└────────────────────────────────────────────────────────────────────┘
```

---

## 2. 模块依赖关系图

```
                    ┌──────────────────┐
                    │   Frontend (TS)  │
                    │   React + Zustand│
                    └────────┬─────────┘
                             │ HTTP/SSE
                             ▼
                    ┌──────────────────┐
                    │  FastAPI Server  │◄──── MCP Client
                    │  (main.py)       │       (stdio)
                    └────────┬─────────┘
                             │
              ┌──────────────┼────────────────┐
              ▼              ▼                ▼
     ┌────────────────┐ ┌──────────┐ ┌──────────────┐
     │ LangGraph      │ │ Auth     │ │ MCP Server   │
     │ Workflow Engine│ │ Middleware│ │ (mcp/run.py) │
     └───────┬────────┘ └──────────┘ └──────────────┘
             │
             ▼
     ┌──────────────────┐
     │  Agent Registry  │
     │  (coordinator)   │
     └──┬────┬────┬────┬┘
        │    │    │    │
        ▼    ▼    ▼    ▼
   ┌────┐ ┌──┐ ┌──┐ ┌────┐
   │Parser│ │JD│ │Writer│ │Review│
   │Agent │ │Ana│ │Agent │ │Agent │
   └──┬───┘ └┬─┘ └──┬──┘ └──┬──┘
      │      │      │       │
      └──────┼──────┼───────┘
             ▼      ▼
     ┌──────────────────┐
     │   LLM Client     │
     │   (OpenAI SDK)   │
     └────────┬─────────┘
              │
              ▼
     ┌──────────────────┐
     │   RAG Service    │
     │   (ChromaDB)     │
     └──────────────────┘
```

### 依赖传递规则

| 模块 | 依赖项 | 依赖方向 |
|------|--------|----------|
| Frontend | FastAPI HTTP API | 消费者 |
| MCP Server | FastAPI 内部服务层 | 消费者 |
| FastAPI Router | LangGraph Workflow, Auth Middleware | 编排 |
| LangGraph Workflow | Agent Registry, LLM Client | 调用 |
| Agent Registry | 各 Agent 实现 | 注册 |
| 各 Agent | LLM Client, RAG Service | 调用 |
| RAG Service | ChromaDB, Embedding Service | 数据 |
| Auth Middleware | Database (User Model) | 数据 |
| LLM Client | 外部 LLM API | 网络 |

---

## 3. 数据流走向

### 3.1 简历优化主流程

```
用户上传简历 + 粘贴 JD
       │
       ▼
┌──────────────────┐     ┌──────────────────┐
│  POST /api/      │     │  文件上传流程     │
│  resume/analyze  │     │  POST /api/      │
│  (文本分析)       │     │  resume/upload   │
└────────┬─────────┘     └────────┬─────────┘
         │                        │
         ▼                        ▼
   ┌──────────┐            ┌──────────────┐
   │ JD       │            │ File Parser  │
   │ Analyzer │            │ (PyMuPDF)    │
   │ Agent    │            └──────────────┘
   └────┬─────┘                    │
        │                          │
        ▼                          ▼
   ┌──────────┐            ┌──────────────┐
   │ 生成     │            │ 结构化文本   │
   │ 修改建议 │            │              │
   └────┬─────┘            └──────────────┘
        │                          │
        └──────────┬───────────────┘
                   ▼
          ┌──────────────────┐
          │  LangGraph       │
          │  Workflow Engine │
          │  1. Deep Dive    │
          │  2. Highlights   │
          │  3. Generate     │
          │  4. Check        │
          │  5. Review       │
          └────────┬─────────┘
                   │
                   ▼
          ┌──────────────────┐
          │  SSE Stream      │
          │  → 前端实时展示   │
          └──────────────────┘
```

### 3.2 用户认证流程

```
用户请求
   │
   ▼
Auth Middleware 拦截
   │
   ├─ 无 Token → 放行（匿名用户，基础功能）
   │
   └─ 有 Token → 验证 JWT
          │
          ├─ 无效 → 返回 401
          │
          └─ 有效 → 注入当前用户 → 检查套餐限额
                 │
                 ├─ 超限 → 返回 429 (升级提示)
                 │
                 └─ 正常 → 放行到业务逻辑
```

### 3.3 MCP 通信流程

```
MCP Client (Claude Desktop)
   │
   │  stdio transport
   ▼
MCP Server (mcp/run.py)
   │
   │  解析工具调用请求
   ▼
┌──────────────────┐
│  Tool Router     │
│  ├─ parse_resume │
│  ├─ analyze_jd   │
│  ├─ optimize     │
│  └─ get_history  │
└────────┬─────────┘
         │
         ▼
   FastAPI 内部服务层
   (复用现有 services/)
         │
         ▼
   LLM + RAG 处理
         │
         ▼
   返回 MCP 标准响应
```

---

## 4. 技术栈决策

| 层 | 技术 | 选型理由 |
|----|------|----------|
| **前端框架** | React 18 + TypeScript | 现有项目基础，TS 提供类型安全 |
| **前端构建** | Vite 5 | 现有，极快 HMR |
| **前端样式** | Tailwind CSS 3 | 原子化 CSS，避免样式冲突 |
| **前端状态** | Zustand 4 | 轻量（<1KB），无 boilerplate |
| **后端框架** | FastAPI | 现有，异步支持好 |
| **工作流引擎** | LangGraph | 有状态图，支持条件分支/回退/HITL |
| **LLM SDK** | OpenAI Python SDK | 现有，兼容国产模型 |
| **向量数据库** | ChromaDB | 轻量级，无需单独部署，嵌入项目 |
| **Embedding** | sentence-transformers | 本地运行，无 API 依赖 |
| **业务数据库** | SQLite/PostgreSQL | SQLAlchemy ORM 抽象，可切换 |
| **认证** | python-jose + passlib | JWT 标准，bcrypt 密码哈希 |
| **MCP 协议** | mcp (fastmcp) | 官方 SDK，支持 stdio/SSE |
| **缓存/限流** | 内存 + Redis（可选） | 本地内存兜底，Redis 可插拔 |

---

## 5. 目录结构（最终目标）

```
MarsResume/
├── docs/                          # 架构文档
│   ├── architecture.md            # 本文件
│   ├── openapi-schema.yaml        # OpenAPI3.0 契约
│   └── contracts.md               # 模块间通信契约
│
├── backend/
│   ├── main.py                    # FastAPI 入口（路由注册）
│   ├── config.py                  # 全局配置
│   ├── requirements.txt           # 依赖清单
│   │
│   ├── routes/                    # API 路由层
│   │   ├── __init__.py
│   │   ├── optimize.py            # 优化相关接口
│   │   ├── resume.py              # 简历文件接口
│   │   ├── auth.py                # 认证接口
│   │   ├── admin.py               # 管理接口
│   │   └── rag.py                 # RAG 管理接口
│   │
│   ├── graph/                     # LangGraph 工作流
│   │   ├── __init__.py
│   │   ├── state.py               # 状态定义
│   │   ├── nodes.py               # 图节点函数
│   │   └── workflow.py            # 图构建与编译
│   │
│   ├── agents/                    # 多 Agent 系统
│   │   ├── __init__.py
│   │   ├── base.py                # BaseAgent 抽象类
│   │   ├── registry.py            # Agent 注册中心
│   │   ├── parser_agent.py        # 简历解析 Agent
│   │   ├── jd_analyzer_agent.py   # JD 分析 Agent
│   │   ├── writer_agent.py        # 优化写作 Agent
│   │   ├── reviewer_agent.py      # 质量检查 Agent
│   │   ├── interview_agent.py     # 面试题 Agent
│   │   └── coordinator_agent.py   # 协调 Agent
│   │
│   ├── mcp/                       # MCP Server
│   │   ├── __init__.py
│   │   ├── server.py              # MCP 工具定义
│   │   └── run.py                 # MCP 启动入口
│   │
│   ├── services/                  # 业务服务层（现有 + 新增）
│   │   ├── llm_client.py          # LLM 客户端（增强）
│   │   ├── skill_engine.py        # 兼容层（对接 LangGraph）
│   │   ├── jd_analyzer.py         # JD 分析（保留兼容）
│   │   ├── file_parser.py         # 文件解析
│   │   ├── docx_editor.py         # Word 编辑
│   │   ├── pdf_generator.py       # PDF 生成
│   │   ├── rag_service.py         # RAG 检索服务
│   │   └── embedding_service.py   # Embedding 服务
│   │
│   ├── auth/                      # 认证鉴权
│   │   ├── __init__.py
│   │   ├── jwt.py                 # JWT 工具
│   │   ├── middleware.py          # FastAPI 中间件
│   │   └── deps.py                # 依赖注入
│   │
│   ├── models/                    # 数据模型
│   │   ├── __init__.py
│   │   ├── base.py                # SQLAlchemy Base
│   │   ├── user.py                # 用户模型
│   │   └── optimization.py        # 优化记录模型
│   │
│   ├── database/                  # 数据库层
│   │   ├── __init__.py
│   │   ├── engine.py              # 引擎与会话
│   │   └── migrations/            # 迁移脚本
│   │
│   ├── middleware/                # 中间件
│   │   ├── __init__.py
│   │   ├── exception_handler.py   # 异常处理（现有）
│   │   └── rate_limit.py          # 限流器（增强）
│   │
│   ├── utils/                     # 工具函数
│   │   ├── ai_utils.py            # AI 工具函数（现有）
│   │   ├── pdf_generator.py       # PDF 生成（现有）
│   │   └── rate_limit.py          # 限流工具（现有）
│   │
│   └── data/                      # 数据文件
│       ├── db.py                  # JSON 存储（兼容层）
│       ├── chroma_db/             # ChromaDB 持久化
│       └── storage.json           # 旧 JSON 存储
│
├── frontend/
│   ├── src/
│   │   ├── main.tsx               # 入口
│   │   ├── App.tsx                # 主应用
│   │   ├── index.css              # 全局样式（Tailwind）
│   │   │
│   │   ├── types/                 # TypeScript 类型
│   │   │   └── index.ts
│   │   │
│   │   ├── stores/                # Zustand 状态
│   │   │   └── appStore.ts
│   │   │
│   │   ├── hooks/                 # 自定义 Hooks
│   │   │   └── useApi.ts
│   │   │
│   │   ├── components/            # 组件
│   │   │   ├── Header.tsx
│   │   │   ├── Hero.tsx
│   │   │   ├── FeatureGrid.tsx
│   │   │   ├── StepIndicator.tsx
│   │   │   ├── ResumeInput.tsx
│   │   │   ├── SuggestionList.tsx
│   │   │   ├── ResultDisplay.tsx
│   │   │   ├── Footer.tsx
│   │   │   └── FAQ.tsx
│   │   │
│   │   └── services/              # API 调用
│   │       └── api.ts
│   │
│   ├── package.json
│   ├── tsconfig.json
│   ├── tailwind.config.js
│   └── vite.config.ts
│
├── scripts/                       # 工具脚本
│   ├── check-contracts.py         # 契约校验脚本
│   └── merge-worktrees.sh         # worktree 合并脚本
│
├── docker-compose.yml             # Docker 部署
├── deploy.sh                      # 部署脚本
└── README.md
```

---

## 6. 接口命名规范

| 规范 | 规则 |
|------|------|
| HTTP 方法 | GET 查询 / POST 创建 / PUT 更新 / DELETE 删除 |
| 路径格式 | `/api/{resource}` 或 `/api/{resource}/{id}` |
| 版本前缀 | 暂不启用版本，用 `/api/` 前缀 |
| 响应格式 | 统一 `{success, data, error, meta}` |
| 错误码 | 统一 `{code, message, detail}` 结构 |
| 分页 | 统一 `{items, total, page, page_size}` |
| SSE 事件 | 统一 `event: {type}\ndata: {json}` |

---

## 7. 模块边界定义

| 模块 | 职责边界 | 禁止行为 |
|------|----------|----------|
| LangGraph | 编排工作流、控制状态流转、条件分支判断 | 不直接调用 LLM，不处理业务逻辑 |
| Agent | 执行具体 LLM 任务、解析响应 | 不控制工作流，不访问数据库 |
| Services | 纯业务逻辑、文件处理、LLM 封装 | 不包含工作流控制逻辑 |
| Routes | 参数校验、路由分发、响应格式化 | 不包含业务逻辑 |
| Models | 数据模型定义、ORM 映射 | 不包含业务逻辑 |
| MCP | 协议适配、工具注册、传输管理 | 不包含业务逻辑 |

---

## 8. 限流与重试策略

| 策略 | 值 |
|------|-----|
| 全局并发 Agent 上限 | 2 |
| 单 Agent 每分钟 LLM 调用上限 | 15 次 |
| 429 重试策略 | 指数退避：2s → 4s → 8s → 16s |
| 最大重试次数 | 5 次 |
| 超限处理 | 自动休眠 Agent，释放配额给其他 Agent |