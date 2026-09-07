# -*- coding: utf-8 -*-
"""Test: STARHEART life-grounding สำหรับดวงนายท่าน — ต้องรันได้จริง + ไม่มีคำเจนนิก"""
import json
import sys

from src.services import starheart_map
from src.services.starheart_narrative import (
    ground_narrative, build_life_context, DEFAULT_LIFE_CONTEXT,
)

CHARTS = r"C:/AI/workspace-scratch/charts_nai_mai.json"
TRANSCRIPTS = r"C:/AI/workspace-scratch/reels_text/_ALL_TRANSCRIPTS.json"


def main() -> int:
    with open(CHARTS, "r", encoding="utf-8") as fh:
        charts = json.load(fh)
    nai = charts["nai"]

    # 1) MAP ต้องรันได้
    mapped = starheart_map.MAP(nai, max_cards=14)
    print(f"[OK] MAP -> {len(mapped)} ใบ (deterministic check)")
    assert starheart_map.MAP(nai, max_cards=14) == mapped, "MAP ไม่ deterministic"

    # 2) life_context จาก reels + facts
    lc = build_life_context(TRANSCRIPTS)
    assert lc["reels_count"] == 14, f"reels_count ต้อง 14 ได้ {lc['reels_count']}"

    # 3) ground_narrative ภาษาไทย
    th = ground_narrative(nai, lc, lang="th")
    assert isinstance(th, str) and len(th) > 200

    # 4) ตรวจคำเจนนิก (ห้ามมี)
    forbidden = ["แปลว่า", "หมายถึง", "สัญลักษณ์ว่า", "means that you",
                 "means you are", "indicates that you are", "in Taurus means"]
    hit = [f for f in forbidden if f in th]
    assert not hit, f"พบคำเจนนิก: {hit}"

    # 5) ต้องมีเรื่องจริงของนาย (เกณฑ์ขั้นต่ำ)
    must = ["AI agency", "847", "soul contract", "no-contact", "Mai",
            "กรงกรรม", "ดาวเสาร์"]
    missing = [m for m in must if m not in th]
    assert not missing, f"ขาดเรื่องจริง: {missing}"

    print("\n===== NARRATIVE ไทย (ดวงนายท่าน) =====\n")
    print(th)
    print("\n===== ตรวจสอบ =====")
    print(f"  MAP cards           : {len(mapped)} ใบ")
    print(f"  reels_count         : {lc['reels_count']}")
    print(f"  ความยาว narrative   : {len(th)} ตัวอักษร")
    print(f"  คำเจนนิกต้องห้าม     : ไม่พบ ✅")
    print(f"  เรื่องจริงครบ       : ✅")

    # 6) EN mirror
    en = ground_narrative(nai, lc, lang="en")
    print(f"\n[OK] EN mirror ความยาว {len(en)} ตัวอักษร")

    # 7) backward-compat: ไม่มี life_context -> คืนข้อความเดิม (chart_narrative)
    from src.services.chart_narrative_full import chart_narrative
    old = chart_narrative("นาย", nai, "th")
    assert "ลัคนาอยู่ราศี" in old, "backward-compat chart_narrative ผิดรูป"
    print("[OK] backward-compat: chart_narrative ไม่มี life_context คงข้อความเดิม")

    # 8) reel_reading เรียก ground_narrative
    from src.services.reel_reading import reel_reading
    rr = reel_reading("นาย", spread="three_card", chart=nai, life_context=lc)
    assert rr.get("grounded") is True
    assert "AI agency" in rr["narrative"]["th"]
    print("[OK] reel_reading ใช้ ground_narrative (grounded=True)")

    print("\nDONE: STARHEART life-grounding ผ่านทุกเกณฑ์")
    return 0


if __name__ == "__main__":
    sys.exit(main())
