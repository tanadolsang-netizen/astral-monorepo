import { useState, useEffect, useRef } from 'react'

const VIEWS = ['home', 'natal', 'tarot', 'synastry', 'vedic', 'horary', 'ai-reading', 'life']

const NAV_LABELS = {
  'home': 'หน้าแรก',
  'natal': 'ดูดวงชะตา',
  'tarot': 'ไพ่ทาโรต์',
  'synastry': 'ดูคู่',
  'vedic': 'เวดิก',
  'horary': 'ถามดวง',
  'ai-reading': 'AI อ่านดวง',
  'life': 'ชีวิตคุณ',
}

const S = {
  hero: {
    pill: '✦ โหราศาสตร์ครบวงจร',
    title1: 'ดาวแต่ละดวง',
    title2: 'เลือกทาง',
    title3: 'เอง',
    title4: 'ให้คุณ',
    description: 'วันที่คุณลืมตามาเกิด ดาวแต่ละดวงจัดเรียงตัวเองให้พอดีจนคุณได้เห็น — มาค้นหาว่าท้องฟ้ากำลังจะบอกอะไรคุณ',
    cta: 'ดูดวงชะตาของคุณ',
  },
  sections: {
    tarot: {
      eyebrow: '🔮 ไพ่ทาโรต์',
      title: 'ไพ่เปิด',
      titleAccent: 'เส้นทาง',
      desc: 'สับไพ่แล้วให้ไพ่ตอบคำถามที่คุณอยากรู้',
      cta: 'เปิดไพ่',
    },
    synastry: {
      eyebrow: '💞 ดูคู่',
      title: 'สองดวง',
      titleAccent: 'เดินด้วยกัน',
      desc: 'เปรียบเทียบดวงชะตาสองคน ดูว่าเราเข้ากันได้แค่ไหน',
      cta: 'ดูคู่',
    },
    vedic: {
      eyebrow: '🪐 เวดิก',
      title: 'โหราศาสตร์',
      titleAccent: 'อินเดียโบราณ',
      desc: 'Nakshatra, Dasha, Yoga — ภาษาของดาวแบบอินเดีย',
      cta: 'ดูดวงเวดิก',
    },
  },
}

const callApi = async (url, body) => {
  const res = await fetch(url, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(body),
  })
  return res.json()
}

const Loading = () => <div style={{
  display: 'inline-flex', alignItems: 'center', gap: '10px',
  fontSize: '14px', color: 'var(--gold)', padding: '20px 0',
}}>
  <span style={{
    width: '18px', height: '18px',
    border: '2px solid var(--gold-soft)',
    borderTopColor: 'var(--gold)',
    borderRadius: '50%',
    display: 'inline-block',
  }} />
  กำลังคำนวณ...
</div>

