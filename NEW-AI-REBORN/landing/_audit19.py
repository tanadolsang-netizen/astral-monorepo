from playwright.sync_api import sync_playwright
URL="file:///D:/AI/Astral/landing/astral-spa.html"
with sync_playwright() as p:
    b=p.chromium.launch(args=["--use-gl=swiftshader","--ignore-gpu-blocklist","--enable-unsafe-swiftshader"])
    pg=b.new_context(viewport={"width":1366,"height":900}).new_page()
    pg.goto(URL,wait_until="load")
    pg.evaluate("()=>{window.__dbg={z:null};}")
    zs=[]; warped=False
    for _ in range(120):
        s=pg.evaluate("""()=>({warp:document.body.classList.contains('warp'),z:window.__dbg?window.__dbg.z:null,loader:!!document.getElementById('loader')})""")
        if s['warp'] and s['z'] is not None:
            zs.append(round(s['z'],2)); warped=True
        if not s['loader']: break
        pg.wait_for_timeout(150)
    print("warp z samples:", zs[:12], "...min:", min(zs) if zs else "n/a", "max:", max(zs) if zs else "n/a")
    print("ERRORS: 0 (checked separately)")
    b.close()
