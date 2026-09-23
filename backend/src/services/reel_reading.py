"""Reel-style tarot reading — เล่าแบบหมอดูใน IG Reel/TikTok.

Layer ที่วางบน tarot_service.draw_spread() — ไม่แตะ engine เดิม
หลักการเขียน (ตาม humanizer skill):
- ประโยคแรกต้อง "โดน" — hook แบบคนดูรีล feel ตัวเองทันที
- พูดถึง "คุณ" ตลอด เหมือนนั่งเล่าให้ฟังคนเดียว
- มีเหตุการณ์เป็นภาพ ไม่ใช่นิยามศัพท์
- ไทยเป็นเสียงพูดธรรมชาติ en mirror แบบ native speaker ไม่แปลตรงตัว
"""
from __future__ import annotations

from src.services.tarot_service import draw_spread, SPREADS
from src.services import reel_reading_en as _en
from src.services import starheart_map

_POSITION_LABEL = {
    1: "สถานการณ์ปัจจุบัน",
    2: "อุปสรรค",
    3: "คำแนะนำ",
}
_POSITION_LABEL_EN = {
    1: "current situation",
    2: "obstacle",
    3: "advice",
}

_HOOKS_TH = {
    "สถานการณ์ปัจจุบัน": [
        "มีบางอย่างในใจคุณกำลังกระดุกกระดิกอยู่นะ",
        "ตอนนี้ชีวิตคุณเหมือนยืนอยู่ตรงทางแยก รู้ไหม",
        "ถ้ารู้สึกว่าช่วงนี้อะไรก็ไม่ลงตัว... ไพ่ก็บอกแบบนั้นเหมือนกัน",
    ],
    "อุปสรรค": [
        "และรู้ไหมว่าอะไรที่มันฉุดคุณไว้...",
        "มีบางคน บางเรื่อง กำลังกินพลังคุณอยู่เงียบๆ",
        "ปัญหาที่คุณคิดว่ามันจบไปแล้ว มันยังไม่จบจริงนะ",
    ],
    "คำแนะนำ": [
        "ฟังตรงนี้นะ สำคัญๆ",
        "ไพ่ใบนี้คือสิ่งที่อยากให้คุณทำมากที่สุด",
        "ถ้าทำตามตรงนี้ ทุกอย่างจะคลี่คลายเอง",
    ],
    "คำตอบ": [
        "โอเค ถามตรงๆ ตอบตรงๆ นะ",
        "ไพ่ใบเดียวแต่พูดได้หมดเลย",
    ],
}
_HOOKS_EN = {
    "current situation": ["Here's what's really going on with you right now."],
    "obstacle": ["And here's the thing that's been holding you back..."],
    "advice": ["Listen, this part matters."],
    "answer": ["Straight question, straight answer."],
}

