import { useRef, useState, useEffect, useCallback } from 'react'
import { Canvas } from '@react-three/fiber'
import CosmicScene from './CosmicScene.jsx'
import OrbitGalaxy from './OrbitGalaxy.jsx'
import NatalWheel from './NatalWheel.jsx'
import CanvasBoundary from './CanvasBoundary.jsx'
import Tarot3D from './Tarot3D.jsx'
import GlitterWarp from './GlitterWarp.jsx'
import BlackHole from './BlackHole.jsx'
import Intro from './Intro.jsx'
import { useAstralApi } from './api.js'

const VIEWS = ['home', 'natal', 'synastry', 'vedic', 'tarot', 'muhurta', 'life']

export default function App() {
  const [view, setView] = useState('home')
  const [warp, setWarp] = useState(false)
  const [introDone, setIntroDone] = useState(false)
  const zoomRef = useRef(0)
  const pendingView = useRef('home')
  const warpDone = useRef(false)
  const { call } = useAstralApi()
  const [orbitSel, setOrbitSel] = useState(null)   // โหนดวงโคจรที่เลือก (BlueYard)
  const [canvasAlive, setCanvasAlive] = useState(true)  // ตัด Canvas เมื่อ WebGL context lost

  // ติดตาม scroll → zoom context (เฉพาะท้ายหน้า)
  useEffect(() => {
    const onScroll = () => {
      const max = Math.max(1, document.documentElement.scrollHeight - innerHeight)
      const prog = (window.scrollY || document.documentElement.scrollTop || 0) / max
      const z = (prog - 0.62) / 0.38
      zoomRef.current = Math.min(1, Math.max(0, z))
    }
    window.addEventListener('scroll', onScroll, { passive: true })
    return () => window.removeEventListener('scroll', onScroll)
  }, [])

  // Enter transition: ซูมหลุมดำ (Black Hole) เมื่อกดเมนู → ดูดกลืนแล้วสลับ view
  const [bh, setBh] = useState(false)
  const goView = useCallback((name) => {
    if (!VIEWS.includes(name) || name === view) return
    pendingView.current = name
    warpDone.current = false
    setBh(true)            // เล่น black hole zoom
  }, [view])

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
        `<tr><td>${b.body}</td><td>${b.sign}</td><td>${b.degree.toFixed(2)}°</td>
         <td>${b.absolute_deg.toFixed(2)}°</td><td>H${b.house ?? '-'}</td></tr>`).join('')
      const asc = d.ascendant || {}
      const els = d.elements || {}
      const elHtml = Object.entries(els).map(([k, v]) =>
        `<span class="el-pill">${k} ${typeof v === 'number' ? v.toFixed(0) : v}</span>`).join('')
      box.innerHTML = `
        <div class="chart-head">🌟 ดวงชะตา <b>${d.name || name}</b>
          <span class="chart-sys">${d.system === 'sidereal' ? 'Sidereal' : 'Tropical'}</span></div>
        <table class="chart-tbl"><thead><tr><th>ดาว</th><th>ราศี</th><th>องศา</th><th>Absolute</th><th>บ้าน</th></tr></thead>
          <tbody>${rows}
          <tr class="asc-row"><td>ASC</td><td>${asc.sign || '-'}</td><td>${(asc.degree||0).toFixed(2)}°</td><td>${(asc.absolute_deg||0).toFixed(2)}°</td><td>H1</td></tr>
          </tbody></table>
        <div class="el-row">${elHtml}</div>
        ${d.caveat ? `<div class="tcaveat">${d.caveat}</div>` : ''}`
    } catch (e) { box.innerHTML = '❌ ' + e; setNatalChart(null) }
  }, [])

  // helper ดึงค่าฟอร์มธรรมดา
  const gv = (id) => document.getElementById(id)?.value || ''
  const prov = (id) => (gv(id).split(',')).map(Number)

  // ดูคู่ Synastry จริง (/v1/synastry/cross-aspects)
  const onSynastry = useCallback(async () => {
    const box = document.getElementById('r-synastry')
    const mk = (p) => ({ name: gv(`s-${p}-name`) || ' ', date: gv(`s-${p}-date`),
      time: (gv(`s-${p}-time`) || '00:00') + ':00', tz_offset_hours: 7,
      lat: prov(`s-${p}-prov`)[0], lon: prov(`s-${p}-prov`)[1], system: 'tropical' })
    if (!gv('s-a-date') || !gv('s-b-date')) { box.classList.add('show'); box.innerHTML = '❌ ระบุวันเกิดทั้งสองท่าน'; return }
    box.classList.add('show'); box.innerHTML = '⏳ กำลังลากเส้น aspect ระหว่างสองดวง...'
    try {
      const res = await fetch('http://127.0.0.1:8000/v1/synastry/cross-aspects', {
        method: 'POST', headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ a: mk('a'), b: mk('b') }) })
      const d = await res.json()
      if (!res.ok) { box.innerHTML = '❌ ' + (d.detail || res.status); return }
      const ca = d.cross_aspects || []
      const rows = ca.slice(0, 12).map(x =>
        `<tr><td>${x.body_a} × ${x.body_b}</td><td class="asp-${x.aspect}">${x.aspect}</td><td>${x.orb?.toFixed(2)}°</td></tr>`).join('')
      const ea = d.elements_a?.dominant, eb = d.elements_b?.dominant
      box.innerHTML = `<div class="chart-head">💞 กระแสสองดวง <b>${mk('a').name}</b> × <b>${mk('b').name}</b></div>
        <div class="el-row"><span class="el-pill">A dominant: ${ea||'-'}</span><span class="el-pill">B dominant: ${eb||'-'}</span></div>
        <table class="chart-tbl"><thead><tr><th>Aspect</th><th>ประเภท</th><th>Orb</th></tr></thead><tbody>${rows}${ca.length>12?`<tr><td colspan="3" style="opacity:.6">…อีก ${ca.length-12} aspects</td></tr>`:''}</tbody></table>
        ${d.caveat?`<div class="tcaveat">${d.caveat}</div>`:''}`
    } catch (e) { box.innerHTML = '❌ ' + e }
  }, [])

  // เวดิกจริง (/v1/vedic/chart)
  const onVedic = useCallback(async () => {
    const box = document.getElementById('r-vedic')
    const date = gv('v-date'), time = (gv('v-time') || '00:00')
    if (!date) { box.classList.add('show'); box.innerHTML = '❌ ระบุวันเกิด'; return }
    const [lat, lon] = prov('v-prov')
    box.classList.add('show'); box.innerHTML = '⏳ กำลังเลื่อนดาวไปตำแหน่ง sidereal...'
    try {
      const res = await fetch('http://127.0.0.1:8000/v1/vedic/chart', {
        method: 'POST', headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ name: gv('v-name') || 'คุณ',
          birth: { date, time, lat, lon, tz_offset_hours: 7 } }) })
      const d = await res.json()
      if (!res.ok) { box.innerHTML = '❌ ' + (d.detail || res.status); return }
      const nk = d.nakshatra || {}
      box.innerHTML = `<div class="chart-head">🪐 ดวงเวดิก <b>${d.person_name||gv('v-name')}</b></div>
        <div class="el-row">
          <span class="el-pill">Lagna: ${d.lagna||'-'}</span>
          <span class="el-pill">สุริยะ: ${d.surya_rashi||'-'}</span>
          <span class="el-pill">จันทรา: ${d.chandra_rashi||'-'}</span>
          <span class="el-pill">Nakshatra: ${nk.name_th||nk.name_en||'-'} (pada ${nk.pada||'-'})</span>
        </div>
        ${d.interpretation?`<p class="vedic-int">${d.interpretation}</p>`:''}
        ${d.caveat?`<div class="tcaveat">${d.caveat}</div>`:''}`
    } catch (e) { box.innerHTML = '❌ ' + e }
  }, [])

  // มูฮูร์ตะจริง (/v1/muhurta/find)
  const onMuhurta = useCallback(async () => {
    const box = document.getElementById('r-muhurta')
    const action = gv('m-action'), date = gv('m-date'), days = +gv('m-days') || 60
    if (!date) { box.classList.add('show'); box.innerHTML = '❌ ระบุวันเริ่มหา'; return }
    const [lat, lon] = prov('m-prov')
    box.classList.add('show'); box.innerHTML = '⏳ กำลังหาชั่วโมงมงคล (อาจใช้เวลาสักครู่)...'
    try {
      const res = await fetch('http://127.0.0.1:8000/v1/muhurta/find', {
        method: 'POST', headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ action, start_date: date, days, lat, lon,
          tz_offset_hours: 7, top_n: 3 }) })
      const d = await res.json()
      if (!res.ok) { box.innerHTML = '❌ ' + (d.detail || res.status); return }
      const wins = (d.windows && Array.isArray(d.windows)) ? d.windows : []
      const rows = wins.slice(0, 5).map(w => {
        const when = (w.when_local || w.start || '-')
        const dt = when.split('T'); const day = dt[0]; const tm = (dt[1]||'').slice(0,5)
        const reasons = (w.reasons_th || []).join(' · ')
        return `<tr><td>${day}</td><td class="asp-good">${tm}</td><td class="asp-good">${w.score??'-'}</td></tr>
          ${reasons?`<tr class="m-reason"><td colspan="3">${reasons}</td></tr>`:''}`
      }).join('')
      box.innerHTML = `<div class="chart-head">⏳ ชั่วโมงมงคลสำหรับ <b>${d.action_th||action}</b></div>
        <table class="chart-tbl"><thead><tr><th>วัน</th><th>เวลา</th><th>คะแนน</th></tr></thead><tbody>${rows||'<tr><td colspan="3">ไม่พบหน้าต่างมงคลในช่วงที่เลือก</td></tr>'}</tbody></table>
        ${d.caveat?`<div class="tcaveat">${d.caveat}</div>`:''}`
    } catch (e) { box.innerHTML = '❌ ' + e }
  }, [])
  useEffect(() => {
    window.__renderTarot = (box, data) => {
      const narr = (data.narrative && (data.narrative.th || data.narrative.en)) || ''
      const cards = data.cards || []
      const flipHtml = cards.map((c, i) => {
        const nm = c.card ? c.card.replace(' of ', ' แห่ง ') : (c.name || '')
        const or = c.orientation === 'reversed' ? ' ( reversed )' : ''
        return `<div class="tcard" data-i="${i}" onclick="if(window.__flipTarot3D)window.__flipTarot3D(${i})">${nm}${or}</div>`
      }).join('')
      const narrHtml = narr
        ? `<div class="tnarr">${narr.replace(/&/g,'&amp;').replace(/</g,'&lt;').split('\n').map(l => {
            const t = l.trim(); if (!t) return ''
            return /^\[/.test(t) ? `<p class="story">${t}</p>` : `<p>${t}</p>`
          }).join('')}</div>` : ''
      const caveat = data.caveat ? `<div class="tcaveat">${data.caveat}</div>` : ''
      box.innerHTML = `<div class="tcards">${flipHtml}</div>${narrHtml}${caveat}`
      window.__tarotCards = cards
    }
  }, [])

  return (
    <>
      <CanvasBoundary>
      {canvasAlive && (
      <Canvas id="bg-canvas" camera={{ position: [0, 0, 10], fov: 60 }} dpr={[1, 1.5]} gl={{ antialias: true }}
        onCreated={({ gl }) => {
          const cv = gl.domElement
          cv.addEventListener('webglcontextlost', (e) => {
            e.preventDefault()
            setCanvasAlive(false)   // ตัด Canvas ออกจาก tree → ปลดบล็อก main thread
          }, false)
        }}>
        <CosmicScene zoomRef={zoomRef} />
        <OrbitGalaxy onSelect={(n) => { setOrbitSel(n); }}
                     selectedId={orbitSel?.id} />
      </Canvas>
      )}
      </CanvasBoundary>
      <div className="grain" />

      <div className="ui" style={{ opacity: introDone ? 1 : 0, transition: 'opacity .8s ease', visibility: introDone ? 'visible' : 'hidden' }}>
        <nav className="nav">
          <div className="brand" onClick={() => goView('home')}>
            <span className="logo">Astral</span>
            <span className="divider" />
            <span className="tag">ดวงดาวจะบอกอะไรคุณ</span>
          </div>
          <div className="navlinks">
            {VIEWS.map(v => (
              <button key={v} className={v === view ? 'active' : ''} onClick={() => goView(v)}>
                {v === 'home' ? 'หน้าแรก' : v === 'natal' ? 'ดวงชะตา' : v === 'synastry' ? 'ดูคู่' :
                 v === 'vedic' ? 'เวดิก' : v === 'tarot' ? 'ไพ่ทาโรต์' : v === 'muhurta' ? 'มูฮูร์ตะ' : 'ชีวิตคุณ'}
              </button>
            ))}
          </div>
        </nav>

        <section className={'view' + (view === 'home' ? ' active' : '')}>
          <div className="hero">
            <span className="pill">✦ ดูดวงอย่างที่โหรหลวงเคยมองฟ้า</span>
            <h1>ดาวแต่ละดวง<br/>ล้วนมี<span className="g">คำบอก</span>ให้คุณ</h1>
            <p>วันที่ท่านลืมตาดูโลก ดาวแต่ละดวงยืนเรียงตำแหน่งให้ได้เห็นแล้ว — ว่าท่านมาเกิดมาเพื่ออะไร จะรักกับใคร และช่วงไหนในชีวิตที่ฟ้าจะประทานของขวัญ</p>
            <div className="cta">
              <button className="btn primary" onClick={() => goView('natal')}>ขอให้ดาวบอกท่าน</button>
              <button className="btn" onClick={() => goView('synastry')}>ดูกระแสใจสองดวง</button>
            </div>
          </div>
          <div className="sec-title"><h2>สิ่งที่<span className="g">ดาว</span>อยากบอกท่าน</h2>
            <p>เลือกสิ่งที่ท่านสงสัยใจ — เราจะอ่านจากตำราโบราณที่ส่งกันมาหลายพันปี แล้วเล่ากลับให้ท่านฟังเป็นภาษาที่เข้าใจได้จริง</p></div>
          <div className="cards">
            {[
              ['🌟','ดวงชะตา','วันเกิดของท่าน คือเข็มทิศชี้ทางมาเกิด — เราจะบอกว่าท่านมีของดีซ่อนที่ไหน และอุปสรรคที่ฟ้าฝากมาให้ฝ่าฟัน'],
              ['💞','ดูคู่','เมื่อดวงท่านไปพบดวงเขา หรือดวงเธอ จะเกิดกระแสไฟบางอย่าง — เราจะบอกว่าสองดวงนี้ช่วยกันหรือจะต้องระวังเรื่องใด'],
              ['🪐','เวดิก','มองผ่านตำราโบราณอินเดีย ดาวจะเลื่อนไปตำแหน่งที่แท้จริงตามฤดูกาล — เห็นธาตุที่ท่านเกิดมาและหน้าที่ที่ฟ้าฝากไว้'],
              ['⏳','มูฮูร์ตะ','มีเรื่องสำคัญจะทำใช่ไหม — เราจะหาชั่วโมงที่ดาวยืนรับรอง ให้สิ่งที่ท่านเริ่มตั้งต้นนั้นเป็นสิริมงคล'],
              ['🔮','ไพ่ทาโรต์','จั่วไพ่ 78 ใบจากสำนักโบราณ สิ่งที่ออกมาไม่ใช่คำทำนายเลื่อนลอย — แต่เป็นเสียงที่สะท้อนสิ่งที่ท่านกังวลอยู่ในใจตอนนี้'],
              ['🌌','ชีวิตคุณ','ดาวไม่หยุดหมุน และแต่ละรอบที่มันผ่าน จะพาเหตุการณ์ใหม่มา — เราจะบอกท่านล่วงหน้าว่าเมื่อไหร่ควรก้าวไปและเมื่อไหร่ควรรอ']
            ].map(([ic, h, p], i) => (
              <div key={i} className="card" data-go={['natal','synastry','vedic','muhurta','tarot','life'][i]} onClick={(e) => goView(e.currentTarget.dataset.go)}>
                <div className="ic">{ic}</div><h3>{h}</h3><p>{p}</p><div className="orn">✦</div>
              </div>
            ))}
          </div>
        </section>

        <section className={'view' + (view === 'natal' ? ' active' : '')}>
          <div className="form-wrap">
            <h2>ดวงชะตา</h2>
            <p className="sub">วันเกิดของท่าน คือเข็มทิศชี้ทางมาเกิด</p>
            <div className="field"><label>ชื่อ</label><input id="n-name" placeholder="ชื่อของท่าน" defaultValue="คุณ" /></div>
            <div className="field"><label>วันเกิด</label><input id="n-date" type="date" /></div>
            <div className="field"><label>เวลาเกิด</label><input id="n-time" type="time" step="1" /></div>
            <div className="field"><label>จังหวัด</label>
              <select id="n-prov">
                <option value="13.7563,100.5018">กรุงเทพมหานคร</option>
                <option value="13.3633,100.9868">ชลบุรี</option>
                <option value="18.7883,98.9853">เชียงใหม่</option>
                <option value="7.8804,98.3923">ภูเก็ต</option>
              </select>
            </div>
            <div className="field"><label>ระบบ</label>
              <select id="n-sys">
                <option value="tropical">Tropical (ตะวันตก)</option>
                <option value="sidereal">Sidereal (เวดิก)</option>
              </select>
            </div>
            <button className="btn primary" onClick={() => onNatal()}>ดูดวงชะตา</button>
            <div className="result" id="r-natal" />
            {natalChart && <NatalWheel chart={natalChart} />}
          </div>
        </section>

        <section className={'view' + (view === 'tarot' ? ' active' : '')}>
          <div className="form-wrap">
            <h2>ไพ่ทาโรต์</h2>
            <p className="sub">โบกไพ่แล้วตั้งคำถามในใจ — ไพ่สามใบนี้จะตอบสิ่งที่ท่านอยากรู้</p>
            <div className="field"><label>คำถามของคุณ</label><input id="t-q" placeholder="สิ่งที่อยากรู้" /></div>
            <button className="btn primary" onClick={() => call('tarot', document.getElementById('r-tarot'), {
              url: '/v1/tarot/draw',
              body: { name: 'คุณ', question: document.getElementById('t-q')?.value || '',
                spread: 'three_card', lang: 'th',
                birth: { date: '1997-05-19', time: '05:45', tz_offset_hours: 7, lat: 13.3633, lon: 100.9868, system: 'tropical' } }
            })}>จั่วไพ่</button>
            <canvas id="tarot3d" />
            <div className="tarot-3d-hint">✦ ลากเพื่อหมุน · คลิกไพ่เพื่อพลิก ✦</div>
            <div className="result" id="r-tarot" />
          </div>
        </section>

        <section className={'view' + (view === 'synastry' ? ' active' : '')}>
          <div className="form-wrap">
            <h2>ดูคู่ · Synastry</h2>
            <p className="sub">เมื่อดวงท่านไปพบดวงเขา หรือดวงเธอ — เราจะอ่าน aspect ที่ลากระหว่างสองดวง</p>
            <div className="pair-grid">
              <div className="pair-col">
                <h4>ท่าน (A)</h4>
                <div className="field"><label>ชื่อ</label><input id="s-a-name" defaultValue="คุณ" /></div>
                <div className="field"><label>วันเกิด</label><input id="s-a-date" type="date" /></div>
                <div className="field"><label>เวลาเกิด</label><input id="s-a-time" type="time" step="1" /></div>
                <div className="field"><label>จังหวัด</label>
                  <select id="s-a-prov">
                    <option value="13.7563,100.5018">กรุงเทพมหานคร</option>
                    <option value="13.3633,100.9868">ชลบุรี</option>
                    <option value="18.7883,98.9853">เชียงใหม่</option>
                    <option value="7.8804,98.3923">ภูเก็ต</option>
                  </select>
                </div>
              </div>
              <div className="pair-col">
                <h4>คู่ (B)</h4>
                <div className="field"><label>ชื่อ</label><input id="s-b-name" defaultValue="เขา" /></div>
                <div className="field"><label>วันเกิด</label><input id="s-b-date" type="date" /></div>
                <div className="field"><label>เวลาเกิด</label><input id="s-b-time" type="time" step="1" /></div>
                <div className="field"><label>จังหวัด</label>
                  <select id="s-b-prov">
                    <option value="13.7,100.5">กรุงเทพฯ/ใกล้เคียง</option>
                    <option value="13.3633,100.9868">ชลบุรี</option>
                    <option value="18.7883,98.9853">เชียงใหม่</option>
                    <option value="7.8804,98.3923">ภูเก็ต</option>
                  </select>
                </div>
              </div>
            </div>
            <button className="btn primary" onClick={() => onSynastry()}>อ่านกระแสสองดวง</button>
            <div className="result" id="r-synastry" />
          </div>
        </section>

        <section className={'view' + (view === 'vedic' ? ' active' : '')}>
          <div className="form-wrap">
            <h2>เวดิก · Vedic</h2>
            <p className="sub">มองผ่านตำราโบราณอินเดีย — ดาวเลื่อนไปตำแหน่ง sidereal ตามฤดูกาล (Lahiri)</p>
            <div className="field"><label>ชื่อ</label><input id="v-name" defaultValue="คุณ" /></div>
            <div className="field"><label>วันเกิด</label><input id="v-date" type="date" /></div>
            <div className="field"><label>เวลาเกิด</label><input id="v-time" type="time" step="1" /></div>
            <div className="field"><label>จังหวัด</label>
              <select id="v-prov">
                <option value="13.7563,100.5018">กรุงเทพมหานคร</option>
                <option value="13.3633,100.9868">ชลบุรี</option>
                <option value="18.7883,98.9853">เชียงใหม่</option>
                <option value="7.8804,98.3923">ภูเก็ต</option>
              </select>
            </div>
            <button className="btn primary" onClick={() => onVedic()}>ดูดวงเวดิก</button>
            <div className="result" id="r-vedic" />
          </div>
        </section>

        <section className={'view' + (view === 'muhurta' ? ' active' : '')}>
          <div className="form-wrap">
            <h2>มูฮูร์ตะ · Muhurta</h2>
            <p className="sub">มีเรื่องสำคัญจะทำใช่ไหม — เราจะหาชั่วโมงที่ดาวยืนรับรอง</p>
            <div className="field"><label>เรื่องที่จะทำ</label>
              <select id="m-action">
                <option value="marriage">แต่งงาน (Marriage)</option>
                <option value="business">เริ่มธุรกิจ (Business)</option>
                <option value="contract">ทำสัญญา (Contract)</option>
                <option value="travel">เดินทาง (Travel)</option>
                <option value="moving">ย้ายบ้าน (Moving)</option>
              </select>
            </div>
            <div className="field"><label>วันเริ่มหา (จากวันนี้)</label><input id="m-date" type="date" /></div>
            <div className="field"><label>ระยะเวลาค้นหา (วัน)</label><input id="m-days" type="number" defaultValue="60" min="7" max="180" /></div>
            <div className="field"><label>จังหวัด</label>
              <select id="m-prov">
                <option value="13.7563,100.5018">กรุงเทพมหานคร</option>
                <option value="13.3633,100.9868">ชลบุรี</option>
                <option value="18.7883,98.9853">เชียงใหม่</option>
                <option value="7.8804,98.3923">ภูเก็ต</option>
              </select>
            </div>
            <button className="btn primary" onClick={() => onMuhurta()}>หาชั่วโมงมงคล</button>
            <div className="result" id="r-muhurta" />
          </div>
        </section>

        <footer>
          <div className="seal">A</div><br/>
          Astral · Est. MMXXVI · โหราศาสตร์ครบวงจร
        </footer>
      </div>

      {/* Orbit Galaxy detail panel (BlueYard — คลิกโหนดดูข้อมูล) */}
      {orbitSel && (
        <div className="orbit-panel">
          <button className="orbit-close" onClick={() => setOrbitSel(null)} aria-label="ปิด">×</button>
          <div className="orbit-dot" style={{ background: orbitSel.color, boxShadow: `0 0 18px ${orbitSel.color}` }} />
          <h3>{orbitSel.label}</h3>
          <p>{orbitSel.desc}</p>
          <button className="btn primary" onClick={() => { const id = orbitSel.id; setOrbitSel(null); goView(id) }}>
            เปิด {orbitSel.label}
          </button>
        </div>
      )}

      {/* Enter transition: ซูมหลุมดำเมื่อกดเมนู */}
      {bh && <BlackHole active={bh} onDone={onBhDone} />}

      {/* tarot 3D overlay (แสดงเมื่อมีไพ่) */}
      {view === 'tarot' && window.__tarotCards && window.__tarotCards.length > 0 && (
        <div style={{ position: 'fixed', bottom: 20, left: 0, right: 0, height: 320, zIndex: 5, pointerEvents: 'none' }}>
          <Tarot3D cards={window.__tarotCards} />
        </div>
      )}

      {/* Intro: Cosmic BG (หน้าโหลด) → Glitter Wrap warp → หน้า landing */}
      <Intro onDone={() => setIntroDone(true)} />
    </>
  )
}
