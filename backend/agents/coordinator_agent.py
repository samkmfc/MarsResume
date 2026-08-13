"""
Coordinator agent — decides workflow routing and agent selection.
"""

from typing import Any, Dict

from agents.base import BaseAgent


class CoordinatorAgent(BaseAgent):
    """Agent for coordinating workflow decisions."""

    async def run(self, context: Dict[str, Any]) -> Dict[str, Any]:
        # Coordinator is a logic-based router, not an LLM agent
        state = context.get("state", {})
        action = context.get("action", "route")

        if action == "route":
            return self._route(state)
        elif action == "should_retry":
            return self._should_retry(state)
        return {"task_id": context.get("task_id", ""), "success": True, "output_data": {"action": "continue"}, "error": None, "metrics": {}}

    def _route(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """Determine the next step in the workflow."""
        if state.get("need_answers"):
            return {"output_data": {"next": "ask_user"}}
        if not state.get("highlights_result"):
            return {"output_data": {"next": "identify_highlights"}}
        if not state.get("optimized_text"):
            return {"output_data": {"next": "generate"}}
        return {"output_data": {"next": "check_metrics"}}

    def _should_retry(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """Determine if retry is needed."""
        retry_count = state.get("retry_count", 0)
        max_retries = state.get("max_retries", 3)
        if retry_count >= max_retries:
            return {"output_data": {"retry": False, "reason": "max_retries_exceeded"}}
        return {"output_data": {"retry": True, "reason": "quality_check_failed"}}