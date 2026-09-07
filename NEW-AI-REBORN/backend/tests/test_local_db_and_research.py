"""Tests for local DB cache and research corpus endpoints."""

from __future__ import annotations

import json
import sqlite3
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from src.main import app
from src.integrations import local_db

client = TestClient(app)

DB_PATH = Path(__file__).resolve().parents[2] / "astral.db"


def test_local_db_connect():
    con = local_db._connect()
    cur = con.cursor()
    cur.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")
    tables = {row[0] for row in cur.fetchall()}
    assert {"charts", "memory", "profiles", "research_corpus", "sessions", "migrations"} <= tables
    con.close()


def test_research_corpus_list():
    r = client.get("/v1/research/corpus")
    assert r.status_code == 200
    items = r.json()
    ids = {x["id"] for x in items}
    assert "asteroids_ephe_guide" in ids
    assert "results" in ids


def test_research_corpus_detail():
    r = client.get("/v1/research/corpus/asteroids_ephe_guide")
    assert r.status_code == 200
    body = r.json()
    assert body["id"] == "asteroids_ephe_guide"
    assert body["category"] == "data"
    assert isinstance(body["data"], dict)


def test_research_categories():
    r = client.get("/v1/research/categories")
    assert r.status_code == 200
    cats = r.json()
    assert "data" in cats
    assert cats["data"] >= 1