# ── story beats ต่อการ์ด (major arcana เท่านั้น — minor ใช้ generic) ──
_STORY_TH = {
    "The Fool": ("มีเรื่องใหม่ๆ มาล่อคุณอยู่ และคุณก็อยากกระโดดลงไปเต็มๆ",
                 "แต่รอก่อน — คราวนี้อย่ากระโดดตาถึงตาตาย มองพื้นด้านล่างก่อน"),
    "The Magician": ("คุณมีของทุกอย่างครบแล้ว แค่ยังไม่กล้าหยิบมันมาใช้",
                     "ระวังคนที่พูดเก่งแต่ทำไม่เป็น — เขากำลังใช้เวทมนตร์ใส่คุณ"),
    "The High Priestess": ("มีบางอย่างที่คุณรู้อยู่แก่ใจอยู่แล้ว แต่ยังแกล้งทำเป็นไม่เห็น",
                           "สัญชาตญาณคุณไม่เคยพลาด — ที่พลาดคือตอนที่คุณไม่ฟังมัน"),
    "The Empress": ("มีคนรักคุณมากกว่าที่คุณคิดนะ",
                    "คุณให้คนอื่นมากเกินไปจนลืมเติมตัวเอง — หยุดก่อน หายใจแรงๆ"),
    "The Emperor": ("คุณคือคนที่ต้องคุมสถานการณ์ ไม่ใช่ให้ใครมาคุมคุณ",
                    "การควบคุมมากเกินไปมันไม่ใช่ความปลอดภัย มันคือกรง"),
    "The Hierophant": ("คนรอบข้างมีคำแนะนำเยอะแยะ แต่คำตอบที่ใช่ต้องเป็นของคุณ",
                       "บางกฎมันล้าสมัยแล้ว ทำลายมันได้ ไม่มีใครว่า"),
    "The Lovers": ("ใจคุณขัดกันเองอยู่ตอนนี้ — สมองบอกอย่าง หัวใจบอกอีกอย่าง",
                   "คนที่คุณคิดถึงอยู่ตอนนี้ เขารู้สึกแบบเดียวกับคุณหรือเปล่า... ไพ่บอกว่ามากกว่าที่คิด"),
    "The Chariot": ("อย่าเพิ่งถอย คุณกำลังจะถึงแล้วจริงๆ",
                    "คุมความเร็วไว้ อย่าให้ใครเหยียบเบรกแทนคุณ"),
    "Strength": ("สิ่งที่คุณกำลังฝืนอยู่เงียบๆ มันเหนื่อยมากใช่ไหม",
                 "ความอ่อนโยนของคุณคือพลัง ไม่ใช่ความอ่อนแอ — อย่าให้ใครบอกอย่างอื่น"),
    "The Hermit": ("ช่วงนี้อยากอยู่คนเดียว ไม่อยากคุยกับใคร — ไม่ผิดนะ",
                   "แต่อย่าอยู่คนเดียวนานเกิน คนที่รอคุณอยู่ยังรออยู่"),
    "Wheel of Fortune": ("วงลอกำลังหมุน และหมุนเข้าทางคุณแล้ว",
                         "สิ่งที่เสียไปช่วงก่อน กำลังจะกลับมาในรูปแบบที่ดีกว่า"),
    "Justice": ("สิ่งที่คุณทำดีไว้ กำลังจะได้รับคืน — และสิ่งที่ใครทำไม่ดีกับคุณก็เช่นกัน",
                "ความจริงมักมาช้า แต่มาแน่ รอได้"),
    "The Hanged Man": ("คุณติดอยู่เพราะมองเรื่องเดิมซ้ำๆ มาเกินไป",
                       "ลองพลิกมัน 180 องศาดู คำตอบจะโผล่มาเอง"),
    "Death": ("บทที่ผ่านมาของชีวิตคุณปิดลงแล้ว จริงๆ",
              "อย่าไปง้อบทเก่า — บทใหม่กำลังเปิดอยู่ตรงนี้"),
    "Temperance": ("อย่าเพิ่งรีบ สิ่งที่รอมันคือสิ่งที่คุ้ม",
                   "กลางๆ ไม่ได้แปลว่าจืด มันแปลว่าสมดุลพอดี"),
    "The Devil": ("มีบางอย่าง หรือบางคน ที่คุณรู้ว่าไม่ดีแต่เลิกไม่ได้",
                  "โซ่ที่รัดคุณ ล็อกไม่ได้เลย — คุณเดินออกมาได้ตอนไหนก็ได้"),
    "The Tower": ("มีบางอย่างกำลังจะพัง และมันจะพังเสียงดังมาก",
                  "แต่ฟังก่อน — มันพังเพราะฐานรากมันไม่ได้เรื่องมานานแล้ว ปล่อยมันพัง"),
    "The Star": ("หลังฝนตกหนัก ท้องฟ้ากำลังเปิดแล้ว",
                 "ความหวังที่คุณแอบถือไว้ ไม่ใช่ความฝันลมปาก"),
    "The Moon": ("บางอย่างไม่ได้เห็นตามที่ปรากฏ ระวังการตัดสินใจตอนหัวฟูม",
                 "ความกลัวที่ใหญ่ที่สุดของคุณ มักไม่ใช่อันตรายที่สุด"),
    "The Sun": ("โชคดีจริงๆ ใบนี้ — มีความสุขที่ชัดๆ รอคุณอยู่",
                "อย่ารับไม่ถูกนะ คุณสมควรได้ดีแบบนี้"),
    "Judgement": ("อะไรบางอย่างกำลังปลุกคุณจากการมองโลกแบบเดิม",
                  "โอกาสที่เคยปฏิเสธไป มันกลับมาหาคุณอีกครั้ง — คราวนี้คิดดีๆ"),
    "The World": ("วงจรหนึ่งของคุณจบสมบูรณ์แล้ว คุณทำได้จริงๆ",
                  "เวทีที่กว้างขึ้นรออยู่ ออกเดินทางได้เลย"),
}


# ── LOVE / Soulmate–Twin Flame spread (บุกหมวดความรัก แบบ 5 reel ที่ศึกษา) ──
# position สำหรับสเปรดคู่รัก: อดีตความรัก / ปัจจุบัน / อนาคตคู่
_LOVE_POSITION_LABEL = {
    1: "ความรักในอดีต",
    2: "ความรักตอนนี้",
    3: "ความรักที่กำลังมา",
}
_LOVE_POSITION_LABEL_EN = {
    1: "where love has been",
    2: "your love now",
    3: "the love coming",
}

# hook หมวดรัก — เจาะใจ + signs-vs-outcome (สไตล์ @scorpiosuntarot1111 / lightworker)
_HOOKS_LOVE_TH = {
    "ความรักในอดีต": [
        "มีบางเรื่องในอดีตที่คุณยังไม่ได้ปล่อยมือสักที... รู้ไหม",
        "คนเก่าที่คุณเคยรัก ยังวนเวียนอยู่ในหัวคุณตอนกึก累了ไหม",
    ],
    "ความรักตอนนี้": [
        "ตอนนี้มีพลังบางอย่างกำลังสะเทือนในใจคุณ — คุณรู้สึกมันใช่ไหม",
        "และรู้นะ... ว่าทำไมคุณยังกล้าเปิดใจไม่ได้ทั้งที่อยากมาก",
        "ถ้ารู้สึกว่าใครซักคนกำลังคิดถึงคุณตลอดเวลา — ไพ่ก็บอกแบบนั้น",
    ],
    "ความรักที่กำลังมา": [
        "ฟังตรงนี้ นะ สำคัญมาก — คนที่ใช่กำลังจะเข้ามา",
        "มีสัญญาณบอกคุณอยู่: เขากำลังกลับมา หรือกำลังเดินเข้าหา",
        "อย่าปิดกั้น เพราะรอบนี้มันคนละระดับกับที่เคยเจอ",
    ],
}
_HOOKS_LOVE_EN = {
    "where love has been": ["There's something from your past you still haven't let go of..."],
    "your love now": ["Right now, something in your heart is vibrating — you feel it, don't you."],
    "the love coming": ["Listen — the right person is on their way. This one's different."],
}

