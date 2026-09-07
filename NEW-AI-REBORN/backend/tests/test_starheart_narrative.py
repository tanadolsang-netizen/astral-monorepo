# -*- coding: utf-8 -*-
"""Test: STARHEART life-grounding สำหรับดวงคุณ — ต้องรันได้จริง + ไม่มีคำเจนนิก"""
import json
import sys

from src.services import starheart_map
from src.services.starheart_narrative import ground_narrative

CHARTS = r"C:/AI/workspace-scratch/charts_nai_mai.json"


def main() -> int:
    try:
        with open(CHARTS, "r", encoding="utf-8") as fh:
            charts = json.load(fh)
    except FileNotFoundError:
        # Fallback: compute chart inline
        from src.services.chart_service import compute_chart
        nai = compute_chart(name="นาย", date="1997-05-19", time="05:45",
                            tz_offset_hours=7.0, lat=13.3611, lon=100.9847,
                            system="tropical")
    else:
        nai = charts["nai"]

    # 1) MAP ต้องรันได้
    mapped = starheart_map.MAP(nai, max_cards=14)
    print(f"[OK] MAP -> {len(mapped)} ใบ (deterministic check)")
    assert starheart_map.MAP(nai, max_cards=14) == mapped, "MAP ไม่ deterministic"

    # 2) ground_narrative ภาษาไทย
    th = ground_narrative(nai, lang="th", user_name="นาย")
    assert isinstance(th, str) and len(th) > 200

    # 3) ตรวจคำเจนนิก (ห้ามมี)
    forbidden = ["แปลว่า", "หมายถึง", "สัญลักษณ์ว่า", "means that you",
                 "means you are", "indicates that you are", "in Taurus means"]
    hit = [f for f in forbidden if f in th]
    assert not hit, f"พบคำเจนนิก: {hit}"

    # 4) ต้องมีเรื่องจริงของนาย (เกณฑ์ขั้นต่ำ)
    must = ["พฤษภ", "ลัคนา", "เสาร์", "ดวงจันทร์"]
    missing = [m for m in must if m not in th]
    assert not missing, f"ขาดเรื่องจริง: {missing}"

    print("\n===== NARRATIVE ไทย (ดวงคุณ) =====\n")
    print(th[:800])
    print(f"\n... (ยาว {len(th)} ตัวอักษร)")
    print("\n===== ตรวจสอบ =====")
    print(f"  MAP cards           : {len(mapped)} ใบ")
    print(f"  ความยาว narrative   : {len(th)} ตัวอักษร")
    print(f"  คำเจนนิกต้องห้าม     : ไม่พบ ✅")
    print(f"  เรื่องจริงครบ       : ✅")

    # 5) EN mirror
    en = ground_narrative(nai, lang="en", user_name="นาย")
    print(f"\n[OK] EN mirror ความยาว {len(en)} ตัวอักษร")

    # 6) reel_reading ยังทำงานได้
    from src.services.reel_reading import reel_reading
    rr = reel_reading("นาย", spread="three_card", chart=nai)
    assert "narrative" in rr
    print("[OK] reel_reading ทำงานได้")

    print("\nDONE: STARHEART life-grounding ผ่านทุกเกณฑ์")
    return 0


if __name__ == "__main__":
    sys.exit(main())