// HTML escape helper — use before injecting any user/server data into innerHTML
const escapeHtml = (str) => {
  if (str == null) return ''
  return String(str)
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;')
    .replace(/'/g, '&#39;')
}

export default function App() {
  const [view, setView] = useState('home')
  const [navScrolled, setNavScrolled] = useState(false)
  const [loading, setLoading] = useState(false)
  const mainRef = useRef(null)

  useEffect(() => {
    const handleScroll = () => setNavScrolled(window.scrollY > 40)
    window.addEventListener('scroll', handleScroll)
    return () => window.removeEventListener('scroll', handleScroll)
  }, [])

  const goView = (name) => {
    if (!VIEWS.includes(name)) return
    setView(name)
    window.scrollTo({ top: 0, behavior: 'smooth' })
  }

<<<<<<< Updated upstream
=======
  const onBhDone = useCallback(() => {
    if (warpDone.current) return
    warpDone.current = true
    setView(pendingView.current)
    window.scrollTo(0, 0)
    setBh(false)
  }, [])

  // ดูดวงชะตาจริงผ่าน /v1/natal/compute (JSON) — render ตารางดาว + wheel
  const [natalChart, setNatalChart] = useState(null)
  const onNatal = useCallback(async () => {
    const box = document.getElementById('r-natal')
    const name = document.getElementById('n-name').value || 'คุณ'
    const date = document.getElementById('n-date').value
    const time = document.getElementById('n-time').value || '00:00:00'
    const prov = document.getElementById('n-prov').value.split(',')
    const sys = document.getElementById('n-sys').value
    if (!date) { box.classList.add('show'); box.innerHTML = '❌ กรุณาระบุวันเกิด'; setNatalChart(null); return }
    box.classList.add('show'); box.innerHTML = '⏳ กำลังคำนวณดวงชะตาให้ท่าน...'
    try {
      const res = await fetch('http://127.0.0.1:8000/v1/natal/compute', {
        method: 'POST', headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          name, date, time: time.length <= 5 ? time + ':00' : time,
          tz_offset_hours: 7, lat: +prov[0], lon: +prov[1], system: sys
        })
      })
      const d = await res.json()
      if (!res.ok) { box.innerHTML = '❌ ' + (d.detail || res.status); setNatalChart(null); return }
      setNatalChart(d)
      const rows = (d.bodies || []).map(b =>
        `<tr><td>${escapeHtml(b.body)}</td><td>${escapeHtml(b.sign)}</td><td>${b.degree.toFixed(2)}°</td>
         <td>${b.absolute_deg.toFixed(2)}°</td><td>H${b.house ?? '-'}</td></tr>`).join('')
      const asc = d.ascendant || {}
      const els = d.elements || {}
      const elHtml = Object.entries(els).map(([k, v]) =>
        `<span class="el-pill">${escapeHtml(k)} ${typeof v === 'number' ? v.toFixed(0) : escapeHtml(v)}</span>`).join('')
      const ascSign = escapeHtml(asc.sign || '-')
      const ascDeg = (asc.degree||0).toFixed(2)
      const ascAbs = (asc.absolute_deg||0).toFixed(2)
      const caveatHtml = d.caveat ? `<div class="tcaveat">${escapeHtml(d.caveat)}</div>` : ''
      box.innerHTML = `
        <div class="chart-head">🌟 ดวงชะตา <b>${escapeHtml(d.name || name)}</b>
          <span class="chart-sys">${d.system === 'sidereal' ? 'Sidereal' : 'Tropical'}</span></div>
        <table class="chart-tbl"><thead><tr><th>ดาว</th><th>ราศี</th><th>องศา</th><th>Absolute</th><th>บ้าน</th></tr></thead>
          <tbody>${rows}
          <tr class="asc-row"><td>ASC</td><td>${ascSign}</td><td>${ascDeg}°</td><td>${ascAbs}°</td><td>H1</td></tr>
          </tbody></table>
        <div class="el-row">${elHtml}</div>
        ${caveatHtml}`
    } catch (e) { box.innerHTML = '❌ ' + e; setNatalChart(null) }
  }, [])

  // helper ดึงค่าฟอร์มธรรมดา
>>>>>>> Stashed changes
  const gv = (id) => document.getElementById(id)?.value || ''

  // ── Natal Chart ──
  const onNatal = async () => {
    const box = document.getElementById('r-natal')
    if (!box) return
    box.classList.add('show')
    box.innerHTML = '<div class="loading"><span></span>กำลังคำนวณดวงชะตา...</div>'
    setLoading(true)
    try {
<<<<<<< Updated upstream
      const date = gv('n-date')
      if (!date) { box.innerHTML = '<span style="color:#c44">กรุณาระบุวันเกิด</span>'; return }
      const time = (gv('n-time') || '12:00') + ':00'
      const prov = gv('n-prov') || '13.7563,100.5018'
      const [lat, lon] = prov.split(',').map(v => parseFloat(v) || 0)
      const d = await callApi('/v1/natal/compute', {
        name: gv('n-name') || 'คุณ', date, time, tz_offset_hours: 7, lat, lon,
        system: gv('n-sys') || 'tropical'
      })
      if (!d.bodies) { box.innerHTML = `<span style="color:#c44">${d.detail || 'คำนวณไม่สำเร็จ'}</span>`; return }
      const rows = d.bodies.map(b =>
        `<tr><td>${b.body}</td><td>${b.sign}</td><td>${b.degree.toFixed(2)}°</td><td>H${b.house ?? '-'}</td></tr>`
      ).join('')
      const asc = d.ascendant || {}
      box.innerHTML = `<div style="font-family:Cinzel,serif;font-size:18px;color:#2e2818;margin-bottom:12px">
        🌟 ดวงชะตา <b>${d.name}</b>
        <span style="font-size:11px;color:#7a1f2b;border:1px solid var(--gold-soft);border-radius:12px;padding:3px 12px;margin-left:8px">${d.system === 'sidereal' ? 'Sidereal' : 'Tropical'}</span>
      </div>
      <table style="width:100%;border-collapse:collapse;font-size:14px;color:#3b3324">
        <thead><tr><th style="text-align:left;padding:8px;color:var(--gold);border-bottom:1px solid var(--gold-soft)">ดาว</th><th style="text-align:left;padding:8px;color:var(--gold);border-bottom:1px solid var(--gold-soft)">ราศี</th><th style="text-align:left;padding:8px;color:var(--gold);border-bottom:1px solid var(--gold-soft)">องศา</th><th style="text-align:left;padding:8px;color:var(--gold);border-bottom:1px solid var(--gold-soft)">บ้าน</th></tr></thead>
        <tbody>${rows}<tr style="font-weight:700;background:rgba(201,168,76,.08)"><td>ASC</td><td>${asc.sign || '-'}</td><td>${(asc.degree||0).toFixed(2)}°</td><td>H1</td></tr></tbody>
      </table>`
    } catch (e) { box.innerHTML = '❌ ' + e.message }
    setLoading(false)
  }
