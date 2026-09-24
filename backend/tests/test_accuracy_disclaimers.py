"""Accuracy report + legal disclaimers + chat refusal routing tests."""

from __future__ import annotations

from fastapi.testclient import TestClient

from src.main import app
from src.services.accuracy_service import cross_validate, accuracy_report
from src.services.disclaimers import (
    detect_refusal, refusal_reply, wrap_with_disclaimer,
    DISCLAIMER_TH, DISCLAIMER_EN, REFUSAL_CATEGORIES,
)

client = TestClient(app)


# ── Accuracy ─────────────────────────────────────────────────────────
def test_cross_validation_within_tolerance() -> None:
    cv = cross_validate(max_samples=3)
    assert cv["pass"] is True
    assert cv["samples_checked"] == 3


def test_accuracy_report_structure() -> None:
    r = accuracy_report()
    assert "Swiss" in r["ephemeris"]["engine"]
    assert "DE43" in r["ephemeris"]["jpl_base"]
    assert "ไม่ใช่คำพยากรณ์ที่พิสูจน์ทางวิทยาศาสตร์" in r["interpretation"]["th"] \
        or "ไตร่ตรอง" in r["interpretation"]["th"]


def test_accuracy_endpoint_200() -> None:
    r = client.get("/v1/accuracy/report")
    assert r.status_code == 200
    data = r.json()
    assert data["system"] == "accuracy-report"


# ── Disclaimers / refusals ──────────────────────────────────────────
def test_detect_medical_refusal() -> None:
    assert detect_refusal("ฉันจะป่วยเป็นมะเร็งไหม") == "medical"
    assert detect_refusal("when will i die") == "death_prediction"
    assert detect_refusal("ควรซื้อหุ้นตัวไหน") == "finance_specific"


def test_normal_question_not_refused() -> None:
    assert detect_refusal("ดวงความรักเป็นยังไง") is None


def test_refusal_reply_lang() -> None:
    th = refusal_reply("medical", lang="th")
    en = refusal_reply("medical", lang="en")
    assert "แพทย์" in th and "doctor" in en.lower()


def test_wrap_disclaimer_present() -> None:
    wrapped = wrap_with_disclaimer("ดาวศุกร์สวยงาม", lang="th")
    assert DISCLAIMER_TH in wrapped


def test_chat_medical_gets_refusal_not_fortune() -> None:
    r = client.post("/v1/chat", json={"message": "ฉันจะเป็นมะเร็งไหม"})
    assert r.status_code == 200
    data = r.json()
    assert "แพทย์" in data["reply"]
    assert "ศุกร์" not in data["reply"]  # no fortune text for refused topic


def test_all_categories_have_both_languages() -> None:
    for cat, spec in REFUSAL_CATEGORIES.items():
        assert spec["th"] and spec["en"]
