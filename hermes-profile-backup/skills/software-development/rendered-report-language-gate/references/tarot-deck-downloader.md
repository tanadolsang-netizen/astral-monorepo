# Tarot Deck Downloader Reference

## Pattern: optional background downloader for card image assets

Use when: real tarot card visuals are desired but assets are not vendored in the repo.

## Implementation

- Create `src/services/tarot_downloader.py`
- Use `ensure_deck_ready(background=True)` to trigger download without blocking PDF generation
- Store images in `assets/tarot/sola-busca/`
- Use `get_card_path(card_name)` fallback when images are missing
- Major Arcana filenames: `00.jpg` through `21.jpg`

## Sources tried

- Wikimedia Sola Busca tarot cards via `https://upload.wikimedia.org/wikipedia/commons/...`
- Internet Archive `https://archive.org/download/rider-waite-tarot/4K/`

## Known failures

- Wikimedia HTML index may not return machine-readable file list; fallback to direct URL construction
- Archive.org may return 404/HTML instead of directory listing
- Network failures must not block PDF generation; always degrade to text-only fallback

## CLI smoke test

```bash
uv run python -c "from src.services.tarot_downloader import ensure_deck_ready; ensure_deck_ready(); import os; print('downloaded:', os.listdir('assets/tarot/sola-busca'))"
```