=======
      const res = await fetch('http://127.0.0.1:8000/v1/synastry/cross-aspects', {
        method: 'POST', headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ a: mk('a'), b: mk('b') }) })
      const d = await res.json()
      if (!res.ok) { box.innerHTML = '❌ ' + (d.detail || res.status); return }
      const ca = d.cross_aspects || []
      const rows = ca.slice(0, 12).map(x =>
        `<tr><td>${escapeHtml(x.body_a)} × ${escapeHtml(x.body_b)}</td><td class="asp-${escapeHtml(x.aspect)}">${escapeHtml(x.aspect)}</td><td>${x.orb?.toFixed(2)}°</td></tr>`).join('')
      const ea = d.elements_a?.dominant, eb = d.elements_b?.dominant
      const aName = escapeHtml(mk('a').name)
      const bName = escapeHtml(mk('b').name)
      const eaStr = escapeHtml(ea || '-')
      const ebStr = escapeHtml(eb || '-')
      const caveatHtml = d.caveat ? `<div class="tcaveat">${escapeHtml(d.caveat)}</div>` : ''
      box.innerHTML = `<div class="chart-head">💞 กระแสสองดวง <b>${aName}</b> × <b>${bName}</b></div>
        <div class="el-row"><span class="el-pill">A dominant: ${eaStr}</span><span class="el-pill">B dominant: ${ebStr}</span></div>
        <table class="chart-tbl"><thead><tr><th>Aspect</th><th>ประเภท</th><th>Orb</th></tr></thead><tbody>${rows}${ca.length>12?`<tr><td colspan="3" style="opacity:.6">…อีก ${ca.length-12} aspects</td></tr>`:''}</tbody></table>
        ${caveatHtml}`
    } catch (e) { box.innerHTML = '❌ ' + e }
  }, [])