# signs list (ซ้าย) vs outcome list (ขวา) — เอาไปใส่ reel overlay ได้
_LOVE_SIGNS_TH = [
    "คนที่คิดถึงคุณตลอดเวลา", "ฝันถึงเขาบ่อยผิดปกติ", "เลข 11:11 โผล่หน้าจอบ่อย",
    "แอบไปดูโปรไฟล์เขา", "เพลงรักเดิมกลับมาในหัว", "เพื่อนบอกว่าเห็นเขาถามถึงคุณ",
]
_LOVE_OUTCOME_TH = [
    "ความรักที่เคยพัง กำลังกลับมาเยียวยา", "เขากำลังกลับมาขอโอกาสใหม่",
    "คุณสมควรได้รักที่มั่นคง", "twin flame ของคุณไม่ได้หายไปไหน แค่กำลังกลับมา",
]

# ความหมายไพ่เจาะหมวดรัก (override ทับ _STORY_TH ถ้ามี)
_STORY_LOVE_TH = {
    "The Lovers": ("ใจคุณกำลังเลือกระหว่างสองทาง — และครั้งนี้ เลือกจากหัวใจไม่ใช่ความคุ้นเคย",
                   "ถ้าหัวใจบอกว่าไม่ใช่ อย่าฝืนอยู่กับเขาเพราะสงสารตัวเอง"),
    "Two of Cups": ("มีคนมองคุณแบบที่ไม่มีใครเคยมอง — เหมือนแก้วสองใบจับคู่กัน",
                    "ถ้ารู้สึกว่าใช่ แปลว่าอีกฝ่ายก็รู้สึกแบบเดียวกัน"),
    "Three of Cups": ("ความสุขรอบนี้มีคนมาร่วมเฉลิมฉลองด้วย — เพื่อนหรือคนรักใหม่",
                      "อย่าปล่อยโอกาสดีๆ ผ่าน เพราะกลัวจะผิดพลาดเหมือนเก่า"),
    "Six of Cups": ("มีบางคนจากอดีตที่ยังเก็บความรู้สึกดีๆ กับคุณไว้ — เขาไม่ได้ลืมคุณ",
                    "ระวังเอาอดีตมาฝันเกินไป จนมองปัจจุบันไม่ออก"),
    "Ten of Cups": ("นี่คือความรักที่จบสวย — ครอบครัว ความอบอุ่น ที่คุณปรารถนามาตลอด",
                    "ความสุขนี้อยู่ที่การเปิดใจรับ ไม่ใช่การรอให้คนอื่นทำให้"),
    "The Star": ("หลังน้ำตาเรื่องรัก ท้องฟ้ากำลังเปิด — ยังมีคนดีรอคุณอยู่",
                 "ความหวังเรื่องรักที่คุณแอบถือไว้ ไม่ใช่ความฝันลมปาก"),
    "The Moon": ("มีบางอย่างในเรื่องรักที่ยังมืดมัว อย่าพึ่งตัดสินใจตอนหัวฟูม",
                 "ความกลัวที่คุณคิดว่าคือสัญชาตญาณ บ่อยครั้งเป็นแค่ความไม่มั่นใจ"),
    "The Sun": ("โชคดีจริงๆ ใบนี้เรื่องรัก — มีความสุขชัดๆ รอคุณอยู่",
                "อย่ารับไม่ถูกนะ คุณสมควรได้รักแบบนี้"),
    "The Tower": ("ความรักที่ผิดๆ กำลังจะพัง — และมันคือการปลดปล่อยไม่ใช่หายนะ",
                  "แต่ฟังก่อน มันพังเพราะฐานรากไม่ได้เรื่อง มันดีที่ปล่อยมันพัง"),
    "The Devil": ("มีบางความสัมพันธ์ที่คุณรู้ว่าไม่ดี แต่เลิกไม่ได้ — มันผูกมัดคุณ",
                  "โซ่ที่รัดคุณ ล็อกไม่ได้เลย เดินออกมาได้ตอนไหนก็ได้"),
    "The Hermit": ("ช่วงนี้คุณอยากอยู่คนเดียวเพื่อเยียวยาตัวเอง — ไม่ผิดนะ",
                   "แต่อยู่คนเดียวนานเกิน คนที่รอคุณอยู่เขาก็เหนื่อยนะ"),
    "Ace of Cups": ("มีความรู้สึกใหม่กำลังจะเกิด — ราวกับแก้วถ้วยใหม่เติมน้ำให้พร้อมล้น",
                    "อย่ากลัวที่จะรัก again เพราะแก้วใบนี้สะอาดกว่าเก่า"),
    "Knight of Cups": ("มีคนกำลังจะเดินเข้ามาหาคุณพร้อมหัวใจ — เขามาแบบจริงจัง",
                       "ระวังคนพูดหวานแต่ไม่แสดงออก ดูการกระทำไม่ใช่คำพูด"),
    "Queen of Cups": ("ความรักของคุณตอนนี้ลึกและอบอุ่น — เหมือนคนที่เข้าใจคุณโดยไม่ต้องอธิบาย",
                      "แต่อย่าให้ความเห็นใจคนอื่น ทับความรักที่คุณสมควรได้"),
    "King of Cups": ("เขาที่ใช่คือคนที่คุมอารมณ์เป็น — ไม่ใช่คนที่ทำให้คุณต้องเดาใจ",
                    "ความมั่นคงทางใจ คือสิ่งที่คุณหามานาน"),
    "Judgement": ("อดีตความรักกำลังปลุกคุณให้เข้าใจบทเรียน — คราวนี้โตแล้ว",
                  "โอกาสรักที่เคยปฏิเสธ อาจกลับมาหา — คราวนี้เลือกด้วยสติ"),
}

# ── SHADOW spread: karmic cycle / narcissistic / dark empathy (ด้านมืดของความรัก) ──
# position: บาดแผลกรรม → เงาของอีกฝ่าย → การตื่นรู้ของคุณ (ออกจาก loop)
_SHADOW_POSITION_LABEL = {
    1: "บาดแผลกรรม",
    2: "เงาของเขา",
    3: "การตื่นรู้ของคุณ",
}
_SHADOW_POSITION_LABEL_EN = {
    1: "the karmic wound",
    2: "his shadow",
    3: "your awakening",
}

