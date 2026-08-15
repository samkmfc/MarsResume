<div align="center">
  <img src="frontend/public/Mars.png" width="500" alt="MarsResume Logo" />
  <h1 align="center">火星简历 · MarsResume</h1>
  <p align="center">
    <strong>AI 驱动的简历优化工具</strong><br />
    上传简历 + 粘贴 JD → AI 逐条分析差距 → 采纳建议导出 PDF
  </p>
  <p>
    <img src="https://img.shields.io/badge/React-18.2-61DAFB?logo=react&logoColor=white" alt="React" />
    <img src="https://img.shields.io/badge/TypeScript-5.3-3178C6?logo=typescript&logoColor=white" alt="TypeScript" />
    <img src="https://img.shields.io/badge/Vite-5-646CFF?logo=vite&logoColor=white" alt="Vite" />
    <img src="https://img.shields.io/badge/FastAPI-0.115-009688?logo=fastapi&logoColor=white" alt="FastAPI" />
    <img src="https://img.shields.io/badge/LangGraph-✓-1A1A1A" alt="LangGraph" />
    <img src="https://img.shields.io/badge/Python-3.11-3776AB?logo=python&logoColor=white" alt="Python" />
  </p>
</div>

---

## 📋 项目简介

火星简历是基于 **Skill 方法论** 的 AI 简历模块优化工具。它深度对比简历与目标 JD，逐条分析差距并给出精准的修改建议，采纳后一键导出排版一致的 PDF。

v3.0 在原有单机工具基础上，引入 **LangGraph 工作流编排、MCP Server、RAG 知识库、JWT 鉴权与 SaaS 多租户能力**，从"单脚本工具"演进为模块化、可扩展的服务架构。

### 核心工作流

```
📄 上传简历 + 📝 粘贴 JD  →  🤖 AI 逐条分析  →  ✅ 采纳/拒绝建议  →  📎 导出 PDF
```

---

## ✨ 功能特性

| 特性 | 说明 |
|------|------|
| 🎯 **JD 精准对齐** | AI 逐条对比简历内容与职位要求，定位差距 |
| ✏️ **逐条修改建议** | 每条建议包含「原文 → 改法 → 原因」，可单独采纳/拒绝 |
| 📄 **Word 排版保留** | 基于原始 .docx 文件精确文本替换，导出排版一致的 PDF |
| ⚡ **流式实时输出** | AI 分析结果边生成边展示（SSE），无需等待完整响应 |
| 🔁 **LangGraph 五步流水线** | 深挖 → 亮点 → 生成 → 指标检查 → 自检，含质量回路与重试 |
| 🧠 **RAG 知识库** | ChromaDB 向量检索，沉淀优秀范例 / JD 模板为优化上下文 |
| 🔌 **MCP Server** | 暴露优化能力为模型上下文协议工具，可被外部 Agent 调用 |
| 🛡️ **JWT 鉴权 + SaaS 计费** | 用户注册/登录、用量计数、Admin 后台、套餐管理 |
| 🔒 **安全防护** | 输入注入检测、速率限制、请求验证 |
| 🤖 **多模型支持** | 兼容 OpenAI 格式的任意 LLM API（DeepSeek / GLM 等国产模型） |

---

## 🏗️ 技术架构

```
┌─────────────────────────────────────────────────────────────┐
│                   浏览器 (React SPA)                          │
│        Vite Dev Server :5173 · Zustand · Tailwind             │
│                          │                                    │
│                     /api/* proxy                              │
│                          ▼                                    │
│                FastAPI Backend :8000                          │
│                          │                                    │
│   ┌──────────────┬───────────┴──────────┬──────────────┐    │
│   ▼              ▼                      ▼              ▼     │
│ SkillEngine   LangGraph              Auth/JWT       Routes   │
│ (五步流水线)   StateGraph            Middleware     auth/    │
│   │              │                                    admin/  │
│   │         ┌────┴────┐                                rag/    │
│   ▼         ▼         ▼                                       │
│ LLM Client  Agents   RAG Service (ChromaDB)                  │
│ (OpenAI SDK) (OO封装) + Embedding                            │
│   │                                                           │
│   ▼                                                           │
│   Sensenova / DeepSeek / GLM ...                              │
│                                                               │
│   持久化分层：  JSON storage → 优化历史                        │
│                SQLAlchemy   → 用户 / SaaS 计费                │
│                ChromaDB     → 向量知识库                      │
└─────────────────────────────────────────────────────────────┘
```

