"""
/api/optimize 接口测试 — 通过 FakeEngine 验证追问分支与完成分支。
"""

def test_optimize_need_answers(client, fake_engine):
    """无 user_answers → 返回追问问题。"""
    fake_engine.result = {"need_answers": True, "questions": ["你用过的最大并发量?"], "known_info": "已知信息"}
    resp = client.post("/api/optimize", json={
        "resume_text": "三年后端经验，熟悉 Python",
        "section_type": "work_experience",
        "section_content": "负责后端服务开发",
        "user_answers": None,
    })
    assert resp.status_code == 200
    data = resp.json()["data"]
    assert data["need_answers"] is True
    assert len(data["questions"]) > 0


def test_optimize_final(client, fake_engine):
    """有最终文本 → 完成分支，保存历史（mock 拦截落盘）。"""
    fake_engine.result = {
        "need_answers": False,
        "final_text": "优化后的工作经历描述，含 STAR 法则与量化指标",
        "changes_summary": [{"original": "x", "suggested": "y", "reason": "z"}],
    }
    resp = client.post("/api/optimize", json={
        "resume_text": "三年后端经验",
        "section_type": "work_experience",
        "section_content": "负责开发",
        "user_answers": "并发量 10万 QPS",
    })
    assert resp.status_code == 200
    data = resp.json()["data"]
    assert data["need_answers"] is False
    assert "优化后" in data["final_text"]


def test_optimize_validation_rejects_empty(client):
    """空 resume_text 触发 Pydantic 校验失败（min_length=1）。"""
    resp = client.post("/api/optimize", json={
        "resume_text": "",
        "section_type": "skills",
        "section_content": "Python",
    })
    assert resp.status_code == 422
