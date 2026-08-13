"""
LangGraph workflow nodes — each node wraps an Agent call.
"""

import json
from typing import Any, Dict

from agents.registry import AgentRegistry
from services.llm_client import LLMClient
from middleware.rate_limiter import concurrency_limiter, RetryHandler


def _get_registry() -> AgentRegistry:
    """Lazy-init agent registry singleton."""
    if not hasattr(_get_registry, "_registry"):
        llm = LLMClient()
        _get_registry._registry = AgentRegistry(llm)
    return _get_registry._registry


async def deep_dive_node(state: Dict[str, Any]) -> Dict[str, Any]:
    """Step 1: Deep dive into resume content."""
    registry = _get_registry()
    agent = registry.get("deep_dive")

    async with concurrency_limiter:
        result = await RetryHandler.execute_with_retry(
            agent.run, {
                "resume_text": state["resume_text"],
                "section_type": state["section_type"],
                "section_content": state["section_content"],
            }
        )

    questions = result.get("output_data", {}).get("questions", [])
    return {
        "deep_dive_result": result.get("output_data", {}),
        "need_answers": len(questions) > 0 and not state.get("user_answers"),
        "questions": questions,
        "known_info": result.get("output_data", {}).get("known_info", ""),
    }


async def identify_highlights_node(state: Dict[str, Any]) -> Dict[str, Any]:
    """Step 2: Identify differentiated highlights."""
    registry = _get_registry()
    agent = registry.get("highlight")

    async with concurrency_limiter:
        result = await RetryHandler.execute_with_retry(
            agent.run, {
                "resume_text": state["resume_text"],
                "section_type": state["section_type"],
                "user_answers": state.get("user_answers", ""),
            }
        )

    return {
        "highlights_result": result.get("output_data", {}),
    }


async def generate_node(state: Dict[str, Any]) -> Dict[str, Any]:
    """Step 3: Generate optimized text."""
    registry = _get_registry()
    writer = registry.get("writer")

    highlights = (state.get("highlights_result") or {}).get("highlights", [])

    async with concurrency_limiter:
        result = await RetryHandler.execute_with_retry(
            writer.run, {
                "resume_text": state["resume_text"],
                "section_type": state["section_type"],
                "section_content": state["section_content"],
                "user_answers": state.get("user_answers", ""),
                "highlights": highlights,
            }
        )

    return {
        "optimized_text": result.get("output_data", {}).get("optimized_text", ""),
        "retry_count": state.get("retry_count", 0) + 1,
    }


async def check_metrics_node(state: Dict[str, Any]) -> Dict[str, Any]:
    """Step 4: Check technical metrics accuracy."""
    registry = _get_registry()
    reviewer = registry.get("reviewer")

    async with concurrency_limiter:
        result = await RetryHandler.execute_with_retry(
            reviewer.run, {
                "task": "check_metrics",
                "text": state.get("optimized_text", ""),
            }
        )

    output = result.get("output_data", {})
    has_issues = output.get("has_issues", False)
    fixed_text = output.get("fixed_text")

    return {
        "metrics_check_result": output,
        "optimized_text": fixed_text if fixed_text else state.get("optimized_text", ""),
    }


async def self_check_node(state: Dict[str, Any]) -> Dict[str, Any]:
    """Step 5: Final quality self-check."""
    registry = _get_registry()
    reviewer = registry.get("reviewer")

    async with concurrency_limiter:
        result = await RetryHandler.execute_with_retry(
            reviewer.run, {
                "task": "self_check",
                "text": state.get("optimized_text", ""),
            }
        )

    output = result.get("output_data", {})
    passed = output.get("passed", False)
    final_version = output.get("final_version")

    return {
        "self_check_result": output,
        "final_text": final_version if final_version else state.get("optimized_text", ""),
    }


def should_ask_user(state: Dict[str, Any]) -> str:
    """Conditional edge: need answers before continuing?"""
    if state.get("need_answers", False):
        return "ask_user"
    return "continue"


def should_retry(state: Dict[str, Any]) -> str:
    """Conditional edge: should retry generation?"""
    max_retries = state.get("max_retries", 3)
    if state.get("retry_count", 0) >= max_retries:
        return "maxed"
    return "retry"


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