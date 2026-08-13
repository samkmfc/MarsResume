"""
Deep dive agent — Step 1: extract questions and known info from resume.
"""

from typing import Any, Dict
from agents.base import BaseAgent
from services.skill_engine import _build_step1_prompt


class DeepDiveAgent(BaseAgent):
    """Agent for deep-diving into resume content."""

    async def run(self, context: Dict[str, Any]) -> Dict[str, Any]:
        prompt = _build_step1_prompt(
            resume_text=context.get("resume_text", ""),
            section_type=context.get("section_type", ""),
            section_content=context.get("section_content", ""),
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
            return {"questions": [], "known_info": "", "missing_info": ""}
        text = text.strip()
        if text.startswith("```"):
            lines = text.split("\n")
            text = "\n".join(lines[1:])
            if text.endswith("```"):
                text = text[:-3]
        try:
            return json.loads(text)
        except json.JSONDecodeError:
            return {"questions": [], "known_info": "", "missing_info": "", "raw": text}