"""
Highlight identification agent — Step 2: identify differentiated highlights.
"""

from typing import Any, Dict
from agents.base import BaseAgent
from services.skill_engine import _build_step2_prompt


class HighlightAgent(BaseAgent):
    """Agent for identifying resume highlights vs routine work."""

    async def run(self, context: Dict[str, Any]) -> Dict[str, Any]:
        prompt = _build_step2_prompt(
            resume_text=context.get("resume_text", ""),
            section_type=context.get("section_type", ""),
            user_answers=context.get("user_answers", ""),
        )
        result = self._call_llm(
            system_prompt=prompt["system_prompt"],
            user_prompt=prompt["user_prompt"],
            user_data=prompt.get("user_data"),
            temperature=0.3,
            response_format="json_object",
        )
        parsed = self._parse_json(result)
        return {
            "task_id": context.get("task_id", ""),
            "success": True,
            "output_data": parsed,
            "error": None,
            "metrics": {"tokens": len(result) // 4},
        }

    def _parse_json(self, text: str) -> dict:
        import json
        if not text:
            return {"highlights": [], "routine": []}
        text = text.strip()
        if text.startswith("```"):
            lines = text.split("\n")
            text = "\n".join(lines[1:])
            if text.endswith("```"):
                text = text[:-3]
        try:
            return json.loads(text)
        except json.JSONDecodeError:
            return {"highlights": [], "routine": [], "raw": text}