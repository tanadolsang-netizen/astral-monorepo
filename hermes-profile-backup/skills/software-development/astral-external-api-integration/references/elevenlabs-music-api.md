# ElevenLabs Music API

## Endpoint

```
POST https://api.elevenlabs.io/v1/music/compose
```

## Authentication

```
xi-api-key: <API_KEY>
```

## Request

```json
{
  "prompt": "Astrological music composition in D Mixolydian, 89 BPM...",
  "duration_seconds": 60,
  "output_format": "mp3_44100_128"
}
```

## Response

- 200: binary audio (MP3)
- 400: invalid request
- 401: invalid API key
- 429: rate limit

## Output formats

- `mp3_44100_128` (default)
- `mp3_44100_192`
- `wav_44100`
- `flac_44100`

## Prompt structure (Astral convention)

```
Astrological music composition in <KEY> <MODE>, <BPM> BPM.
Mood: <ELEMENT_MOOD>. Rhythm: <QUALITY_RHYTHM>.
Key layers: <PLANET> as <TIMBRE> in <NOTE> (<REGISTER>); ...
Harmonic relationships: <P1>-<P2>: <HARMONY>; ...
Sun in <SIGN> gives the core melodic identity.
Moon in <SIGN> shapes the emotional undertone.
Ascendant in <SIGN> sets the opening atmosphere.
Duration: 60 seconds, cinematic arc from intro through development to resolution.
```

## Mapping tables

### Signs → Notes

| Sign | Note |
|------|------|
| Aries | C |
| Taurus | D |
| Gemini | E |
| Cancer | F |
| Leo | G |
| Virgo | A |
| Libra | B |
| Scorpio | C# |
| Sagittarius | D# |
| Capricorn | F# |
| Aquarius | G# |
| Pisces | A# |

### Signs → Modes

| Sign | Mode |
|------|------|
| Aries | Lydian |
| Taurus | Mixolydian |
| Gemini | Dorian |
| Cancer | Aeolian |
| Leo | Ionian |
| Virgo | Phrygian |
| Libra | Lydian |
| Scorpio | Locrian |
| Sagittarius | Mixolydian |
| Capricorn | Dorian |
| Aquarius | Aeolian |
| Pisces | Phrygian |

### Planets → Tempo (BPM offset)

| Planet | BPM |
|--------|-----|
| Sun | 0 |
| Moon | -5 |
| Mercury | +10 |
| Venus | -8 |
| Mars | +20 |
| Jupiter | -3 |
| Saturn | -15 |
| Uranus | +15 |
| Neptune | -10 |
| Pluto | -20 |
| ASC | +5 |
| MC | +8 |

### Planets → Timbre

| Planet | Timbre |
|--------|--------|
| Sun | bright brass, golden pad |
| Moon | ethereal choir, soft strings |
| Mercury | pizzicato strings, glockenspiel |
| Venus | warm pad, nylon guitar |
| Mars | distorted drums, aggressive synth |
| Jupiter | orchestral brass, cathedral organ |
| Saturn | deep bass, slow cello |
| Uranus | electric synth, glitch |
| Neptune | ambient pad, reverb wash |
| Pluto | sub bass, dark drone |
| ASC | opening motif, piano |
| MC | climactic brass, timpani |

### Houses → Register

| House | Register |
|-------|----------|
| 1 | mid-range, personal |
| 2 | low-mid, warm |
| 3 | mid, conversational |
| 4 | low, foundational |
| 5 | mid-high, expressive |
| 6 | mid, detailed |
| 7 | high-mid, relational |
| 8 | low, intense |
| 9 | high, expansive |
| 10 | very high, prominent |
| 11 | high, ethereal |
| 12 | very low, subliminal |

### Aspects → Harmony

| Aspect | Harmony |
|--------|---------|
| conjunction | unison, merged timbre |
| sextile | major third, gentle harmony |
| square | tritone, dissonant tension |
| trine | perfect fifth, flowing harmony |
| opposition | octave apart, call and response |
| quincunx | minor second, unsettled |
| semi-sextile | subtle chromatic shift |
| semi-square | mild friction, syncopation |
| sesquiquadrate | complex polyrhythm |
| quintile | sparkling high harmonics |
| bi-quintile | crystalline overtones |

### Elements → Mood

| Element | Mood |
|---------|------|
| Fire | energetic, passionate, driving |
| Earth | grounded, steady, organic |
| Air | light, airy, intellectual |
| Water | flowing, emotional, deep |

### Qualities → Rhythm

| Quality | Rhythm |
|---------|--------|
| Cardinal | strong downbeat, initiating pulse |
| Fixed | steady ostinato, persistent groove |
| Mutable | syncopated, shifting meter |
