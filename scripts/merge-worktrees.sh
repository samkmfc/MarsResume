#!/bin/bash
# worktree 合并脚本 — 按批次将各模块分支合并到 master
# 用法: bash scripts/merge-worktrees.sh [batch]

set -e

BATCH=${1:-all}

echo "=========================================="
echo " MarsResume worktree 合并脚本"
echo "=========================================="

# 确保在 master 分支
git checkout master
git pull origin master 2>/dev/null || true

merge_branch() {
    local branch=$1
    local name=$2
    echo ""
    echo "--- 合并 $name ($branch) ---"
    if git branch --list "$branch" | grep -q "$branch"; then
        if git merge --no-ff "$branch" -m "Merge $name into master" 2>/dev/null; then
            echo "✅ $name 合并成功"
        else
            echo "❌ $name 合并冲突，请手动解决"
            echo "   解决后运行: git merge --continue"
            exit 1
        fi
    else
        echo "⚠️  分支 $branch 不存在，跳过"
    fi
}

case $BATCH in
    1|batch1)
        echo "批次1: 核心底层模块"
        merge_branch "feat/langgraph-workflow" "LangGraph + 多Agent"
        merge_branch "feat/mcp-server" "MCP Server"
        ;;
    2|batch2)
        echo "批次2: 业务能力层"
        merge_branch "feat/rag-knowledge-base" "RAG 知识库"
        merge_branch "feat/saas-auth" "SaaS 鉴权"
        ;;
    3|batch3)
        echo "批次3: 上层交互"
        merge_branch "feat/frontend-upgrade" "前端升级"
        ;;
    all)
        echo "全批次合并"
        merge_branch "feat/langgraph-workflow" "LangGraph + 多Agent"
        merge_branch "feat/mcp-server" "MCP Server"
        merge_branch "feat/rag-knowledge-base" "RAG 知识库"
        merge_branch "feat/saas-auth" "SaaS 鉴权"
        merge_branch "feat/frontend-upgrade" "前端升级"
        echo ""
        echo "✅ 所有模块合并完成"
        echo "运行契约校验: python scripts/check-contracts.py --all"
        ;;
    *)
        echo "用法: bash scripts/merge-worktrees.sh [batch1|batch2|batch3|all]"
        exit 1
        ;;
esac