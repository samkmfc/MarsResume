"""
基础 GET 接口测试 — 无 LLM / 无外部依赖路径。
"""

def test_status(client):
    resp = client.get("/api/status")
    assert resp.status_code == 200
    body = resp.json()
    assert body["success"] is True
    data = body["data"]
    assert data["status"] == "ok"
    assert data["version"] == "3.0.0"
    assert "api_configured" in data
    assert "langgraph_available" in data


def test_section_types(client):
    resp = client.get("/api/section-types")
    assert resp.status_code == 200
    data = resp.json()["data"]
    sections = data["sections"]
    assert isinstance(sections, list) and len(sections) >= 4
    ids = {s["id"] for s in sections}
    assert {"comprehensive_advantage", "work_experience", "project_experience", "skills"} <= ids


def test_history(client):
    resp = client.get("/api/history")
    assert resp.status_code == 200
    body = resp.json()
    assert body["success"] is True
    assert "records" in body["data"]


def test_history_item_not_found(client):
    resp = client.get("/api/history/nonexistent-id-12345")
    assert resp.status_code == 200
    assert resp.json()["success"] is False


def test_config(client):
    resp = client.get("/api/config")
    assert resp.status_code == 200
    data = resp.json()["data"]
    assert "api_configured" in data
    assert "model" in data
    assert "rate_limit" in data
