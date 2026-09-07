"""Ground-up PDF renderer — replaces the ad-hoc HTML assembly in weasy_brochure.py.

Design goals
- One class (`SectionRenderer`) owns all section normalization. Nothing
  reaches HTML assembly without going through it first.
- `sanitize_text()` is a strict per-language whitelist, not just a
  blocklist: TH output keeps Thai script + ASCII, EN output keeps ASCII
  only. Anything else (CJK, Cyrillic, Greek, stray symbols) is dropped.
- Lang-aware typography: TH gets a larger H1/H2 for tone-mark legibility;
  both languages render body text at line-height 1.7.
- `render_brochure_v2()` is a drop-in replacement for
  `weasy_brochure.render_brochure()` — same signature, same return value.
"""

from __future__ import annotations

import base64
import html
import os
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Sequence

try:
    from weasyprint import HTML, CSS
except (ImportError, OSError):
    HTML = None  # weasyprint unavailable (no GTK on Windows) — PDF endpoints disabled

from src.services.narrative_sanitizer import sanitize_narrative
from src.services.narrative_gate import apply_narrative_gate

_REPO = Path(__file__).resolve().parents[2]
FONT_DIR = _REPO / "assets" / "fonts"
ART_DIR = _REPO / "assets" / "art"
_GOLD = "#9a7b34"
_IVORY = "#f6f0e2"
_INK = "#3b3324"
_SOFT = "rgba(154,123,52,.35)"

_TYPO = {
    "th": {
        "font": '"Noto Sans Thai", "Sarabun", "Segoe UI", Tahoma, sans-serif',
        "h1": "26pt",
        "h2": "13pt",
        "body": "10.5pt",
        "line_height": "1.7",
    },
    "en": {
        "font": '"Segoe UI", "Noto Sans Thai", "Sarabun", Tahoma, sans-serif',
        "h1": "24pt",
        "h2": "12.5pt",
        "body": "10.5pt",
        "line_height": "1.7",
    },
}

_DEFAULT_TITLE = {"th": "รายงานดวงชะตา", "en": "Astral Report"}

# Whitelist ranges: ASCII (tab/CR/LF + printable 0x20-0x7E) covers digits,
# latin, and punctuation needed by both languages; the Thai block adds
# consonants/vowels/tone marks for TH output.
_ASCII_PRINTABLE = "\x09\x0A\x0D\x20-\x7E"
_THAI_BLOCK = "\u0E00-\u0E7F"
_TH_KEEP = re.compile(f"[^{_ASCII_PRINTABLE}{_THAI_BLOCK}]")
_EN_KEEP = re.compile(f"[^{_ASCII_PRINTABLE}]")


def _lang_key(lang: str) -> str:
    return "th" if str(lang).lower().startswith("th") else "en"


def sanitize_text(text: object, lang: str = "th") -> str:
    """Whitelist-filter text for the target language.

    Runs the shared `sanitize_narrative` pass first (known garbled tokens,
    stray scripts, fullwidth punctuation), then drops anything outside the
    language's allowed character set so no CJK/Cyrillic/Greek leftovers or
    off-language text can survive into the PDF.
    """
    if text is None:
        return ""
    s = sanitize_narrative(str(text), lang=lang)
    keep = _TH_KEEP if _lang_key(lang) == "th" else _EN_KEEP
    s = keep.sub("", s)
    s = re.sub(r"[ \t]+", " ", s)
    s = re.sub(r"\s+([,.;:!?])", r"\1", s)
    return s.strip()


@dataclass
class RenderedSection:
    title: str
    lines: list[str]
    is_html: bool


class SectionRenderer:
    """Normalizes raw section dicts into sanitized, render-ready sections.

    Every section any PDF builder touches must flow through `render()`
    (or `render_one()`) so sanitization happens in exactly one place,
    regardless of which caller produced the raw dict.
    """

    def __init__(self, lang: str = "th"):
        self.lang = lang

    def render_one(self, sec: dict) -> RenderedSection:
        title = sanitize_text(sec.get("title", ""), self.lang)
        raw_lines = sec.get("lines", []) or []
        lines = [sanitize_text(line, self.lang) for line in raw_lines]
        lines = [line for line in lines if line]
        is_html = any("<" in line and ">" in line for line in lines)
        return RenderedSection(title=title, lines=lines, is_html=is_html)

    def render(self, sections: Sequence[dict]) -> list[RenderedSection]:
        return [self.render_one(sec) for sec in sections]


