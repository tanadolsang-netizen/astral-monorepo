"""Draconic chart + Harmonic charts (H4/H5/H7/H9).

Draconic = natal longitudes shifted by −True North Node.
Harmonic Hn = (longitude × n) mod 360.
"""
from __future__ import annotations

from src.services.grand.human_design import true_north_node


def _nn_lon(jd_ut: float) -> float:
    return float(true_north_node(jd_ut))


def draconic_chart(bodies: dict[str, float], jd_ut: float) -> dict:
    nn = _nn_lon(jd_ut)
    out = {}
    for name, lon in bodies.items():
        out[name] = (float(lon) - nn) % 360.0
    out["North Node"] = 0.0  # node itself anchors the draconic zodiac
    out["South Node"] = 180.0
    return {"system": "draconic", "node_longitude": round(nn, 4), "bodies": out}


def harmonic_chart(bodies: dict[str, float], n: int) -> dict:
    if n < 1:
        raise ValueError("harmonic number must be >= 1")
    out = {name: (float(lon) * n) % 360.0 for name, lon in bodies.items()}
    return {"system": f"harmonic-H{n}", "bodies": out}


def _aspect(a: float, b: float, orb_limit: float) -> str | None:
    d = abs(a - b) % 360
    if d > 180:
        d = 360 - d
    targets = [(0, "conjunction"), (60, "sextile"), (90, "square"),
               (120, "trine"), (180, "opposition")]
    for t, name in targets:
        if abs(d - t) <= orb_limit:
            return f"{name} ({round(d, 1)}°)"
    return None


def draconic_report(natal_bodies: dict[str, float], jd_ut: float,
                    orb: float = 5.0) -> dict:
    dr = draconic_chart(natal_bodies, jd_ut)
    # soul-contact aspects: draconic planets conjunct natal planets
    contacts = []
    for name, dlon in dr["bodies"].items():
        if name in ("North Node", "South Node"):
            continue
        if name in natal_bodies:
            asp = _aspect(dlon, float(natal_bodies[name]), orb)
            if asp and asp.startswith("conjunction"):
                contacts.append(f"{name} draconic conjunct natal {name}")
    SIGNS_TH = ["เมษ", "พฤษภ", "เมถุน", "กรกฎ", "สิงห์", "กันย์",
                "ตุลย์", "พิจิก", "ธนู", "มกร", "กุมภ์", "มีน"]
    sun_th = SIGNS_TH[int(dr["bodies"]["Sun"] // 30) % 12]
    return {
        **dr,
        "soul_contacts": contacts,
        "interpretation": {
            "th": (
                f"Draconic chart เลื่อนจักรวาลไปยึดที่โหนดกรรม — "
                f"ดวงอาทิตย์ดวงจริง (draconic) ขึ้นราศี{sun_th} "
                f"คือ 'ตัวตนก่อนกำเนิด' ที่คุณถือมา และมี soul contact "
                f"{len(contacts)} จุดที่ดวงปัจจุบันสอดคล้องกับภาระเก่า"
            ),
            "en": (
                f"Draconic zodiac re-anchors to the nodes — draconic Sun "
                f"reveals the pre-incarnation self; {len(contacts)} soul-contact(s) "
                f"with the natal chart."
            ),
        },
    }


def harmonics_report(natal_bodies: dict[str, float]) -> list[dict]:
    themes = {
        4: ("H4 stability & foundation", "โครงสร้างและความมั่นคง"),
        5: ("H5 love & creativity", "ความรักและการสร้างสรรค์"),
        7: ("H7 mysticism & inspiration", "ลี้ลับและแรงบันดาลใจ"),
        9: ("H9 navamsa-correspondence", "สอดคล้องกับ navamsa (พลังในการสมรส)"),
    }
    reports = []
    for n, (en, th) in themes.items():
        h = harmonic_chart(natal_bodies, n)
        reports.append({"harmonic": n, "theme_en": en, "theme_th": th,
                        "bodies": h["bodies"]})
    return reports
