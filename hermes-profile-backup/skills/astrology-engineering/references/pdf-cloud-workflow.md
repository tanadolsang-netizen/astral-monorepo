# PDF Generation + Cloud Upload Workflow (verified 2026-08-22)

## Dependencies
```bash
python -m pip install fpdf2
```

## Windows Font Strategy
- Use **Calibri** (built-in on Windows) via fpdf2 Unicode support
- Font files: `C:/Windows/Fonts/calibri.ttf`, `calibrib.ttf`, `calibrii.ttf`, `calibriz.ttf`
- Register with `pdf.add_font('Calibri', '', 'C:/Windows/Fonts/calibri.ttf')` (no `uni=True` in fpdf2 >=2.5)
- Set explicit margins: `pdf.set_left_margin(15); pdf.set_right_margin(15)`
- Compute usable width: `w = pdf.w - pdf.l_margin - pdf.r_margin`; pass to `multi_cell(w, ...)`

## Markdown → PDF Conversion (minimal)
```python
from fpdf import FPDF

pdf = FPDF()
pdf.add_page()
pdf.set_auto_page_break(auto=True, margin=20)
pdf.set_left_margin(15)
pdf.set_right_margin(15)

pdf.add_font('Calibri', '', 'C:/Windows/Fonts/calibri.ttf')
pdf.add_font('Calibri', 'B', 'C:/Windows/Fonts/calibrib.ttf')

w = pdf.w - pdf.l_margin - pdf.r_margin

for line in md_content.split('\n'):
    # Sanitize unicode chars Calibri may lack
    line = line.replace('\u2212', '-').replace('\u2013', '-').replace('\u2014', '-')
    
    if line.startswith('# '):
        pdf.set_font('Calibri', 'B', 14)
        pdf.ln(4)
        pdf.multi_cell(w, 8, line[2:])
    elif line.startswith('## '):
        pdf.set_font('Calibri', 'B', 12)
        pdf.ln(3)
        pdf.multi_cell(w, 7, line[3:])
    elif line.startswith('### '):
        pdf.set_font('Calibri', 'B', 11)
        pdf.ln(2)
        pdf.multi_cell(w, 6, line[4:])
    elif line.startswith('|') and '|' in line[1:]:
        continue  # skip tables
    elif line.strip() == '':
        pdf.ln(3)
    else:
        pdf.set_font('Calibri', '', 10)
        pdf.multi_cell(w, 5, line)

pdf.output('output.pdf')
```

## Cloud Upload (tmpfiles.org)
```bash
curl -s -F "file=@output.pdf" https://tmpfiles.org/api/v1/upload
# Response: {"status":"success","data":{"url":"https://tmpfiles.org/<id>/output.pdf"}}
# Direct download: https://tmpfiles.org/dl/<id>/output.pdf
# Expires ~7 days. No auth required. Works for PDF/MD/TXT.
```

## Verified Run (Malang 1999-04-29)
- API server: `uvicorn src.main:app --port 8001` (background)
- POST `/v1/natal/compute` with tropical + sidereal
- Markdown reading → PDF → tmpfiles.org → shareable link
- Total pipeline: ~2 min end-to-end