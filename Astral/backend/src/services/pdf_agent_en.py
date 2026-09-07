"""PDF writing specialist agent — English narrative only."""

from __future__ import annotations

import hashlib
from dataclasses import dataclass

from src.services.synastry_scoring import compute_synastry_profile
from src.services.element_service import compute_element_balance
from src.services.tarot_service import draw_spread
from src.services.tarot_downloader import get_card_path, ensure_deck_ready


@dataclass(frozen=True)
class Persona:
    name: str
    sun: str
    moon: str
    mercury: str
    asc: str


@dataclass(frozen=True)
class CoupleContext:
    a: Persona
    b: Persona
    score: int = 0
    top_bond: str = ""
    top_dimension: str = ""
    top_friction: str = ""


def _seed(name_a: str, name_b: str, spread: str) -> int:
    return int(hashlib.sha256(f"{name_a}|{name_b}|{spread}".encode()).hexdigest()[:8], 16)


def section_overview(ctx: CoupleContext) -> list[str]:
    a, b = ctx.a, ctx.b
    return [
        f"At first glance, {a.name} seems slow to open up. But once they feel safe, their {a.sun} Sun and {a.asc} Ascendant reveal something genuine — honest, even when they are not loud.",
        f"On the other side, {b.name} is always prepared. Their {b.sun} Sun and {b.asc} Ascendant love planning; before acting, they need to see the full picture.",
        f"Their meeting was no accident. It was two lives quietly refined across time, and when they finally crossed paths, both knew.",
        f"{a.name}'s Moon in {a.moon} needs emotional safety — no criticism, no pressure. {b.name}'s Moon in {b.moon} wants something lasting, not just feelings, but a future they can actually see.",
        "",
        "",
    ]


def section_bonds(ctx: CoupleContext) -> list[str]:
    a, b = ctx.a, ctx.b
    return [
        f"Picture this: {a.name} is drained by obligations and almost pulls away. Instead of calling, they reach for {b.name} — not out of duty, but because they need someone nearby. That is not drama; that is real synastry.",
        f"The core strength is that both Moons see the world through complementary lenses. {a.name} needs emotional safety through tangible stability. {b.name} needs security through systems and planning. Being together does not mean zero conflict; it means conflict they know how to solve.",
        f"{a.name}'s Mercury in {a.mercury} connects with {b.name}'s Ascendant. Communication is rarely a battle. They think alike, even when they sound different. Deliberate or measured, they always understand each other.",
        "",
        "",
    ]


def section_frictions(ctx: CoupleContext) -> list[str]:
    a, b = ctx.a, ctx.b
    return [
        f"No pair is friction-free, and this one is no exception. Imagine a sharp argument that silences the whole room — that is not a disaster, it is a signal. When Mars energy clashes, it does not mean love loses; it means both are practicing how to fight fair.",
        f"{a.name}'s {a.asc} Ascendant squaring {b.name}'s {b.sun} Sun creates an almost dangerous pull — but it is not. It is the kind of tension that makes you lean in closer, not run away. Outsiders may think it is too much; insiders know it is just heat.",
        f"Bottom line: none of these frictions are dealbreakers. They are the work this pair does together. With patience, with words before explosions, conflict does not accumulate — it transforms into shared history.",
        "",
        "",
    ]


def section_score(ctx: CoupleContext) -> list[str]:
    score = ctx.score
    return [
        f"The score: {score}/100 — not the highest, but it tells the truth. This relationship has more room to grow than comfort zone.",
        f"The standout aspect: {ctx.top_bond} — {ctx.top_dimension}. This is the reason they stay, not just the reason they fell in love.",
        f"Chemistry, communication, and stability are all present. The remaining friction is a learning curve they can walk together. {score} is not a failure — it is a relationship that is not easy, but worth it.",
        "",
        "",
    ]


