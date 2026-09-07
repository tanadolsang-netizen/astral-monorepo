import pypdf
r = pypdf.PdfReader(r"C:/AI/reports/astral-natal-nai-thai.pdf")
print("pages:", len(r.pages))
txt = "\n".join((p.extract_text() or "") for p in r.pages)
for kw in ["soul contract", "AI agency", "กรงกรรม", "Saturn Return", "ดาว"]:
    print(f"{kw!r}: {txt.count(kw)}")
