"""WeasyPrint brochure PDF generator.

Design goals
- Always TH/EN bilingual.
- One source of truth: sections come from the report endpoints,
  not from ad-hoc hardcoded strings.
- Premium print styling: ivory background, gold rules, section cards,
  Thai-safe font stack, page breaks between sections.
- All section content flows through `section_renderer()` so sanitization
  and normalization happen in exactly one place before HTML assembly.
"""

from __future__ import annotations

import os
from pathlib import Path
from typing import Sequence

from weasyprint import HTML, CSS

from src.services.narrative_sanitizer import sanitize_narrative

_REPO = Path(__file__).resolve().parents[2]
FONT_DIR = _REPO / "assets" / "fonts"
ART_DIR = _REPO / "assets" / "art"
_GOLD = "#9a7b34"
_IVORY = "#f6f0e2"
_INK = "#3b3324"
_SOFT = "rgba(154,123,52,.35)"

# Lang-aware typography scale: TH needs taller line-height for tone marks;
# EN reads fine tighter and slightly smaller at H1.
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
        "line_height": "1.55",
    },
}

_DEFAULT_TITLE = {"th": "รายงานดวงชะตา", "en": "Astral Report"}


def _lang_key(lang: str) -> str:
    return "th" if str(lang).lower().startswith("th") else "en"


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
    # Embed local fonts when available; fall back to system names above.
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
        return "data:image/jpeg;base64," + __import__("base64").b64encode(path.read_bytes()).decode()
    except Exception:
        return ""


def _pick_cover_art(theme_hint: str = "") -> str:
    # Prefer local CC0 art when it matches the report theme; otherwise fallback.
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
    # Return at most one embedded artwork URI for the first section when relevant.
    art_map = {}
    uri = _pick_cover_art(theme_hint)
    if uri and section_count > 0:
        art_map[1] = uri
    return art_map


def sanitize_text(text: object, lang: str = "th") -> str:
    """Strip CJK/Cyrillic/Greek artifacts and known garbled tokens from any text.

    Thin wrapper over the shared `sanitize_narrative` safety net so every
    string that reaches the PDF (titles, lines, footers) goes through the
    same one-place cleanup, regardless of source.
    """
    if text is None:
        return ""
    return sanitize_narrative(str(text), lang=lang)


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


def section_renderer(sections: Sequence[dict], lang: str = "th") -> list[dict]:
    """Normalize raw section dicts into a single sanitized shape before HTML assembly.

    Every section becomes `{"title": str, "lines": list[str], "is_html": bool}`
    with all text run through `sanitize_text()`, so the HTML-building loop in
    `render_brochure()` never touches raw, un-sanitized report content.
    """
    normalized = []
    for sec in sections:
        title = sanitize_text(sec.get("title", ""), lang)
        raw_lines = sec.get("lines", []) or []
        lines = [sanitize_text(line, lang) for line in raw_lines]
        is_html = any("<" in line and ">" in line for line in lines)
        normalized.append({"title": title, "lines": lines, "is_html": is_html})
    return normalized


def render_brochure(
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

    Backward-compatible with the old `render_pdf(...)` signature used in
    `reports.py`, including optional biwheel/tarot extras.
    """
    title = _resolve_title(title, person_name, theme_hint, lang)
    if not subtitle:
        subtitle = "" if person_name else _DEFAULT_TITLE[_lang_key(lang)]
    subtitle = sanitize_text(subtitle, lang)
    css = CSS(string=_build_css(lang) + _font_faces())

    cover_art = _pick_cover_art(theme_hint or title)
    body_parts = [
        "<div class='cover'>",
        "<div class='brand'>ASTRAL · Astrology Engine</div>",
        f"<h1>{title}</h1>",
        f"<div class='sub'>{subtitle}</div>",
    ]
    if cover_art:
        body_parts.append(f"<img class='cover-art' src='{cover_art}' alt='cover art'/>")
        body_parts.append("<div class='cover-credit'>Cover artwork · The Met Open Access</div>")
    body_parts.append("</div>")

    sections = section_renderer(sections, lang)
    section_art = section_art or _section_art_map(theme_hint or title, len(sections))
    for idx, sec in enumerate(sections, start=1):
        body_parts.append('<div class="section">')
        body_parts.append(f"<div class='title'>{sec['title']}</div>")
        art_uri = section_art.get(idx)
        if art_uri:
            body_parts.append(f"<img class='cover-art' src='{art_uri}' alt='section art'/>")
        if sec["is_html"]:
            body_parts.append(f"<div class='body'>{'<br/>'.join(sec['lines'])}</div>")
        else:
            for line in sec["lines"]:
                body_parts.append(f"<div class='line'>{line.replace(chr(10), '<br/>')}</div>")
        body_parts.append("</div>")

    if raw_section:
        body_parts.append('<div class="section raw-section">')
        body_parts.append(f"<div class='title'>{sanitize_text(raw_title, lang) or (_DEFAULT_TITLE[_lang_key(lang)])}</div>")
        body_parts.append(f"<div class='body'>{sanitize_text(raw_section, lang)}</div>")
        body_parts.append("</div>")

    if footer:
        body_parts.append(f"<div class='footer'>{sanitize_text(footer, lang)}</div>")

    html = HTML(string="\n".join(body_parts), base_url=str(_REPO))
    html.write_pdf(str(out_path), stylesheets=[css])
    return str(out_path)
