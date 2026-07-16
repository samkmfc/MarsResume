"""
简历优化引擎 — 实现 SKILL.md 的 5 步方法论

设计原则：
- Prompt 模块化：每个步骤的 prompt 独立定义，便于维护
- 结构化输出：使用 response_format="json_object" 确保 AI 返回合法 JSON
- 注入防护：通过 fence_user_data + INJECTION_GUARD 防御注入
- 上下文分离：系统指令（受信任）与用户数据（不受信任）严格分离
"""

import json
from typing import Optional

from services.llm_client import LLMClient
from utils.ai_utils import sanitize_input


# ── 分步 Prompt 定义 ──────────────────────────────────────

SYSTEM_PROMPT_SKILL_EXPERT = """你是一位资深的 AI 产品经理简历优化专家。
你的核心原则：
1. 内容优先于语言 — 先确保每个 bullet 有独特的项目支撑和差异化亮点，再考虑措辞
2. 一次产出，不做微调 — 收集足够信息后一次性交付完整版本
3. 用项目展示能力，不堆砌技术名词
4. 每个 bullet 用不同的项目或数据，不要重复用同一个案例
5. 标签即说明，不重复解释

输出必须使用中文。"""

SYSTEM_PROMPT_METRICS_CHECK = """你是一位严谨的技术指标校对专家。
检查简历中的技术术语和指标是否准确，修正常见的术语误用。"""

SYSTEM_PROMPT_QUALITY_CHECK = """你是一位严格的简历质量检查员。
按照检查清单逐项审核简历内容，确保输出质量达到交付标准。"""


# ── Step 1: 深挖项目内容 ──────────────────────────────────

def _build_step1_prompt(resume_text: str, section_type: str, section_content: str) -> dict:
    """构建 Step 1 的提示词"""
    user_prompt = """你正在帮助一位 AI 产品经理优化简历。以下是他的简历和需要优化的模块。

## 需要优化的模块
{section_type}

## 任务
分析这份简历，按照以下必问清单，列出你需要向用户追问的问题。
注意：如果简历中已经包含了这些信息，则不需要追问。

必问清单：
1. 这个项目你的角色是什么？独立做还是带团队？带了几个人？
2. 用的具体工具/平台叫什么名字？（如 Cursor、MCP、Dify 等具体产品名）
3. 你说的"效率提升"是用什么指标衡量的？准确率？时间？成本？
4. 这个数据是最有说服力的那个吗？有没有更亮眼的？
5. 项目的业务背景是什么？解决了谁的什么问题？

请输出 JSON 格式，包含以下字段：
- questions: 需要追问的问题列表
- known_info: 简历中已有的信息总结
- missing_info: 缺失的关键信息描述
""".format(section_type=section_type)

    combined_data = f"## 简历原文\n{resume_text}\n\n## 该模块当前内容\n{section_content}"

    return {
        "system_prompt": SYSTEM_PROMPT_SKILL_EXPERT,
        "user_prompt": user_prompt,
        "user_data": combined_data,
    }


# ── Step 2: 识别差异化亮点 ────────────────────────────────

def _build_step2_prompt(resume_text: str, section_type: str, user_answers: str) -> dict:
    """构建 Step 2 的提示词"""
    user_prompt = """基于用户的简历和补充信息，识别出差异化亮点。

## 需要优化的模块
{section_type}

## 任务
将用户的经历分为两类：
- 差异化亮点：主导团队用新工具、多维度横评模型、从0到1搭系统等
- 常规PM工作：排期、需求文档、原型、会议协调等（在工作经历里自然体现）

判断标准：**这件事，一个普通产品经理也能做吗？** 如果能，归为常规；如果不能，归为亮点。

输出 JSON 格式：
{{
    "highlights": [
        {{"tag": "亮点标签", "project": "项目名称", "detail": "具体做了什么", "reason": "为什么这是差异化亮点"}}
    ],
    "routine": [
        {{"content": "常规工作内容", "handling": "在工作经历中自然体现"}}
    ]
}}
""".format(section_type=section_type)

    combined_data = f"## 简历原文\n{resume_text}\n\n## 用户补充信息\n{user_answers}"

    return {
        "system_prompt": SYSTEM_PROMPT_SKILL_EXPERT,
        "user_prompt": user_prompt,
        "user_data": combined_data,
    }


# ── Step 3: 生成终版 ──────────────────────────────────────

