"""Pure-English meanings for all 78 tarot cards (no TH/EN mix).

Mirror of tarot_meanings_th.TAROT_MEANINGS_TH, used by the EN PDF build and
the EN side of reel_reading. Each card has upright + reversed meanings.
"""
# fmt: off
TAROT_MEANINGS_EN: dict[str, dict[str, str]] = {
    # ── Major Arcana ──
    "The Fool": {
        "upright": "A new beginning with a free spirit. The courage to step forward without needing to know the destination is your gift right now.",
        "reversed": "Beware hesitation and fear of change. Leaping without looking may bring poor results; understand before you act.",
    },
    "The Magician": {
        "upright": "Everything you desire is already in front of you. You hold the full set of tools; just pick them up. This season is about action backed by will.",
        "reversed": "Beware deception and things that only appear real. Someone may be fooling you, or you are wasting your own talent. Scattered energy is the problem now.",
    },
    "The High Priestess": {
        "upright": "Something you already know in your gut, yet you pretend not to see. Your intuition never fails; what fails is when you stop listening to it.",
        "reversed": "You may be ignoring your inner voice. Do not let outside noise drown the truth of your heart.",
    },
    "The Empress": {
        "upright": "Abundance is blossoming: love, money, and all you have nurtured for so long. Just remember to pause and care for yourself too.",
        "reversed": "You give to others so much that you forget to refill yourself. Stop, breathe deeply, and turn back to what you need.",
    },
    "The Emperor": {
        "upright": "You are the one who must command the situation, not let anyone command you. The stability you build is a base others lean on.",
        "reversed": "Too much control is not safety; it is a cage you lock yourself into. Learn to loosen your grip.",
    },
    "The Hierophant": {
        "upright": "Those around you offer much advice, but the right answer must be your own. Some inherited rules are simply outdated.",
        "reversed": "It is time to break the old frame that no longer fits you. Do what you believe; no one will blame you.",
    },
    "The Lovers": {
        "upright": "Your heart is divided right now: mind says one thing, heart says another. The one you think of feels the same more than you know.",
        "reversed": "A relationship or choice that is out of sync is creating confusion. Choose what aligns with your deepest values.",
    },
    "The Chariot": {
        "upright": "Do not step back; you are nearly there. Hold your speed, and do not let anyone press the brake for you.",
        "reversed": "Your aim may slip from control through emotion swinging like the wind. Rein yourself in first.",
    },
    "Strength": {
        "upright": "What you quietly endure is exhausting, isn't it? Your gentleness is power, not weakness. Let no one tell you otherwise.",
        "reversed": "Your patience is shaking. Do not push with force beyond what is healthy; settle your emotions first.",
    },
    "The Hermit": {
        "upright": "Lately you want quiet, not much talk; that is fine. But do not stay alone too long; the one who waits still waits.",
        "reversed": "You are so hidden others cannot reach you, or you flee problems into the dark. Try working with others again.",
    },
    "Wheel of Fortune": {
        "upright": "The wheel is turning, and turning in your favor. What you lost before returns in a better form.",
        "reversed": "The wheel may turn away for a while. Cracks in fortune come from what you refuse to release. Wait for the next turn.",
    },
    "Justice": {
        "upright": "What you do well returns to you, and so does what others do wrong to you. Truth is often late, but it comes.",
        "reversed": "You may be avoiding responsibility, or judging someone unfairly. Settle what remains owed.",
    },
    "The Hanged Man": {
        "upright": "You are stuck on the same old view. Flip it one hundred eighty degrees and the answer appears.",
        "reversed": "You stall without changing perspective. Waiting without purpose is draining your energy.",
    },
    "Death": {
        "upright": "A chapter of your life has truly closed. Do not cling to the old page; a new one is already opening here.",
        "reversed": "You struggle to hold on to what is over. Refusing to let go keeps you from moving on.",
    },
    "Temperance": {
        "upright": "Do not rush; what waits is worth it. The middle path is not bland; it is balance, just right.",
        "reversed": "Your life is off balance now: too much of one thing, too little of another. Realign the rhythm.",
    },
    "The Devil": {
        "upright": "Something or someone you know is no good, yet you cannot quit, because it has become a soft cage.",
        "reversed": "The light is returning and you begin to see the chains that bind you. You can walk out whenever you realize it.",
    },
    "The Tower": {
        "upright": "Something is about to fall, and it will fall loudly. But hear this: it falls because the foundation was unsound for too long. Let it fall.",
        "reversed": "You survived a harsh crisis but still tremble inside. Rebuilding before you recover may break you again.",
    },
    "The Star": {
        "upright": "After heavy rain the sky is opening. The hope you secretly hold is not empty words.",
        "reversed": "Your confidence dims for a while. Do not let self-doubt extinguish the star that still shines.",
    },
    "The Moon": {
        "upright": "Things are not as they appear; beware deciding while dizzy. The biggest fear is rarely the real danger.",
        "reversed": "The confusion clears; truth emerges from the fog. The moonlight shows a path you once lost.",
    },
    "The Sun": {
        "upright": "Truly lucky card: clear happiness awaits. Do not refuse it; you deserve this.",
        "reversed": "Happiness is still there, briefly shaded by cloud. Do not let insecurity dim your sun.",
    },
    "Judgement": {
        "upright": "Something awakens you from the old way of seeing. A chance you once refused returns; this time, choose well.",
        "reversed": "You still slumber to the call, or ignore lessons fate keeps sending.",
    },
    "The World": {
        "upright": "A cycle of your life is complete; you truly did it. A wider stage awaits; go forth.",
        "reversed": "You are almost at the goal but lack a clean finish. Do not jump to the next cycle before closing this one.",
    },

    # ── Wands ──
    "Ace of Wands": {
        "upright": "A spark of new opportunity just lit; enthusiasm is blazing. Seize it before the fire dies.",
        "reversed": "Your enthusiasm stumbles briefly; a new project stalls for lack of drive.",
    },
    "Two of Wands": {
        "upright": "You stand at a crossroads, weighing what you have against what you might reach. Dare to dream far.",
        "reversed": "Uncertainty keeps you only watching the world instead of walking. Time to decide.",
    },
    "Three of Wands": {
        "upright": "What you started is expanding; your sight sees a wider horizon. Success begins to grow.",
        "reversed": "Progress slows, waiting on others or on signals that never come. The delay drags on.",
    },
    "Four of Wands": {
        "upright": "Reason to celebrate; your base grows steady, with people ready to stand beside you.",
        "reversed": "The celebration is incomplete; you may feel apart even among others.",
    },
    "Five of Wands": {
        "upright": "Competition or clashing views heat up. Do not get pulled in too deep; it is normal.",
        "reversed": "The noise begins to settle; the mess that was conflict finds its place.",
    },
    "Six of Wands": {
        "upright": "Victory is yours; recognition from those around you makes you proud of the work.",
        "reversed": "Victory is not yet real as hoped; pride may be pricked by criticism.",
    },
    "Seven of Wands": {
        "upright": "You defend your position; others may challenge, but your stance is solid.",
        "reversed": "Fatigue from the fight weighs on you; you wonder why you endure at all.",
    },
    "Eight of Wands": {
        "upright": "Things move fast as arrows; news or chance brings swift change.",
        "reversed": "The frantic speed stumbles; delay makes the smooth rhythm catch.",
    },
    "Nine of Wands": {
        "upright": "You near the shore but stay watchful. Old wounds make you cautious; that is fine.",
        "reversed": "Exhaustion makes you quit before the line, or drop guard and get hit again.",
    },
    "Ten of Wands": {
        "upright": "You carry a full load of duties; the weight tires you, yet the goal is near.",
        "reversed": "Time to set down what is unnecessary. Some burdens you carry yourself for no reason.",
    },
    "Page of Wands": {
        "upright": "Good news or a new chance arrives; your heart is full of fresh curiosity.",
        "reversed": "Enthusiasm turns to fluster, or a new project fails at the first turn.",
    },
    "Knight of Wands": {
        "upright": "You ride forward swift, hot, and quick to finish almost in a blink.",
        "reversed": "Speed without direction makes you stumble; a project fails for lack of readiness.",
    },
    "Queen of Wands": {
        "upright": "You radiate confidence and charm; others are drawn by your warm, decisive power.",
        "reversed": "Confidence turns to ego, or you lose the spark that once drew people.",
    },
    "King of Wands": {
        "upright": "You are a leader with vision, decisive, driving others forward by foresight.",
        "reversed": "Authoritarian use of power, or restless drive without direction, ruins what you built.",
    },

    # ── Cups ──
    "Ace of Cups": {
        "upright": "New feeling overflows: love, compassion, or the birth of an open heart.",
        "reversed": "Feeling is held inside, or a bond not yet ready to bloom. Fill the cup first.",
    },
    "Two of Cups": {
        "upright": "Two hearts join hands; a balanced, beautiful bond is forming.",
        "reversed": "The once-shared understanding skews; a partner loses trust.",
    },
    "Three of Cups": {
        "upright": "Reason to celebrate with friends; shared joy sweetens life.",
        "reversed": "The party turns excessive, or a friend group falls out of tune.",
    },
    "Four of Cups": {
        "upright": "You sit staring at what you have, bored, missing the new cup life offers. Notice it.",
        "reversed": "The restlessness eases; you begin to accept what once bored you. New choice appears.",
    },
    "Five of Cups": {
        "upright": "You watch only the spilled cups, forgetting the ones still standing behind. Turn around.",
        "reversed": "The sorrow heals; you accept the loss and begin to walk on.",
    },
    "Six of Cups": {
        "upright": "Sweet memories from the past drift in; the charm of yesterday warms you.",
        "reversed": "You sink into the past, unwilling to move on, or old matters haunt you.",
    },
    "Seven of Cups": {
        "upright": "Imagination floats like mist; many choices but none yet real.",
        "reversed": "The dream settles into a mindful choice instead of drifting.",
    },
    "Eight of Cups": {
        "upright": "You walk away from what once mattered, knowing it no longer answers your heart.",
        "reversed": "You cling to what is over; not leaving keeps you from moving on.",
    },
    "Nine of Cups": {
        "upright": "Your wish nears truth; the row of cups says happiness is within reach.",
        "reversed": "The satisfaction gained is less than imagined; outer joy not yet filling within.",
    },
    "Ten of Cups": {
        "upright": "Full happiness of family and bond; this is the aim many wish for.",
        "reversed": "Harmony at home frays, or expected joy not yet real as dreamed.",
    },
    "Page of Cups": {
        "upright": "News from the heart arrives; fresh feeling may surprise you.",
        "reversed": "The feeling is not yet real, or news carries a jest not meant seriously.",
    },
    "Knight of Cups": {
        "upright": "The messenger of love approaches; a heart chance or dream offered beautifully.",
        "reversed": "The sweet feeling may hide deception; do not fall for illusion.",
    },
    "Queen of Cups": {
        "upright": "You connect with feeling deeply, gentle and truly understanding of others.",
        "reversed": "Flooding emotion drowns you in feeling, clouding clear reason.",
    },
    "King of Cups": {
        "upright": "You command emotion with wisdom, balancing heart and reason with respect.",
        "reversed": "Suppressed emotion erupts, or you use coolness to mask sincerity.",
    },

    # ── Swords ──
    "Ace of Swords": {
        "upright": "A clear truth flashes in mind; sharp thought cuts through the fog of confusion.",
        "reversed": "Thoughts still unordered, or words slipped may wound. Mind the unsharpened blade.",
    },
    "Two of Swords": {
        "upright": "You blindfold yourself to avoid choosing between two equal weights.",
        "reversed": "The inner conflict clears; you dare remove the blindfold and decide.",
    },
    "Three of Swords": {
        "upright": "A heart pierced threefold, often from disappointment or parting; painful but passing.",
        "reversed": "The wound begins to heal; the inner rift mends and fades.",
    },
    "Four of Swords": {
        "upright": "Time to rest; the weary mind needs calm to recover.",
        "reversed": "You rise from rest, but if you keep lying low it becomes avoidance.",
    },
    "Five of Swords": {
        "upright": "A victory won with cost; sometimes retreat is wiser than winning not worth it.",
        "reversed": "You begin mending the broken tie, saving face to keep what matters more.",
    },
    "Six of Swords": {
        "upright": "You row across waters that calm; moving from sorrow toward safety.",
        "reversed": "The passage not yet clear; you drift with hesitation, not releasing the past.",
    },
    "Seven of Swords": {
        "upright": "A hidden plan or shortcut not clean; beware one who hides a blade behind.",
        "reversed": "The secret plan is caught, or you tire of the covert game.",
    },
    "Eight of Swords": {
        "upright": "You feel bound in a cage of your own thoughts, forgetting the gate is open.",
        "reversed": "The binding net frays; you see the way out and dare to move.",
    },
    "Nine of Swords": {
        "upright": "Late-night worry gnaws the mind; fear is usually larger than reality.",
        "reversed": "The panic calms; you face what frightened and find it not so dreadful.",
    },
    "Ten of Swords": {
        "upright": "A painful but decisive end; the final stitch says this chapter is done, truly.",
        "reversed": "You narrowly escape disaster; still breath to begin anew.",
    },
    "Page of Swords": {
        "upright": "News or new thought arrives like an arrow; a curious youth watches the world sharply.",
        "reversed": "Curiosity turns to gossip or careless chatter without intent.",
    },
    "Knight of Swords": {
        "upright": "You charge ahead with keen thought, fast as lightning, not stopping for thorns.",
        "reversed": "Speed without caution crashes into the wall; beware words that wound.",
    },
    "Queen of Swords": {
        "upright": "You see the world with clarity and directness, decisive in speech, not self-deceived.",
        "reversed": "Sharpness turns cutting, or you use reason to sever tenderness.",
    },
    "King of Swords": {
        "upright": "You decide with keen reason, a leader guided by justice and wisdom.",
        "reversed": "Power used tyrannically, or decisions without heart, harm what surrounds you.",
    },

    # ── Pentacles ──
    "Ace of Pentacles": {
        "upright": "A new chance in money or stability just conceived; this seed grows if tended.",
        "reversed": "The material chance stumbles, or an investment not yet blooming as hoped.",
    },
    "Two of Pentacles": {
        "upright": "You juggle between work and life with skill, spinning two spheres.",
        "reversed": "The balance once held tilts; you lose poise between money and time.",
    },
    "Three of Pentacles": {
        "upright": "Work done together shows result; your skill earns recognition from the knowing.",
        "reversed": "Cooperation stumbles from a team out of tune, or craft not yet up to standard.",
    },
    "Four of Pentacles": {
        "upright": "You clutch what you have tightly; security is good, but sometimes gripped by fear to share.",
        "reversed": "The clinging eases; you release what was hoarded, or lose a part unintentionally.",
    },
    "Five of Pentacles": {
        "upright": "Lately you feel lacking or left out, but look: light waits beyond the window.",
        "reversed": "The hardship clears; you find a way out of the want you thought stuck.",
    },
    "Six of Pentacles": {
        "upright": "Giving and receiving are balanced; you are in a rhythm where fortune or people bring wealth. Be the one who offers too.",
        "reversed": "Imbalance in give and take; you may be used, or too anxious to lend a hand.",
    },
    "Seven of Pentacles": {
        "upright": "You gaze at the field you planted, awaiting fruit that grows slow; patience repays.",
        "reversed": "The effort seems fruitless; you begin to doubt the wait is worth it.",
    },
    "Eight of Pentacles": {
        "upright": "Diligent craft accumulates finer work with each day.",
        "reversed": "Diligence fades; repetitive work becomes going through the motions without heart.",
    },
    "Nine of Pentacles": {
        "upright": "You harvest what you nurtured; independence and comfort earned by your own hand.",
        "reversed": "The success gained is less steady than it seems; solitude turns lonely and uneasy.",
    },
    "Ten of Pentacles": {
        "upright": "Stability of family and legacy passed on; you rest in a warm, secure circle.",
        "reversed": "Harmony of wealth frays, or inherited burden turns to pressure.",
    },
    "Page of Pentacles": {
        "upright": "Good news in study or work arrives; a youth begins with curious intent.",
        "reversed": "The new interest fails at the first turn, or study not yet progressing as hoped.",
    },
    "Knight of Pentacles": {
        "upright": "You persist step by step, slow but clear; steady as a mountain even when calm.",
        "reversed": "The routine begins to gnaw; the once-steady path turns into a stuck frame.",
    },
    "Queen of Pentacles": {
        "upright": "You care for home and work with warmth; a base full of nurturing.",
        "reversed": "Caring for others too much neglects yourself; the security starts to shake within.",
    },
    "King of Pentacles": {
        "upright": "You command wealth with wisdom; prosperous, grounded, giving others a sense of safety.",
        "reversed": "Wealth turns to anxiety, or you use material power to pressure others.",
    },
}
# fmt: on