>>>>>>> Stashed changes

  // ── Tarot ──
  const onTarot = async () => {
    const box = document.getElementById('r-tarot')
    if (!box) return
    box.classList.add('show')
    box.innerHTML = '<div class="loading"><span></span>ไพ่กำลังถูกสับ...</div>'
    setLoading(true)
    try {
      const d = await callApi('/v1/tarot/draw', {
        name: 'คุณ', question: gv('t-q') || '', spread: 'three_card', lang: 'th',
      })
      if (!d.cards) { box.innerHTML = `<span style="color:#c44">${d.detail || 'ไม่สามารถสับไพ่ได้'}</span>`; return }
      const cards = d.cards.map((c, i) => {
        const nm = (c.card || c.name || '').replace(/ of /g, ' แห่ง ')
        const or = c.orientation === 'reversed' ? ' 🔄' : ''
        return `<div style="background:linear-gradient(135deg,rgba(154,123,52,.15),rgba(201,168,76,.08));border:1px solid var(--gold-soft);border-radius:12px;padding:12px 16px;font-size:14px;color:#0a0712;cursor:pointer;transition:all .3s" onmouseover="this.style.transform='translateY(-4px)'" onmouseout="this.style.transform=''">🃏 ${nm}${or}</div>`
      }).join('')
      const narr = d.narrative || d.reading || ''
      box.innerHTML = `<div style="display:flex;gap:12px;flex-wrap:wrap;margin-bottom:16px">${cards}</div>
      ${narr ? `<p style="line-height:1.9;font-size:15px;color:#3b3324">${narr}</p>` : ''}
      ${d.caveat ? `<div style="margin-top:12px;font-size:12px;opacity:.6;border-top:1px dashed var(--gold-soft);padding-top:12px">${d.caveat}</div>` : ''}`
    } catch (e) { box.innerHTML = '❌ ' + e.message }
    setLoading(false)
  }

  // ── AI Reading ──
  const onAiReading = async () => {
    const box = document.getElementById('r-ai')
    if (!box) return
    box.classList.add('show')
    box.innerHTML = '<div class="loading"><span></span>AI กำลังวิเคราะห์ดวงชะตา...</div>'
    setLoading(true)
    try {
      const date = gv('ai-date')
      if (!date) { box.innerHTML = '<span style="color:#c44">กรุณาระบุวันเกิด</span>'; return }
      const time = (gv('ai-time') || '12:00') + ':00'
      const prov = gv('ai-prov') || '13.7563,100.5018'
      const [lat, lon] = prov.split(',').map(v => parseFloat(v) || 0)
      const d = await callApi('/v1/ai/reading', {
        name: gv('ai-name') || 'คุณ', date, time, tz_offset_hours: 7, lat, lon, system: 'tropical'
      })
      if (!d.sections) { box.innerHTML = `<span style="color:#c44">${d.detail || 'ไม่สามารถสร้าง narrative ได้'}</span>`; return }
      let html = ''
      for (const [section, paras] of Object.entries(d.sections)) {
        if (paras && paras.length) {
          html += `<div style="margin-bottom:20px"><h4 style="font-family:Cinzel,serif;color:#2e2818;margin-bottom:8px">${section}</h4>`
          for (const p of paras) html += `<p style="line-height:1.85;font-size:15px;color:#3b3324;margin-bottom:8px">${p}</p>`
          html += `</div>`
        }
      }
      box.innerHTML = html || '<span style="color:#c44">ไม่สามารถสร้าง narrative ได้</span>'
    } catch (e) { box.innerHTML = '❌ ' + e.message }
    setLoading(false)
  }

  // ── Vedic ──
  const onVedic = async () => {
    const box = document.getElementById('r-vedic')
    if (!box) return
    box.classList.add('show')
    box.innerHTML = '<div class="loading"><span></span>กำลังเลื่อนดาวไปตำแหน่ง sidereal...</div>'
    setLoading(true)
    try {
      const date = gv('v-date')
      if (!date) { box.innerHTML = '<span style="color:#c44">กรุณาระบุวันเกิด</span>'; return }
      const time = (gv('v-time') || '12:00') + ':00'
      const prov = gv('v-prov') || '13.7563,100.5018'
      const [lat, lon] = prov.split(',').map(v => parseFloat(v) || 0)
      const d = await callApi('/v1/vedic/chart', {
        name: gv('v-name') || 'คุณ', birth: { date, time, lat, lon, tz_offset_hours: 7 }
      })
      if (!d.lagna) { box.innerHTML = `<span style="color:#c44">${d.detail || 'คำนวณไม่สำเร็จ'}</span>`; return }
      const nk = d.nakshatra || {}
<<<<<<< Updated upstream
      box.innerHTML = `<div style="font-family:Cinzel,serif;font-size:18px;color:#2e2818;margin-bottom:12px">🪐 ดวงเวดิก <b>${d.person_name}</b></div>
      <div style="display:flex;gap:8px;flex-wrap:wrap;margin-bottom:16px">
        <span style="font-size:12px;background:rgba(154,123,52,.1);border:1px solid var(--gold-soft);border-radius:14px;padding:5px 14px;color:#3b3324">Lagna: ${d.lagna || '-'}</span>
        <span style="font-size:12px;background:rgba(154,123,52,.1);border:1px solid var(--gold-soft);border-radius:14px;padding:5px 14px;color:#3b3324">สุริยะ: ${d.surya_rashi || '-'}</span>
        <span style="font-size:12px;background:rgba(154,123,52,.1);border:1px solid var(--gold-soft);border-radius:14px;padding:5px 14px;color:#3b3324">จันทรา: ${d.chandra_rashi || '-'}</span>
        <span style="font-size:12px;background:rgba(154,123,52,.1);border:1px solid var(--gold-soft);border-radius:14px;padding:5px 14px;color:#3b3324">Nakshatra: ${nk.name_th || nk.name_en || '-'} (pada ${nk.pada || '-'})</span>
      </div>
      ${d.interpretation ? `<p style="line-height:1.85;font-size:15px;color:#3b3324;margin-top:12px">${d.interpretation}</p>` : ''}`
    } catch (e) { box.innerHTML = '❌ ' + e.message }
    setLoading(false)
  }
=======
      const personName = escapeHtml(d.person_name || gv('v-name'))
      const lagna = escapeHtml(d.lagna || '-')
      const surya = escapeHtml(d.surya_rashi || '-')
      const chandra = escapeHtml(d.chandra_rashi || '-')
      const nkName = escapeHtml(nk.name_th || nk.name_en || '-')
      const nkPada = escapeHtml(nk.pada || '-')
      const interpHtml = d.interpretation ? `<p class="vedic-int">${escapeHtml(d.interpretation)}</p>` : ''
      const caveatHtml = d.caveat ? `<div class="tcaveat">${escapeHtml(d.caveat)}</div>` : ''
      box.innerHTML = `<div class="chart-head">🪐 ดวงเวดิก <b>${personName}</b></div>
        <div class="el-row">
          <span class="el-pill">Lagna: ${lagna}</span>
          <span class="el-pill">สุริยะ: ${surya}</span>
          <span class="el-pill">จันทรา: ${chandra}</span>
          <span class="el-pill">Nakshatra: ${nkName} (pada ${nkPada})</span>
        </div>
        ${interpHtml}
        ${caveatHtml}`
    } catch (e) { box.innerHTML = '❌ ' + e }
  }, [])
