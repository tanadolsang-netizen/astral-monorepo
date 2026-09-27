"""The disclaimer every reading endpoint returns.

Each file under raw/ already ends with this caveat, but until now it never
crossed the API boundary — clients had no way to surface it. Keeping it in
one constant means the wording can't drift between endpoints.
"""

CAVEAT_EN = (
    "For reflection and entertainment; not medical, legal, or financial advice."
)

CAVEAT_TH = (
    "เพื่อการไตร่ตรองและความบันเทิงเท่านั้น "
    "ไม่ใช่คำแนะนำทางการแพทย์ กฎหมาย หรือการเงิน"
)

CAVEAT = f"{CAVEAT_TH} / {CAVEAT_EN}"
