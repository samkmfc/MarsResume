"""
Reviewer agent — Steps 4 & 5: metrics check + self-check.
"""

from typing import Any, Dict
from agents.base import BaseAgent
from services.skill_engine import _build_step4_prompt, _build_step5_prompt


class ReviewerAgent(BaseAgent):
    """Agent for quality review: metrics check and self-check."""

    async def run(self, context: Dict[str, Any]) -> Dict[str, Any]:
        task = context.get("task", "self_check")
        text = context.get("text", "")

        if task == "check_metrics":
            prompt = _build_step4_prompt(text)
            temperature = 0.2
            response_format = "json_object"
        else:
            prompt = _build_step5_prompt(text)
            temperature = 0.2
            response_format = "json_object"

        result = self._call_llm(
            system_prompt=prompt["system_prompt"],
            user_prompt=prompt["user_prompt"],
            user_data=prompt.get("user_data"),
            temperature=temperature,
            response_format=response_format,
        )
        parsed = self._parse_json(result)
        return {
            "task_id": context.get("task_id", ""),
            "success": True,
            "output_data": parsed,
            "error": None,
            "metrics": {"tokens": len(result) // 4, "task": task},
        }

    def _parse_json(self, text: str) -> dict:
        import json
        if not text:
            return {}
        text = text.strip()
        if text.startswith("```"):
            lines = text.split("\n")
            text = "\n".join(lines[1:])
            if text.endswith("```"):
                text = text[:-3]
        try:
            return json.loads(text)
        except json.JSONDecodeError:
            return {"raw": text}