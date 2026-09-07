import pypdf

r = pypdf.PdfReader(r"C:/AI/reports/astral-couple-nai-mai-thai.pdf")
txt = "\n".join((p.extract_text() or "") for p in r.pages)
# show context around a real-life keyword
for kw in ["AI agency", "กรงกรรม", "ดาว", "พฤษภ"]:
    i = txt.find(kw)
    print(f"\n===== context around {kw!r} =====")
    print(txt[max(0,i-120):i+200] if i >= 0 else "NOT FOUND")
