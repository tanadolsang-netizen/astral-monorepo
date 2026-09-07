"""AI หมอดูอาจารย์ดาว — ระบบแชทโหราศาสตร์

ลำดับการเรียก AI:
1. ผู้ให้บริการที่ตั้งค่าเอง (ASTRAL_LLM_API_KEY + ASTRAL_LLM_BASE_URL)
2. Groq (GROQ_API_KEY — สมัครฟรี, 30 req/min, Llama 3.3 70B)
3. OpenRouter (OPENROUTER_API_KEY — สมัครฟรี, model:free = ไม่เสียเงิน)
4. Rule-based fallback — ตอบจาก keywords, ไม่ต้องพึ่ง AI เลย

วิธีตั้งค่า (เลือกอย่างใดอย่างหนึ่ง):

  # ง่ายสุด: Groq (ฟรี)
  export GROQ_API_KEY=gsk_xxxxx

  # หรือ: OpenRouter (ฟรี ถ้าใช้ model:free)
  export OPENROUTER_API_KEY=sk-or-xxxxx

  # หรือ: ใช้ AI ของตัวเอง
  export ASTRAL_LLM_API_KEY=sk-xxxxx
  export ASTRAL_LLM_BASE_URL=https://api.openai.com/v1
  export ASTRAL_LLM_MODEL=gpt-4o-mini
"""

from __future__ import annotations

import os
import urllib.request
import json

SYSTEM_PROMPT = """คุณคือ "หมอดูอาจารย์ดาว" โหราสายไทยผู้มีประสบการณ์ 30 ปี ที่พูดจาอบอุ่น เข้าใจคน และตรงไปตรงมา

กติกาการตอบ:
1. ตอบเป็นภาษาเดียวกับที่ผู้ใช้ถาม (ถามไทยตอบไทย ถามอังกฤษตอบอังกฤษ)
2. โทนเสียง: เหมือนหมอดูนั่งเล่าให้ฟังต่อหน้า — เรียกผู้ใช้ว่า "คุณ" พูดเป็นกันเอง ไม่เป็นทางการ ไม่ใช้ศัพท์บัญญัติจนกว่าจะจำเป็น
3. เชื่อมคำตอบกับหลักโหราศาสตร์เสมอ (ราศี ดาวเคราะห์ ดวงจันทร์ ลัคนา ทรานซิต) เมื่อมีข้อมูล birth chart ของผู้ใช้ ให้อ้างอิงจาก context ที่แนบมา
4. เจาะจง มีภาพ — เล่าเป็นเหตุการณ์ที่ผู้ใช้จินตนาการตามได้ ไม่พูดกว้างๆ จนใช้ได้กับใครก็ได้
5. จบคำตอบด้วยคำแนะนำที่ทำได้จริง 1-2 ข้อ

ข้อห้าม (ตอบปฏิเสธอย่างสุภาพและเสนอมุมโหรแทน):
6. ไม่วินิจฉัยโรค ไม่แนะนำการรักษาพยาบาล — บอกว่า "เรื่องสุขภาพให้ถามแพทย์ แต่ดูดวงสุขภาพในแง่การดูแลตัวเองได้"
7. ไม่ให้คำแนะนำลงทุน/หุ้น/คริปโตจำเพาะ — บอกว่า "เรื่องลงทุนให้ปรึกษาผู้เชี่ยวชาญ แต่ดวงการเงินในภาพรวมดูได้"
8. ไม่ทำนายความตาย ไม่ทำนายวันที่แน่นอนของเหตุการณ์ร้ายแรง — เปลี่ยนเป็นช่วงเวลาที่ควรระวังและวิธีเสริมดวง
9. ไม่ทำนายการตั้งครรภ์ ไม่ตัดสินความสัมพันธ์ที่ผิดจรรยาบรรณให้เด็ดขาด — ให้มุมมองและให้ผู้ใช้ตัดสินใจเอง
10. ถ้าถามนอกหัวข้อโหราศาสตร์/ดวงชะตา ให้ยิ้มๆ ตอบว่า "เรื่องนี้อาจารย์ขอโฟกัสเรื่องดวงให้นะ"

ความยาว: กระชับ 3-6 ประโยค ยกเว้นผู้ใช้ขอรายละเอียด"""


# ── ผู้ให้บริการ AI ──────────────────────────────────────────────

