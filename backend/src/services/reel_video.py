"""Reel video automation — narration -> TTS audio -> MP4 video assembly.

Pipeline: reel_reading.py narrative → per-slide PNG (Pillow) → TTS mp3
(provider-agnostic via tts config) → ffmpeg concat to vertical 1080x1920.

ffmpeg required on PATH (bundled check); graceful degradation: if ffmpeg
or Pillow missing, returns script+audio plan without video.
"""
from __future__ import annotations

import os
import shutil
import subprocess
from pathlib import Path

from src.services.reel_reading import reel_reading

W, H = 1080, 1920


def _check_ffmpeg() -> str | None:
    return shutil.which("ffmpeg")


def build_reel_script(name: str, spread: str = "single",
                      seed=None, lang: str = "th") -> dict:
    """Step 1: narration beats as slide list."""
    r = reel_reading(name, spread=spread, seed=seed)
    narr = r["narrative"].get(lang) or r["narrative"]["th"]
    cards = []
    for c in r["cards"]:
        cards.append({
            "card": c["card"],
            "position": c["position"],
            "orientation": c.get("orientation", "upright"),
            "image_url": c.get("image_url"),
        })
    # split narration into slides by lines/paragraphs
    slides = [s.strip() for s in narr.split("\n") if s.strip()]
    if not slides:
        slides = [narr]
    return {
        "system": "reel-video-script",
        "lang": lang,
        "slides": slides,
        "cards": cards,
        "hook": slides[0][:60],
    }


