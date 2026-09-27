#!/usr/bin/env python3
"""Tarot draw — genuine randomness (secrets.SystemRandom), same convention
already used in this vault's tarot notes (e.g. "Tarot - Two Spreads
(13 ส.ค. 2026).md"). Major Arcana get individual meanings; Minor Arcana are
built from suit x rank so 56 cards don't need hand-written entries each —
meanings follow standard RWS (A.E. Waite, 1911) themes.
"""
import secrets

SUITS = {
    'Wands': {'th': 'ไม้เท้า', 'theme': 'ไฟ แรงบันดาลใจ การลงมือทำ ความกล้า'},
    'Cups': {'th': 'ถ้วย', 'theme': 'น้ำ อารมณ์ ความรัก ความสัมพันธ์'},
    'Swords': {'th': 'ดาบ', 'theme': 'อากาศ ความคิด ความจริง ความขัดแย้ง'},
    'Pentacles': {'th': 'เหรียญ', 'theme': 'ดิน เงินทอง งาน ร่างกาย ความมั่นคง'},
}
RANKS = ['Ace', 'Two', 'Three', 'Four', 'Five', 'Six', 'Seven', 'Eight', 'Nine', 'Ten',
         'Page', 'Knight', 'Queen', 'King']
RANK_TH = {'Ace': 'เอซ', 'Two': 'สอง', 'Three': 'สาม', 'Four': 'สี่', 'Five': 'ห้า', 'Six': 'หก',
           'Seven': 'เจ็ด', 'Eight': 'แปด', 'Nine': 'เก้า', 'Ten': 'สิบ',
           'Page': 'เพจ', 'Knight': 'อัศวิน', 'Queen': 'ราชินี', 'King': 'ราชา'}
RANK_MEANING = {
    'Ace': 'จุดเริ่มต้นใหม่ พลังงานดิบที่เพิ่งเกิด', 'Two': 'ทางเลือก ความสมดุล การจับคู่',
    'Three': 'การขยายตัว การร่วมมือ ผลลัพธ์แรกที่เห็น', 'Four': 'ความมั่นคง โครงสร้าง การหยุดพัก',
    'Five': 'ความขัดแย้ง การเปลี่ยนแปลง ความไม่แน่นอน', 'Six': 'ความสมดุลกลับคืน ความกลมกลืน',
    'Seven': 'การประเมิน ความอดทน ทบทวนก่อนก้าวต่อ', 'Eight': 'การเคลื่อนไหว ความก้าวหน้า',
    'Nine': 'ใกล้จุดสูงสุด ความอ่อนล้าหรือความสำเร็จที่ใกล้เข้ามา', 'Ten': 'จุดสมบูรณ์ จบวงจร',
    'Page': 'การเรียนรู้ ข่าวสารใหม่ ความอยากรู้อยากเห็น', 'Knight': 'การลงมือทำ การเดินทาง พลังงานเคลื่อนที่',
    'Queen': 'ความเป็นผู้ใหญ่ทางอารมณ์ การดูแล ความเข้าใจลึกซึ้ง', 'King': 'ความเป็นผู้นำ การควบคุมพลังงานได้เต็มที่',
}

