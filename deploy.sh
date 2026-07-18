#!/bin/bash
# ── 火星简历 · 阿里云部署脚本 ──────────────────────────────
# 用法：chmod +x deploy.sh && ./deploy.sh
# 说明：在阿里云 Ubuntu 服务器上首次部署时运行

set -e

echo "========================================"
echo "   🔵 火星简历 · MarsResume 部署脚本"
echo "========================================"
echo ""

# ── 1. 检查系统 ────────────────────────────────────────────
echo "[1/6] 检查系统环境..."
if ! command -v docker &> /dev/null; then
    echo "  → 安装 Docker..."
    curl -fsSL https://get.docker.com | bash
    sudo usermod -aG docker "$USER"
    echo "  ✅ Docker 安装完成"
else
    echo "  ✅ Docker 已安装: $(docker --version)"
fi

if ! command -v docker compose &> /dev/null; then
    echo "  → 安装 Docker Compose..."
    sudo apt-get update
    sudo apt-get install -y docker-compose-plugin
    echo "  ✅ Docker Compose 安装完成"
else
    echo "  ✅ Docker Compose 已安装"
fi

# ── 2. 配置环境变量 ────────────────────────────────────────
echo ""
echo "[2/6] 配置环境变量..."
if [ ! -f .env ]; then
    if [ -f .env.production ]; then
        cp .env.production .env
        echo "  ⚠️  已从 .env.production 创建 .env 文件"
        echo "  ⚠️  请编辑 .env 填入你的 LLM_API_KEY:"
        echo "      nano .env"
        echo "      然后重新运行此脚本"
        exit 1
    else
        echo "  ❌ 未找到 .env.production 文件"
        exit 1
    fi
else
    echo "  ✅ .env 文件已存在"
fi

# 读取服务器 IP
SERVER_IP=$(curl -s http://checkip.amazonaws.com 2>/dev/null || curl -s https://api.ipify.org 2>/dev/null || echo "你的服务器IP")
echo "  ℹ️  服务器公网 IP: $SERVER_IP"

# ── 3. 构建并启动 ──────────────────────────────────────────
echo ""
echo "[3/6] 构建 Docker 镜像..."
docker compose build

echo ""
echo "[4/6] 启动服务..."
docker compose up -d

# ── 4. 检查状态 ────────────────────────────────────────────
echo ""
echo "[5/6] 检查服务状态..."
sleep 3
if docker compose ps | grep -q "Up"; then
    echo "  ✅ 服务运行中"
else
    echo "  ⚠️  服务状态："
    docker compose ps
fi

# ── 5. 配置防火墙 ──────────────────────────────────────────
echo ""
echo "[6/6] 配置防火墙..."
if command -v ufw &> /dev/null; then
    sudo ufw allow 80/tcp 2>/dev/null || true
    echo "  ✅ 防火墙已放行 80 端口"
else
    echo "  ℹ️  请确保阿里云安全组已放行 80 端口"
    echo "     登录阿里云控制台 → 安全组 → 入方向添加:"
    echo "     端口: 80/80, 协议: TCP, 授权对象: 0.0.0.0/0"
fi

echo ""
echo "========================================"
echo "   ✅ 部署完成！"
echo "========================================"
echo ""
echo "   访问地址: http://$SERVER_IP"
echo "   API 文档: http://$SERVER_IP/api/docs"
echo ""
echo "   常用命令:"
echo "   docker compose logs -f        # 查看日志"
echo "   docker compose restart        # 重启服务"
echo "   docker compose pull && docker compose up -d  # 更新"
echo ""
echo "   如果遇到问题，请检查:"
echo "   1. .env 文件中的 LLM_API_KEY 是否正确"
echo "   2. 阿里云安全组是否放行了 80 端口"
echo "   3. 运行 docker compose logs -f 查看详细日志"
echo "========================================"