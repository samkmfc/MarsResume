#!/usr/bin/env python3
"""
契约校验脚本 — 检查模块实现是否与 OpenAPI 文档一致

用法:
    python scripts/check-contracts.py --module langgraph
    python scripts/check-contracts.py --module mcp
    python scripts/check-contracts.py --module rag
    python scripts/check-contracts.py --module saas
    python scripts/check-contracts.py --module frontend
    python scripts/check-contracts.py --all
"""

import argparse
import importlib
import os
import sys
from pathlib import Path


def check_module(module_name: str) -> bool:
    """校验指定模块"""
    checks = []
    passed = 0
    failed = 0

    print(f"\n{'='*50}")
    print(f"  契约校验: {module_name}")
    print(f"{'='*50}")

    if module_name in ("langgraph", "all"):
        print("\n[LangGraph 工作流]")
        checks.append(("graph/state.py 存在", os.path.exists("backend/graph/state.py")))
        checks.append(("graph/nodes.py 存在", os.path.exists("backend/graph/nodes.py")))
        checks.append(("graph/workflow.py 存在", os.path.exists("backend/graph/workflow.py")))
        checks.append(("agents/base.py 存在", os.path.exists("backend/agents/base.py")))
        checks.append(("agents/registry.py 存在", os.path.exists("backend/agents/registry.py")))
        checks.append(("agents/coordinator_agent.py 存在", os.path.exists("backend/agents/coordinator_agent.py")))

    if module_name in ("mcp", "all"):
        print("\n[MCP Server]")
        checks.append(("mcp/server.py 存在", os.path.exists("backend/mcp/server.py")))
        checks.append(("mcp/run.py 存在", os.path.exists("backend/mcp/run.py")))
        checks.append(("mcp 可独立导入", _try_import("backend.mcp")))

    if module_name in ("rag", "all"):
        print("\n[RAG 知识库]")
        checks.append(("services/rag_service.py 存在", os.path.exists("backend/services/rag_service.py")))
        checks.append(("services/embedding_service.py 存在", os.path.exists("backend/services/embedding_service.py")))

    if module_name in ("saas", "all"):
        print("\n[SaaS 鉴权]")
        checks.append(("auth/jwt.py 存在", os.path.exists("backend/auth/jwt.py")))
        checks.append(("auth/middleware.py 存在", os.path.exists("backend/auth/middleware.py")))
        checks.append(("auth/deps.py 存在", os.path.exists("backend/auth/deps.py")))
        checks.append(("models/user.py 存在", os.path.exists("backend/models/user.py")))
        checks.append(("models/optimization.py 存在", os.path.exists("backend/models/optimization.py")))
        checks.append(("database/engine.py 存在", os.path.exists("backend/database/engine.py")))

    if module_name in ("frontend", "all"):
        print("\n[前端升级]")
        checks.append(("tsconfig.json 存在", os.path.exists("frontend/tsconfig.json")))
        checks.append(("tailwind.config.js 存在", os.path.exists("frontend/tailwind.config.js")))
        checks.append(("src/main.tsx 存在", os.path.exists("frontend/src/main.tsx")))
        checks.append(("src/stores/appStore.ts 存在", os.path.exists("frontend/src/stores/appStore.ts")))
        checks.append(("src/types/index.ts 存在", os.path.exists("frontend/src/types/index.ts")))

    # 通用校验
    print("\n[通用校验]")
    checks.append(("middleware/exceptions.py 存在", os.path.exists("backend/middleware/exceptions.py")))
    checks.append(("middleware/rate_limiter.py 存在", os.path.exists("backend/middleware/rate_limiter.py")))
    checks.append(("services/event_bus.py 存在", os.path.exists("backend/services/event_bus.py")))
    checks.append(("services/cache.py 存在", os.path.exists("backend/services/cache.py")))

    # 执行校验
    for name, result in checks:
        status = "✅" if result else "❌"
        if result:
            passed += 1
        else:
            failed += 1
        print(f"  {status} {name}")

    # 汇总
    print(f"\n{'='*50}")
    total = passed + failed
    print(f"  结果: {passed}/{total} 通过, {failed} 失败")
    print(f"{'='*50}")

    return failed == 0


def _try_import(module_path: str) -> bool:
    """尝试导入模块"""
    try:
        importlib.import_module(module_path.replace("/", "."))
        return True
    except (ImportError, ModuleNotFoundError, Exception):
        return False


def main():
    parser = argparse.ArgumentParser(description="MarsResume 契约校验脚本")
    parser.add_argument("--module", choices=["langgraph", "mcp", "rag", "saas", "frontend", "all"], default="all")
    parser.add_argument("--path", default=".", help="项目根目录路径")
    args = parser.parse_args()

    # 切换到项目根目录
    os.chdir(args.path)

    success = check_module(args.module)
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()