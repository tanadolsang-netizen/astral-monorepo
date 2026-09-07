from playwright.sync_api import sync_playwright
import json, statistics

URL = "http://localhost:4193/"
OUT = "D:/AI/Astral/landing/_audit_app_result.txt"

def main():
    lines = []
    with sync_playwright() as p:
        b = p.chromium.launch(args=[
            "--use-gl=swiftshader", "--ignore-gpu-blocklist",
            "--enable-unsafe-swiftshader", "--enable-webgl"
        ])
        ctx = b.new_context(viewport={"width": 1366, "height": 900})
        pg = ctx.new_page()

        console_errors = []
        page_errors = []
        pg.on("console", lambda m: console_errors.append(f"{m.type}: {m.text}") if m.type in ("error", "warning") else None)
        pg.on("pageerror", lambda e: page_errors.append(str(e)))

        pg.goto(URL, wait_until="load")
        # รอ intro + loader จบ
        pg.wait_for_timeout(4500)

        # วัด FPS 60 วินาที (3600 frames) ผ่าน requestAnimationFrame
        fps = pg.evaluate("""() => new Promise(res => {
            let frames = 0, start = performance.now();
            function loop(t){
                frames++;
                if (t - start < 6000) requestAnimationFrame(loop);
                else res(Math.round(frames / ((t - start)/1000)));
            }
            requestAnimationFrame(loop);
        })""")

        # ทดสอบ interaction: คลิกโหนดวงโคจร (ตรงกลางล่าง) + สลับ view ผ่าน nav
        try:
            # คลิกตรงกลางล่าง (จุดที่โหนดโคจรผ่าน) เพื่อทดสอบ orbit interaction
            box = pg.viewport_size
            pg.mouse.click(int(box["width"]*0.5), int(box["height"]*0.72))
            pg.wait_for_timeout(1500)
            # ปิด panel ถ้ามี
            try: pg.click(".orbit-close", timeout=1500)
            except: pass
            pg.click("text=ดวงชะตา", timeout=3000)
            pg.wait_for_timeout(2500)
            pg.click("text=หน้าแรก", timeout=3000)
            pg.wait_for_timeout(2500)
        except Exception as e:
            lines.append(f"INTERACTION ERR: {e}")

        # วัด FPS รอบ 2 หลัง interaction
        fps2 = pg.evaluate("""() => new Promise(res => {
            let frames = 0, start = performance.now();
            function loop(t){
                frames++;
                if (t - start < 4000) requestAnimationFrame(loop);
                else res(Math.round(frames / ((t - start)/1000)));
            }
            requestAnimationFrame(loop);
        })""")

        # จำนวน WebGL contexts / canvas
        canvases = pg.evaluate("() => document.querySelectorAll('canvas').length")

        lines.append(f"FPS (idle, 6s): {fps}")
        lines.append(f"FPS (after interaction, 4s): {fps2}")
        lines.append(f"canvas count: {canvases}")
        lines.append(f"console errors/warnings: {len(console_errors)}")
        for e in console_errors[:15]:
            lines.append(f"  - {e}")
        lines.append(f"page errors: {len(page_errors)}")
        for e in page_errors[:15]:
            lines.append(f"  - {e}")

        b.close()

    report = "\n".join(lines)
    with open(OUT, "w", encoding="utf-8") as f:
        f.write(report)
    print(report)

if __name__ == "__main__":
    main()
