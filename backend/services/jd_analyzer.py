"""
JD 对齐分析引擎 — 将简历与职位描述进行对比分析
- 逐条生成修改建议（原文 → 建议改法 → 原因）
- 支持结构化 JSON 输出
"""

import json
from typing import Optional
from services.llm_client import LLMClient

# ── System Prompt ──

SYSTEM_JD_EXPERT = """你是一位资深 AI 招聘专家 + 简历优化顾问。
你的任务是将候选人简历与目标职位描述(JD)进行逐条对比分析，
给出精准的修改建议，帮助候选人提高简历与 JD 的匹配度。

核心原则：
1. 每条建议必须对应 JD 中的具体一条要求
2. 建议要具体可操作，不能空洞
3. 保留候选人真实的经历和数据，只优化表达方式
4. 确保每条建议有明确的修改原因（对齐 JD 哪条要求）
5. 用中文输出"""


# ── Prompt Builder ──

def _build_analyze_prompt(resume_text: str, jd_text: str) -> dict:
    """构建分析提示词"""
    user_prompt = f"""请将以下简历与职位描述进行逐条对比分析，生成修改建议。

## 任务要求
1. 逐条分析简历中的每个模块（综合优势、工作经历、项目经验、技能）
2. 对比 JD 中的每条要求，找出简历中需要改进的地方
3. 每条建议必须包含：原文、建议修改、修改原因、重要程度

## 重要
- 只建议"怎么改"，不编造候选人没有的经历
- 每条建议的原因要明确关联到 JD 的某条要求
- 严重程度：high=JD 核心要求但简历缺失/表述差，medium=有提升空间，low=锦上添花

## 输出 JSON 格式
{{
    "suggestions": [
        {{
            "id": "唯一ID",
            "section": "综合优势/工作经历/项目经验/技能/格式",
            "original": "原文片段",
            "suggested": "建议修改文本",
            "reason": "对齐 JD 的哪条要求，为什么这样改",
            "severity": "high/medium/low"
        }}
    ],
    "summary": {{
        "match_score": 70,
        "strengths": ["简历已有的优势1", "简历已有的优势2"],
        "gaps": ["与 JD 的差距1", "与 JD 的差距2"],
        "key_improvements": "最关键的改进方向"
    }}
}}"""

    combined_data = f"## 简历原文\n{resume_text}\n\n## 职位描述(JD)\n{jd_text}"

    return {
        "system_prompt": SYSTEM_JD_EXPERT,
        "user_prompt": user_prompt,
        "user_data": combined_data,
    }


# ── Analyzer Class ──

class JDAnalyzer:
    def __init__(self, llm: LLMClient):
        self.llm = llm

    def analyze(self, resume_text: str, jd_text: str) -> dict:
        """
        分析简历与 JD 的匹配度，返回逐条建议。

        Returns:
            dict: {
                "suggestions": [...],
                "summary": {...}
            }
        """
        prompt = _build_analyze_prompt(resume_text, jd_text)

        result = self.llm.chat(
            system_prompt=prompt["system_prompt"],
            user_prompt=prompt["user_prompt"],
            user_data=prompt.get("user_data"),
            temperature=0.3,
            response_format="json_object",
        )

        return self._parse_json(result)

    def _parse_json(self, text: str) -> dict:
        """安全解析 JSON"""
        if not text:
            return {"suggestions": [], "summary": {}}
        text = text.strip()
        if text.startswith("```"):
            lines = text.split("\n")
            text = "\n".join(lines[1:])
            if text.endswith("```"):
                text = text[:-3]
        try:
            return json.loads(text)
        except json.JSONDecodeError:
            return {"suggestions": [], "summary": {}}