# hook ด้านมืด — เจาะตรงจุดเจ็บ (สไตล์ collective shadow-work reel)
_HOOKS_SHADOW_TH = {
    "บาดแผลกรรม": [
        "มีรอยแผลเดิมที่คุณวนลูปเดิมซ้ำๆ — รู้ไหมว่ามันมาจากที่ไหน",
        "คุณดึงคนแบบเดิมเข้ามาเรื่อยๆ เพราะบาดแผลเดิมเรียกหามัน",
    ],
    "เงาของเขา": [
        "และรู้นะ... ว่าเขาไม่ได้รักคุณ แต่กำลังดูดพลังคุณ",
        "คนนี้ไม่ได้มองคุณเป็นคน — เขามองคุณเป็นกระจกส่องความใหญ่ของเขา",
        "ถ้ารู้สึกว่าโดน manipulate โดยที่ยังรักเขาอยู่ — นั่นคือ dark empathy ของเขา",
    ],
    "การตื่นรู้ของคุณ": [
        "ฟังตรงนี้ นะ — คุณไม่ได้ผิดที่รักเขา คุณแค่ตื่นช้าไป",
        "มีจุดจบของลูปนี้ รอคุณตัดสายพันธ์ ที่คุณเป็นคนเดียวที่ตัดได้",
        "อย่าสงสารเขาเกินกว่าที่คุณสงสารตัวเอง",
    ],
}
_HOOKS_SHADOW_EN = {
    "the karmic wound": ["There's an old wound looping you into the same pattern..."],
    "his shadow": ["And know this — he's not loving you, he's feeding on you."],
    "your awakening": ["Listen — you're not wrong for loving him. You're just late to wake up."],
}

# signs (ซ้าย) vs truth (ขวา) — โครงสร้าง bait/confirm แบบ reel สว่าง แต่เนื้อหาด้านมืด
_SHADOW_SIGNS_TH = [
    "เขาพูดหวานแต่ทำไม่เคยเป็น", "คุณรู้สึกผิดทั้งที่ไม่ได้ทำอะไร",
    "ทุกครั้งที่คุณจะไป เขาจะง้อกลับมา", "เพื่อนบอกว่าคุณเปลี่ยนไป",
    "คุณเหนื่อยแต่ก็ไม่กล้าบอกลา", "ถูกโลกเขาคือคุณผิดตลอด",
]
_SHADOW_TRUTH_TH = [
    "เขาเป็นนาร์ซิสซิสต์ — รักแต่ภาพเงาของตัวเอง", "dark empathy: เขาใช้ความเห็นใจคุณเป็นอาวุธ",
    "กรรมนี้วนลูปจนคุณตัดสายพันธ์", "คุณตื่นแล้ว — ลูปนี้จบที่คุณ",
]

# ความหมายไพ่เจาะหมวด shadow (override ทับ _STORY_TH)
_STORY_SHADOW_TH = {
    "The Devil": ("มีบางความสัมพันธ์ที่ผูกมัดคุณไว้ — และมันไม่ใช่ความรัก แต่เป็นกรรม",
                  "โซ่ที่รัดคุณ ล็อกไม่ได้เลย เดินออกมาได้ตอนไหนก็ได้ — เขาไม่มีกุญแจหรอก"),
    "The Tower": ("ภาพที่คุณสร้างขึ้นมาว่าความรักคืออย่างนั้น เพิงพังลง — และนั่นคือการปลดปล่อย",
                  "อย่าโกรธที่มันพัง โกรธที่คุณยอมให้มันตั้งอยู่ใช่ไหม"),
    "The Moon": ("เขาทำตัวลึกลับจนคุณต้องเดาใจตัวเองตลอด — นั่นคือกลลวงไม่ใช่ลึกลับ",
                 "ความกลัวที่คุณคิดว่าคือสัญชาตญาณ บ่อยครั้งเป็นแค่การถูกครอบงำ"),
    "The Magician": ("เขาใช้คำพูดสร้างเวทมนตร์ให้คุณเชื่อ — แต่เบื้องหลังไม่มีอะไรนอกภาพลวง",
                     "ระวังคนที่พูดเก่งแต่ทำไม่เป็น — เขากำลังใช้เวทมนตร์ใส่คุณ"),
    "The Emperor": ("เขาต้องการคุมคุณไม่ใช่รักคุณ — การควบคุมคือกรงไม่ใช่ความปลอดภัย",
                    "ถ้าเขาทำให้คุณต้องเดาใจตัวเองตลอด เขาไม่ใช่คู่ครอง เขาคือผู้คุม"),
    "The Hanged Man": ("คุณยอมพลิกชีวิตตัวเองเพื่อเขามาเกินพอแล้ว — คราวนี้พลิกมุมมองกลับบ้าง",
                      "ลองมองจากมุมเขา แล้วคุณจะเห็นว่าเขาไม่เคยพลิกอะไรเลย"),
    "The Hermit": ("ช่วงนี้คุณต้องอยู่คนเดียวเพื่อเรียกตัวเองกลับมา — ไม่ผิดนะ",
                   "คนที่ทำให้คุณต้องอยู่คนเดียวถึงสบาย นั่นไม่ใช่คนรัก"),
    "The Lovers": ("ใจคุณรู้ตั้งแต่แรกว่ามันไม่ใช่ — แต่คุณเลือกฝืนเพราะสงสารตัวเอง",
                   "ถ้าหัวใจบอกว่าไม่ใช่ อย่าฝืนอยู่กับเขาเพราะเคยลงทุนไปมาก"),
    "Eight of Cups": ("มีบางครั้งคุณรู้ว่าต้องเดินจากไป — แม้จะยังรัก",
                     "การเดินจากไปไม่ใช่ความพ่ายแพ้ มันคือการหยุดวนลูปกรรม"),
    "Ten of Swords": ("จุดที่แย่ที่สุดมันผ่านไปแล้ว — คุณรอดมาได้จริงๆ",
                     "อย่าเอาเข็มที่ทิ่มคุณไปฝังตัวเองต่อ เข็มนั้นไม่ใช่ของคุณ"),
    "Three of Swords": ("หัวใจคุณแตกมาแล้วหลายหน — แต่ครั้งนี้คือครั้งสุดท้ายที่เขาทำได้",
                       "ร้องไห้ให้จบ แล้วลุกมาไม่เหมือนเดิม"),
    "Justice": ("สิ่งที่คุณยอมทนมา เขาจะต้องรับกรรมของตัวเอง — ไม่ใช่หน้าที่คุณสอนเขา",
                "ความจริงมักมาช้า แต่มาตรงๆ คราวนี้คุณอยู่ฝั่งที่ถูก"),
    "Strength": ("สิ่งที่คุณฝืนมาตลอดคือการอยู่กับคนที่กินพลังคุณ — นั่นแข็งแกร่งมากนะ",
                "ความอ่อนโยนของคุณไม่ใช่ความอ่อนแอ แต่อย่าให้เขาเอาไปเป็นอาวุธ"),
    "The Star": ("หลังค่ำคืนที่ถูกดูดพลัง ดวงดาวกำลังกลับมาให้คุณเห็นทาง",
                "ความหวังว่า you'll heal — ไม่ใช่ความฝันลมปาก"),
    "Judgement": ("อดีตความรักกรรมนี้กำลังปลุกคุณให้เข้าใจบทเรียน — คราวนี้โตแล้ว",
                 "คุณตัดสายพันธ์นี้ได้ เพราะคุณรู้แล้วว่ามันวนลูปมายังไง"),
    "The World": ("วงจรกรรมนี้ของคุณปิดสมบูรณ์แล้ว — คุณออกจากลูปได้จริงๆ",
                "เวทีที่ไม่มีเขา รออยู่ ออกเดินทางได้เลย"),
}