def _build_step3_prompt(
    resume_text: str, section_type: str, section_content: str,
    user_answers: str, highlights: list,
) -> dict:
    """构建 Step 3 的提示词"""
    highlights_text = json.dumps(highlights, ensure_ascii=False) if isinstance(highlights, list) else str(highlights)

    user_prompt = f"""基于所有信息，按照框架输出优化后的简历模块。

## 需要优化的模块
{section_type}

## 输出框架

### 综合优势模块（如果优化的是综合优势）
[姓名] | [年限]+[方向] | [公司（背景，规模）]

● [优势1标签]：[具体项目]+[做了什么]+[差异化亮点]；
● [优势2标签]：[具体项目]+[做了什么]+[差异化亮点]；
● [优势3标签]：[具体项目]+[做了什么]+[差异化亮点]

每条 bullet 要求：
- 至少包含一个具体项目名称
- 至少包含一个量化数据
- 展示的是"做了什么"而非"具备什么能力"
- 三条之间不能用同一个数据/同一个项目

### 其他模块（工作经历、项目经验）
每个项目/经历的 bullet 遵循：
[动作] + [具体做了什么] + [用了什么工具/方法] + [量化结果]

## 重要
- 去掉"闭环""赋能""具备...能力"等 AI 高频词
- 标签后面不要重复解释标签含义
- 整体读起来像真人写的，不像 AI 模板
- 数字用"约"留余地，不夸大

## 识别出的差异化亮点
{highlights_text}

## 用户补充信息
{user_answers}

请直接输出优化后的文本，无需额外 JSON 包装。"""

    combined_data = f"## 简历原文\n{resume_text}\n\n## 该模块当前内容\n{section_content}"

    return {
        "system_prompt": SYSTEM_PROMPT_SKILL_EXPERT,
        "user_prompt": user_prompt,
        "user_data": combined_data,
    }


# ── Step 4: 技术指标准确性检查 ────────────────────────────

def _build_step4_prompt(optimized_text: str) -> dict:
    """构建 Step 4 的提示词"""
    user_prompt = f"""检查以下简历优化文本中的技术指标是否准确。

## 常见错误对照表
| 常见误写 | 正确术语 |
|----------|----------|
| 回调率 | 召回率 (Recall) |
| 准确性 | 准确率 (Accuracy) |
| 识别率 | 识别准确率（需明确是 Accuracy 还是 Recall）|
| 校验效率 | 需要量化 |

质检场景特殊注意：
- 召回率 > 精确率（漏检代价远高于误检）
- 成本 = API调用成本/token消耗/算力成本

输出 JSON 格式：
{{
    "has_issues": true/false,
    "issues": [
        {{"original": "原文中的错误写法", "suggestion": "建议修改为", "reason": "修改原因"}}
    ],
    "fixed_text": "修正后的完整文本（如果有问题才输出，没问题则输出null）"
}}"""

    return {
        "system_prompt": SYSTEM_PROMPT_METRICS_CHECK,
        "user_prompt": user_prompt,
        "user_data": optimized_text,
    }


# ── Step 5: 交付前自检 ────────────────────────────────────

def _build_step5_prompt(optimized_text: str) -> dict:
    """构建 Step 5 的提示词"""
    user_prompt = """对以下简历优化文本进行最终质量检查。

## 检查清单
- [ ] 每条 bullet 都有具体项目名？
- [ ] 每条 bullet 都有量化数据？
- [ ] 三条之间没有重复使用同一个数据？
- [ ] 没有"闭环""赋能""具备...能力"等 AI 高频词？
- [ ] 标签后面没有重复解释标签含义？
- [ ] 角色描述准确？
- [ ] 技术术语准确？
- [ ] 数字可信（用"约"留余地，不夸大）？
- [ ] 整体读起来像真人写的，不像 AI 模板？

输出 JSON 格式：
{{
    "passed": true/false,
    "checks": [
        {{"item": "检查项", "result": "通过/未通过", "detail": "说明"}}
    ],
    "suggestions": ["改进建议1", "改进建议2"],
    "final_version": "修改后的终版（如果全部通过则输出null）"
}}"""

    return {
        "system_prompt": SYSTEM_PROMPT_QUALITY_CHECK,
        "user_prompt": user_prompt,
        "user_data": optimized_text,
    }


# ── 变更摘要 ──────────────────────────────────────────────

def _build_summary_prompt(original: str, optimized: str) -> dict:
    """生成修改前后对比说明"""
    user_prompt = """简要对比以下简历修改前后的关键改动，输出 3-5 条要点。

输出 JSON 格式：
{{"changes": ["改动1", "改动2", "改动3"]}}"""

    combined_data = f"## 修改前\n{original[:1000]}\n\n## 修改后\n{optimized[:1000]}"

    return {
        "system_prompt": "你是一位简历修改顾问，总结关键改动要点。",
        "user_prompt": user_prompt,
        "user_data": combined_data,
    }


