"""EN narrative beats for reel-style tarot — mirrors reel_reading.py TH data.

Kept in a separate module so the Thai voice file stays clean; the reading
composes th + en side by side.
"""
from __future__ import annotations

_HOOKS_EN = {
    "current situation": [
        "Something's been bothering you lately, hasn't it?",
        "You're standing at a crossroads right now.",
        "If nothing feels quite right these days — the cards agree.",
    ],
    "obstacle": [
        "And here's what's been holding you back...",
        "Someone, something is quietly draining your energy.",
        "The problem you thought was over? It isn't. Not yet.",
    ],
    "advice": [
        "Listen closely, this part matters.",
        "This card is what you most need to hear.",
        "Do this, and things start moving on their own.",
    ],
    "answer": [
        "Straight question, straight answer.",
        "One card, and it says plenty.",
    ],
}

# upright beat, reversed beat
_STORY_EN = {
    "The Fool": ("A new adventure is calling you, and you want to leap in with everything.",
                 "But wait — this time look before you leap. Check the ground first."),
    "The Magician": ("You already have every tool you need. You just haven't dared to pick them up.",
                     "Watch out for someone who talks brilliantly but delivers nothing."),
    "The High Priestess": ("Deep down you already know the answer. You're just pretending not to see it.",
                           "Your intuition is never wrong. It only fails when you refuse to listen."),
    "The Empress": ("Someone cares about you far more than you realize.",
                    "You give too much and refill too little. Stop. Breathe."),
    "The Emperor": ("You're the one meant to run the show — don't hand anyone else the reins.",
                    "Total control isn't safety. It's a cage."),
    "The Hierophant": ("Everyone around you has advice. The right answer still has to be yours.",
                       "Some rules are outdated. Break them — nobody's watching."),
    "The Lovers": ("Your head says one thing, your heart another.",
                   "That person on your mind? They feel more than they show."),
    "The Chariot": ("Don't turn back now. You're closer than you think.",
                    "Hold your own pace. Don't let anyone brake for you."),
    "Strength": ("Quietly holding it all together is exhausting, isn't it?",
                 "Your gentleness is strength, not weakness. Don't let anyone tell you otherwise."),
    "The Hermit": ("Wanting space right now isn't wrong.",
                   "Just don't stay gone too long — someone is still waiting for you."),
    "Wheel of Fortune": ("The wheel is turning, and it's turning your way.",
                         "What you lost is coming back in a better shape."),
    "Justice": ("The good you did is coming back to you. So is what someone did to you.",
                "Truth arrives late, but it always arrives. Wait well."),
    "The Hanged Man": ("You're stuck because you've been looking at the same picture too long.",
                       "Flip it 180 degrees. The answer appears on its own."),
    "Death": ("An old chapter of your life has already closed. Truly.",
              "Don't go back for it. A new page is open right here."),
    "Temperance": ("Don't rush. What's worth having is worth waiting for.",
                   "Middle ground isn't blandness. It's balance."),
    "The Devil": ("There's something — or someone — you know is bad for you but can't quit.",
                  "Those chains were never locked. You can walk out whenever you choose."),
    "The Tower": ("Something is about to break, and it will be loud.",
                  "But listen — it breaks because its foundation failed long ago. Let it fall."),
    "The Star": ("After the storm, the sky is finally clearing.",
                 "The hope you secretly hold? It's not a fantasy."),
    "The Moon": ("Not everything is what it appears to be. Don't decide while your head spins.",
                 "Your biggest fear is rarely your greatest danger."),
    "The Sun": ("This is one of the good ones — real happiness is waiting for you.",
                "Don't fumble it. You deserve this."),
    "Judgement": ("Something is waking you up from an old way of seeing.",
                  "The opportunity you once refused is back. Think carefully this time."),
    "The World": ("A whole cycle of your life is complete. You actually did it.",
                  "A bigger stage awaits. Go walk onto it."),
}

_CLOSING_EN = "...and if this felt like it was about you — it is."


def hook_for(position_th: str, i: int) -> str | None:
    hooks = _HOOKS_EN.get(position_th)
    return hooks[i % len(hooks)] if hooks else None


def story_for(card_name: str, orientation: str) -> str | None:
    pair = _STORY_EN.get(card_name)
    if not pair:
        return None
    return pair[1] if orientation == "reversed" else pair[0]


def generic_minor_story(card_name: str, orientation: str) -> str:
    suit = card_name.rsplit(" of ", 1)[-1]
    rank = card_name.split(" of ")[0]
    domain = {
        "Wands": "work and ambition",
        "Cups": "feelings and love",
        "Swords": "thoughts and words",
        "Pentacles": "money and stability",
    }[suit]
    verb = {
        "Ace": "is about to begin", "Two": "is weighing options",
        "Three": "is growing", "Four": "has gone still — maybe too still",
        "Five": "just hit friction", "Six": "is turning around",
        "Seven": "is biding time", "Eight": "is speeding up",
        "Nine": "is almost at the finish", "Ten": "has peaked",
        "Page": "brings news", "Knight": "moves fast",
        "Queen": "rests fully in your hands", "King": "answers to you alone",
    }.get(rank, "")
    tail = "but it stumbles midway" if orientation == "reversed" else "and the timing favors you"
    return f"In {domain}: {verb} — {tail}."