### 技术栈

| 层 | 技术 |
|------|------|
| **前端** | React 18 + TypeScript 5 + Vite 5 + Zustand + Tailwind CSS |
| **后端** | Python 3.11 + FastAPI + Uvicorn |
| **工作流** | LangGraph（状态图编排 + 条件回路） |
| **Agent** | 面向对象 Agent 体系（Coordinator / DeepDive / Highlight / Writer / Reviewer） |
| **MCP** | 模型上下文协议 Server（暴露优化能力为工具） |
| **RAG** | ChromaDB + sentence-transformers 向量检索 |
| **鉴权** | JWT + SaaS 多租户（用量计数 / 套餐） |
| **数据库** | JSON（优化历史）+ SQLAlchemy/SQLite（用户）+ ChromaDB（向量） |
| **LLM SDK** | OpenAI Python SDK（兼容格式） |
| **文件处理** | PyMuPDF (PDF)、python-docx (Word)、Pillow (图片) |
| **PDF 生成** | python-docx 替换 → ReportLab / Word COM 导出 |

---

## 🚀 快速开始

### 前置条件

- Node.js ≥ 18
- Python ≥ 3.11
- 一个兼容 OpenAI 格式的 LLM API Key
- （可选）启用 RAG：`pip install chromadb sentence-transformers`
- （可选）Word→PDF 高保真导出：Windows 需安装 Microsoft Word（走 COM）

### 1. 克隆 & 安装

```bash
git clone https://github.com/samkmfc/MarsResume.git
cd MarsResume
```

#### 前端

```bash
cd frontend
npm install
npm run dev     # → http://localhost:5173
```

#### 后端

```bash
cd backend
python -m venv venv
# Windows: venv\Scripts\activate
# macOS/Linux: source venv/bin/activate
pip install -r requirements.txt
```

### 2. 配置环境变量

```bash
cp backend/.env.example backend/.env
```

编辑 `backend/.env`：

```ini
# LLM API 配置
LLM_API_KEY=your_api_key_here
LLM_BASE_URL=https://token.sensenova.cn/v1
LLM_MODEL=deepseek-v4-flash

# 服务端口
SERVER_PORT=8000

# CORS 允许的前端地址
CORS_ORIGINS=http://localhost:5173,http://localhost:3000

# JWT 鉴权（SaaS）
JWT_SECRET=your_jwt_secret_here
JWT_ALGORITHM=HS256
JWT_EXPIRE_MINUTES=1440
```

### 3. 启动后端

```bash
cd backend
uvicorn main:app --reload --port 8000
# → http://localhost:8000
# → API 文档: http://localhost:8000/docs
```

### 4. （可选）启动 MCP Server

```bash
cd backend
python -m mcp_server.run
```

### 5. 使用

打开 `http://localhost:5173`，上传简历 → 粘贴 JD → 点击分析。

> **系统依赖说明：** 后端依赖 `pdf2image` 库，在 Linux/macOS 上需安装 `poppler-utils`：
> `sudo apt install poppler-utils` / `brew install poppler`

---

## 📁 项目结构