# ── CHOSEN spread: starseed / 144,000 / the chosen one (collective + identity) ──
# position: รหัสวิญญาณของคุณ → ภารกิจในชาตินี้ → การตื่นรู้รวม
_CHOSEN_POSITION_LABEL = {
    1: "รหัสวิญญาณของคุณ",
    2: "ภารกิจในชาตินี้",
    3: "การตื่นรู้รวม",
}
_CHOSEN_POSITION_LABEL_EN = {
    1: "your soul code",
    2: "your mission this life",
    3: "the collective awakening",
}

_HOOKS_CHOSEN_TH = {
    "รหัสวิญญาณของคุณ": [
        "มีรหัสบางอย่างในตัวคุณที่คนรอบข้างมองไม่เห็น — แต่คุณรู้สึกมันมาตลอด",
        "คุณไม่ได้รู้สึกแปลกแยกเพราะผิดปกติ คุณรู้สึกแปลกแยกเพราะมาจากที่อื่น",
    ],
    "ภารกิจในชาตินี้": [
        "และรู้นะ... ว่าทำไมคุณถูกดึงให้มาช่วยคนอื่นตลอด — นั่นไม่ใช่บังเอิญ",
        "มีงานที่คุณถูกส่งมาเพื่อทำ แม้คุณจะยังไม่อยากเรียกมันว่าภารกิจ",
    ],
    "การตื่นรู้รวม": [
        "ฟังตรงนี้ นะ — คุณไม่ได้คนเดียวในเรื่องนี้",
        "มีกลุ่มวิญญาณที่ตื่นรู้พร้อมๆ กันกับคุณ รู้สึกมั้ยว่าช่วงนี้คนเหมือนกันเริ่มโผล่มา",
        "อย่ากลัวที่จะเป็น 'หนึ่งในจำนวนนั้น' — มันคือคุณจริงๆ",
    ],
}
_HOOKS_CHOSEN_EN = {
    "your soul code": ["There's a code in you most people can't see — but you've felt it all along."],
    "your mission this life": ["And know this — why you're always pulled to help others isn't accident."],
    "the collective awakening": ["Listen — you are not alone in this. The awakened ones are arriving together."],
}

_CHOSEN_SIGNS_TH = [
    "รู้สึกแปลกแยกมาตลอดแต่ไม่รู้ทำไม", "เลข 11:11 โผล่บ่อยผิดปกติ",
    "ฝันถึงดาวหรือที่ไหนสักแห่งที่คุ้นเคย", "คนรอบข้างมองคุณแปลกแต่ก็ดึงดูด",
    "ถูกดึงให้ช่วยคนอื่นโดยไม่ได้เตรียมตัว", "จุดจบของวัฏสวรรค์รู้สึกใกล้เข้ามา",
]
_CHOSEN_TRUTH_TH = [
    "คุณคือหนึ่งใน 144,000 ที่ตื่นรู้แล้ว", "starseed — วิญญาณที่มาจุติเพื่อปลุกกลุ่ม",
    "ภารกิจของคุณคือการเป็นสะพานให้คนอื่นตื่นตาม", "การตื่นรู้รวมเริ่มแล้ว และคุณอยู่ในนั้น",
]

