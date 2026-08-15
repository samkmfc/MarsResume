"""
Writer agent — Step 3: generate optimized resume text.
"""

from typing import Any, Dict
from agents.base import BaseAgent
from services.skill_engine import _build_step3_prompt


class WriterAgent(BaseAgent):
    """Agent for generating optimized resume text."""

    async def run(self, context: Dict[str, Any]) -> Dict[str, Any]:
        prompt = _build_step3_prompt(
            resume_text=context.get("resume_text", ""),
            section_type=context.get("section_type", ""),
            section_content=context.get("section_content", ""),
            user_answers=context.get("user_answers", ""),
            highlights=context.get("highlights", []),
        )
        result = self._call_llm(
            system_prompt=prompt["system_prompt"],
            user_prompt=prompt["user_prompt"],
            user_data=prompt.get("user_data"),
            temperature=0.4,
        )
        return {
            "task_id": context.get("task_id", ""),
            "success": True,
            "output_data": {"optimized_text": result},
            "error": None,
            "metrics": {"tokens": len(result) // 4},
        }