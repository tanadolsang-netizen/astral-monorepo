from playwright.sync_api import sync_playwright

URL = "http://localhost:4193/"

with sync_playwright() as p:
    b = p.chromium.launch(args=["--use-gl=swiftshader","--ignore-gpu-blocklist","--enable-unsafe-swiftshader"])
    pg = b.new_context(viewport={"width":1366,"height":900}).new_page()
    errs = []
    pg.on("pageerror", lambda e: errs.append(str(e)))
    pg.on("console", lambda m: errs.append(f"{m.type}: {m.text}") if m.type=="error" else None)
    pg.goto(URL, wait_until="load")
    pg.wait_for_timeout(4500)  # รอ intro จบ

    # เข้า view natal ผ่าน nav button (มี black hole transition → รอ)
    pg.click(".navlinks button:has-text('ดวงชะตา')", timeout=5000)
    pg.wait_for_timeout(3500)  # รอ black hole + view active

    # debug: เช็คว่า view natal active
    vstate = pg.evaluate("""() => {
        const secs=[...document.querySelectorAll('section.view')];
        const natal=secs.find(s=>s.querySelector('#n-name'));
        return natal? natal.className : 'NO_NATAL_SECTION';
    }""")
    print("natal section class:", vstate)

    # กรอกฟอร์ม (ต้องโผล่ก่อน)
    pg.wait_for_selector("#n-name:visible", timeout=8000)
    pg.fill("#n-name", "Mark")
    pg.fill("#n-date", "1997-05-19")
    pg.fill("#n-time", "05:45")
    pg.select_option("#n-prov", "13.3633,100.9868")
    pg.select_option("#n-sys", "tropical")

    # กดดูดวงชะตา
    pg.click("button.btn.primary:has-text('ดูดวงชะตา')", timeout=5000)
    pg.wait_for_timeout(2500)

    # เช็คผลลัพธ์
    html = pg.evaluate("() => { const r=document.getElementById('r-natal'); return r? r.innerHTML : 'NO_BOX'; }")
    has_tbl = "chart-tbl" in html
    has_asc = "ASC" in html and "พฤษภ" in html
    print("natal box rendered:", "YES" if html and "NO_BOX" not in html else "NO")
    print("chart table present:", has_tbl)
    print("ASC Taurus present:", has_asc)
    print("page errors:", len(errs))
    for e in errs[:8]: print("  -", e)

    b.close()
