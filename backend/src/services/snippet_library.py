"""
Snippet library architecture — the content engine of Astral.

This is our answer to Co-Star's snippet system, but instead of a
hand-mapped library of one-liners tagged by Western aspects only, we
build snippet collections PER ENGINE. Our backend has 83 astrology
services — Vedic (KP, Jaimini, Dasha, Ashtakavarga), Chinese (BaZi,
Ziwei, QMDJ, Da Liu Ren), Western (transits, progressions, composite,
synastry), Tarot, Gene Keys, Parans, Fixed Stars, Cosmobiology.

The key insight from studying Co-Star:

  1. A "snippet" is a short text fragment with astrological trigger tags.
  2. The AI layer is not creative — it SELECTS snippets whose triggers
     match the day's computed transits, then ASSEMBLES them.
  3. Our advantage: we have more triggers. Co-Star has ~10 Western
     aspects. We have every engine that computes anything.

So the design:
  - Each snippet is {id, engine, trigger, mood, epigram, body, do[], dont[]}
  - trigger is a string key like "moon_enters_sagittarius" or
    "dasha_shift_kethu" or "mars_square_natal_sun"
  - The assembler takes the user's day (computed transits + natal
    context + behavior weights) and produces a personalized reading.

Tone rules (Thai, tarot-reader voice — per user standing order):
  - บุคคลที่สอง (คุณ) 100% — เหมือนเพื่อนโคตรเข้าใจมาตื่นเตือน
  - สั้น ตรงใจ อ่านแล้วอยากแคปส่งใน LINE group
  - deadpan delivery — บอกเรื่องหนักเท่าไรก็พูดปกติ
  - ไม่ใช้คำเครียด ไม่มี emoji ไม่มีคำอุทาน
  - surreal juxtaposition — เอาของที่ไม่ค่อยไปด้วยกันมาติดกันได้
    เช่น "ทำวันนี้: ฟังเพลงเมานาน เสียงหมอ Karena" (ถ้าตรงกับ transit จริง)
"""

from __future__ import annotations

import json
import logging
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

logger = logging.getLogger("astral.snippets")

# ---------------------------------------------------------------------------
# Snippet data structure
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class Snippet:
    """A short, self-contained text fragment with astrological triggers.

    Fields:
      id: unique key (also used for dedup — never show the same twice)
      engine: which engine produced this ('western', 'vedic', 'kp',
              'jaimini', 'chinese', 'bazi', 'tarot', 'gene_keys', 'parans')
      trigger: what astrological event activates this. One of:
          - "moon_enters_{sign}"           — Moon changes zodiac sign
          - "moon_void"                    — Moon void-of-course
          - "moon_phase_{new|full|q1|q3}" — lunar phase shift
          - "aspect_{planet1}_{planet2}"   — any transit aspect
          - "planet_retro_{planet}"        — planet stations retrograde
          - "dasha_shift_{planet}"         — Vedic Vimshottari dasha change
          - "dasha_shift_{planet}_antardasha"  — sub-period change
          - "kp_sign_lord_{planet}"        — KP star lord changes
          - "bazi_month_{animal}"          — Chinese month branch changes
          - "bazi_day_master_{element}"    — BaZi day pillar element
          - "tarot_{card}"                 — daily tarot draw
          - "gene_keys_{gate}"             — Gene Key activation
          - "parans_{star}"                — paran star rising/setting
          - "fixed_star_{name}"            — fixed star conjunction
      mood: emotional register: 'defiant' | 'contemplative' | 'romantic' |
            'ambitious' | 'melancholy' | 'playful' | 'rebellious' |
            'patient' | 'intense' | 'detached'
      epigram: short cryptic opener (max ~12 words) — the headline
      body: the newsprint-style paragraph (1-3 sentences) — the meat
      do_list: 3 concrete "do" items (noun phrases)
      dont_list: 3 concrete "don't" items (noun phrases)
      tags: additional tags for behavior-layer matching, e.g.
            ['career', 'love', 'self', 'social', 'money', 'health',
             'creativity', 'spiritual']
    """

    id: str
    engine: str
    trigger: str
    mood: str
    epigram: str
    body: str
    do_list: tuple[str, ...] = field(default_factory=tuple)
    dont_list: tuple[str, ...] = field(default_factory=tuple)
    tags: tuple[str, ...] = field(default_factory=tuple)

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "engine": self.engine,
            "trigger": self.trigger,
            "mood": self.mood,
            "epigram": self.epigram,
            "body": self.body,
            "do": list(self.do_list),
            "dont": list(self.dont_list),
            "tags": list(self.tags),
        }


