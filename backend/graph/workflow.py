"""
LangGraph workflow — build and compile the state graph.
"""

from langgraph.graph import StateGraph, END
from graph.state import OptimizationState
from graph.nodes import (
    deep_dive_node,
    identify_highlights_node,
    generate_node,
    check_metrics_node,
    self_check_node,
    should_ask_user,
    is_metrics_ok,
    is_self_check_ok,
)


def build_optimization_graph() -> StateGraph:
    """Build the resume optimization workflow graph."""

    workflow = StateGraph(OptimizationState)

    # ── Register nodes ──
    workflow.add_node("deep_dive", deep_dive_node)
    workflow.add_node("identify_highlights", identify_highlights_node)
    workflow.add_node("generate", generate_node)
    workflow.add_node("check_metrics", check_metrics_node)
    workflow.add_node("self_check", self_check_node)

    # ── Set entry point ──
    workflow.set_entry_point("deep_dive")

    # ── Add edges ──
    # After deep dive: need answers or continue?
    workflow.add_conditional_edges(
        "deep_dive",
        should_ask_user,
        {
            "ask_user": END,  # Pause, wait for user answers
            "continue": "identify_highlights",
        },
    )

    # After highlights: generate
    workflow.add_edge("identify_highlights", "generate")

    # After generate: check metrics
    workflow.add_edge("generate", "check_metrics")

    # After check metrics: fix or proceed
    workflow.add_conditional_edges(
        "check_metrics",
        is_metrics_ok,
        {
            "fix": "generate",  # Regenerate with fixes
            "ok": "self_check",
        },
    )

    # After self check: done or rework
    workflow.add_conditional_edges(
        "self_check",
        is_self_check_ok,
        {
            "rework": "generate",  # Rework generation
            "done": END,
        },
    )

    return workflow.compile()


# Compiled graph singleton
optimization_graph = build_optimization_graph()