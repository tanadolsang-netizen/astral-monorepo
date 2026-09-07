"""PDF report endpoint — contract + real Thai text rendering."""

from __future__ import annotations

import os

from fastapi.testclient import TestClient

from src.main import app

client = TestClient(app)


def test_reports_health() -> None:
    r = client.get("/v1/reports/health")
    assert r.status_code == 200
    assert r.json()["ok"] is True


def test_thai_font_available_on_ci() -> None:
    # bundled Sarabun must exist so Thai text renders on Linux CI too
    from src.services.pdf_report_service import thai_font_available
    assert thai_font_available() is True


def test_build_pdf_thai() -> None:
    req = {
        "person_name": "สมชาย ใจดี",
        "lang": "th",
        "sections": [
            {
                "title": "ดวงกำเนิด",
                "lines": [
                    "ลัคนาของคุณขึ้นราศีเมษ พญาคือดาวอังคาร — เป็นคนใจกล้า ตัดสินใจเร็ว",
                    "ดวงจันทร์อยู่ราศีกรกฎ ทำให้ฝังใจเรื่องครอบครัวเป็นที่หนึ่ง",
                ],
            },
            {
                "title": "ทรานซิตเด่นเดือนนี้",
                "lines": [
                    "ดาวพฤหัสฯ ทำมุมสามเหลี่ยม (120°) กับดาวเกิดศุกร์ (เหลือ 1.2°) — หนุนเรื่องเงินและความรัก",
                ],
            },
        ],
    }
    r = client.post("/v1/reports/pdf", json=req)
    assert r.status_code == 200
    data = r.json()
    assert data["ok"] is True
    assert data["sections"] == 2
    assert os.path.exists(data["file"])
    # PDF magic bytes
    with open(data["file"], "rb") as f:
        head = f.read(5)
    assert head == b"%PDF-"
    os.remove(data["file"])
    os.rmdir(os.path.dirname(data["file"]))


def test_download_pdf_returns_file() -> None:
    req = {
        "person_name": "Test User",
        "lang": "en",
        "sections": [{"title": "Overview", "lines": ["Your Sun is in Leo."]}],
    }
    r = client.post("/v1/reports/pdf/download", json=req)
    assert r.status_code == 200
    assert r.headers["content-type"].startswith("application/pdf")
    assert b"%PDF-" in r.content[:8]


def test_pdf_rejects_empty_sections() -> None:
    r = client.post("/v1/reports/pdf", json={"sections": []})
    assert r.status_code == 422


def test_pdf_rejects_bad_lang() -> None:
    r = client.post(
        "/v1/reports/pdf",
        json={"lang": "jp", "sections": [{"title": "x", "lines": ["y"]}]},
    )
    assert r.status_code == 422
