<div align="center">
  <img src="frontend/public/Mars.png" width="88" alt="MarsResume Logo" />
  <h1 align="center">火星简历 · MarsResume</h1>
  <p align="center">
    <strong>AI 驱动的简历优化工具</strong><br />
    上传简历 + 粘贴 JD → AI 逐条分析差距 → 采纳建议导出 PDF
  </p>
  <p>
    <img src="https://img.shields.io/badge/React-18.2-61DAFB?logo=react&logoColor=white" alt="React" />
    <img src="https://img.shields.io/badge/Vite-5-646CFF?logo=vite&logoColor=white" alt="Vite" />
    <img src="https://img.shields.io/badge/FastAPI-0.115-009688?logo=fastapi&logoColor=white" alt="FastAPI" />
    <img src="https://img.shields.io/badge/Python-3.11-3776AB?logo=python&logoColor=white" alt="Python" />
  </p>
</div>

---

## 📋 项目简介

火星简历是基于 **Skill 方法论** 的 AI 简历模块优化工具。它深度对比简历与目标 JD，逐条分析差距并给出精准的修改建议，采纳后一键导出排版一致的 PDF。

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
| ⚡ **流式实时输出** | AI 分析结果边生成边展示，无需等待完整响应 |
| 🛡️ **安全防护** | 输入注入检测、速率限制、请求验证 |
| 🔌 **多模型支持** | 兼容 OpenAI 格式的任意 LLM API（支持 DeepSeek / GLM 等国产模型） |

---

## 🏗️ 技术架构

```
┌─────────────────────────────────────────────────────┐
│                  浏览器 (React SPA)                    │
│              Vite Dev Server :5173                    │
│                        │                              │
│                   /api/* proxy                         │
│                        ▼                              │
│              FastAPI Backend :8000                    │
│                        │                              │
│        ┌───────────────┼───────────────┐             │
│        ▼               ▼               ▼             │
│   LLM Client    File Parser      Docx Editor         │
│   (OpenAI SDK)  (PyMuPDF)       (python-docx)        │
│        │                                              │
│        ▼                                              │
│   Sensenova / DeepSeek / GLM ...                      │
└─────────────────────────────────────────────────────┘
```

### 技术栈

| 层 | 技术 |
|------|------|
| **前端** | React 18 + Vite 5 + CSS Variables |
| **后端** | Python 3.11 + FastAPI + Uvicorn |
| **数据库** | 本地 JSON 文件持久化 |
| **LLM SDK** | OpenAI Python SDK（兼容格式） |
| **文件处理** | PyMuPDF (PDF)、python-docx (Word)、Pillow (图片) |
| **PDF 生成** | python-docx 替换 → ReportLab 导出 |

---

## 🚀 快速开始

### 前置条件

- Node.js ≥ 18
- Python ≥ 3.11
- 一个兼容 OpenAI 格式的 LLM API Key

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
```

### 3. 启动后端

```bash
cd backend
uvicorn main:app --reload --port 8000
# → http://localhost:8000
# → API 文档: http://localhost:8000/docs
```

### 4. 使用

打开 `http://localhost:5173`，上传简历 → 粘贴 JD → 点击分析。

> **系统依赖说明：** 后端依赖 `pdf2image` 库，在 Linux/macOS 上需安装 `poppler-utils`：  
> `sudo apt install poppler-utils` / `brew install poppler`

---

## 📁 项目结构