def section_advice(ctx: CoupleContext) -> list[str]:
    a, b = ctx.a, ctx.b
    return [
        f"Love does not fail because two people are wrong — it fails because they speak different languages. {a.name} loves through presence, through doing, through quiet consistency. {b.name} loves through words, through affirmation, through making sure the important things get said out loud.",
        f"For {a.name}: let {b.name} feel heard. You do not need a long explanation — just one sentence that says you matter. Showing emotion is not weakness. It is the bridge.",
        f"For {b.name}: {a.name}'s silence is not distance — it is a slow-burn love language. If you ever wonder what they are feeling, do not push for words. Just be there. That is when they open up.",
        f"Together: carve out calm talk-time before things heat up. Three minutes of pause before speaking can save hours of repair. Both Mars energies run hot — but that is also what makes the connection electric. Swap small talk for a compliment tomorrow and see what happens.",
        "",
    ]


def build_synastry_sections(
    name_a: str,
    name_b: str,
    chart_a: dict,
    chart_b: dict,
    spread: str = "three_card",
) -> tuple[list[dict], str, str]:
    def _sign(body_name: str, chart: dict) -> str:
        for b in chart.get("bodies", []):
            if b.get("body") == body_name:
                return b.get("sign", "")
        return ""

    sun_a = _sign("Sun", chart_a)
    moon_a = _sign("Moon", chart_a)
    mercury_a = _sign("Mercury", chart_a)
    asc_a = chart_a.get("ascendant", {}).get("sign", "")

    sun_b = _sign("Sun", chart_b)
    moon_b = _sign("Moon", chart_b)
    mercury_b = _sign("Mercury", chart_b)
    asc_b = chart_b.get("ascendant", {}).get("sign", "")

    a_p = Persona(name_a, sun_a, moon_a, mercury_a, asc_a)
    b_p = Persona(name_b, sun_b, moon_b, mercury_b, asc_b)

    profile = compute_synastry_profile(chart_a, chart_b)
    score = int(profile.get("overall", 0))
    top_bonds = profile.get("top_bonds", [])
    top = top_bonds[0] if top_bonds else {}
    frictions = profile.get("frictions", [])
    top_friction = frictions[0] if frictions else {}

    ctx = CoupleContext(
        a=a_p,
        b=b_p,
        score=score,
        top_bond=top.get("pair", ""),
        top_dimension=top.get("dimension", ""),
        top_friction=top_friction.get("aspect", ""),
    )

    sections = [
        {"title": f"Relationship Overview — {name_a} + {name_b}", "lines": section_overview(ctx)},
        {"title": f"The Bonds That Hold — {name_a} + {name_b}", "lines": section_bonds(ctx)},
        {"title": f"The Edges That Grow — {name_a} + {name_b}", "lines": section_frictions(ctx)},
        {"title": f"Compatibility Score — {score}/100", "lines": section_score(ctx)},
        {"title": f"The Oracle's Advice — {name_a} + {name_b}", "lines": section_advice(ctx)},
    ]

    seed_a = _seed(name_a, name_b, spread)
    seed_b = _seed(name_b, name_a, spread)
    cards_a = draw_spread(name_a, spread=spread, seed=seed_a, element_balance=compute_element_balance(chart_a))
    cards_b = draw_spread(name_b, spread=spread, seed=seed_b, element_balance=compute_element_balance(chart_b))

    def _tarot_html(cards, title):
        rows = []
        for c in cards:
            path = get_card_path(c["card"])
            if path:
                img_src = f"file:///{path.as_posix()}"
                img_html = f"<div class=\"tcard-img\"><img src=\"{img_src}\" alt=\"{c['card']}\"/></div>"
            else:
                img_html = ""
            rows.append(f"""
              <div class="tcard">
                {img_html}
                <div class="tcard-pos">{c['position']}</div>
                <div class="tcard-name">🃏 {c['card']}</div>
                <div class="tcard-mean">{c['meaning']}</div>
              </div>""")
        return f'<div class="trow-head">{title}</div><div class="trow">{"".join(rows)}</div>'

    tarot_html = _tarot_html(cards_a["cards"], f"Tarot of {name_a}") + '<div style="height:4mm"></div>' + _tarot_html(cards_b["cards"], f"Tarot of {name_b}")
    tarot_title = f"Tarot Archetypes — {name_a} + {name_b}"

    return sections, tarot_html, tarot_title


def _persona_from_chart(name: str, chart: dict) -> Persona:
    def _sign(body_name: str) -> str:
        for b in chart.get("bodies", []):
            if b.get("body") == body_name:
                return b.get("sign", "")
        return ""
    return Persona(
        name=name,
        sun=_sign("Sun"),
        moon=_sign("Moon"),
        mercury=_sign("Mercury"),
        asc=chart.get("ascendant", {}).get("sign", ""),
    )


