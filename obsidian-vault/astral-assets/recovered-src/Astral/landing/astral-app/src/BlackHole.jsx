import { useRef, useEffect } from 'react'

/*
  Black Hole transition (originkit "blackhole" clone):
  orbiting particles + simulated gravity inflow + glowing event horizon
  ใช้เป็น Enter transition เมื่อกดเมนู → ซูมเข้าหลุมดำ ดูดกลืน แล้วสลับ view
*/

export default function BlackHole({ active, onDone, duration = 1100 }) {
  const cvRef = useRef()
  const raf = useRef()
  const doneRef = useRef(false)

  useEffect(() => {
    if (!active) return
    const cv = cvRef.current
    if (!cv) return
    const ctx = cv.getContext('2d')
    let W, H, cx, cy
    const dpr = Math.min(2, window.devicePixelRatio || 1)
    function resize() {
      W = cv.width = innerWidth * dpr
      H = cv.height = innerHeight * dpr
      cx = W / 2; cy = H / 2
    }
    resize()
    addEventListener('resize', resize)

    const N = 520
    const parts = Array.from({ length: N }, () => {
      const a = Math.random() * Math.PI * 2
      const r = (0.25 + Math.random() * 0.9) * Math.min(W, H)
      return { a, r, sp: 0.4 + Math.random() * 1.2, sz: (Math.random() * 1.5 + 0.6) * dpr,
        hue: Math.random() < 0.4 ? '#ffe9b0' : Math.random() < 0.7 ? '#c9a84c' : '#7a6aff' }
    })
    const t0 = performance.now()
    doneRef.current = false

    function frame(now) {
      const t = (now - t0) / duration       // 0..1
      const ease = t * t                      // เร่งเข้าหาลูก
      ctx.clearRect(0, 0, W, H)
      ctx.fillStyle = 'rgba(5,3,12,' + (0.15 + ease * 0.7) + ')'
      ctx.fillRect(0, 0, W, H)
      // event horizon (หลุมดำ) ใหญ่ขึ้นตามเวลา
      const bh = (0.02 + ease * 0.42) * Math.min(W, H)
      // accretion glow
      const g = ctx.createRadialGradient(cx, cy, bh * 0.7, cx, cy, bh * 2.2)
      g.addColorStop(0, 'rgba(255,220,150,0)')
      g.addColorStop(0.6, 'rgba(201,168,76,' + (0.5 * (1 - t)) + ')')
      g.addColorStop(1, 'rgba(122,106,255,0)')
      ctx.fillStyle = g
      ctx.beginPath(); ctx.arc(cx, cy, bh * 2.2, 0, 7); ctx.fill()
      // อนุภาคโคจร + ดูดเข้าหาลูก
      for (const p of parts) {
        p.a += p.sp * 0.02 * (1 + ease * 3)
        const rr = p.r * (1 - ease * 0.92)     // หดเข้าหาลูก
        const x = cx + Math.cos(p.a) * rr
        const y = cy + Math.sin(p.a) * rr * 0.62
        ctx.globalAlpha = 1 - t * 0.3
        ctx.fillStyle = p.hue
        ctx.beginPath(); ctx.arc(x, y, p.sz * (1 - ease * 0.5), 0, 7); ctx.fill()
      }
      ctx.globalAlpha = 1
      // ดำกลาง
      ctx.fillStyle = '#05030c'
      ctx.beginPath(); ctx.arc(cx, cy, bh, 0, 7); ctx.fill()

      if (t >= 1) {
        if (!doneRef.current) { doneRef.current = true; onDone && onDone() }
        return
      }
      raf.current = requestAnimationFrame(frame)
    }
    raf.current = requestAnimationFrame(frame)
    return () => { cancelAnimationFrame(raf.current); removeEventListener('resize', resize) }
  }, [active, duration, onDone])

  if (!active) return null
  return <canvas ref={cvRef} style={{ position: 'fixed', inset: 0, zIndex: 80, pointerEvents: 'none' }} />
}