```
MarsResume/
├── frontend/                        # React 前端
│   ├── public/
│   │   └── Mars.png                 # Logo 图标
│   └── src/
│       ├── App.jsx                  # 主应用（路由/布局）
│       ├── index.css                # 全局样式
│       ├── context/
│       │   └── FormContext.jsx       # 全局状态管理
│       └── components/
│           ├── StepIndicator.jsx     # 步骤指示器
│           ├── ResumeInput.jsx       # 简历/JD 输入面板
│           ├── SuggestionList.jsx    # 修改建议列表
│           ├── ApiConfig.jsx         # API 配置面板
│           ├── QuestionFlow.jsx      # 智能问答流
│           └── ResultDisplay.jsx     # 结果对比展示
│
├── backend/                         # Python 后端
│   ├── main.py                      # FastAPI 入口 & 路由
│   ├── config.py                    # 统一配置管理
│   ├── requirements.txt             # Python 依赖
│   ├── .env                         # 环境变量（已 gitignore）
│   ├── schemas/                     # Pydantic 模型
│   │   ├── request.py               # 请求模型
│   │   ├── response.py              # 响应模型
│   │   └── file.py                  # 文件上传模型
│   ├── services/                    # 核心业务逻辑
│   │   ├── llm_client.py            # LLM API 客户端
│   │   ├── skill_engine.py          # Skill 分析引擎
│   │   ├── jd_analyzer.py           # JD 解析器
│   │   ├── file_parser.py           # 文件上传 & 文本提取
│   │   └── docx_editor.py           # Word 替换 & PDF 导出
│   ├── middleware/
│   │   └── exception_handler.py     # 全局异常处理
│   ├── utils/
│   │   ├── ai_utils.py              # AI 工具函数（注入防护）
│   │   ├── pdf_generator.py         # PDF 生成引擎
│   │   └── rate_limit.py            # API 速率限制
│   └── data/
│       └── db.py                    # JSON 持久化
│
├── Mars.png                         # Logo 源文件
├── .gitignore
└── README.md
```

---

## 📡 API 接口

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/api/status` | 健康检查 & API 配置状态 |
| POST | `/api/optimize` | 提交完整优化请求 |
| POST | `/api/optimize/stream` | **流式优化**（SSE，实时输出） |
| POST | `/api/resume/upload` | 上传简历文件（PDF/Word/图片） |
| POST | `/api/resume/analyze` | 分析简历与 JD 匹配度 |
| POST | `/api/resume/export-pdf` | 导出优化后的 PDF |
| GET | `/api/section-types` | 获取简历模块类型列表 |
| GET | `/api/config` | 获取当前配置 |
| GET | `/api/history` | 获取优化历史列表 |
| GET | `/api/history/{id}` | 获取单条优化详情 |

完整 API 文档请访问 `http://localhost:8000/docs` (Swagger UI)。

---

## 🧠 Skill 方法论

火星简历的核心基于 **Skill 方法论** —— 将简历优化分解为三个递进阶段：

| 阶段 | 描述 |
|------|------|
| **Step 1 · 定位现状** | 提取简历各模块原文，识别当前表述 |
| **Step 2 · 定位差异** | 逐条对比 JD 要求，找出匹配度差距 |
| **Step 3 · 生成建议** | 为每条差异生成「原文→改法→原因」的结构化建议 |

这种结构化方法确保了建议的准确性、可解释性和可操作性。

---

## 🔧 生产部署

详见 [部署指南](#-部署指南)，推荐单台 VPS + Nginx 反代方案：

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
    }
}
```

---

## 🧪 测试

```bash
# 后端
cd backend
python -c "
from main import app
from fastapi.testclient import TestClient
client = TestClient(app)
resp = client.get('/api/status')
print('Status:', resp.status_code, resp.json())
"
```

---

## 🛤️ 路线图

- [x] 简历文件解析（PDF / Word / 图片）
- [x] 流式 AI 分析输出
- [x] Word → PDF 排版保留导出
- [ ] AI 简历打分功能
- [ ] 多语言简历优化
- [ ] 用户系统 & 历史记录管理
- [ ] 批量简历处理
- [ ] 面试题库生成

---

## 📄 许可证

本项目基于 [Apache License 2.0](LICENSE) 开源。

---

<div align="center">
  <sub>Built with ❤️ by <a href="https://github.com/samkmfc">@samkmfc</a></sub>
</div>
