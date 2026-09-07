"""Ask Me Anything — AI astrologer chat endpoint.

ใช้ AI หลายตัวเรียงตามลำดับ:
1. ตัวที่ตั้งค่าเอง (env)
2. Groq (ถ้ามี key)
3. Pollinations (ฟรี ไม่ต้อง key)

ถ้าทุกตัวไม่ว่าง → rule-based fallback อัตโนมัติ
"""

from __future__ import annotations

from fastapi import APIRouter
from pydantic import BaseModel, Field

from src.services.astro_chat_service import chat_completion, build_context, LLMConfig
from src.services.disclaimers import detect_refusal, refusal_reply, DISCLAIMER_TH, DISCLAIMER_EN
from src.services.classical_rag import build_context_block

router = APIRouter()


class ChatMessage(BaseModel):
    role: str = Field(pattern="^(user|assistant)$")
    content: str = Field(min_length=1, max_length=2000)


class ChatRequest(BaseModel):
    message: str = Field(min_length=1, max_length=1000)
    history: list[ChatMessage] = Field(default_factory=list, max_length=20)
    birth_data: dict | None = None
    recent_readings: list[str] = Field(default_factory=list, max_length=5)


class ChatResponse(BaseModel):
    reply: str
    engine: str  # "llm" (ชื่อผู้ให้บริการ) หรือ "rules"


def _rule_reply(text: str) -> str:
    t = text.lower()
    if any(k in t for k in ("รัก", "ความรัก", "love", "แฟน")):
        return ("เรื่องความรักช่วงนี้ ดาวศุกร์กำลังโคจรเข้ามุมที่ดีนะครับ "
                "ถ้ายังโสด เปิดใจออกมากหน่อย ปลายสัปดาห์มีโอกาสเจอคนที่คุยถูกคอ "
                "ส่วนใครมีคู่แล้ว ช่วงพระจันทร์เต็มดวงให้เวลากันมากขึ้น ความเข้าใจจะดีขึ้นเอง 🌙")
    if any(k in t for k in ("งาน", "career", "job", "ธุรกิจ")):
        return ("ดวงการงานช่วงนี้ ดาวพฤหัสฯ หนุนบ้านเกียรติยศ โอกาสใหญ่กำลังเข้ามา "
                "แต่ให้รอหลังดาวพุธเดินหน้าก่อน แล้วค่อยตัดสินใจครั้งใหญ่ "
                "ที่ผ่านมาคุณวางฐานไว้ดีแล้ว ตอนนี้แค่เลือกจังหวะให้ถูก 💼")
    if any(k in t for k in ("เงิน", "money", "การเงิน", "finance", "ลงทุน")):
        return ("ดวงการเงินมองภาพรวม ช่วงนี้เหมาะกับการสะสมมากกว่าการผลาญ "
                "ดวงไม่ได้บอกตัวเลขหุ้นนะครับ แต่บอกจังหวะได้ว่าปลายเดือนมีกระแสเงินเข้า "
                "เก็บก่อน แล้วค่อยพิจารณาทีละขั้น 💰")
    if any(k in t for k in ("สุขภาพ", "health", "ป่วย")):
        return ("เรื่องสุขภาพให้ถามแพทย์นะครับ แต่ดูดวงสุขภาพในแง่การดูแลได้ "
                "ดาวเสาร์ชวนเหนื่อยสะสมช่วงนี้ นอนให้พอ ออกกำลังกายเบาๆ "
                "ให้ดวงและร่างกายเป็นธรรมชาติ 🙏")
    return ("อาจารย์รับทราบคำถามของคุณแล้วครับ ช่วงดาวที่โคจรตอนนี้เน้นเรื่องการเริ่มต้นใหม่ "
            "ให้สังเกตสัญญาณรอบตัวสัก 2-3 วัน แล้วค่อยตัดสินใจ "
            "ถ้าอยากให้อ่านลึกขึ้น ลองถามเจาะเรื่องรัก การงาน หรือการเงินดูนะ 🌟")


@router.get("/health")
def chat_health() -> dict:
    """ตรวจสอบสถานะ AI — บอกว่าผู้ให้บริการตัวไหน online"""
    cfg = LLMConfig()
    if not cfg.enabled:
        return {"ok": True, "engine": "rules", "providers": []}
    active = cfg.get_active_provider()
    return {
        "ok": True,
        "engine": active["name"] if active else "rules",
        "providers": [p["name"] for p in cfg.providers],
    }


@router.post("")
def ask(req: ChatRequest) -> ChatResponse:
    messages = [{"role": m.role, "content": m.content} for m in req.history]
    messages.append({"role": "user", "content": req.message})

    context = build_context(req.birth_data, req.recent_readings)
    if context:
        messages.insert(0, {"role": "system",
                            "content": "User context:\n" + "\n".join(context)})

    refusal_cat = detect_refusal(req.message)
    if refusal_cat:
        lang = "th" if any("\u0e0e" <= ch <= "\u0e5b" for ch in req.message) else "en"
        return ChatResponse(reply=refusal_reply(refusal_cat, lang), engine="rules")

    # ลอง AI ทีละตัว — ถ้าไม่มี key ก็ยังใช้ Pollinations ได้
    cfg = LLMConfig()
    if cfg.enabled:
        rag_block = build_context_block(req.message)
        if rag_block:
            messages = [{"role": "system", "content": rag_block}] + messages
        llm_reply = chat_completion(messages)
        if llm_reply:
            active = cfg.get_active_provider()
            engine_name = active["name"] if active else "llm"
            lang = "th" if any("\u0e0e" <= ch <= "\u0e5b" for ch in req.message) else "en"
            disc = DISCLAIMER_TH if lang == "th" else DISCLAIMER_EN
            return ChatResponse(reply=f"{llm_reply}\n\n— {disc}", engine=engine_name)

    return ChatResponse(reply=_rule_reply(req.message), engine="rules")
