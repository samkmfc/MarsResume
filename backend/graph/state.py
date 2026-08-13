"""
Graph state definition for the LangGraph resume optimization workflow.

TypedDict-based state schema with retry counters and error accumulation.
"""

from typing import Optional, List, Dict, Any, TypedDict, Annotated
import operator


class OptimizationState(TypedDict):
    # ── Inputs ──
    resume_text: str
    jd_text: Optional[str]
    section_type: str
    section_content: str
    user_answers: Optional[str]

    # ── Step results ──
    deep_dive_result: Optional[Dict[str, Any]]
    highlights_result: Optional[Dict[str, Any]]
    optimized_text: Optional[str]
    metrics_check_result: Optional[Dict[str, Any]]
    self_check_result: Optional[Dict[str, Any]]
    final_text: Optional[str]
    changes_summary: Optional[List[str]]

    # ── Control flow ──
    need_answers: bool
    questions: List[str]
    known_info: str
    retry_count: int
    max_retries: int
    errors: Annotated[List[str], operator.add]