```
MarsResume/
├── frontend/                        # React + TypeScript 前端
│   └── src/
│       ├── App.tsx                  # 主应用（路由/布局）
│       ├── main.tsx                 # 入口
│       ├── index.css                # 全局样式 (Tailwind)
│       ├── stores/
│       │   └── appStore.ts          # Zustand 全局状态
│       ├── services/
│       │   └── api.ts               # API 客户端
│       ├── types/
│       │   └── index.ts             # 类型定义
│       └── components/
│           ├── Header.tsx
│           ├── FeatureGrid.tsx
│           ├── StepIndicator.tsx     # 步骤指示器
│           ├── ResumeInput.tsx       # 简历/JD 输入面板
│           ├── SuggestionList.tsx    # 修改建议列表
│           ├── ApiConfig.jsx         # API 配置面板
│           ├── QuestionFlow.jsx      # 智能问答流
│           ├── ResultDisplay.jsx     # 结果对比展示
│           ├── FAQ.tsx
│           └── Footer.tsx
│
├── backend/                         # Python 后端
│   ├── main.py                      # FastAPI 入口 & 核心路由
│   ├── config.py                    # 统一配置管理
│   ├── agents/                      # Agent 体系（LangGraph 节点的 OO 封装）
│   │   ├── base.py                  # BaseAgent 抽象基类
│   │   ├── coordinator_agent.py     # 路由协调
│   │   ├── deep_dive_agent.py       # 深挖分析
│   │   ├── highlight_agent.py       # 亮点识别
│   │   ├── writer_agent.py          # 文案生成
│   │   ├── reviewer_agent.py        # 自检审阅
│   │   └── registry.py              # Agent 注册表
│   ├── graph/                       # LangGraph 工作流
│   │   ├── state.py                 # 优化状态定义
│   │   ├── nodes.py                 # 图节点实现
│   │   └── workflow.py              # 图构建与编译
│   ├── mcp_server/                  # MCP Server（模型上下文协议）
│   │   ├── server.py
│   │   └── run.py
│   ├── auth/                        # JWT 鉴权
│   │   ├── jwt.py
│   │   ├── deps.py
│   │   └── middleware.py
│   ├── routes/                      # 路由模块
│   │   ├── auth.py                  # /api/auth/*
│   │   ├── admin.py                 # /api/admin/*
│   │   └── rag.py                   # /api/rag/*
│   ├── database/                    # SQLAlchemy（用户 / SaaS）
│   │   └── engine.py
│   ├── models/                      # ORM 模型
│   │   ├── base.py
│   │   ├── user.py
│   │   └── optimization.py
│   ├── schemas/                     # Pydantic 模型
│   │   ├── request.py
│   │   ├── response.py
│   │   └── file.py
│   ├── services/                    # 核心业务逻辑
│   │   ├── llm_client.py            # LLM API 客户端
│   │   ├── skill_engine.py          # Skill 分析引擎（五步流水线）
│   │   ├── jd_analyzer.py           # JD 解析器
│   │   ├── file_parser.py           # 文件上传 & 文本提取
│   │   ├── docx_editor.py           # Word 替换 & PDF 导出
│   │   ├── rag_service.py           # RAG 知识库
│   │   ├── embedding_service.py     # 向量嵌入
│   │   ├── cache.py
│   │   └── event_bus.py
│   ├── middleware/
│   │   ├── exception_handler.py     # 全局异常处理
│   │   ├── exceptions.py
│   │   └── rate_limiter.py
│   ├── utils/
│   │   ├── ai_utils.py              # AI 工具函数（注入防护）
│   │   ├── pdf_generator.py         # ReportLab PDF 生成
│   │   └── rate_limit.py            # API 速率限制
│   └── data/
│       ├── db.py                    # JSON 持久化（优化历史）
│       └── (marsresume.db / chroma_db/ 运行时生成，不入库)
│
├── docs/                            # 架构文档 + 接口契约
├── scripts/
│   └── check-contracts.py           # 接口契约校验
├── docker-compose.yml
├── deploy.sh / deploy_aliyun.py     # 部署脚本
├── Mars.png / new2.png              # Logo
└── README.md
```

> **持久化分层说明**：项目使用三套各司其职的存储——
> - `data/db.py`（JSON）保存优化历史记录，轻量、零依赖；
> - `database/engine.py`（SQLAlchemy/SQLite）保存用户与 SaaS 计费数据；
> - ChromaDB 保存 RAG 向量知识库。
> 三者职责不重叠，并非冗余。

---

## 📡 API 接口