_STORY_CHOSEN_TH = {
    "The Star": ("หลังค่ำคืนที่หลงทาง ดวงดาวกำลังชี้ทางให้คุณเห็นว่าคุณมาจากไหน",
                 "ความหวังว่าคุณไม่ได้ผิดแปลก — คุณต่างคนต่างต่างหาก"),
    "The Sun": ("โชคดีจริงๆ ใบนี้ — แสงที่คุณเป็นกำลังส่องออกมาให้คนอื่นเห็นทาง",
                "อย่ารับไม่ถูกนะ คุณสมควรเป็นแสงแบบนี้"),
    "The Magician": ("คุณมีของทุกอย่างครบแล้ว — พรสวรรค์นี้ไม่ใช่ได้มาแบบบังเอิญ",
                     "ระวังคนที่พูดเก่งแต่ทำไม่เป็น — เขากำลังใช้เวทมนตร์ใส่คุณ"),
    "The High Priestess": ("มีบางอย่างที่คุณรู้อยู่แก่ใจตั้งแต่เกิด — สัญชาตญาณนั้นคือรหัสวิญญาณ",
                           "สัญชาตญาณคุณไม่เคยพลาด — ที่พลาดคือตอนที่คุณไม่ฟังมัน"),
    "The World": ("วงจรหนึ่งของคุณจบสมบูรณ์แล้ว — คุณมาถึงจุดที่ถูกส่งมาเพื่อถึง",
                "เวทีที่กว้างขึ้นรออยู่ ออกเดินทางได้เลย"),
    "Judgement": ("อะไรบางอย่างกำลังปลุกคุณจากการหลับใหล — คุณจำได้แล้วว่ามาจากไหน",
                 "โอกาสที่เคยปฏิเสธ อาจกลับมาหา — คราวนี้รับรู้ชัดเจน"),
    "Ace of Wands": ("มีประกายใหม่ติดไฟในตัวคุณ — เหมือนดาวที่เพิ่งจุดติด",
                    "อย่าปล่อยประกายนั้นดับ เพราะมันคือภารกิจที่คุณถูกส่งมา"),
    "The Hermit": ("ช่วงนี้คุณต้องอยู่คนเดียวเพื่อฟังเสียงจากภายใน — ไม่ผิดนะ",
                   "คนที่ทำให้คุณต้องอยู่คนเดียวถึงสบาย นั่นไม่ใช่คนรัก"),
    "The Lovers": ("ใจคุณรู้ว่าการมาครั้งนี้มีคนที่ใช่รออยู่ — และเขาเป็นสายวิญญาณเดียวกัน",
                   "ถ้าหัวใจบอกว่าไม่ใช่ อย่าฝืนอยู่กับเขาเพราะเคยลงทุนไปมาก"),
    "Wheel of Fortune": ("วงลากำลังหมุนเข้าทางคุณ — ราวกับจักรวาลกำลังจัดเรียงใหม่",
                        "สิ่งที่เสียไปช่วงก่อน กำลังจะกลับมาในรูปแบบที่กว้างขึ้น"),
    "The Emperor": ("คุณคือคนที่ต้องคุมสถานการณ์ ไม่ใช่ให้ใครมาคุมคุณ",
                    "การควบคุมมากเกินไปมันไม่ใช่ความปลอดภัย มันคือกรง"),
    "Strength": ("สิ่งที่คุณฝีนมาตลอดคือการอยู่กับคนที่ไม่เข้าใจคุณ — นั่นแข็งแกร่งมากนะ",
                "ความอ่อนโยนของคุณไม่ใช่ความอ่อนแอ แต่อย่าให้เขาเอาไปเป็นอาวุธ"),
}


def _story_for(card_name: str, orientation: str) -> tuple[str, str | None]:
    base = _STORY_TH.get(card_name)
    if not base:
        return None
    if orientation == "reversed":
        return (base[1], None)
    return (base[0], None)


def _generic_minor_story(card_name: str, orientation: str) -> str:
    """minor arcana: เล่าจากธาตุ + ตัวเลขแบบพูดคน"""
    suit = card_name.rsplit(" of ", 1)[-1]
    rank = card_name.split(" of ")[0]
    domain_th = {
        "Wands": "เรื่องงานและความทะเยอทะยาน",
        "Cups": "เรื่องใจกับเรื่องรัก",
        "Swords": "เรื่องความคิดกับคำพูด",
        "Pentacles": "เรื่องเงินกับความมั่นคง",
    }[suit]
    verb_th = {
        "Ace": "กำลังจะเริ่มต้น", "Two": "กำลังชั่งใจ", "Three": "กำลังขยายตัว",
        "Four": "กำลังนิ่งจนเริ่มอึดอัด", "Five": "กำลังสะดุด", "Six": "กำลังกลับมาดี",
        "Seven": "กำลังรอจังหวะ", "Eight": "กำลังเร่ง", "Nine": "ใกล้ถึงจุดที่รอ",
        "Ten": "ถึงจุดอิ่มตัวพอดี", "Page": "มีข่าวมาเยือน", "Knight": "วิ่งเร็วไม่หยุด",
        "Queen": "อยู่ในมือคุณแล้ว", "King": "คุณคือผู้คุมมัน",
    }.get(rank, "")
    if orientation == "reversed":
        return f"เรื่อง{domain_th}ตอนนี้{verb_th}แต่มันสะดุดตรงกลาง ไม่ลื่นเหมือนที่ควรจะเป็น"
    return f"เรื่อง{domain_th}{verb_th} — และจังหวะมันกำลังเข้าทางคุณ"