def _build_css(lang: str = "th") -> str:
    t = _TYPO[_lang_key(lang)]
    return f"""
@page {{
  size: A4;
  margin: 14mm 14mm 18mm 14mm;
  @bottom-center {{
    content: counter(page);
    color: {_GOLD};
    font-family: {t['font']};
    font-size: 9pt;
  }}
}}
html, body {{
  background: {_IVORY};
  color: {_INK};
  font-family: {t['font']};
  font-size: {t['body']};
  line-height: {t['line_height']};
}}
.cover {{
  page-break-after: always;
  background: radial-gradient(circle at top left, rgba(154,123,52,.12), transparent 40%), {_IVORY};
  border: 1px solid {_GOLD};
  border-radius: 14px;
  padding: 28mm 22mm;
  text-align: center;
  position: relative;
  overflow: hidden;
}}
.cover .brand {{
  color: {_GOLD};
  letter-spacing: .18em;
  font-size: 10pt;
  text-transform: uppercase;
}}
.cover h1 {{
  color: {_GOLD};
  font-size: {t['h1']};
  margin: 10px 0 6px;
}}
.cover .sub {{
  color: {_INK};
  opacity: .85;
  font-size: 12pt;
}}
.cover-art {{
  width: 96mm;
  max-height: 88mm;
  object-fit: cover;
  border-radius: 10px;
  margin: 10px auto 12px;
  display: block;
  border: 1px solid {_SOFT};
  box-shadow: 0 4px 18px rgba(90,60,20,.18);
}}
.cover-credit {{
  color: #8a774e;
  font-size: 8.5pt;
  font-style: italic;
  margin-top: 4px;
}}
.section {{
  background: #fff;
  border: 1px solid {_SOFT};
  border-radius: 10px;
  padding: 12px 14px;
  margin: 10px 0 14px;
  page-break-inside: avoid;
}}
.section .title {{
  color: {_GOLD};
  font-size: {t['h2']};
  font-weight: bold;
  border-bottom: 1px solid {_SOFT};
  padding-bottom: 6px;
  margin-bottom: 8px;
}}
.section .body {{
  font-size: {t['body']};
  line-height: {t['line_height']};
  color: {_INK};
}}
.section .body b {{
  color: #33291a;
}}
.line {{
  margin: 5px 0;
}}
.footer {{
  margin-top: 14px;
  border-top: 1px solid {_SOFT};
  padding-top: 8px;
  color: #6b6355;
  font-size: 9pt;
  text-align: center;
}}
.biwheel-wrap, .card-art {{ display:none; }}
"""


def _font_faces() -> str:
    faces = []
    try:
        for name in sorted(FONT_DIR.glob("*.ttf")):
            family = name.stem.replace("-", " ")
            faces.append(
                f"""
@font-face {{
  font-family: '{family}';
  src: url('file:///{name.as_posix()}') format('truetype');
}}
"""
            )
    except Exception:
        pass
    return "\n".join(faces)


def _data_uri(path: Path) -> str:
    try:
        return "data:image/jpeg;base64," + base64.b64encode(path.read_bytes()).decode()
    except Exception:
        return ""


def _pick_cover_art(theme_hint: str = "") -> str:
    mapping = {
        "venus": "venus_mars", "taurus": "venus_mars", "libra": "venus_mars",
        "diana": "diana", "moon": "diana", "cancer": "diana",
        "cupid": "cupid_psyche", "psyche": "cupid_psyche", "pisces": "cupid_psyche",
        "vedic": "diana", "bazi": "cupid_psyche", "human design": "venus_mars",
        "ziwei": "diana", "grand summary": "venus_mars", "natal": "venus_mars",
    }
    key = None
    for k, v in mapping.items():
        if k in theme_hint.lower():
            key = v
            break
    if not key:
        key = "venus_mars"
    path = ART_DIR / f"{key}.jpg"
    return _data_uri(path) if path.exists() else ""


def _section_art_map(theme_hint: str = "", section_count: int = 1) -> dict[int, str]:
    art_map = {}
    uri = _pick_cover_art(theme_hint)
    if uri and section_count > 0:
        art_map[1] = uri
    return art_map


def _resolve_title(title: str, person_name: str, theme_hint: str, lang: str) -> str:
    if title:
        return sanitize_text(title, lang)
    lang_key = _lang_key(lang)
    brand = _DEFAULT_TITLE[lang_key]
    if not person_name:
        return brand
    if theme_hint:
        if lang_key == "en":
            return f"{brand} {theme_hint.title()} — {person_name}"
        return f"{brand} ({theme_hint.title()}) — {person_name}"
    return f"{brand} — {person_name}"