# ── 引擎主类 ──────────────────────────────────────────────

class SkillEngine:
    def __init__(self, llm: LLMClient):
        self.llm = llm

    def _call_json(self, prompt_builder: dict, temperature: float = 0.3) -> dict:
        """调用 LLM 并解析 JSON 结果"""
        result = self.llm.chat(
            system_prompt=prompt_builder["system_prompt"],
            user_prompt=prompt_builder["user_prompt"],
            user_data=prompt_builder.get("user_data"),
            temperature=temperature,
            response_format="json_object",
        )
        return self._parse_json(result)

    def step1_deep_dive(self, resume_text: str, section_type: str, section_content: str) -> dict:
        """Step 1: 深挖项目内容"""
        return self._call_json(
            _build_step1_prompt(resume_text, section_type, section_content),
            temperature=0.3,
        )

    def step2_identify_highlights(self, resume_text: str, section_type: str, user_answers: str) -> dict:
        """Step 2: 识别差异化亮点"""
        return self._call_json(
            _build_step2_prompt(resume_text, section_type, user_answers),
            temperature=0.3,
        )

    def step3_generate(
        self, resume_text: str, section_type: str, section_content: str,
        user_answers: str, highlights: list,
    ) -> str:
        """Step 3: 用框架产出终版（非 JSON 输出）"""
        prompt_builder = _build_step3_prompt(
            resume_text, section_type, section_content,
            user_answers, highlights,
        )
        result = self.llm.chat(
            system_prompt=prompt_builder["system_prompt"],
            user_prompt=prompt_builder["user_prompt"],
            user_data=prompt_builder.get("user_data"),
            temperature=0.4,
        )
        return result

    def step4_check_metrics(self, optimized_text: str) -> dict:
        """Step 4: 技术指标准确性检查"""
        return self._call_json(
            _build_step4_prompt(optimized_text),
            temperature=0.2,
        )

    def step5_self_check(self, optimized_text: str) -> dict:
        """Step 5: 交付前自检"""
        return self._call_json(
            _build_step5_prompt(optimized_text),
            temperature=0.2,
        )

    def optimize(
        self, resume_text: str, section_type: str, section_content: str,
        user_answers: Optional[str] = None,
    ) -> dict:
        """
        执行完整 5 步优化流程
        """
        results = {}

        # Step 1: 深挖
        deep_dive = self.step1_deep_dive(resume_text, section_type, section_content)
        results["step1"] = deep_dive

        # 如果用户没有提供补充信息，返回需要追问的问题
        if not user_answers:
            return {
                "need_answers": True,
                "questions": deep_dive.get("questions", []),
                "known_info": deep_dive.get("known_info", ""),
                "step1_result": deep_dive,
            }

        # Step 2: 识别亮点
        highlights = self.step2_identify_highlights(resume_text, section_type, user_answers)
        results["step2"] = highlights

        # Step 3: 生成
        optimized = self.step3_generate(
            resume_text, section_type, section_content,
            user_answers, highlights.get("highlights", []),
        )
        results["step3_optimized"] = optimized

        # Step 4: 指标检查
        metrics_check = self.step4_check_metrics(optimized)
        results["step4"] = metrics_check

        final_text = metrics_check.get("fixed_text") or optimized
        results["final_text"] = final_text

        # Step 5: 自检
        self_check = self.step5_self_check(final_text)
        results["step5"] = self_check

        if self_check.get("final_version"):
            results["final_text"] = self_check["final_version"]

        # 生成变更摘要
        changes_summary = self._generate_summary(section_content, results["final_text"])

        return {
            "need_answers": False,
            "results": results,
            "final_text": results["final_text"],
            "changes_summary": changes_summary,
        }

    def _generate_summary(self, original: str, optimized: str) -> list:
        """生成修改前后对比说明"""
        prompt_builder = _build_summary_prompt(original, optimized)
        result = self._call_json(prompt_builder, temperature=0.2)
        return result.get("changes", [])

    def _parse_json(self, text: str) -> dict:
        """从 LLM 输出中解析 JSON（安全 fallback）"""
        if not text:
            return {}
        text = text.strip()
        # 尝试移除 markdown 代码块标记
        if text.startswith("```"):
            lines = text.split("\n")
            text = "\n".join(lines[1:])
            if text.endswith("```"):
                text = text[:-3]
        try:
            return json.loads(text)
        except json.JSONDecodeError:
            return {"raw": text}