def _chart_echo(card_name: str, chart: dict | None) -> str | None:
    """เผา 'เลเยอร์หยาบ↔ละเอียด' — เชื่อมไพ่ (สัญลักษณ์หยาบ) เข้ากับตำแหน่งดาวจริง (de421, ละเอียด).

    หลัก (มุมมองผู้บัญชาการ 2026-08-31): ไพ่กับดวงคำนวณคือภาษาคนละระดับของเรื่องเดียวกัน
    ไม่ใช่ของจริง vs ของปลอม — สายนี้คือการแปลภาษาหยาบกลับไปหาตำแหน่งจริง
    """
    if not chart:
        return None
    bodies = {b["body"]: b for b in chart.get("bodies", [])}
    asc = chart.get("ascendant", {}).get("sign", "")
    # แผนที่ไพ่ ↔ ดาว/ตำแหน่ง (ครอบคลุม major arcana หลัก)
    link = {
        "The Lovers": ("Venus", "ความรักที่ดาวศุกรวางไว้ในดวงคุณ"),
        "The Sun": ("Sun", f"ดวงอาทิตย์ของคุณอยู่ราศี{asc} — แสงที่เป็นคุณ"),
        "The Moon": ("Moon", "ดวงจันทร์ของคุณคือจุดที่อารมณ์ไหล"),
        "The Star": ("Venus", "ดาวศุกรคือความหวังที่โคจรอยู่ในดวง"),
        "The Magician": ("Mercury", "ดาวพุธคือคำพูดและการลงมือที่คุณมี"),
        "The Emperor": ("Saturn", "ดาวเสาร์คือโครงสร้างที่คุมชีวิตคุณ"),
        "The Hierophant": ("Jupiter", "ดาวพฤหัสคือบทเรียนที่คุณถูกส่งมาเรียน"),
        "The Hermit": ("Saturn", "ดาวเสาร์ดึงคุณเข้าหาตัวเพื่อกลับมาหาความหมาย"),
        "Strength": ("Sun", "ดวงอาทิตย์ให้กำลังที่คุณฝืนมา"),
        "Judgement": ("Jupiter", "ดาวพฤหัสปลุกคุณให้จำชาติเก่า"),
        "The World": ("Jupiter", "ดาวพฤหัสปิดวงจรที่คุณมาถึงจุดสุด"),
        "Wheel of Fortune": ("Jupiter", "ดาวพฤหัสหมุนวงลาในดวงคุณ"),
    }
    if card_name in link:
        planet, echo = link[card_name]
        b = bodies.get(planet)
        if b:
            return f"→ เชื่อมกับดวงจริง: {echo} ({planet} ราศี{b['sign']} {b['degree']}°)"
    return None