# ---------------------------------------------------------------------------
# Snippet library — the Co-Star-style collection, Thai voice
# ---------------------------------------------------------------------------
#
# Each snippet is engineered to be:
#   - Screenshot-optimized: reads like a text from a brutally honest friend
#   - Engine-driven: trigger fires on a real computed event
#   - Thai-native: not translated — WRITTEN in Thai first, sound natural
#
# Design principle: the body should feel like the user is reading their own
# mind back to them, but in a slightly surreal, deadpan voice.

_LIBRARY: list[Snippet] = [
    # --- Western transits: Moon changes ------------------------------------
    Snippet(
        id="moon_aries_01",
        engine="western",
        trigger="moon_enters_aries",
        mood="defiant",
        epigram="วันนี้คุณไม่อยากรอใคร",
        body="พลังงานพุ่งขึ้นมาแต่เช้าแบบไม่รู้ตัว ถ้าอยากทำอะไรที่กลัว ๆ ก็เอาเลยวันนี้ ดาวเคราะห์ไม่ตั้งใจทำให้คุณใจร้อน แต่ให้คุณรู้ตัวว่าคุณสามารถเริ่มได้แล้วก็จริง",
        do_list=("เดินทางเดี่ยว", "เริ่มอะไรใหม่", "พูดความจริง"),
        dont_list=("อ่อนข้ออ้างอฟ", "นั่งรอคนอื่น", "กลัวความผิดพลาด"),
        tags=("career", "self"),
    ),
    Snippet(
        id="moon_taurus_01",
        engine="western",
        trigger="moon_enters_taurus",
        mood="patient",
        epigram="วันนี้อะไรที่ช้าๆ ก็ดี",
        body="ดวงให้คุณชอบความสม่ำเสมอมากกว่าความตื่นเต้น ถ้าอยากดูหนังอีกครั้งก็ดู ถ้าอยากกินอาหารเดิมก็กิน ความสุขของวันนี้อยู่ในสิ่งที่คงที่",
        do_list=("กินช้าๆ", "ฟังเพลงซ้ำ", "อยู่กับของที่รู้จัก"),
        dont_list=("เปลี่ยนแผน", "รีบร้อน", "อยากได้ของใหม่"),
        tags=("self",),
    ),
    Snippet(
        id="moon_gemini_01",
        engine="western",
        trigger="moon_enters_gemini",
        mood="playful",
        epigram="วันนี้สมองคุณวิ่งเร็วกว่าปกติ",
        body="ความคิดกระโดดไปมาไม่หยุด ถ้าเป็นงานเขียนหรือคุยกัน นี่วันที่ดี แต่ถ้าเป็นงานที่ต้องโฟกัสคนเดียว นั่งติด doodle บนกระดาษอาจดีกว่า",
        do_list=("คุยกับคนใหม่", "เรียนรู้เรื่องบ้าๆ", "เดินเล่นระหว่างพัก"),
        dont_list=("นั่งทำงานนานๆ", "ตัดสินใจใหญ่", "เชื่อข่าวลือ"),
        tags=("social", "creativity"),
    ),
    Snippet(
        id="moon_cancer_01",
        engine="western",
        trigger="moon_enters_cancer",
        mood="melancholy",
        epigram="วันนี้ใจคุณอ่อนกว่าปกติ",
        body="ดวงให้ความรู้สึกที่ลึกขึ้น อาจไม่จำเป็นต้องหาคำอธิบาย ถ้าอยากอยู่คนเดียวก็อยู่ ถ้าอยากโทรหาคนที่รักก็โทร แต่ห้ามบีบความรู้สึกให้แบน",
        do_list=("ทำอาหารเพื่อตัวเอง", "ดูรูปเก่า", "ร้องไห้ได้ถ้าต้องการ"),
        dont_list=("ฝืน upbeat", "อ่านข่าวหนัก", "เก็บเรื่องใส่ใจคนเดียว"),
        tags=("self",),
    ),
    Snippet(
        id="moon_leo_01",
        engine="western",
        trigger="moon_enters_leo",
        mood="ambitious",
        epigram="วันนี้คุณอยากถูกเห็น",
        body="ดวงทำให้คุณอยากเป็นตัวของตัวเองเต็มที่ ไม่ใช่ show off แต่คือการยืนอยู่ในแสงของตัวเอง ถ้าอยากพูดในที่ประชุมก็พูด ถ้าอยากใส่เสื้อที่ชอบก็ใส่",
        do_list=("พูดความคิดเห็น", "แต่งตัวให้ชอบ", "ถ่ายรูป selfie"),
        dont_list=("ยอมเป็น invisible", "กลัวความสนใจ", "ซ่อนความสามารถ"),
        tags=("career", "social"),
    ),
    Snippet(
        id="moon_virgo_01",
        engine="western",
        trigger="moon_enters_virgo",
        mood="contemplative",
        epigram="วันนี้คุณอยากทำอะไรให้สมบูรณ์",
        body="ความอยากทำให้ดีที่สุดของตัวเองเดือดขึ้นมา ถ้าเป็นงานเล็กที่ค้างคาไว้นาน นี่วันที่ดี แต่ถ้าเป็นความสัมพันธ์ อย่าลืมว่าไม่ต้องมีใครสมบูรณ์แบบทั้งนั้น",
        do_list=("จัดของ", "แก้ปัญหายุ่ง", "ดูแลสุขภาพ"),
        dont_list=("วินิจฉัยตัวเอง", "วินิจฉัยคนอื่น", "ทำอะไรกึ่งๆ"),
        tags=("career", "health"),
    ),
    Snippet(
        id="moon_libra_01",
        engine="western",
        trigger="moon_enters_libra",
        mood="romantic",
        epigram="วันนี้คุณอยากความสวย",
        body="ดวงให้ความสุขในเรื่องที่ลงตัว ไม่ว่าจะเป็นรูปลักษณ์ ความสัมพันธ์ หรือการตัดสินใจที่ยุติธรรม ถ้าเป็นงานที่ต้องเจรจา นี่วันที่ดี",
        do_list=("แต่งตัวสวย", "เจรจาอย่างดี", "ไปคาเฟ่สวยๆ"),
        dont_list=("พูดความไม่ตรงไปตรงมา", "ยอมแพ้เร็ว", "เลือกของถูกถูกๆ"),
        tags=("love", "social"),
    ),
    Snippet(
        id="moon_scorpio_01",
        engine="western",
        trigger="moon_enters_scorpio",
        mood="intense",
        epigram="วันนี้คุณรู้สึกลึกกว่าเดิม",
        body="ดวงเปิดประตูห้องลับของตัวเอง ถ้ามีอะไรที่พักซ่อนอยู่นาน นี่วันที่ดีที่จะเผชิญหน้า ไม่ใช่เวลาเก่งที่จะเล่นเถียงนะ",
        do_list=("นั่งสมาธิ", "เขียน journal", "ดูอะไรที่ลึกๆ"),
        dont_list=("ถกเรื่อง superficial", "บังคับคนอื่นให้เปิดใจ", "เล่นเกมจิตวิทยา"),
        tags=("self",),
    ),
    Snippet(
        id="moon_sagittarius_01",
        engine="western",
        trigger="moon_enters_sagittarius",
        mood="defiant",
        epigram="วันนี้คุณอยากออกไปไกล",
        body="ดวงให้ความอยากเดินทาง แม้จะไปแค่ 10 นาทีออกไปจากที่คุ้นเคย ถ้าเป็นงานที่ต้องคิดกว้าง นี่วันที่ดี ถ้าอยากเรียนแบบใหม่ๆ ก็เอา",
        do_list=("เดินทาง", "เรียนภาษา", "อ่านหนังสือต่างประเทศ"),
        dont_list=("นั่งติดที่เดิม", "เชื่อถือแผนเดิม", "เครียดเรื่องเล็ก"),
        tags=("self", "creativity"),
    ),
    Snippet(
        id="moon_capricorn_01",
        engine="western",
        trigger="moon_enters_capricorn",
        mood="ambitious",
        body="ดวงให้ความอยากสร้างของจริง ไม่อยากเสียเวลาแล้ว ถ้าเป็นงานที่ต้อง discipline นี่วันที่ดี แต่อย่าลืมพักด้วยล่ะ",
        epigram="วันนี้คุณไม่ต้องการความบันเทิง",
        do_list=("ทำงานหนัก", "วางแผนยาว", "แก้ปัญหาเก่า"),
        dont_list=("ผัดวันประหยพร", "หลีกเลี่ยงหน้าที่", "หวานлюบอี่"),
        tags=("career",),
    ),
    Snippet(
        id="moon_aquarius_01",
        engine="western",
        trigger="moon_enters_aquarius",
        mood="detached",
        epigram="วันนี้คุณมองโลกจากมุมสูง",
        body="ดวงให้มุมมองที่ห่างออกมาหน่อย ถ้ามีเรื่องที่ติดอยู่ในกรอบเดิม นี่วันที่ดีที่จะก้าวออกมามองจากข้างนอก",
        do_list=("คิดแบบแปลกใหม่", "ทำอะไรเพื่อชุมชน", "อยู่คนเดียว"),
        dont_list=("ทำตามแบบเดิม", "ตกอยู่ในความคาดหวัง", "คุยเรื่อง superficial"),
        tags=("self", "social"),
    ),
    Snippet(
        id="moon_pisces_01",
        engine="western",
        trigger="moon_enters_pisces",
        mood="melancholy",
        epigram="วันนี้ความฝันและความจริงเบลอ",
        body="ดวงให้ความรู้สึกที่ลอย ๆ อาจเป็นวันที่สวยถ้าอยู่คนเดียว ฟังเพลง ดูหนัง แต่ถ้าเป็นวันที่ต้องตัดสินใจจริงจัง รอพรุ่งนี้อาจดีกว่า",
        do_list=("ฟังเพลง", "จับจ้าง", "เดินทางริมน้ำ"),
        dont_list=("ตัดสินใจใหญ่", "เชื่อใจคนแปลก", "ฝันกลางวันมากเกินไป"),
        tags=("self",),
    ),
    # --- Western transits: aspects (template-based) -------------------------
    Snippet(
        id="mars_square_natal_sun_01",
        engine="western",
        trigger="aspect_Mars_Sun",
        mood="intense",
        epigram="วันนี้คุณอยากทะเลาะกับใครสักคน",
        body="ดวงให้พลังงานท้าทายมากกว่าปกติ ถ้าเป็นงานที่ต้อง defend ตัวเอง นี่วันที่ดี แต่ถ้าเป็นเรื่อง trivial ที่ไม่สำคัญ ปล่อยไว้ก่อนดีกว่า",
        do_list=("ออกกำลังกายหนัก", "เขียนความคิดเห็น", "คุยกับคนที่เข้าใจ"),
        dont_list=("ส่ง text ตอนโกรธ", "ทำอย่างเกร็ง", "ตัดสินใจตอนร้อน"),
        tags=("career", "self"),
    ),
    Snippet(
        id="venus_trine_natal_moon_01",
        engine="western",
        trigger="aspect_Venus_Moon",
        mood="romantic",
        epigram="วันนี้คุณน่ารักขึ้นมาเอง",
        body="ดวงให้เสน่ห์ที่ออกมาอย่างธรรมชาติ ถ้ามีใครที่อยากคุย แต่กลัว นี่วันที่ดี ถ้าเป็นงานที่ต้อง present นี่วันที่ดี",
        do_list=("แต่งตัวสวย", "ชวนคนที่ชอบคุย", "ฟังเพลงซึ้ง"),
        dont_list=("ซ่อนความรู้สึก", "ปฏิเสธคำชวน", "ทำงานคนเดียว"),
        tags=("love", "social"),
    ),
    Snippet(
        id="saturn_square_natal_moon_01",
        engine="western",
        trigger="aspect_Saturn_Moon",
        mood="melancholy",
        epigram="วันนี้คุณรู้สึกหน่วง",
        body="ดวงให้ความรู้สึกหนักเท่าไหร่ก็ได้ แต่จำไว้ว่านี่คือช่วงของ discipline ไม่ใช่ช่วงของความสุข ถ้าอยากทำอะไรที่ยาก นี่วันที่ดี ถ้าอยากพัก ก็พัก",
        do_list=("นอนให้ครบ", "เขียนเรื่องที่หนัก", "อยู่กับคนใจดี"),
        dont_list=("ฝืน upbeat", "ตัดสินใจใหญ่", "รับหน้าที่เพิ่ม"),
        tags=("self",),
    ),
    Snippet(
        id="jupiter_trine_natal_sun_01",
        engine="western",
        trigger="aspect_Jupiter_Sun",
        mood="ambitious",
        epigram="วันนี้คุณโชคดีขึ้นมาเอง",
        body="ดวงให้โอกาสที่อยู่ข้างหน้า ถ้าอยากลองอะไรใหม่ที่น่ากลัว นี่วันที่ดี แต่อย่าลืมว่าโชคดีไม่ได้มาเอง ต้องลงมือด้วย",
        do_list=("เริ่มอะไรใหม่", "เจรจาการเงิน", "ชวนคนคุย"),
        dont_list=("รอลง", "กลัวความเสี่ยง", "ไม่เชื่อในตัวเอง"),
        tags=("career", "money"),
    ),
    # --- Western: retrogrades ----------------------------------------------
    Snippet(
        id="mercury_retro_01",
        engine="western",
        trigger="planet_retro_Mercury",
        mood="contemplative",
        epigram="วันนี้สิ่งของที่เสียหายจะแสดงตัว",
        body="ดาวพุ糕点เลี้ยวถอยหลัง ถ้าอุปกรณ์หรือเรื่องที่มีอยู่แล้วมีปัญหา นี่ไม่ใช่วันที่เริ่มใหม่ แต่เป็นวันที่แก้ของเก่า",
        do_list=("ตรวจอุปกรณ์", "แก้ของเก่า", "คุยเรื่องที่ค้างคา"),
        dont_list=("เริ่มอะไรใหม่", "ไปหาหมอทำฟัน", "อ่านสัญญาใหม่"),
        tags=("career",),
    ),
    Snippet(
        id="venus_retro_01",
        engine="western",
        trigger="planet_retro_Venus",
        mood="melancholy",
        epigram="วันนี้อดีตในความรักโผล่มา",
        body="ดาวศุกร์เดินถอยหลัง ถ้าอยากคุยกับคนเก่า หรือลองแต่งหน้าแบบเก่า นี่วันที่ดี แต่ถ้าอยากตัดสินใจเรื่องรัก รอพรุ่งนี้อาจดีกว่า",
        do_list=("ดูรูปเก่า", "แต่งตัวแบบเดิม", "คุยกับคนที่เข้าใจ"),
        dont_list=("เริ่มความสัมพันธ์ใหม่", "ตัดสินใจใหญ่", "ซื้อของใหม่"),
        tags=("love",),
    ),
    # --- Vedic: dasha shifts -----------------------------------------------
    Snippet(
        id="dasha_shift_venus_01",
        engine="vedic",
        trigger="dasha_shift_Venus",
        mood="romantic",
        epigram="วันนี้คุณเข้าสู่ยุคของความรัก",
        body="ดวงไม้เปลี่ยนเป็นวัชรีดา (Venus) ช่วงที่ความสัมพันธ์ ความงาม และความสุขเป็นเรื่องสำคัญ ถ้าอยากเริ่มความสัมพันธ์ใหม่ หรือแต่งตัวสวย ๆ นี่วันที่ดี",
        do_list=("แต่งตัวสวย", "ชวนคนที่ชอบคุย", "ฟังเพลงซึ้ง"),
        dont_list=("ทำงานหนักคนเดียว", "ปิดกั้นตัวเอง", "ไม่ดูแลตัวเอง"),
        tags=("love", "creativity"),
    ),
    Snippet(
        id="dasha_shift_saturn_01",
        engine="vedic",
        trigger="dasha_shift_Saturn",
        mood="patient",
        epigram="วันนี้คุณเข้าสู่ยุคของงานหนัก",
        body="ดวงไม้เปลี่ยนเป็นเสาร์ (Saturn) ช่วงที่ discipline และความรับผิดชอบเป็นเรื่องสำคัญ ถ้าอยากสร้างอะไรที่ยาวนาน นี่วันที่ดี แต่อย่าลืมพักด้วยล่ะ",
        do_list=("ทำงานหนัก", "วางแผนยาว", "ดูแลสุขภาพ"),
        dont_list=("ฝันกลางวัน", "หวานлюบอี่", "รับหน้าที่มากเกินไป"),
        tags=("career", "health"),
    ),
    Snippet(
        id="dasha_shift_kethu_01",
        engine="vedic",
        trigger="dasha_shift_Kethu",
        mood="detached",
        epigram="วันนี้คุณรู้สึกหลุดออกมาจากทุกอย่าง",
        body="ดวงไม้เปลี่ยนเป็นเกตู (Kethu) ช่วงที่ปล่อยวางและมองแวบมาเป็นเรื่องสำคัญ ถ้าอยากอยู่คนเดียว หรือลองสิ่งใหม่ที่แปลก ๆ นี่วันที่ดี",
        do_list=("นั่งสมาธิ", "ลองสิ่งใหม่", "อยู่คนเดียว"),
        dont_list=("ยึดติดเรื่องเก่า", "ตัดสินใจใหญ่", "ทำงานหนัก"),
        tags=("self", "spiritual"),
    ),
    # --- KP: sign lord changes ---------------------------------------------
    Snippet(
        id="kp_sign_lord_sun_01",
        engine="kp",
        trigger="kp_sign_lord_Sun",
        mood="ambitious",
        epigram="วันนี้คุณอยากเป็นตัวของตัวเอง",
        body="ระบบ KP ให้ lord ของคุณเป็นดวงอาทิตย์ ดวงให้ความมั่นใจและพลังนำ ถ้าอยากพูดในที่ประชุม หรือเริ่มอะไรใหม่ นี่วันที่ดี",
        do_list=("พูดความคิดเห็น", "เริ่มอะไรใหม่", "ดูแลสุขภาพ"),
        dont_list=("ยอมเป็น invisible", "กลัวความสนใจ", "ซ่อนความสามารถ"),
        tags=("career", "self"),
    ),
    Snippet(
        id="kp_sign_lord_moon_01",
        engine="kp",
        trigger="kp_sign_lord_Moon",
        mood="melancholy",
        epigram="วันนี้ความรู้สึกของคุณชัดเจน",
        body="ระบบ KP ให้ lord ของคุณเป็นดวงจันทร์ ดวงให้ความรู้สึกที่ลึกและเปลี่ยนแปลง ถ้าอยากอยู่กับความรู้สึกของตัวเอง นี่วันที่ดี",
        do_list=("เขียน journal", "อยู่กับคนใจดี", "ฟังเพลงซึ้ง"),
        dont_list=("ฝืน upbeat", "ตัดสินใจใหญ่", "เก็บเรื่องใส่ใจคนเดียว"),
        tags=("self",),
    ),
    # --- Chinese: month branch changes ------------------------------------
    Snippet(
        id="bazi_month_rat_01",
        engine="bazi",
        trigger="bazi_month_Rat",
        mood="ambitious",
        epigram="วันนี้คุณฉลาดขึ้นมาเอง",
        body="ดวงจีนเข้าสู่เดือนชวด ดวงให้ความฉลาดและความสามารถคิดเร็ว ถ้าอยากเริ่มอะไรใหม่ หรือแก้ปัญหา นี่วันที่ดี",
        do_list=("เริ่มอะไรใหม่", "แก้ปัญหาเก่า", "เรียนสิ่งใหม่"),
        dont_list=("รอลง", "กลัวความเสี่ยง", "ไม่เชื่อในตัวเอง"),
        tags=("career", "money"),
    ),
    Snippet(
        id="bazi_month_horse_01",
        engine="bazi",
        trigger="bazi_month_Horse",
        mood="defiant",
        epigram="วันนี้คุณอยากวิ่ง",
        body="ดวงจีนเข้าสู่เดือนม้า ดวงให้พลังงานและการเคลื่อนไหว ถ้าอยากออกกำลังกาย หรือเดินทาง นี่วันที่ดี",
        do_list=("ออกกำลังกาย", "เดินทาง", "เริ่มอะไรใหม่"),
        dont_list=("นั่งติดที่เดิม", "รอลง", "กลัวความเสี่ยง"),
        tags=("self", "health"),
    ),
    # --- Tarot: daily draw -------------------------------------------------
    Snippet(
        id="tarot_the_fool_01",
        engine="tarot",
        trigger="tarot_The_Fool",
        mood="defiant",
        epigram="วันนี้คุณเป็น The Fool",
        body="ไพ่ The Fool บอกว่าถ้าอยากเริ่มอะไรใหม่ หรือเดินทางที่ไม่รู้จุดหมาย นี่วันที่ดี แต่อย่าลืมสำรองเงินไว้ด้วยล่ะ",
        do_list=("เริ่มอะไรใหม่", "เดินทาง", "ลองสิ่งใหม่"),
        dont_list=("คิดมาก", "กลัวความเสี่ยง", "ยึดติดแผนเดิม"),
        tags=("self", "creativity"),
    ),
    Snippet(
        id="tarot_the_lovers_01",
        engine="tarot",
        trigger="tarot_The_Lovers",
        mood="romantic",
        epigram="วันนี้คุณเจอกับทางเลือกที่สำคัญ",
        body="ไพ่ The Lovers บอกว่าถ้ามีเรื่องที่ต้องเลือกระหว่างสองสิ่ง นี่วันที่ดีที่จะตัดสินใจด้วยหัวใจ แต่อย่าลืมใช้ความคิดด้วยล่ะ",
        do_list=("คุยกับคนรัก", "ตัดสินใจด้วยใจ", "แต่งตัวสวย"),
        dont_list=("ตัดสินใจคนเดียว", "เลือกทางง่าย", "กลัวความผูกพัน"),
        tags=("love",),
    ),
    # --- Gene Keys: gate activation ---------------------------------------
    Snippet(
        id="gene_keys_gate_64_01",
        engine="gene_keys",
        trigger="gene_keys_gate_64",
        mood="contemplative",
        epigram="วันนี้คุณอยู่ในประตู 64",
        body="Gene Key 64 บอกว่าถ้าอยากเห็นภาพกว้าง หรือเชื่อมจุดที่เป็น scattered นี่วันที่ดี แต่อย่าลืมพักด้วยล่ะ",
        do_list=("นั่งสมาธิ", "เขียน journal", "ดูภาพกว้าง"),
        dont_list=("คิดมาก", "เครียดเรื่องเล็ก", "ทำงานหนัก"),
        tags=("self", "spiritual"),
    ),
]