MAJOR = [
    ('The Fool', 'คนโง่/ผู้เริ่มต้น', 'จุดเริ่มต้นใหม่ที่ไร้เดียงสาแต่เต็มไปด้วยศักยภาพ — ก้าวไปโดยเชื่อใจจักรวาล'),
    ('The Magician', 'นักมายากล', 'มีทุกอย่างพร้อมอยู่แล้วในมือ ถึงเวลาลงมือทำให้เป็นจริง'),
    ('The High Priestess', 'นักบวชหญิง', 'ปัญญาภายใน สัญชาตญาณ ความลับที่ยังไม่เปิดเผย'),
    ('The Empress', 'จักรพรรดินี', 'ความอุดมสมบูรณ์ ความรักที่เติบโต การสร้างสรรค์'),
    ('The Emperor', 'จักรพรรดิ', 'โครงสร้าง อำนาจ ความมั่นคงที่สร้างด้วยเหตุผล'),
    ('The Hierophant', 'สังฆราช', 'ประเพณี ระบบความเชื่อ การเรียนรู้จากผู้มีประสบการณ์'),
    ('The Lovers', 'คู่รัก', 'การเลือกที่มาจากใจจริง ความสัมพันธ์ ความสอดคล้องของค่านิยม'),
    ('The Chariot', 'รถศึก', 'ความมุ่งมั่น ชัยชนะจากการควบคุมพลังที่ขัดแย้งกันได้'),
    ('Strength', 'พลัง', 'ความแข็งแรงที่มาจากความอ่อนโยน ไม่ใช่การบังคับ'),
    ('The Hermit', 'ฤๅษี', 'การถอยเข้าไปหาตัวเอง ค้นหาคำตอบจากภายใน'),
    ('Wheel of Fortune', 'กงล้อแห่งโชคชะตา', 'วัฏจักรของชีวิตที่หมุนอยู่เสมอ การเปลี่ยนแปลงที่ควบคุมไม่ได้ทั้งหมด'),
    ('Justice', 'ความยุติธรรม', 'ผลจากการกระทำ ความสมดุลระหว่างเหตุและผล'),
    ('The Hanged Man', 'ชายแขวนคอ', 'การหยุดมองในมุมใหม่ ยอมปล่อยเพื่อให้เห็นสิ่งที่ซ่อนอยู่'),
    ('Death', 'ความตาย', 'จุดจบของบทหนึ่งเพื่อให้บทใหม่เริ่มได้ — การเปลี่ยนแปลงที่จำเป็น'),
    ('Temperance', 'ความพอประมาณ', 'การผสมผสานที่ลงตัว ความอดทน สายกลาง'),
    ('The Devil', 'ปีศาจ', 'พันธนาการที่ผูกตัวเองไว้ แรงดึงดูดที่ทั้งเสพติดและจำกัด'),
    ('The Tower', 'หอคอย', 'โครงสร้างเดิมพังทลายกะทันหัน เปิดทางให้ความจริงและการสร้างใหม่'),
    ('The Star', 'ดวงดาว', 'ความหวัง การเยียวยาหลังพายุผ่านไป'),
    ('The Moon', 'ดวงจันทร์', 'ความไม่ชัดเจน ความกลัวที่ซ่อนอยู่ในจิตใต้สำนึก'),
    ('The Sun', 'ดวงอาทิตย์', 'ความสุขที่จริงใจ ความสำเร็จ ความชัดเจน'),
    ('Judgement', 'การพิพากษา', 'การตื่นรู้ การให้อภัยตัวเอง เรียกสิ่งที่ผ่านมากลับมาทบทวน'),
    ('The World', 'โลก', 'ความสมบูรณ์ วงจรหนึ่งจบลงอย่างสวยงาม'),
]


def _build_deck():
    deck = [{'name': name, 'name_th': th, 'meaning': m, 'arcana': 'major'} for name, th, m in MAJOR]
    for suit, s in SUITS.items():
        for rank in RANKS:
            deck.append({
                'name': f'{rank} of {suit}',
                'name_th': f'{RANK_TH[rank]} — {s["th"]}',
                'meaning': f'{RANK_MEANING[rank]} ในบริบทของ{s["theme"]}',
                'arcana': 'minor',
            })
    return deck


DECK = _build_deck()


def draw_card():
    rng = secrets.SystemRandom()
    card = rng.choice(DECK)
    reversed_ = rng.choice([True, False])
    meaning = card['meaning']
    if reversed_:
        if card['arcana'] == 'major':
            meaning = f'พลังงานเดียวกันแต่หันเข้าด้านใน หรือกำลังถูกต่อต้าน/บล็อกอยู่: {meaning}'
        else:
            meaning = f'พลังงานถูกกั้นไว้ชั่วคราว ยังไม่ไหลออกมาเต็มที่: {meaning}'
    return {
        'name': card['name'], 'name_th': card['name_th'],
        'orientation': 'reversed' if reversed_ else 'upright',
        'meaning': meaning,
    }


if __name__ == '__main__':
    import json as _json
    print(_json.dumps(draw_card(), ensure_ascii=False, indent=2))
