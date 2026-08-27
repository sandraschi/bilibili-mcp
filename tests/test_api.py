"""Tests for the FastAPI REST surface (health, capabilities, tools, logs)."""

from __future__ import annotations

from fastapi.testclient import TestClient

from bilibili_mcp.server import app

client = TestClient(app)


def test_health_ok():
    r = client.get("/api/health")
    assert r.status_code == 200
    body = r.json()
    assert body["status"] == "ok"
    assert body["server"] == "bilibili-mcp"
    assert body["tool_count"] > 0


def test_capabilities():
    r = client.get("/api/capabilities")
    assert r.status_code == 200
    body = r.json()
    assert body["features"]["explore"] is True
    assert body["features"]["transcript"] is True


def test_tools_list():
    r = client.get("/api/tools")
    assert r.status_code == 200
    names = r.json()["tools"]
    assert "bilibili_explore" in names
    assert "bilibili_transcript" in names


def test_logs():
    r = client.get("/api/logs")
    assert r.status_code == 200
    assert "logs" in r.json()
