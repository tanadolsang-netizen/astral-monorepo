from fastapi.testclient import TestClient

from src.integrations.supabase_client import User
from src.main import app
from src.routers import memory as memory_router
from src.services import hermes_memory_service as memory_service

client = TestClient(app)

_TEST_USER = User(id="test-user", email="test@astral.app")


def _authorize():
    app.dependency_overrides[memory_router._require_user] = lambda: _TEST_USER


def _deauthorize():
    app.dependency_overrides.pop(memory_router._require_user, None)


def test_memory_summary_empty(tmp_path, monkeypatch):
    _authorize()
    monkeypatch.setattr(memory_service, "MEMORY_DIR", tmp_path)

    res = client.get("/v1/memory/summary")
    assert res.status_code == 200
    assert res.json() == {
        "memory_bytes": 0,
        "memory_entries": 0,
        "user_bytes": 0,
        "user_entries": 0,
    }


def test_memory_append_and_read_roundtrip(tmp_path, monkeypatch):
    _authorize()
    monkeypatch.setattr(memory_service, "MEMORY_DIR", tmp_path)

    res = client.post("/v1/memory/entries", json={"target": "memory", "content": "first note"})
    assert res.status_code == 200
    assert res.json() == {"index": 0, "content": "first note"}

    res = client.post("/v1/memory/entries", json={"target": "memory", "content": "second note"})
    assert res.status_code == 200
    assert res.json()["index"] == 1

    res = client.get("/v1/memory/entries", params={"target": "memory"})
    assert res.status_code == 200
    assert [e["content"] for e in res.json()] == ["first note", "second note"]

    raw = (tmp_path / "MEMORY.md").read_text(encoding="utf-8")
    assert raw == "first note\n§\nsecond note"


def test_memory_append_rejects_empty_content(tmp_path, monkeypatch):
    _authorize()
    monkeypatch.setattr(memory_service, "MEMORY_DIR", tmp_path)

    res = client.post("/v1/memory/entries", json={"target": "memory", "content": "   "})
    assert res.status_code == 400


def test_memory_requires_auth(tmp_path, monkeypatch):
    _deauthorize()
    monkeypatch.setattr(memory_service, "MEMORY_DIR", tmp_path)
    try:
        res = client.get("/v1/memory/summary")
        assert res.status_code == 401
    finally:
        _authorize()


def test_memory_sessions_missing_db_returns_empty(tmp_path, monkeypatch):
    _authorize()
    monkeypatch.setattr(memory_service, "STATE_DB", tmp_path / "does-not-exist.db")

    res = client.get("/v1/memory/sessions", params={"query": "hello"})
    assert res.status_code == 200
    assert res.json() == {"results": []}
