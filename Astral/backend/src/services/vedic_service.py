"""Vedic astrology engine — rashi (Moon sign), nakshatra, navamsa sign.

Sidereal positions via Lahiri ayanamsa. Uses the existing chart_service
(compute_chart) for tropical longitudes, converts to sidereal.
Thai interpretive strings written in natural Thai-astrologer voice.
"""
from __future__ import annotations

from src.services.chart_service import compute_chart

# Lahiri ayanamsa approximations per year (J2000=23.85°, drift ~50.29"/yr)
_AYANAMSA_J2000 = 23.85
_ARCSEC_PER_YEAR = 50.29

RASHI_EN = [
    "Mesha", "Vrishabha", "Mithuna", "Karka", "Simha", "Kanya",
    "Tula", "Vrischika", "Dhanu", "Makara", "Kumbha", "Meena",
]
RASHI_TH = [
    "เมษ", "พฤษภ", "มิถุน", "กรกฎ", "สิงห์", "กันย์",
    "ตุลย์", "วิศรภ", "ธนู", "มกร", "กุมภ์", "มีน",
]
NAKSHATRA_TH = [
    "อัศวินี", "ภรณี", "กฤตติกา", "โรหินี", "มฤคศิระ", "อาทรา",
    "ปุนรรวสุ", "ปุษยะ", "อาศลิษา", "มฆะ", "ปุรผลคุณี", "อุตรผลคุณี",
    "หัสตะ", "จิตรา", "สวาตี", "วิศาขา", "อนุราธ", "เชฏฐา",
    "มูละ", "ปุรผษฐ์", "อุตรผษฐ์", "ศรวณะ", "ศรวิษฐา", "ศตภิษัช",
    "ปุรภัทรบท", "อุตรับทรบท", "เรวดี",
]


def _ayanamsa(dt_utc) -> float:
    year = dt_utc.year + (dt_utc.timetuple().tm_yday / 365.25)
    return _AYANAMSA_J2000 + (year - 2000.0) * _ARCSEC_PER_YEAR / 3600.0


def _sidereal(lon_tropical: float, dt_utc) -> float:
    return (lon_tropical - _ayanamsa(dt_utc)) % 360.0


