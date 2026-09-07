"""Premium PDF + tarot images endpoints."""

from __future__ import annotations

from fastapi.testclient import TestClient

from src.main import app
from src.services.tarot_images import card_image_url, CARD_INDEX

client = TestClient(app)


def test_premium_pdf_renders() -> None:
    r = client.post("/v1/reports/premium", json={
        "person_name": "สมชาย",
        "lang": "th",
        "theme": "regency",
        "sections": [{"title": "ดวงกำเนิด", "lines": ["ลัคนาพฤษภ ใจคนมั่นคง"]}],
    })
    assert r.status_code == 200
    data = r.json()
    assert data["ok"] is True


def test_premium_pdf_download() -> None:
    r = client.post("/v1/reports/premium/download", json={
        "person_name": "Test User",
        "lang": "en",
        "theme": "cosmic",
        "sections": [{"title": "Overview", "lines": ["Sun in Taurus."]}],
    })
    assert r.status_code == 200
    assert r.headers["content-type"].startswith("application/pdf")
    assert b"%PDF-" in r.content[:8]


def test_premium_rejects_bad_theme() -> None:
    r = client.post("/v1/reports/premium", json={
        "theme": "steampunk",
        "sections": [{"title": "x", "lines": ["y"]}],
    })
    assert r.status_code == 422


def test_card_index_covers_78() -> None:
    assert len(CARD_INDEX) == 78
    assert CARD_INDEX["The Fool"] == 0
    assert CARD_INDEX["The World"] == 21
    assert CARD_INDEX["King of Pentacles"] == 77


def test_card_image_url_none_when_deck_incomplete() -> None:
    # deck may be mid-download; missing file must yield None, never a bad path
    url = card_image_url("The Fool")
    if url is not None:
        assert url.startswith("/tarot/sola-busca/")
    assert card_image_url("Nonexistent Card") is None


def test_tarot_draw_returns_image_fields() -> None:
    r = client.post("/v1/tarot/draw", json={"name": "img-test", "spread": "single"})
    assert r.status_code == 200
    data = r.json()
    assert "image_url" in data["cards"][0]
    assert "deck" in data
    assert set(data["deck"].keys()) == {"have", "total", "complete"}
