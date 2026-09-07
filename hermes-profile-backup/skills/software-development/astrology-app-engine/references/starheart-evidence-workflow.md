# STARHEART evidence workflow (reel transcription + clip↔chart matching)

Recipe used 2026-08-31 to prove reel readings reflect real charts (coarse↔fine).

## 1. Transcribe IG reels → text

Whisper is NOT importable via plain `uv run python` even after `uv pip install openai-whisper` (interpreter mismatch). Use the `--with` flag instead:

```bash
cd C:/AI/NEW-AI-REBORN
uv run --with openai-whisper python transcribe_script.py
```

ffmpeg is available at the WinGet path:
`C:/Users/ADMIN/AppData/Local/Microsoft/WinGet/Packages/Gyan.FFmpeg_Microsoft.Winget.Source_8wekyb3d8bbwe/ffmpeg-9.0-full_build/bin/ffmpeg`

Extract audio (16kHz mono wav):
```bash
ffmpeg -y -i clip.mp4 -vn -ac 1 -ar 16000 -f wav out.wav
```

Transcribe (auto language detect; Thai+English reels both detected as `en` text but content is fine):
```python
import whisper
m = whisper.load_model('base')
r = m.transcribe('out.wav', language=None, task='transcribe')
open('out.txt','w',encoding='utf-8').write(r['text'])
```

**BUG FIX (hit this session):** `glob.glob(...)` returns **str**, not Path. Do NOT call `.read_text()` on the result — use `open(t, encoding='utf-8').read()`. A combine step that did `for t in glob.glob(...): all_txt[t.stem] = t.read_text(...)` crashed with `AttributeError: 'str' object has no attribute 'read_text'`. Fix: `all_txt[pathlib.Path(t).stem] = open(t, encoding='utf-8').read()`.

## 2. Match clips ↔ chart (coarse↔fine)

```python
from src.services.chart_service import compute_chart
from src.services import starheart_map as sh
from datetime import date, time
ca = compute_chart('นาย', date(1997,5,19), time(5,45), tz_offset_hours=7.0, lat=13.3611, lon=100.9836)
spread = sh.MAP(ca)   # deterministic — same chart ⇒ identical every run
for c in spread:
    print(c['card'], c['orientation'], '|', c['feature_source'])
```

Each card carries `feature_source` (which planet/house/aspect generated it). Match each reel clip's theme to a `feature_source` and tally a hit-rate %. The 14-clip IG evidence set lives at `C:/AI/workspace-scratch/reels_text/_ALL_TRANSCRIPTS.json` (25,853 chars) and charts at `C:/AI/workspace-scratch/charts_nai_mai.json`.

## 3. Prospective proof

```python
from src.services import prediction_log as pl
pl.pre_register(chart, claim_text, expected_event)  # created_at must precede expected_event
```
Store at `C:/AI/NEW-AI-REBORN/data/prediction_log.json`. Run `hit_rate_audit` later to compute survivorship-safe accuracy per `mechanism_tag`.