>>>>>>> Stashed changes

  // ── Horary ──
  const onHorary = async () => {
    const box = document.getElementById('r-horary')
    if (!box) return
    box.classList.add('show')
    box.innerHTML = '<div class="loading"><span></span>ถามจักรวาล...</div>'
    setLoading(true)
    try {
<<<<<<< Updated upstream
      const q = gv('h-q')
      if (!q) { box.innerHTML = '<span style="color:#c44">พิมพ์คำถามก่อน</span>'; return }
      const prov = gv('h-prov') || '13.7563,100.5018'
      const [lat, lon] = prov.split(',').map(v => parseFloat(v) || 0)
      const d = await callApi('/v1/horary/ask', { question: q, tz_offset_hours: 7, lat, lon, system: 'tropical' })
      if (!d.ascendant) { box.innerHTML = `<span style="color:#c44">${d.detail || 'คำนวณไม่สำเร็จ'}</span>`; return }
      const asc = d.ascendant || {}
      const moon = d.moon || {}
      box.innerHTML = `<div style="font-family:Cinzel,serif;font-size:18px;color:#2e2818;margin-bottom:12px">🔮 คำตอบจากจักรวาล</div>
      <div style="display:flex;gap:8px;flex-wrap:wrap;margin-bottom:16px">
        <span style="font-size:12px;background:rgba(154,123,52,.1);border:1px solid var(--gold-soft);border-radius:14px;padding:5px 14px;color:#3b3324">ASC: ${asc.sign || '-'} ${(asc.degree||0).toFixed(1)}°</span>
        <span style="font-size:12px;background:rgba(154,123,52,.1);border:1px solid var(--gold-soft);border-radius:14px;padding:5px 14px;color:#3b3324">Moon: ${moon.sign || '-'} ${(moon.degree||0).toFixed(1)}°</span>
      </div>
      <p style="margin-top:12px;color:#3b3324;line-height:1.8"><i>"${q}"</i><br/>ตอบเมื่อ: ${d.asked_at_local || '-'}</p>`
    } catch (e) { box.innerHTML = '❌ ' + e.message }
    setLoading(false)
  }
=======
      const res = await fetch('http://127.0.0.1:8000/v1/muhurta/find', {
        method: 'POST', headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ action, start_date: date, days, lat, lon,
          tz_offset_hours: 7, top_n: 3 }) })
      const d = await res.json()
      if (!res.ok) { box.innerHTML = '❌ ' + (d.detail || res.status); return }
      const wins = (d.windows && Array.isArray(d.windows)) ? d.windows : []
      const actionTh = escapeHtml(d.action_th || action)
      const rows = wins.slice(0, 5).map(w => {
        const when = (w.when_local || w.start || '-')
        const dt = when.split('T'); const day = escapeHtml(dt[0]); const tm = escapeHtml((dt[1]||'').slice(0,5))
        const reasons = (w.reasons_th || []).map(r => escapeHtml(r)).join(' · ')
        const score = w.score ?? '-'
        return `<tr><td>${day}</td><td class="asp-good">${tm}</td><td class="asp-good">${score}</td></tr>
          ${reasons?`<tr class="m-reason"><td colspan="3">${reasons}</td></tr>`:''}`
      }).join('')
      const caveatHtml = d.caveat ? `<div class="tcaveat">${escapeHtml(d.caveat)}</div>` : ''
      box.innerHTML = `<div class="chart-head">⏳ ชั่วโมงมงคลสำหรับ <b>${actionTh}</b></div>
        <table class="chart-tbl"><thead><tr><th>วัน</th><th>เวลา</th><th>คะแนน</th></tr></thead><tbody>${rows||'<tr><td colspan="3">ไม่พบหน้าต่างมงคลในช่วงที่เลือก</td></tr>'}</tbody></table>
        ${caveatHtml}`
    } catch (e) { box.innerHTML = '❌ ' + e }
  }, [])
  useEffect(() => {
    window.__renderTarot = (box, data) => {
      const narr = (data.narrative && (data.narrative.th || data.narrative.en)) || ''
      const cards = data.cards || []
      const flipHtml = cards.map((c, i) => {
        const rawNm = c.card ? c.card.replace(' of ', ' แห่ง ') : (c.name || '')
        const nm = escapeHtml(rawNm)
        const or = c.orientation === 'reversed' ? ' ( reversed )' : ''
        return `<div class="tcard" data-i="${i}" onclick="if(window.__flipTarot3D)window.__flipTarot3D(${i})">${nm}${escapeHtml(or)}</div>`
      }).join('')
      const narrHtml = narr
        ? `<div class="tnarr">${escapeHtml(narr).split('\n').map(l => {
            const t = l.trim(); if (!t) return ''
            return /^\[/.test(t) ? `<p class="story">${t}</p>` : `<p>${t}</p>`
          }).join('')}</div>` : ''
      const caveat = data.caveat ? `<div class="tcaveat">${escapeHtml(data.caveat)}</div>` : ''
      box.innerHTML = `<div class="tcards">${flipHtml}</div>${narrHtml}${caveat}`
      window.__tarotCards = cards
    }
  }, [])