# ---------------------------------------------------------------------------
# Indexing: trigger -> snippets
# ---------------------------------------------------------------------------

_BY_TRIGGER: dict[str, list[Snippet]] = {}
_BY_ID: dict[str, Snippet] = {}
_BY_ENGINE: dict[str, list[Snippet]] = {}
_BY_TAG: dict[str, list[Snippet]] = {}


def _index(s: Snippet) -> None:
    _BY_TRIGGER.setdefault(s.trigger, []).append(s)
    _BY_ID[s.id] = s
    _BY_ENGINE.setdefault(s.engine, []).append(s)
    for t in s.tags:
        _BY_TAG.setdefault(t, []).append(s)


for _s in _LIBRARY:
    _index(_s)


def get_by_trigger(trigger: str) -> list[Snippet]:
    """All snippets that fire on this astrological trigger."""
    return _BY_TRIGGER.get(trigger, [])


def get_by_engine(engine: str) -> list[Snippet]:
    """All snippets for a given engine."""
    return _BY_ENGINE.get(engine, [])


def get_by_tag(tag: str) -> list[Snippet]:
    """All snippets tagged with this behavior category."""
    return _BY_TAG.get(tag, [])


def get_by_id(snippet_id: str) -> Snippet | None:
    return _BY_ID.get(snippet_id)