def _rashi_index(sidereal_lon: float) -> int:
    return int(sidereal_lon // 30) % 12


def _nakshatra_index(sidereal_lon: float) -> int:
    return int(sidereal_lon // (360 / 27)) % 27


def _pada(sidereal_lon: float) -> int:
    return int((sidereal_lon % (360 / 27)) // (360 / 108)) + 1


def compute_vedic(
    birth_datetime_local: str,
    lat: float,
    lon: float,
    tz_offset_hours: float = 7.0,
    person_name: str = "",
) -> dict:
    """birth_datetime_local: 'YYYY-MM-DDTHH:MM' (local time at birth place)."""
    from datetime import datetime, timedelta

    naive = datetime.fromisoformat(birth_datetime_local)
    utc_dt = naive - timedelta(hours=tz_offset_hours)

    chart = compute_chart("vedic", utc_dt.date(), utc_dt.time(),
                          tz_offset_hours=0, lat=lat, lon=lon)
    planets = {p["body"]: p["absolute_deg"] for p in chart["bodies"]}

    moon_sid = _sidereal(planets["Moon"], utc_dt)
    sun_sid = _sidereal(planets["Sun"], utc_dt)
    asc_sid = _sidereal(chart["ascendant"]["absolute_deg"], utc_dt)

    moon_rashi = _rashi_index(moon_sid)
    sun_rashi = _rashi_index(sun_sid)
    asc_rashi = _rashi_index(asc_sid)
    nak = _nakshatra_index(moon_sid)

    result = {
        "system": "vedic",
        "ayanamsa": round(_ayanamsa(utc_dt), 4),
        "lagna": {
            "index": asc_rashi,
            "sign_en": RASHI_EN[asc_rashi],
            "sign_th": RASHI_TH[asc_rashi],
        },
        "chandra_rashi": {
            "index": moon_rashi,
            "sign_en": RASHI_EN[moon_rashi],
            "sign_th": RASHI_TH[moon_rashi],
        },
        "surya_rashi": {
            "index": sun_rashi,
            "sign_en": RASHI_EN[sun_rashi],
            "sign_th": RASHI_TH[sun_rashi],
        },
        "nakshatra": {
            "index": nak,
            "name_th": NAKSHATRA_TH[nak],
            "name_en": _NAKSHATRA_EN[nak],
            "pada": _pada(moon_sid),
        },
    }

    result["interpretation"] = {"th": _interp_th(result), "en": _interp_en(result)}
    if person_name:
        result["person_name"] = person_name
    return result


_NAKSHATRA_EN = [
    "Ashwini", "Bharani", "Krittika", "Rohini", "Mrigashira", "Ardra",
    "Punarvasu", "Pushya", "Ashlesha", "Magha", "Purva Phalguni", "Uttara Phalguni",
    "Hasta", "Chitra", "Swati", "Vishakha", "Anuradha", "Jyeshtha",
    "Mula", "Purvashadha", "Uttarashadha", "Shravana", "Dhanishta", "Shatabhisha",
    "Purva Bhadrapada", "Uttara Bhadrapada", "Revati",
]

_TRAIT_TH = {
    0: "ใจกล้า เอาอยู่ เริ่มอะไรก่อนใครเสมอ",
    1: "มุ่งมั่น ถือคอมากไปหน่อย แต่ซื่อสัตย์แน่นอน",
    2: "ฉลาดแหลมคม พูดตรง บางครั้งคำพูดไปถึงหัวใจคน",
    3: "มีเสน่ห์ สวยหรือหล่อ เป็นที่รักของคนรอบข้าง",
    4: "อยากรู้อยากเห็น ช่างสังเกต ชอบค้นหาความจริง",
    5: "คิดเร็ว พูดเร็ว ใจลอยบ้าง แต่มีพรสวรรค์ด้านภาษา",
    6: "ใจดี ให้ที่พักพิงคนอื่นได้เสมอ",
    7: "น่าเชื่อถือ ดูแลคนเก่ง ใครได้อยู่ใกล้สบายใจ",
    8: "ลึกลับ จับใจคนเก่ง อย่าลืมว่าความลับต้องอยู่กับเรา",
    9: "มีบารมี เกิดมาเป็นพ่อครัวแม่ครัวคน ผู้นำโดยกำเนิด",
    10: "รักสวยรักงาม มีศิลป์ในตัว ชอบความสะดวกสบาย",
    11: "อบอุ่น เอื้อเฟื้อ เป็นที่พึ่งของคนทุกวัย",
    12: "ฝีมือดี ทำอะไรลงมือเองได้หมด งานมือเป็นเลิศ",
    13: "สร้างสรรค์ มีเสน่ห์ งานศิลปะกับการออกแบบเข้ากันดี",
    14: "อิสระ ชอบเดินทาง การค้าขายรุ่งเรือง ใจยังไงก็ลอยหาไกล",
    15: "มุ่งเป้าหมาย ชนะการแข่งขัน รางวัลมักมาเยือน",
    16: "จริงใจ มีมิตรแท้ ผ่านพายุแล้วรุ่งเรืองเสมอ",
    17: "เก่าก่อน มีวาสนา ผู้อาวุโสให้ความเมตตา",
    18: "หัวแหลม วิจัยลึก รากฐานเก่าให้ผลใหม่เสมอ",
    19: "เผื่อใจกว้าง ใจสูง ทำบุญได้ผลไว",
    20: "มั่นคง ฟังดี ทำอะไรมีหลักการ เจ้าของธุรกิจที่ดี",
    21: "ฟังเก่ง เรียนรู้ไว ความรู้ไหลเข้าหาเสมอ",
    22: "มั่งคั่ง มีเพื่อนมาก จัดระเบียบชีวิตเป็นเลิศ",
    23: "รักษาคน รักษาโรค ใจบุญ มีคนขอบคุณเสมอ",
    24: "ศรัทธาแรงกล้า ทางธรรมเปิดกว้าง",
    25: "ใจดีลึก ปกป้องคนอ่อนแอ ความสงบคือความร่ำรวย",
    26: "โชคดี ให้และได้ ทางเดินชีวิตราบรื่นกว่าเพื่อน",
}


def _interp_th(r: dict) -> str:
    ch = r["chandra_rashi"]
    nk = r["nakshatra"]
    lg = r["lagna"]
    trait = _TRAIT_TH.get(nk["index"], "")
    return (
        f"ลัคนาขึ้น{lg['sign_th']} — ภาพจำแรกที่คนเห็นคุณคือความ{('มั่นใจ' if asc_trait(lg['index']) else 'สุขุม')} "
        f"ดวงจันทร์ (จิตใจ) อยู่{ch['sign_th']} ดวงอาทิตย์ (ตัวตน) อยู่{r['surya_rashi']['sign_th']}. "
        f"ดาวเกิดอยู่ในนักษัตร{nk['name_th']} บทที่ {nk['pada']} — {trait}. "
        f"โดยรวมถือว่าจิตใจเป็นศูนย์กลางดวงชะตา ใช้จิตใจที่มั่นคงนำการตัดสินใจ แล้วทุกอย่างจะเดินตาม"
    )


def asc_trait(i: int) -> bool:
    return i in (0, 2, 4, 7, 8, 9)


def _interp_en(r: dict) -> str:
    ch = r["chandra_rashi"]
    nk = r["nakshatra"]
    return (
        f"Ascendant in {r['lagna']['sign_en']}; Moon (mind) in {ch['sign_en']}, "
        f"Sun (self) in {r['surya_rashi']['sign_en']}. Birth star: "
        f"{nk['name_en']} pada {nk['pada']} — {_TRAIT_TH.get(nk['index'], '')} "
        f"(the mind leads this chart; steady inner life steers every decision)"
    )
