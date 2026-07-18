# ── 火星简历 · 后端 Dockerfile ──────────────────────────────
# 基于 Python 3.11 构建 FastAPI 生产镜像

FROM python:3.11-slim

WORKDIR /app

# 安装系统依赖（pdf2image 需要 poppler-utils）
RUN apt-get update && apt-get install -y --no-install-recommends \
    poppler-utils \
    && rm -rf /var/lib/apt/lists/*

# 复制依赖并安装
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 复制源码
COPY . .

# 创建上传目录
RUN mkdir -p uploads

# 暴露端口
EXPOSE 8000

# 生产启动（关闭 reload，开启多 worker）
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "2"]