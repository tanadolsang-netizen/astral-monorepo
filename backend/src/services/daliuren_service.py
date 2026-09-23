"""Da Liu Ren 大六壬 — three-transmission divination (simplified classical)."""

from __future__ import annotations

from datetime import datetime

BRANCHES = ["子", "丑", "寅", "卯", "辰", "巳", "午", "未", "申", "酉", "戌", "亥"]
BRANCHES_TH = ["จื่อ(หนู)", "โฉ่ว(วัว)", "อิน(เสือ)", "เหมา(กระต่าย)",
               "เฉิ่น(มังกร)", "สื่อ(งู)", "อู่(ม้า)", "เหว่ย(แพะ)",
               "เชิน(ลิง)", "หยิ่ว(ไก่)", "สวี(หมา)", "ไฮ่(หมู)"]
TWELVE_GENERALS = ["貴人", "騰蛇", "朱雀", "六合", "勾陳", "青龍",
                   "天空", "白虎", "太常", "玄武", "太陰", "天后"]
GENERALS_TH = ["กุ้ยเหริน (เทพผู้ใหญ่)", "เถิงเสวย", "จูชวี", "ลิ่วเหอ",
               "โกวเฉิน", "ชิงหลง", "เทียนคง", "ปั๋วหู", "ไท่ซ่าง",
               "เสวนอู่", "ไท่อิน", "เทียนโห่ว"]


def _day_branch_idx(dt: datetime) -> int:
    jdn = (dt.toordinal() + 1721425)
    return jdn % 12


def _month_branch_idx(dt: datetime) -> int:
    # month branch: 寅=Jan-ish per solar calendar convention
    return (dt.month + 1) % 12


def compute_daliuren(question_dt_local: datetime, intent: str = "decision") -> dict:
    hour_branch = ((question_dt_local.hour + 1) // 2) % 12
    day_branch = _day_branch_idx(question_dt_local)
    month_branch = _month_branch_idx(question_dt_local)

    # four courses: day stem-branch pairs simplified to branch relations
    c1, c2 = day_branch, (day_branch + hour_branch) % 12
    c3, c4 = month_branch, (month_branch + hour_branch) % 12
    courses = [c1, c2, c3, c4]

    # three transmissions:贼克 method simplified — pick branches with conflicts
    seen = set()
    transmissions = []
    for b in courses:
        if b not in seen:
            transmissions.append(b)
            seen.add(b)
    while len(transmissions) < 3:
        nxt = (transmissions[-1] + 4) % 12  # classical step pattern
        transmissions.append(nxt)
    transmissions = transmissions[:3]

    noble_offset = hour_branch % 12
    generals = _rotate_list(TWELVE_GENERALS, noble_offset)
    generals_th = _rotate_list(GENERALS_TH, noble_offset)

    t_th = [BRANCHES_TH[b] for b in transmissions]
    th = (
        f"ต้าหลิวเหริน เวลา{question_dt_local.strftime('%H:%M')} — "
        f"สามสื่อสาร: {' → '.join(t_th)}. "
        f"เทพประจำสื่อสารแรก {generals_th[transmissions[0]]} "
        f"{'บอกว่าทางเดินชัดเจน ก้าวได้' if intent == 'decision' else 'รอสัญญาณเพิ่ม'}"
    )
    en = (
        f"DLR at {question_dt_local.strftime('%H:%M')}: transmissions "
        f"{[BRANCHES[b] for b in transmissions]}, first general "
        f"{generals[transmissions[0]]}."
    )
    return {
        "system": "da-liu-ren", "intent": intent,
        "courses": [BRANCHES_TH[c] for c in courses],
        "three_transmissions": t_th,
        "general_first": generals_th[transmissions[0]],
        "interpretation": {"th": th, "en": en},
    }


def _rotate_list(seq: list, offset: int) -> list:
    n = len(seq)
    return [seq[(i - offset) % n] for i in range(n)]