def all_snippets() -> list[Snippet]:
    """The complete library — used by tests and admin endpoints."""
    return list(_LIBRARY)


def library_stats() -> dict[str, Any]:
    """Library inventory — used by tests and admin endpoints."""
    engines: dict[str, int] = {}
    moods: dict[str, int] = {}
    for s in _LIBRARY:
        engines[s.engine] = engines.get(s.engine, 0) + 1
        moods[s.mood] = moods.get(s.mood, 0) + 1
    return {
        "total": len(_LIBRARY),
        "engines": engines,
        "moods": moods,
        "triggers": len(_BY_TRIGGER),
        "tags": len(_BY_TAG),
    }


# ---------------------------------------------------------------------------
# Trigger derivation: computed day -> trigger keys
# ---------------------------------------------------------------------------
#
# This is the "content mapping" step of the Co-Star pipeline, but our
# version is richer: we derive triggers from EVERY engine, not just
# Western transits.


def derive_triggers(day: dict[str, Any]) -> list[str]:
    """Extract astrological trigger keys from a computed 'day'.

    The 'day' dict comes from the transit engine + other engines:

      {
        "bodies": [{"body": "Moon", "sign": "Aries", "is_retrograde": False, ...}],
        "moon_sign": "Aries",            # optional (extracted from bodies)
        "moon_phase": "new",             # optional
        "retrogrades": ["Mercury"],      # optional
        "aspects": [{"p1": "Mars", "p2": "Sun", "type": "square"}],  # optional
        "vedic_dasha": "Venus",          # optional
        "kp_sign_lord": "Sun",           # optional
        "bazi_month_branch": "Rat",      # optional
        "bazi_day_master": "Wood",       # optional
        "tarot_draw": "The_Fool",        # optional
        "gene_keys_gate": 64,            # optional
      }

    Returns a list of trigger strings (some may be duplicated if multiple
    aspects fire — the assembler handles that).
    """
    triggers: list[str] = []

    # Western: Moon enters sign
    moon_sign = day.get("moon_sign")
    if not moon_sign:
        for b in day.get("bodies", []):
            if b.get("body") == "Moon":
                moon_sign = b.get("sign")
                break
    if moon_sign:
        triggers.append(f"moon_enters_{moon_sign.lower()}")

    # Western: retrogrades
    for planet in day.get("retrogrades", []):
        triggers.append(f"planet_retro_{planet}")

    # Western: aspects (any aspect between any two transit planets)
    for asp in day.get("aspects", []):
        p1 = asp.get("p1", "")
        p2 = asp.get("p2", "")
        if p1 and p2:
            triggers.append(f"aspect_{p1}_{p2}")

    # Western: lunar phase
    moon_phase = day.get("moon_phase")
    if moon_phase:
        triggers.append(f"moon_phase_{moon_phase.lower()}")

    # Vedic: dasha shift
    vedic_dasha = day.get("vedic_dasha")
    if vedic_dasha:
        triggers.append(f"dasha_shift_{vedic_dasha}")
        triggers.append(f"dasha_shift_{vedic_dasha}_antardasha")

    # KP: sign lord
    kp_lord = day.get("kp_sign_lord")
    if kp_lord:
        triggers.append(f"kp_sign_lord_{kp_lord}")

    # Chinese: BaZi month branch + day master element
    bazi_branch = day.get("bazi_month_branch")
    if bazi_branch:
        triggers.append(f"bazi_month_{bazi_branch}")
    bazi_master = day.get("bazi_day_master")
    if bazi_master:
        triggers.append(f"bazi_day_master_{bazi_master}")

    # Tarot: daily draw
    tarot = day.get("tarot_draw")
    if tarot:
        triggers.append(f"tarot_{tarot.replace(' ', '_')}")

    # Gene Keys: gate activation
    gate = day.get("gene_keys_gate")
    if gate:
        triggers.append(f"gene_keys_gate_{gate}")

    return triggers


