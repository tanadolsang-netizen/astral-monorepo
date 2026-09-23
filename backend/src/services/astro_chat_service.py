"""AI หมอดูอาจารย์ดาว — ระบบแชทโหราศาสตร์

Uses unified LLM client (OpenAI SDK → local Ollama Qwen3-8B).
Falls back to rule-based replies if LLM is unreachable.
"""

from __future__ import annotations

import logging
import json

from src.services.llm_client import get_llm_client

logger = logging.getLogger("astral.astro_chat_service")

SYSTEM_PROMPT = """คุณคือ "หมอดูอาจารย์ดาว" โหราสายไทยผู้มีประสบการณ์ 30 ปี ที่พูดจาอบอุ่น เข้าใจคน และตรงไปตรงมา

กติกาการตอบ:
1. ตอบเป็นภาษาเดียวกับที่ผู้ใช้ถาม (ถามไทยตอบไทย ถามอังกฤษตอบอังกฤษ)
2. โทนเสียง: เหมือนหมอดูนัดเล่าให้ฟังต่อหน้า — เรียกผู้ใช้ว่า "คุณ" พูดเป็นกันเอง ไม่เป็นทางการ ไม่ใช้ศัพท์บัญญัติจนกว่าจะจำเป็น
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


def chat_completion(messages: list[dict], max_tokens: int = 500,
                    temperature: float = 0.8) -> str | None:
    """Call LLM via unified client (Ollama Qwen3-8B)."""
    try:
        # Prepend system prompt if not already present
        if not any(m.get("role") == "system" for m in messages):
            messages = [{"role": "system", "content": SYSTEM_PROMPT}] + messages
        
        client = get_llm_client()
        return client.chat_raw(messages=messages, max_tokens=max_tokens, temperature=temperature)
    except Exception as e:
        logger.warning(f"LLM call failed, falling back to rules: {e}")
        return None


def build_context(birth_data: dict | None, recent_readings: list[str] | None) -> list[str]:
    """Build user-specific context for embedding in messages."""
    ctx = []
    if birth_data:
        ctx.append("Birth chart data: " + json.dumps(birth_data, ensure_ascii=False))
    for r in (recent_readings or [])[-3:]:
        ctx.append("Recent reading excerpt: " + r[:400])
    return ctx


def get_provider_status() -> dict:
    """Check LLM provider status via unified client."""
    try:
        client = get_llm_client()
        health = client.health_check()
        return {
            "ok": health["ok"],
            "model": client.model,
            "base_url": client._base_url,
            "provider": "ollama",
            "error": health.get("error"),
        }
    except Exception as e:
        logger.error(f"Provider status check failed: {e}")
        return {"ok": False, "error": str(e)}


# Legacy class for backward compatibility
class LLMConfig:
    def __init__(self) -> None:
        try:
            client = get_llm_client()
            health = client.health_check()
            self.use_api = health["ok"]
        except Exception:
            self.use_api = False

    @property
    def enabled(self) -> bool:
        return self.use_api

    def get_active_provider(self) -> dict | None:
        if self.use_api:
            return {"name": "ollama"}
        return None