>>>>>>> Stashed changes

  return (
    <div className="ui" ref={mainRef}>
      {/* ── Navigation ── */}
      <nav className={`nav ${navScrolled ? 'scrolled' : ''}`}>
        <div className="brand" onClick={() => goView('home')}>
          <span className="logo">ASTRAL</span>
          <span className="tag">โหราศาสตร์ครบวงจร</span>
        </div>
        <div className="navlinks">
          {VIEWS.map(v => (
            <button key={v} className={v === view ? 'active' : ''} onClick={() => goView(v)}>
              {NAV_LABELS[v]}
            </button>
          ))}
        </div>
      </nav>

      {/* ── Home View ── */}
      <section className={`view ${view === 'home' ? 'active' : ''}`}>
        <div className="hero">
          <span className="pill">{S.hero.pill}</span>
          <h1>
            {S.hero.title1}<br />
            {S.hero.title2} <span className="g">{S.hero.title3}</span> {S.hero.title4}
          </h1>
          <p>{S.hero.description}</p>
          <div className="cta">
            <button className="btn primary" onClick={() => goView('natal')}>{S.hero.cta}</button>
            <button className="btn" onClick={() => goView('tarot')}>เปิดไพ่ทาโรต์</button>
          </div>
        </div>

        <div className="section">
          <span className="eyebrow">{S.sections.tarot.eyebrow}</span>
          <h2>{S.sections.tarot.title}<br /><span className="g">{S.sections.tarot.titleAccent}</span></h2>
          <p>{S.sections.tarot.desc}</p>
          <button className="btn primary" onClick={() => goView('tarot')}>{S.sections.tarot.cta}</button>
        </div>

        <div className="section">
          <span className="eyebrow">{S.sections.synastry.eyebrow}</span>
          <h2>{S.sections.synastry.title}<br /><span className="g">{S.sections.synastry.titleAccent}</span></h2>
          <p>{S.sections.synastry.desc}</p>
          <button className="btn primary" onClick={() => goView('synastry')}>{S.sections.synastry.cta}</button>
        </div>

        <div className="section">
          <span className="eyebrow">{S.sections.vedic.eyebrow}</span>
          <h2>{S.sections.vedic.title}<br /><span className="g">{S.sections.vedic.titleAccent}</span></h2>
          <p>{S.sections.vedic.desc}</p>
          <button className="btn primary" onClick={() => goView('vedic')}>{S.sections.vedic.cta}</button>
        </div>

        <footer>
          <div className="seal">A</div>
          <br />Astral · Est. MMXXVI · โหราศาสตร์ครบวงจร
        </footer>
      </section>

      {/* ── Natal Chart ── */}
      <section className={`view ${view === 'natal' ? 'active' : ''}`}>
        <div className="form-wrap">
          <h2>ดูดวงชะตา</h2>
          <p className="sub">วันเวลาและสถานที่เกิด — ดาวฤกษ์บอกอะไรคุณ</p>
          <div className="field"><label>ชื่อ</label><input id="n-name" placeholder="ชื่อของคุณ" defaultValue="คุณ" /></div>
          <div className="field"><label>วันเกิด</label><input id="n-date" type="date" /></div>
          <div className="field"><label>เวลาเกิด</label><input id="n-time" type="time" step="1" /></div>
          <div className="field"><label>จังหวัด</label><select id="n-prov">
            <option value="13.7563,100.5018">กรุงเทพมหานคร</option>
            <option value="13.3633,100.9868">ชลบุรี</option>
            <option value="18.7883,98.9853">เชียงใหม่</option>
            <option value="7.8804,98.3923">ภูเก็ต</option>
          </select></div>
          <div className="field"><label>ระบบ</label><select id="n-sys">
            <option value="tropical">Tropical</option>
            <option value="sidereal">Sidereal</option>
          </select></div>
          <button className="btn primary" onClick={onNatal}>ดูดวงชะตาของฉัน</button>
          <div className="result" id="r-natal" />
        </div>
      </section>

      {/* ── Tarot ── */}
      <section className={`view ${view === 'tarot' ? 'active' : ''}`}>
        <div className="form-wrap">
          <h2>ไพ่ทาโรต์</h2>
          <p className="sub">สับไพ่แล้วให้ไพ่ตอบคำถามที่คุณอยากรู้</p>
          <div className="field"><label>คำถามของคุณ</label><input id="t-q" placeholder="สิ่งที่อยากรู้..." /></div>
          <button className="btn primary" onClick={onTarot}>เปิดไพ่</button>
          <div className="result" id="r-tarot" />
        </div>
      </section>

      {/* ── Synastry ── */}
      <section className={`view ${view === 'synastry' ? 'active' : ''}`}>
        <div className="form-wrap">
          <h2>ดูคู่</h2>
          <p className="sub">เปรียบเทียบดวงชะตาสองคน</p>
          <div style={{display:'grid',gridTemplateColumns:'1fr 1fr',gap:'24px',margin:'12px 0'}}>
            <div>
              <h4 style={{fontFamily:'Cinzel,serif',color:'var(--gold)',marginBottom:'10px'}}>คนที่ 1</h4>
              <div className="field"><label>ชื่อ</label><input id="s-a-name" defaultValue="คุณ" /></div>
              <div className="field"><label>วันเกิด</label><input id="s-a-date" type="date" /></div>
              <div className="field"><label>เวลาเกิด</label><input id="s-a-time" type="time" step="1" /></div>
              <div className="field"><label>จังหวัด</label><select id="s-a-prov">
                <option value="13.7563,100.5018">กรุงเทพ</option>
                <option value="13.3633,100.9868">ชลบุรี</option>
              </select></div>
            </div>
            <div>
              <h4 style={{fontFamily:'Cinzel,serif',color:'var(--gold)',marginBottom:'10px'}}>คนที่ 2</h4>
              <div className="field"><label>ชื่อ</label><input id="s-b-name" defaultValue="เขา" /></div>
              <div className="field"><label>วันเกิด</label><input id="s-b-date" type="date" /></div>
              <div className="field"><label>เวลาเกิด</label><input id="s-b-time" type="time" step="1" /></div>
              <div className="field"><label>จังหวัด</label><select id="s-b-prov">
                <option value="13.7563,100.5018">กรุงเทพ</option>
                <option value="13.3633,100.9868">ชลบุรี</option>
              </select></div>
            </div>
          </div>
          <button className="btn primary" onClick={() => {
            const box = document.getElementById('r-synastry')
            if (!box) return
            box.classList.add('show')
            box.innerHTML = '<div class="loading"><span></span>กำลังคำนวณความเข้ากัน...</div>'
            const mk = (p) => {
              const prov = (gv(`s-${p}-prov`) || '13.7563,100.5018').split(',').map(v => parseFloat(v) || 0)
              return { name: gv(`s-${p}-name`) || ' ', date: gv(`s-${p}-date`), time: (gv(`s-${p}-time`) || '12:00') + ':00', tz_offset_hours: 7, lat: prov[0], lon: prov[1], system: 'tropical' }
            }
            Promise.all([
              callApi('/v1/synastry/cross-aspects', { a: mk('a'), b: mk('b') }),
              callApi('/v1/natal/compute', mk('a')),
              callApi('/v1/natal/compute', mk('b')),
            ]).then(([syn, ra, rb]) => {
              if (!ra.bodies || !rb.bodies) { box.innerHTML = '<span style="color:#c44">คำนวณไม่สำเร็จ</span>'; return }
              const ca = syn.cross_aspects || []
              const rows = ca.slice(0, 12).map(x => `<tr><td>${x.body_a} × ${x.body_b}</td><td style="color:var(--gold)">${x.aspect}</td><td>${x.orb?.toFixed(2)}°</td></tr>`).join('')
              box.innerHTML = `<div style="font-family:Cinzel,serif;font-size:18px;color:#2e2818;margin-bottom:12px">💞 กระแสสองดวง <b>${mk('a').name}</b> × <b>${mk('b').name}</b></div>
              <table style="width:100%;border-collapse:collapse;font-size:14px;color:#3b3324">
                <thead><tr><th style="text-align:left;padding:8px;color:var(--gold);border-bottom:1px solid var(--gold-soft)">Aspect</th><th style="text-align:left;padding:8px;color:var(--gold);border-bottom:1px solid var(--gold-soft)">ประเภท</th><th style="text-align:left;padding:8px;color:var(--gold);border-bottom:1px solid var(--gold-soft)">Orb</th></tr></thead>
                <tbody>${rows}</tbody></table>`
            }).catch(e => { box.innerHTML = '❌ ' + e.message })
          }}>ดูคู่ของเรา</button>
          <div className="result" id="r-synastry" />
        </div>
      </section>

      {/* ── Vedic ── */}
      <section className={`view ${view === 'vedic' ? 'active' : ''}`}>
        <div className="form-wrap">
          <h2>ดวงเวดิก</h2>
          <p className="sub">โหราศาสตร์อินเดียโบราณ — Nakshatra, Dasha, Yoga</p>
          <div className="field"><label>ชื่อ</label><input id="v-name" placeholder="ชื่อของคุณ" defaultValue="คุณ" /></div>
          <div className="field"><label>วันเกิด</label><input id="v-date" type="date" /></div>
          <div className="field"><label>เวลาเกิด</label><input id="v-time" type="time" step="1" /></div>
          <div className="field"><label>จังหวัด</label><select id="v-prov">
            <option value="13.7563,100.5018">กรุงเทพมหานคร</option>
            <option value="13.3633,100.9868">ชลบุรี</option>
            <option value="18.7883,98.9853">เชียงใหม่</option>
          </select></div>
          <button className="btn primary" onClick={onVedic}>ดูดวงเวดิก</button>
          <div className="result" id="r-vedic" />
        </div>
      </section>

      {/* ── Horary ── */}
      <section className={`view ${view === 'horary' ? 'active' : ''}`}>
        <div className="form-wrap">
          <h2>ถามดวง · Horary</h2>
          <p className="sub">ถามคำถาม แล้วดูดาวตอบจากจักรวาลตอนที่คุณถาม</p>
          <div className="field"><label>คำถามของคุณ</label><input id="h-q" placeholder="เช่น ผมควรรักเขาไหม? หรือ งานนี้ไหวไหม?" /></div>
          <div className="field"><label>จังหวัด</label><select id="h-prov">
            <option value="13.7563,100.5018">กรุงเทพมหานคร</option>
            <option value="13.3633,100.9868">ชลบุรี</option>
          </select></div>
          <button className="btn primary" onClick={onHorary}>ถามดาวตอบคุณ</button>
          <div className="result" id="r-horary" />
        </div>
      </section>

      {/* ── AI Reading ── */}
      <section className={`view ${view === 'ai-reading' ? 'active' : ''}`}>
        <div className="form-wrap">
          <h2>AI อ่านดวง</h2>
          <p className="sub">AI วิเคราะห์ดวงชะตาอย่างลึกซึ้ง — ตรงบุคคล ไม่ซ้ำใคร</p>
          <div className="field"><label>ชื่อ</label><input id="ai-name" placeholder="ชื่อของคุณ" defaultValue="คุณ" /></div>
          <div className="field"><label>วันเกิด</label><input id="ai-date" type="date" /></div>
          <div className="field"><label>เวลาเกิด</label><input id="ai-time" type="time" step="1" /></div>
          <div className="field"><label>จังหวัด</label><select id="ai-prov">
            <option value="13.7563,100.5018">กรุงเทพมหานคร</option>
            <option value="13.3633,100.9868">ชลบุรี</option>
            <option value="18.7883,98.9853">เชียงใหม่</option>
          </select></div>
          <button className="btn primary" onClick={onAiReading}>ให้ AI อ่านดวง</button>
          <div className="result" id="r-ai" style={{ whiteSpace: 'pre-wrap', lineHeight: 1.8 }} />
        </div>
      </section>

      {/* ── Life Report ── */}
      <section className={`view ${view === 'life' ? 'active' : ''}`}>
        <div className="form-wrap">
          <h2>ชีวิตคุณ</h2>
          <p className="sub">ดูดวงชะตาครบวงจร — Natal, Tarot, Transit, AI Reading</p>
          <div className="field"><label>ชื่อ</label><input id="l-name" placeholder="ชื่อของคุณ" defaultValue="คุณ" /></div>
          <div className="field"><label>วันเกิด</label><input id="l-date" type="date" /></div>
          <div className="field"><label>เวลาเกิด</label><input id="l-time" type="time" step="1" /></div>
          <div className="field"><label>จังหวัด</label><select id="l-prov">
            <option value="13.7563,100.5018">กรุงเทพมหานคร</option>
            <option value="13.3633,100.9868">ชลบุรี</option>
            <option value="18.7883,98.9853">เชียงใหม่</option>
          </select></div>
          <button className="btn primary" onClick={() => {
            const date = gv('l-date')
            if (!date) { alert('กรุณาระบุวันเกิด'); return }
            goView('natal')
            setTimeout(() => {
              const nDate = document.getElementById('n-date')
              const nTime = document.getElementById('n-time')
              const nName = document.getElementById('n-name')
              const nProv = document.getElementById('n-prov')
              if (nDate) nDate.value = date
              if (nTime) nTime.value = gv('l-time') || '12:00'
              if (nName) nName.value = gv('l-name') || 'คุณ'
              if (nProv) nProv.value = gv('l-prov') || '13.7563,100.5018'
              onNatal()
            }, 300)
          }}>ดูชีวิตฉัน</button>
        </div>
      </section>
    </div>
  )
}