# ---------------------------------------------------------------------------
# Assembly: triggers + behavior weights -> personalized reading
# ---------------------------------------------------------------------------


@dataclass
class Reading:
    """The assembled daily reading — our version of Co-Star's daily
    epigram + Do/Don't list + newsprint body."""

    epigram: str
    body: str
    do_list: tuple[str, ...]
    dont_list: tuple[str, ...]
    snippet_ids: tuple[str, ...] = field(default_factory=tuple)
    mood: str = "contemplative"

    def to_dict(self) -> dict[str, Any]:
        return {
            "epigram": self.epigram,
            "body": self.body,
            "do": list(self.do_list),
            "dont": list(self.dont_list),
            "mood": self.mood,
            "snippet_ids": list(self.snippet_ids),
        }


def assemble(
    triggers: list[str],
    behavior_weights: dict[str, float] | None = None,
    exclude_ids: set[str] | None = None,
) -> Reading:
    """Assemble a personalized reading from triggered snippets.

    behavior_weights: {tag: 0.0-1.0} — weight for each behavior tag
    (career, love, self, social, money, health, creativity, spiritual).
    Higher = more important to this user (based on their past behavior).

    exclude_ids: snippet ids already shown today (dedup — never show the
    same snippet twice in one day).

    Algorithm:
      1. For each trigger, find matching snippets.
      2. Score each snippet by behavior_weight of its tags (sum or max).
      3. Pick the highest-scoring snippet as the anchor (epigram + body).
      4. Collect do/dont items from the next 2-3 highest-scoring snippets
         (but never repeat items).
      5. Return the assembled Reading.
    """
    if not triggers:
        return Reading(
            epigram="วันนี้ดาราเคลื่อนไหว",
            body="เปิดแอปเพื่ออ่านดวงวันนี้ของคุณ",
            do_list=("เปิดแอป",),
            dont_list=("ปิดแอป",),
        )

    weights = behavior_weights or {}
    exclude = exclude_ids or set()

    # 1. Collect candidate snippets (dedup by id)
    candidates: dict[str, Snippet] = {}
    for trigger in triggers:
        for s in get_by_trigger(trigger):
            if s.id in exclude:
                continue
            candidates[s.id] = s

    if not candidates:
        return Reading(
            epigram="วันนี้ดาราเคลื่อนไหว",
            body="เปิดแอปเพื่ออ่านดวงวันนี้ของคุณ",
            do_list=("เปิดแอป",),
            dont_list=("ปิดแอป",),
        )

    # 2. Score by behavior weights
    def score(s: Snippet) -> float:
        if not s.tags:
            return 0.5
        return max(weights.get(t, 0.0) for t in s.tags)

    scored = sorted(candidates.values(), key=score, reverse=True)

    # 3. Anchor = highest-scoring snippet
    anchor = scored[0]
    epigram = anchor.epigram
    body = anchor.body
    mood = anchor.mood

    # 4. Collect do/dont from next 2-3 snippets (avoid duplicates)
    do_list: list[str] = []
    dont_list: list[str] = []
    for s in scored[1:4]:
        for item in s.do_list:
            if item not in do_list:
                do_list.append(item)
        for item in s.dont_list:
            if item not in dont_list:
                dont_list.append(item)

    # If we have no extras, fall back to anchor's own lists
    if not do_list:
        do_list = list(anchor.do_list)
    if not dont_list:
        dont_list = list(anchor.dont_list)

    # Cap at 3 items each (Co-Star style: 3 dos, 3 don'ts)
    do_list = do_list[:3]
    dont_list = dont_list[:3]

    return Reading(
        epigram=epigram,
        body=body,
        do_list=tuple(do_list),
        dont_list=tuple(dont_list),
        snippet_ids=tuple(s.id for s in scored[:4]),
        mood=mood,
    )