def render_slides(script: dict, out_dir: str,
                  bg_color: tuple = (26, 11, 46),
                  accent: tuple = (255, 152, 0)) -> list[str]:
    """Step 2: render each slide to PNG with Pillow. Returns paths."""
    try:
        from PIL import Image, ImageDraw, ImageFont
    except ImportError:
        raise RuntimeError("Pillow not installed")

    os.makedirs(out_dir, exist_ok=True)
    font_path = None
    _asset_font = Path(__file__).resolve().parents[2] / "assets" / "fonts"
    candidates = [
        str(_asset_font / "Sarabun-Bold.ttf"),
        str(_asset_font / "Sarabun-Regular.ttf"),
        "C:/Windows/Fonts/tahoma.ttf",
    ]
    for cand in candidates:
        if Path(cand).exists():
            font_path = cand
            break

    def font(size):
        if font_path:
            return ImageFont.truetype(font_path, size)
        return ImageFont.load_default()

    paths = []
    for i, text in enumerate(script["slides"]):
        img = Image.new("RGB", (W, H), bg_color)
        d = ImageDraw.Draw(img)

        # accent bar
        d.rounded_rectangle([40, 40, W - 40, 52], radius=6,
                            fill=accent)

        # card name big at top
        if i < len(script["cards"]):
            d.text((W // 2, 220), script["cards"][i]["card"],
                   font=font(72), fill=(255, 255, 255), anchor="mm")

        # wrap text manually ~22 chars Thai
        wrapped = ""
        line = ""
        for ch in text:
            line += ch
            if len(line) >= 24 or ch == "\n":
                wrapped += line + "\n"
                line = ""
        wrapped += line

        d.multiline_text((W // 2, H // 2 + 100), wrapped.strip(),
                         font=font(56), fill=(240, 240, 245),
                         anchor="ma", spacing=28, align="center")

        # page dots
        for k in range(len(script["slides"])):
            x = W // 2 - (len(script["slides"]) * 30) // 2 + k * 30
            color = accent if k == i else (90, 80, 120)
            d.ellipse([x, H - 140, x + 18, H - 122], fill=color)

        p = os.path.join(out_dir, f"slide_{i:02d}.png")
        img.save(p)
        paths.append(p)
    return paths


def assemble_video(slide_paths: list[str], audio_paths: list[str] | None,
                   out_path: str, seconds_per_slide: float = 3.5) -> str | None:
    """Step 3+4: concat slides (+ optional audio) into MP4 via ffmpeg.

    Returns output path, or None if ffmpeg unavailable.
    """
    ff = _check_ffmpeg()
    if not ff:
        return None

    work = os.path.dirname(out_path) or "."
    list_file = os.path.join(work, "_reel_concat.txt")
    has_audio = bool(audio_paths) and len(audio_paths) == len(slide_paths)

    with open(list_file, "w", encoding="utf-8") as f:
        for i, sp in enumerate(slide_paths):
            dur = seconds_per_slide
            if has_audio:
                try:
                    probe = subprocess.run(
                        ["ffprobe", "-v", "quiet", "-show_entries",
                         "format=duration", "-of",
                         "csv=p=0", audio_paths[i]],
                        capture_output=True, text=True, timeout=20)
                    dur = max(float(probe.stdout.strip()), 1.5)
                except Exception:
                    pass
            f.write(f"file '{sp}'\nduration {dur}\n")
        f.write(f"file '{slide_paths[-1]}'\n")  # concat quirk: last file twice

    cmd = [ff, "-y", "-f", "concat", "-safe", "0", "-i", list_file]
    if has_audio:
        # concat audios into one track first
        alist = os.path.join(work, "_reel_audio.txt")
        with open(alist, "w", encoding="utf-8") as f:
            for a in audio_paths:
                f.write(f"file '{a}'\n")
        merged = os.path.join(work, "_reel_audio.m4a")
        subprocess.run([ff, "-y", "-f", "concat", "-safe", "0",
                        "-i", alist, "-c", "copy", merged],
                       capture_output=True, timeout=60)
        cmd += ["-i", merged, "-shortest"]
    cmd += [
        "-vf", f"scale={W}:{H}:force_original_aspect_ratio=decrease,"
               f"pad={W}:{H}:(ow-iw)/2:(oh-ih)/2",
        "-r", "30", "-pix_fmt", "yuv420p",
        "-c:v", "libx264", "-preset", "fast",
    ]
    if has_audio:
        cmd += ["-c:a", "aac", "-b:a", "128k"]
    cmd.append(out_path)

    subprocess.run(cmd, capture_output=True, timeout=300)
    try:
        os.remove(list_file)
    except OSError:
        pass
    return out_path if os.path.exists(out_path) else None


def generate_reel(name: str, out_dir: str, spread: str = "single",
                  seed=None, lang: str = "th",
                  tts_fn=None) -> dict:
    """Full pipeline entry. tts_fn(text)->mp3path is injected by caller.

    Returns dict describing produced artifacts.
    """
    script = build_reel_script(name, spread, seed, lang)
    slides_dir = os.path.join(out_dir, "slides")
    slide_paths = render_slides(script, slides_dir)

    audio_paths = None
    if tts_fn is not None:
        audio_paths = []
        adir = os.path.join(out_dir, "audio")
        os.makedirs(adir, exist_ok=True)
        for i, text in enumerate(script["slides"]):
            try:
                ap = tts_fn(text[:800])   # provider cap guard
                audio_paths.append(ap)
            except Exception:
                audio_paths = None
                break

    out_video = os.path.join(out_dir, f"astral_reel_{name or 'draw'}.mp4")
    video = assemble_video(slide_paths, audio_paths, out_video)

    ok = video and os.path.exists(video) and \
        os.path.getsize(video) > 10_000
    th = ("สร้างรีลเสร็จแล้ว — เปิดดูได้เลย" if ok else
          "ทำสคริปต์+สไลด์เสร็จ แต่ยังไม่ได้ไฟล์วิดีโอ "
          "(ต้องมี ffmpeg บนเครื่อง)")
    en = ("Reel rendered." if ok else
          "Script+slides ready; video requires ffmpeg.")

    return {
        "system": "reel-video-pipeline",
        "script": script,
        "slides": len(slide_paths),
        "video_path": video if ok else None,
        "has_audio": bool(audio_paths),
        "interpretation": {"th": th, "en": en},
    }
