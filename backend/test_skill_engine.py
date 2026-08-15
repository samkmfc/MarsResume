"""
SkillEngine 纯函数与降级逻辑测试 — 不依赖真实 LLM。
"""

from services.skill_engine import (
    _build_step1_prompt,
    _build_step3_prompt,
    SkillEngine,
)
from conftest import FakeLLM


def test_build_step1_prompt_structure():
    pb = _build_step1_prompt("三年后端经验", "work_experience", "负责服务开发")
    assert isinstance(pb, dict)
    assert "system_prompt" in pb and "user_prompt" in pb
    assert "work_experience" in pb["user_prompt"] or "工作" in pb["user_prompt"]


def test_build_step3_prompt_structure():
    pb = _build_step3_prompt(
        "三年后端经验", "work_experience", "负责开发",
        "并发 10万 QPS", ["高并发处理"],
    )
    assert isinstance(pb, dict)
    assert "system_prompt" in pb and "user_prompt" in pb


def test_parse_json_handles_plain_json():
    eng = SkillEngine(FakeLLM('{"a": 1, "b": 2}'))
    out = eng._parse_json('{"a": 1, "b": 2}')
    assert out == {"a": 1, "b": 2}


def test_parse_json_handles_invalid_does_not_crash():
    """无效 JSON → 降级返回 dict，不抛异常。"""
    eng = SkillEngine(FakeLLM())
    out = eng._parse_json("not a json {{{")
    assert isinstance(out, dict)


def test_generate_summary_returns_list():
    eng = SkillEngine(FakeLLM('{"summary": [{"original":"a","suggested":"b","reason":"c"}]}'))
    out = eng._generate_summary("原文", "优化后")
    assert isinstance(out, list)