### 核心

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/api/status` | 健康检查 & API 配置状态（含 langgraph 可用性） |
| POST | `/api/optimize` | 提交完整优化请求（LangGraph 驱动，支持追问） |
| POST | `/api/optimize/stream` | **流式优化**（SSE，逐 token 推送五步结果） |
| POST | `/api/resume/upload` | 上传简历文件（PDF/Word/图片） |
| POST | `/api/resume/analyze` | 分析简历与 JD 匹配度，返回逐条建议 |
| POST | `/api/resume/export-pdf` | 导出优化后的 PDF |
| GET | `/api/section-types` | 获取简历模块类型列表 |
| GET | `/api/config` | 获取当前配置 |
| GET | `/api/history` | 获取优化历史列表 |
| GET | `/api/history/{id}` | 获取单条优化详情 |

### 鉴权 / SaaS（`/api/auth`）

| 方法 | 路径 | 说明 |
|------|------|------|
| POST | `/api/auth/register` | 用户注册 |
| POST | `/api/auth/login` | 用户登录（返回 JWT） |
| GET | `/api/auth/me` | 获取当前用户信息 |

### 管理后台（`/api/admin`）

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/api/admin/users` | 分页查询用户 |
| PUT | `/api/admin/users/{user_id}/plan` | 修改用户套餐 |

### RAG 知识库（`/api/rag`）

| 方法 | 路径 | 说明 |
|------|------|------|
| POST | `/api/rag/add-example` | 添加优秀范例 |
| POST | `/api/rag/add-jd-template` | 添加 JD 模板 |
| GET | `/api/rag/search` | 向量检索 |
| GET | `/api/rag/stats` | 知识库统计 |

完整 API 文档请访问 `http://localhost:8000/docs` (Swagger UI)。

---

## 🧠 Skill 方法论

火星简历的核心基于 **Skill 方法论** —— 将简历优化分解为递进阶段，并由 LangGraph 编排为带质量回路的状态图：

| 阶段 | 描述 |
|------|------|
| **Step 1 · 定位现状** | 提取简历各模块原文，深挖分析，生成追问问题 |
| **Step 2 · 定位差异** | 识别亮点，逐条对比 JD 要求，找出匹配度差距 |
| **Step 3 · 生成建议** | 为每条差异生成「原文→改法→原因」的结构化建议 |
| **Step 4 · 指标检查** | 校验生成结果的量化指标，不达标则回流重生成 |
| **Step 5 · 自检** | Reviewer 复核，通过则定稿，否则回工 |

这种结构化方法确保了建议的准确性、可解释性和可操作性。

---

## 🔧 生产部署

推荐单台 VPS + Nginx 反代方案：

```nginx
server {
    listen 80;
    server_name your-domain.com;

    root /path/to/frontend/dist;
    index index.html;
    location / { try_files $uri $uri/ /index.html; }

    location /api/ {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_read_timeout 120s;
        # SSE 流式所需
        proxy_buffering off;
        proxy_cache off;
    }
}
```

Docker 一键部署见 `docker-compose.yml` / `deploy.sh` / `deploy_aliyun.py`。

---

## 🧪 测试

```bash
# 后端
cd backend
pytest                      # 单元 + 接口测试

# 前端
cd frontend
npm run test                # vitest
```

接口契约校验：

```bash
python scripts/check-contracts.py
```

---

## 🛤️ 路线图

- [x] 简历文件解析（PDF / Word / 图片）
- [x] 流式 AI 分析输出
- [x] Word → PDF 排版保留导出
- [x] LangGraph 五步流水线（含质量回路）
- [x] RAG 知识库（范例 / JD 模板检索）
- [x] MCP Server（能力工具化）
- [x] 用户系统 & JWT 鉴权 & SaaS 计费
- [ ] AI 简历打分功能
- [ ] 多语言简历优化
- [ ] 批量简历处理
- [ ] 面试题库生成

---

## 📄 许可证

本项目基于 [Apache License 2.0](LICENSE) 开源。

---

<div align="center">
  <sub>Built with ❤️ by <a href="https://github.com/samkmfc">@samkmfc</a></sub>
</div>