def build_natal_sections(name: str, chart: dict) -> list[dict]:
    persona = _persona_from_chart(name, chart)
    return [
        {
            "title": f"personality portrait — {name}",
            "lines": [
                f"{name} does not walk into a room trying to impress anyone. With Sun in {persona.sun} and {persona.asc} Ascendant, they show up steady — and that alone changes the energy around them.",
                f"The Moon in {persona.moon} keeps their emotional world private. They need a harbor, not a spotlight.",
                f"Mercury in {persona.mercury} tied to the Ascendant makes communication intentional. They choose words carefully because they know they carry weight.",
                "Here is the part people miss: beneath the calm surface, there is a restless mind asking whether what they are building actually matters.",
                "The real lesson is not about confidence. It is about allowing yourself to be seen without performing.",
                "",
                "",
            ],
        }
    ]


def build_composite_sections(name_a: str, name_b: str, chart_a: dict, chart_b: dict) -> list[dict]:
    from src.services.composite_service import compute_composite
    composite = compute_composite(chart_a, chart_b)
    sun = next((b["sign"] for b in composite.get("bodies", []) if b["body"] == "Sun"), "")
    moon = next((b["sign"] for b in composite.get("bodies", []) if b["body"] == "Moon"), "")
    asc = composite.get("ascendant", {}).get("sign", "")
    return [
        {
            "title": f"composite midpoint — {name_a} + {name_b}",
            "lines": [
                f"{name_a} + {name_b} composite chart shows Sun in {sun}, Moon in {moon}, Ascendant in {asc}. This pair is not two separate individuals; it is a new entity born from the midpoint between them.",
                f"The energies do not add directly; they average into a middle ground both can reach. That is what makes composite humanize the relationship.",
                f"The composite chart is not a super couple blueprint. It is a map of relationship energy both must develop together.",
                "",
                "",
            ],
        }
    ]


def build_transit_sections(name: str, natal_chart: dict, transits: list[dict]) -> list[dict]:
    hits = transits[:8]
    return [
        {
            "title": f"transit now — {name}",
            "lines": [
                f"The planets are never truly asleep. There are {len(hits)} notable hits right now — not every transit turns life upside down, but some signals deserve attention.",
                f"The important directions: Saturn and Jupiter being aspected by current planets is not punishment; it is a reminder.",
                f"The caution window: if Jupiter or Saturn is hit by an applying aspect, watch for sudden home or finance shifts. This is an investment choice, not random luck.",
                "",
                "",
            ],
        }
    ]


def build_muhurta_sections(action: str, windows: list[dict]) -> list[dict]:
    top = windows[:3]
    if not top:
        return [{"title": f"muhurta — {action}", "lines": ["No auspicious windows found in this range.", ""]}]
    return [
        {
            "title": f"muhurta — {action} / electional timing",
            "lines": [
                f"Top window for {action}: {top[0]['when_local']} — score {top[0]['score']} — reasons: {'; '.join(top[0].get('reasons_en', [])[:2])}",
                f"Second: {top[1]['when_local'] if len(top) > 1 else '-'} — score {top[1]['score'] if len(top) > 1 else '-'} — reasons: {'; '.join(top[1].get('reasons_en', [])[:2]) if len(top) > 1 else '-'}",
                f"Third: {top[2]['when_local'] if len(top) > 2 else '-'} — score {top[2]['score'] if len(top) > 2 else '-'} — reasons: {'; '.join(top[2].get('reasons_en', [])[:2]) if len(top) > 2 else '-'}",
                "",
                "",
            ],
        }
    ]


def sanitize_narrative(text: str) -> str:
    """Final safety net: strip non-EN artifacts before rendering."""
    import re
    artifacts = [
        "Axami", "Kps", "εστι", "oportun", " Ars", "Kritikal",
        "wajik indian", "cuatro palos", "etalon", "rutin",
        " estat分析", "cross-reference", " audience", "від",
    ]
    for art in artifacts:
        text = text.replace(art, "")
    text = re.sub(r"\s+", " ", text).strip()
    return text