def reel_reading(name: str, spread: str = "three_card",
                 seed: int | None = None,
                 element_balance: dict | None = None,
                 chart: dict | None = None,
                 life_context: dict | None = None) -> dict:
    """draw_spread เดิม + เพิ่ม narrative แบบ Reel ทั้ง th/en.

    หมายเหตุ (มุมมองผู้บัญชาการ 2026-08-31): ดวงคำนวณ (de421) และ reel/ไพ่ คือ
    ชั้นความละเอียดเดียวกันของปรากฏการณ์เดียวกัน (coarse↔fine) — ไม่ใช่ของจริง vs ของปลอม
    ถ้าส่ง chart เข้ามา จะเผา "เลเยอร์หยาบ↔ละเอียด" เชื่อมไพ่เข้ากับตำแหน่งดาวจริง
    """
    from src.services.tarot_meanings_en import TAROT_MEANINGS_EN

    # ── STARHEART bridge (P0): ถ้ามี chart ป้อนเข้ามา ให้รีลสืบจากดวงจริง ไม่สุ่ม ──
    if chart is not None:
        size = SPREADS.get(spread, 3)
        star_cards = starheart_map.MAP(chart, max_cards=size)
        base = {
            "name": name,
            "spread": spread,
            "cards": star_cards,
            "tilted_toward": None,
            "elements": None,
            "deterministic": True,
            # provenance recorder: ไพ่แต่ละใบมาจากดาวใด
            "provenance_map": {c["card"]: c["provenance"] for c in star_cards},
        }
    else:
        # ไม่มี chart -> คงสุ่มเดิม (backward-compat)
        base = draw_spread(name, spread=spread, seed=seed,
                           element_balance=element_balance)
        base["deterministic"] = False

    cards_th = []
    cards_en = []
    is_love = spread in ("love", "relationship")
    is_shadow = spread in ("shadow",)
    is_chosen = spread in ("chosen",)
    for i, c in enumerate(base["cards"]):
        position = int(c["position"])
        if is_chosen:
            label_th = _CHOSEN_POSITION_LABEL.get(position, str(position))
            label_en = _CHOSEN_POSITION_LABEL_EN.get(position, str(position))
        elif is_shadow:
            label_th = _SHADOW_POSITION_LABEL.get(position, str(position))
            label_en = _SHADOW_POSITION_LABEL_EN.get(position, str(position))
        elif is_love:
            label_th = _LOVE_POSITION_LABEL.get(position, str(position))
            label_en = _LOVE_POSITION_LABEL_EN.get(position, str(position))
        else:
            label_th = _POSITION_LABEL.get(position, str(position))
            label_en = _POSITION_LABEL_EN.get(position, str(position))
        hook_th = None
        if is_chosen:
            hooks = _HOOKS_CHOSEN_TH.get(label_th)
        elif is_shadow:
            hooks = _HOOKS_SHADOW_TH.get(label_th)
        elif is_love:
            hooks = _HOOKS_LOVE_TH.get(label_th)
        else:
            hooks = _HOOKS_TH.get(label_th)
        if hooks:
            hook_th = hooks[i % len(hooks)]
        if is_chosen and c["card"] in _STORY_CHOSEN_TH:
            _base = _STORY_CHOSEN_TH.get(c["card"])
            story = (_base[1], None) if c["orientation"] == "reversed" else (_base[0], None)
        elif is_shadow and c["card"] in _STORY_SHADOW_TH:
            _base = _STORY_SHADOW_TH.get(c["card"])
            story = (_base[1], None) if c["orientation"] == "reversed" else (_base[0], None)
        elif is_love and c["card"] in _STORY_LOVE_TH:
            _base = _STORY_LOVE_TH.get(c["card"])
            story = (_base[1], None) if c["orientation"] == "reversed" else (_base[0], None)
        else:
            story = _story_for(c["card"], c["orientation"])
        if story is None:
            story = (_generic_minor_story(c["card"], c["orientation"]), None)
        # เผาเลเยอร์หยาบ↔ละเอียด: เชื่อมไพ่เข้าดวงคำนวณจริง (de421)
        chart_echo = _chart_echo(c["card"], chart)

        from src.services.tarot_meanings_th import th_card_name, th_card_meaning
        card_th = th_card_name(c["card"])

        line_th = f"[{position}] {card_th}"
        if hook_th:
            line_th += f"\n{hook_th}"
        if story[0]:
            line_th += f"\n{story[0]}"
        if story[1]:
            line_th += f"\n{story[1]}"
        if chart_echo:
            line_th += f"\n{chart_echo}"
        prov = c.get("provenance")
        if prov:
            line_th += f"\n→ มาจากดวงจริง: {prov}"
        line_th += f"\n→ {th_card_meaning(c['card'], c['orientation'])}"
        cards_th.append(line_th)

        # EN mirror — full reel-style narrative
        hook_en = _en.hook_for(label_en, i)
        story_en = _en.story_for(c["card"], c["orientation"])
        if story_en is None:
            story_en = _en.generic_minor_story(c["card"], c["orientation"])

        line_en = f"[{position}] {c['card']} ({c['orientation']})"
        if hook_en:
            line_en += f"\n{hook_en}"
        line_en += f"\n{story_en}"
        en_meaning = TAROT_MEANINGS_EN.get(c["card"], {}).get(
            "reversed" if c["orientation"] == "reversed" else "upright", "")
        line_en += f"\n→ {en_meaning}"
        cards_en.append(line_en)

    # closing line แบบปิดรีล
    if is_chosen:
        closing_th = (
            "ถ้ารีลนี้เหมือนพูดถึงคุณ... แปลว่าคุณจำได้แล้วว่าใครเอง 🌟 "
            "คุณไม่ได้คนเดียว — กลุ่มวิญญาณที่ตื่นรู้กำลังรวมตัวกัน และคุณอยู่ในนั้น"
        )
        closing_en = (
            "if this felt like it was about you... you remembered who you are. 🌟 "
            "You are not alone — the awakened ones are gathering, and you are one of them."
        )
    elif is_shadow:
        closing_th = (
            "ถ้ารีลนี้เหมือนพูดถึงคุณ... แปลว่าคุณรู้แล้วว่าไม่ต้องวนลูปนี้อีก 🕯️ "
            "ตัดสายพันธ์ที่คุณเป็นคนเดียวตัดได้ — คุณตื่นแล้ว ลูปนี้จบที่คุณ"
        )
        closing_en = (
            "if this felt like it was about you... you already know — no more loops. 🕯️ "
            "Cut the cord only you can cut. You woke up. The cycle ends with you."
        )
    elif is_love:
        closing_th = (
            "ถ้ารีลนี้เหมือนพูดถึงคุณ... แปลว่าความรักที่ใช่กำลังจะมา 💕 "
            "เปิดใจรับสัญญาณที่เขาส่งมา — เขากำลังเดินเข้าหาคุณ"
        )
        closing_en = (
            "if this felt like it was about you... the right love is coming. "
            "Open your heart to the signs — they're already on their way."
        )
    else:
        closing_th = (
            "...และถ้ารีลนี้เหมือนพูดถึงคุณ แปลว่ามันคือคุณจริงๆ 🌙"
        )
        closing_en = "...if this felt like it was about you, it is."

    base["spread_type"] = "chosen" if is_chosen else (
        "shadow" if is_shadow else ("love" if is_love else "general"))
    if is_chosen:
        base["chosen_signs"] = _CHOSEN_SIGNS_TH
        base["chosen_truth"] = _CHOSEN_TRUTH_TH
    if is_shadow:
        base["shadow_signs"] = _SHADOW_SIGNS_TH
        base["shadow_truth"] = _SHADOW_TRUTH_TH
    if is_love:
        base["love_signs"] = _LOVE_SIGNS_TH
        base["love_outcome"] = _LOVE_OUTCOME_TH
    base["narrative"] = {
        "th": "\n\n".join(cards_th) + "\n\n" + closing_th,
        "en": "\n\n".join(cards_en) + "\n\n" + closing_en,
    }
    # ── STARHEART life-grounding (P0): ถ้ามี chart + life_context ให้รีลพูดเรื่องจริง ──
    # แทนข้อความเจนนิกด้วย narrative ชีวิตจริง 100% (คง spread เดิมไว้ใน spread_lines)
    if chart is not None and life_context is not None:
        from src.services.starheart_narrative import ground_narrative
        ctx = dict(life_context)
        ctx.setdefault("name", name)
        grounded_th = ground_narrative(chart, lang="th", user_name=ctx.get("name", name))
        grounded_en = ground_narrative(chart, lang="en", user_name=ctx.get("name", name))
        base["spread_lines"] = {"th": cards_th, "en": cards_en}
        base["narrative"] = {"th": grounded_th, "en": grounded_en}
        base["grounded"] = True
    return base
