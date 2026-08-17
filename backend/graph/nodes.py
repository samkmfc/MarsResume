"""
LangGraph workflow nodes — each node wraps a SkillEngine step.
"""

import asyncio
from typing import Any, Dict

from services.llm_client import LLMClient
from services.skill_engine import SkillEngine
from utils.rate_limit import concurrency_limiter, RetryHandler


def _get_engine() -> SkillEngine:
    """Lazy-init SkillEngine singleton."""
    if not hasattr(_get_engine, "_engine"):
        llm = LLMClient()
        _get_engine._engine = SkillEngine(llm)
    return _get_engine._engine


async def _run_sync(fn, *args, **kwargs):
    """Run a synchronous SkillEngine method in a thread pool."""
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(None, fn, *args, **kwargs)


async def deep_dive_node(state: Dict[str, Any]) -> Dict[str, Any]:
    """Step 1: Deep dive into resume content."""
    engine = _get_engine()
    async with concurrency_limiter:
        result = await RetryHandler.execute_with_retry(
            _run_sync, engine.step1_deep_dive,
            state["resume_text"], state["section_type"], state["section_content"],
        )

    questions = result.get("questions", [])
    return {
        "deep_dive_result": result,
        "need_answers": len(questions) > 0 and not state.get("user_answers"),
        "questions": questions,
        "known_info": result.get("known_info", ""),
    }


async def identify_highlights_node(state: Dict[str, Any]) -> Dict[str, Any]:
    """Step 2: Identify differentiated highlights."""
    engine = _get_engine()
    async with concurrency_limiter:
        result = await RetryHandler.execute_with_retry(
            _run_sync, engine.step2_identify_highlights,
            state["resume_text"], state["section_type"], state.get("user_answers", ""),
        )

    return {"highlights_result": result}


async def generate_node(state: Dict[str, Any]) -> Dict[str, Any]:
    """Step 3: Generate optimized text."""
    engine = _get_engine()
    highlights = (state.get("highlights_result") or {}).get("highlights", [])

    async with concurrency_limiter:
        result = await RetryHandler.execute_with_retry(
            _run_sync, engine.step3_generate,
            state["resume_text"], state["section_type"], state["section_content"],
            state.get("user_answers", ""), highlights,
        )

    return {
        "optimized_text": result,
        "retry_count": state.get("retry_count", 0) + 1,
    }


async def check_metrics_node(state: Dict[str, Any]) -> Dict[str, Any]:
    """Step 4: Check technical metrics accuracy."""
    engine = _get_engine()
    async with concurrency_limiter:
        result = await RetryHandler.execute_with_retry(
            _run_sync, engine.step4_check_metrics,
            state.get("optimized_text", ""),
        )

    has_issues = result.get("has_issues", False)
    fixed_text = result.get("fixed_text")

    return {
        "metrics_check_result": result,
        "optimized_text": fixed_text if fixed_text else state.get("optimized_text", ""),
    }


async def self_check_node(state: Dict[str, Any]) -> Dict[str, Any]:
    """Step 5: Final quality self-check."""
    engine = _get_engine()
    async with concurrency_limiter:
        result = await RetryHandler.execute_with_retry(
            _run_sync, engine.step5_self_check,
            state.get("optimized_text", ""),
        )

    final_version = result.get("final_version")

    return {
        "self_check_result": result,
        "final_text": final_version if final_version else state.get("optimized_text", ""),
    }


# ── Conditional edge functions ──


def should_ask_user(state: Dict[str, Any]) -> str:
    """Conditional edge: need answers before continuing?"""
    if state.get("need_answers", False):
        return "ask_user"
    return "continue"


def is_metrics_ok(state: Dict[str, Any]) -> str:
    """Conditional edge: metrics check passed?"""
    result = state.get("metrics_check_result", {})
    if result.get("has_issues", False):
        return "fix"
    return "ok"


def is_self_check_ok(state: Dict[str, Any]) -> str:
    """Conditional edge: self-check passed?"""
    result = state.get("self_check_result", {})
    if not result.get("passed", False) and state.get("retry_count", 0) < state.get("max_retries", 3):
        return "rework"
    return "done"