def _build_providers() -> list[dict]:
    """สร้างรายการผู้ให้บริการจาก environment variables

    ลำดับ: custom → groq → openrouter (เรียงตาม priority)
    """
    providers = []

    # 1. ผู้ให้บริการที่ตั้งค่าเอง (สูงสุด)
    custom_key = os.getenv("ASTRAL_LLM_API_KEY", "")
    custom_base = os.getenv("ASTRAL_LLM_BASE_URL", "")
    custom_model = os.getenv("ASTRAL_LLM_MODEL", "")
    custom_provider = os.getenv("ASTRAL_LLM_PROVIDER", "")

    if custom_key and custom_base:
        if "openrouter" in custom_provider:
            providers.append({
                "name": "openrouter",
                "base_url": custom_base.rstrip("/"),
                "model": custom_model or "meta-llama/llama-3.3-70b-instruct:free",
                "api_key": custom_key,
                "priority": 0,
            })
        else:
            providers.append({
                "name": "custom",
                "base_url": custom_base.rstrip("/"),
                "model": custom_model or "gpt-4o-mini",
                "api_key": custom_key,
                "priority": 0,
            })
    elif custom_key:
        providers.append({
            "name": "openai",
            "base_url": "https://api.openai.com/v1",
            "model": custom_model or "gpt-4o-mini",
            "api_key": custom_key,
            "priority": 0,
        })

    # 2. Groq (ฟรี 30 req/min, สมัครที่ console.groq.com)
    groq_key = os.getenv("GROQ_API_KEY", "")
    if groq_key:
        providers.append({
            "name": "groq",
            "base_url": "https://api.groq.com/openai/v1",
            "model": os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile"),
            "api_key": groq_key,
            "priority": 1,
        })

    # 3. OpenRouter (ฟรี ถ้าใช้ model:free, สมัครที่ openrouter.ai)
    or_key = os.getenv("OPENROUTER_API_KEY", "")
    if or_key:
        providers.append({
            "name": "openrouter",
            "base_url": "https://openrouter.ai/api/v1",
            "model": os.getenv("OPENROUTER_MODEL", "meta-llama/llama-3.3-70b-instruct:free"),
            "api_key": or_key,
            "priority": 2,
        })

    return sorted(providers, key=lambda p: p["priority"])


class LLMConfig:
    """ตั้งค่า LLM — ลองทีละผู้ให้บริการ"""

    def __init__(self) -> None:
        self.providers = _build_providers()
        self._active_provider: dict | None = None

    @property
    def enabled(self) -> bool:
        return len(self.providers) > 0

    def get_active_provider(self) -> dict | None:
        if self._active_provider:
            return self._active_provider
        if self.providers:
            self._active_provider = self.providers[0]
            return self._active_provider
        return None


def _call_provider(provider: dict, messages: list[dict],
                   max_tokens: int = 500, temperature: float = 0.8) -> str | None:
    """เรียก OpenAI-compatible API"""
    payload = json.dumps({
        "model": provider["model"],
        "messages": [{"role": "system", "content": SYSTEM_PROMPT}] + messages,
        "max_tokens": max_tokens,
        "temperature": temperature,
    }).encode()

    headers = {
        "Content-Type": "application/json",
        "User-Agent": "Astral-Chat/1.0",
    }
    api_key = provider.get("api_key", "")
    if api_key:
        headers["Authorization"] = f"Bearer {api_key}"

    req = urllib.request.Request(
        f"{provider['base_url']}/chat/completions",
        data=payload,
        headers=headers,
    )
    try:
        resp = json.load(urllib.request.urlopen(req, timeout=30))
        return resp["choices"][0]["message"]["content"]
    except Exception:
        return None


def chat_completion(messages: list[dict], max_tokens: int = 500,
                    temperature: float = 0.8) -> str | None:
    """ลองเรียก AI ทีละตัว — ถ้าตัวไหนไม่ว่าง ข้ามไปตัวถัดไป

    ถ้าไม่มีผู้ให้บริการใดเลย คืน None → ให้ caller ใช้ rule-based fallback
    """
    cfg = LLMConfig()
    if not cfg.enabled:
        return None

    for provider in cfg.providers:
        result = _call_provider(provider, messages, max_tokens, temperature)
        if result:
            cfg._active_provider = provider
            return result

    return None


def build_context(birth_data: dict | None, recent_readings: list[str] | None) -> list[str]:
    """สร้างข้อมูลเฉพาะผู้ใช้สำหรับฝังใน system message"""
    ctx = []
    if birth_data:
        ctx.append("Birth chart data: " + json.dumps(birth_data, ensure_ascii=False))
    for r in (recent_readings or [])[-3:]:
        ctx.append("Recent reading excerpt: " + r[:400])
    return ctx


def get_provider_status() -> dict:
    """ตรวจสอบสถานะผู้ให้บริการทั้งหมด"""
    cfg = LLMConfig()
    return {
        "providers": [p["name"] for p in cfg.providers],
        "active": cfg.get_active_provider()["name"] if cfg.get_active_provider() else None,
        "enabled": cfg.enabled,
    }