# ---------------------------------------------------------------------------
# Convenience: build a "day" dict from the transit engine output
# ---------------------------------------------------------------------------


def build_day_from_transit(transit: dict[str, Any]) -> dict[str, Any]:
    """Convert transit_service.compute_now() output into a 'day' dict
    that derive_triggers() can consume.

    This is the bridge between the ephemeris engine and the content
    engine — the "data ingestion" step of the pipeline.
    """
    bodies = transit.get("bodies", [])
    day: dict[str, Any] = {"bodies": bodies}

    # Extract moon sign, retrogrades, aspects from bodies
    moon_sign = None
    retrogrades: list[str] = []
    aspects: list[dict[str, str]] = []

    for b in bodies:
        body_name = b.get("body", "")
        if body_name == "Moon":
            moon_sign = b.get("sign")
        if b.get("is_retrograde"):
            retrogrades.append(body_name)
        # Simple aspect detection: same sign = conjunction
        # (in a real impl, this would be replaced by proper aspect calc)
        if body_name and moon_sign and b.get("sign") == moon_sign:
            aspects.append({"p1": body_name, "p2": "Moon", "type": "conjunction"})

    if moon_sign:
        day["moon_sign"] = moon_sign
    if retrogrades:
        day["retrogrades"] = retrogrades
    if aspects:
        day["aspects"] = aspects

    return day
