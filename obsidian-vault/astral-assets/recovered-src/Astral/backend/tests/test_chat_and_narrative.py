"""AI chat endpoint + reel EN narrative completeness."""

from __future__ import annotations

from fastapi.testclient import TestClient

from src.main import app
from src.services.astro_chat_service import SYSTEM_PROMPT, LLMConfig
from src.routers.chat import _rule_reply

client = TestClient(app)


# ── chat guardrails ──────────────────────────────────────────────────
def test_system_prompt_has_guardrails() -> None:
    p = SYSTEM_PROMPT
    assert "โหร" in p  # persona
    assert "แพทย์" in p and "ลงทุน" in p  # scope limits
    assert "ภาษาเดียวกับที่ผู้ใช้ถาม" in p


def test_rule_fallback_topics() -> None:
    assert "ศุกร์" in _rule_reply("ความรักของฉันเป็นยังไง")
    assert "พฤหัส" in _rule_reply("งานของผมจะดีไหม")
    assert "แพทย์" in _rule_reply("ฉันจะป่วยเมื่อไหร่")  # health redirect
    assert "หุ้น" not in _rule_reply("ควรซื้อหุ้นตัวไหน") or "ปรึกษา" in _rule_reply("ควรซื้อหุ้นตัวไหน")


def test_chat_endpoint_rules_engine() -> None:
    r = client.post("/v1/chat", json={"message": "ดวงความรักเป็นยังไงบ้าง"})
    assert r.status_code == 200
    data = r.json()
    # Pollinations is free (no key needed) → engine will be 'pollinations' or 'rules'
    assert data["engine"] in ("pollinations", "rules", "pollinations-gemini", "pollinations-mistral")
    assert len(data["reply"]) > 30


def test_chat_rejects_empty_message() -> None:
    r = client.post("/v1/chat", json={"message": ""})
    assert r.status_code == 422


def test_llm_config_no_key_fallback(monkeypatch) -> None:
    monkeypatch.delenv("ASTRAL_LLM_API_KEY", raising=False)
    monkeypatch.delenv("GROQ_API_KEY", raising=False)
    monkeypatch.delenv("OPENROUTER_API_KEY", raising=False)
    cfg = LLMConfig()
    # Without any API key → disabled, falls back to rule-based replies
    assert cfg.enabled is False
    assert len(cfg.providers) == 0


def test_llm_config_reads_env(monkeypatch) -> None:
    monkeypatch.setenv("ASTRAL_LLM_API_KEY", "sk-test")
    monkeypatch.setenv("ASTRAL_LLM_MODEL", "test-model")
    monkeypatch.setenv("ASTRAL_LLM_BASE_URL", "https://api.openai.com/v1")
    cfg = LLMConfig()
    assert cfg.enabled is True
    custom = [p for p in cfg.providers if p["name"] == "custom"]
    assert len(custom) == 1
    assert custom[0]["model"] == "test-model"


def test_chat_health_reports_engine() -> None:
    r = client.get("/v1/chat/health")
    assert r.status_code == 200
    body = r.json()
    # Health reports the active provider name or 'rules'
    assert body["engine"] in ("rules", "pollinations", "pollinations-gemini", "pollinations-mistral", "groq", "openai", "openrouter", "custom")
    assert "providers" in body


# ── reel EN narrative ────────────────────────────────────────────────
def test_en_narrative_full_beats() -> None:
    from src.services.reel_reading import reel_reading
    from src.services.reel_reading_en import _HOOKS_EN
    from src.services.tarot_meanings_th import th_card_name
    r = reel_reading("en-test", spread="three_card", seed=42)
    th = r["narrative"]["th"]
    en = r["narrative"]["en"]
    for c in r["cards"]:
        assert th_card_name(c["card"]) in th and c["card"] in en
    # EN must now contain story beats beyond the bare meaning
    assert len(en) > len(th) * 0.5
    all_hooks = [h for hooks in _HOOKS_EN.values() for h in hooks]
    assert any(h in en for h in all_hooks)


def test_en_major_arcana_has_story() -> None:
    from src.services.reel_reading_en import story_for
    assert "leap" in (story_for("The Fool", "upright") or "")
    assert "break" in (story_for("The Tower", "upright") or "")
    assert "chains were never locked" in (story_for("The Devil", "reversed") or "")