def render_brochure_v2(
    sections: Sequence[dict],
    out_path: str | os.PathLike[str],
    *,
    title: str = "",
    subtitle: str = "",
    person_name: str = "",
    lang: str = "th",
    theme_hint: str = "",
    footer: str = "",
    biwheel: str = "",
    section_art: dict[int, str] | None = None,
    raw_section: str = "",
    raw_title: str = "",
) -> str:
    """Render a premium brochure PDF from prepared sections.

    Drop-in replacement for `weasy_brochure.render_brochure()` — same
    keyword signature and return value — backed by `SectionRenderer` and
    the strict per-language `sanitize_text()` whitelist.
    """
    title = _resolve_title(title, person_name, theme_hint, lang)
    if not subtitle:
        subtitle = "" if person_name else _DEFAULT_TITLE[_lang_key(lang)]
    subtitle = sanitize_text(subtitle, lang)
    sections = apply_narrative_gate(list(sections), lang)
    css = CSS(string=_build_css(lang) + _font_faces())

    cover_art = _pick_cover_art(theme_hint or title)
    body_parts = [
        "<div class='cover'>",
        "<div class='brand'>อัสทรัล · ระบบโหราศาสตร์</div>",
        f"<h1>{html.escape(title)}</h1>",
        f"<div class='sub'>{html.escape(subtitle)}</div>",
    ]
    if cover_art:
        body_parts.append(f"<img class='cover-art' src='{cover_art}' alt='cover art'/>")
        body_parts.append("<div class='cover-credit'>ภาพประกอบปก · มหาพิพิธภัณฑ์เมท เปิดให้เข้าถึงเสรี</div>")
    body_parts.append("</div>")

    rendered = SectionRenderer(lang).render(sections)
    section_art = section_art or _section_art_map(theme_hint or title, len(rendered))
    for idx, sec in enumerate(rendered, start=1):
        body_parts.append('<div class="section">')
        body_parts.append(f"<div class='title'>{html.escape(sec.title)}</div>")
        art_uri = section_art.get(idx)
        if art_uri:
            body_parts.append(f"<img class='cover-art' src='{art_uri}' alt='section art'/>")
        if sec.is_html:
            body_parts.append(f"<div class='body'>{'<br/>'.join(html.escape(line) for line in sec.lines)}</div>")
        else:
            for line in sec.lines:
                body_parts.append(f"<div class='line'>{html.escape(line).replace(chr(10), '<br/>')}</div>")
        body_parts.append("</div>")

    if raw_section:
        body_parts.append('<div class="section raw-section">')
        body_parts.append(f"<div class='title'>{html.escape(sanitize_text(raw_title, lang)) or _DEFAULT_TITLE[_lang_key(lang)]}</div>")
        body_parts.append(f"<div class='body'>{html.escape(sanitize_text(raw_section, lang))}</div>")
        body_parts.append("</div>")

    if footer:
        body_parts.append(f"<div class='footer'>{html.escape(sanitize_text(footer, lang))}</div>")

    html = HTML(string="\n".join(body_parts), base_url=str(_REPO))
    html.write_pdf(str(out_path), stylesheets=[css])
    return str(out_path)


def _demo() -> None:
    # ponytail: logic-only self-check, no PDF write (that needs weasyprint's
    # native deps, not just the import). Fails loudly if sanitize/normalize
    # logic regresses.
    mixed = "สวัสดี 你好 Привет Γειά hello (   ) 123"
    th_out = sanitize_text(mixed, "th")
    en_out = sanitize_text(mixed, "en")
    assert "你好" not in th_out and "Привет" not in th_out and "Γειά" not in th_out
    assert "สวัสดี" in th_out and "hello" in th_out and "123" in th_out
    assert "สวัสดี" not in en_out and "你好" not in en_out
    assert "hello" in en_out and "123" in en_out

    sections = SectionRenderer("th").render(
        [{"title": "หัวข้อ 中文", "lines": ["บรรทัด 1 Кириллица", "", "line two"]}]
    )
    assert sections[0].title == "หัวข้อ"
    assert sections[0].lines == ["บรรทัด 1", "line two"]

    assert _resolve_title("", "", "", "th") == "รายงานดวงชะตา"
    assert _resolve_title("", "", "", "en") == "Astral Report"
    print("pdf_renderer self-check OK")


if __name__ == "__main__":
    _demo()
