from playwright.sync_api import sync_playwright
URL="file:///D:/AI/Astral/landing/astral-spa.html"
errs=[]
with sync_playwright() as p:
    b=p.chromium.launch(args=["--use-gl=swiftshader","--ignore-gpu-blocklist","--enable-unsafe-swiftshader"])
    pg=b.new_context(viewport={"width":1366,"height":900}).new_page()
    pg.on("pageerror",lambda e:errs.append("PAGEERR:"+str(e)))
    pg.on("console",lambda m:errs.append("ERR:"+m.text) if m.type=="error" else None)
    pg.goto(URL,wait_until="load")
    # จับช่วง warp (~3.2s) กับ landing (~5s)
    pg.wait_for_timeout(3200)
    warp=pg.evaluate("()=>document.body.classList.contains('warp')")
    cloudsBlur=pg.evaluate("()=>getComputedStyle(document.getElementById('clouds')).filter")
    pg.screenshot(path="D:/AI/Astral/landing/_warp.png")
    pg.wait_for_timeout(2000)
    loaderGone=pg.evaluate("()=>!document.getElementById('loader')")
    warpGone=pg.evaluate("()=>!document.body.classList.contains('warp')")
    wrapVisible=pg.evaluate("()=>{const w=document.querySelector('.wrap');return w?getComputedStyle(w).opacity:'none';}")
    pg.screenshot(path="D:/AI/Astral/landing/_landing.png")
    print("warp@3.2s:",warp,"| clouds filter:",cloudsBlur)
    print("loaderGone@5s:",loaderGone,"| warpGone:",warpGone,"| wrap opacity:",wrapVisible)
    print("ERRORS:",len(errs)); [print(" ✗",e[:120]) for e in errs[:8]]
    b.close()
