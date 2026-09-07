import { useMemo } from 'react'

/* ── Natal Chart Wheel (SVG) ──
   รับ chart จาก /v1/natal/compute (houses, bodies, ascendant, midheaven)
   วาดวงล้อ 360°: ริมนอก=ราศี 12, แบ่งบ้าน 12, จุดดาวตาม absolute_deg */

const SIGNS = ['Aries','Taurus','Gemini','Cancer','Leo','Virgo','Libra','Scorpio','Sagittarius','Capricorn','Aquarius','Pisces']
const SIGN_TH = ['เมษ','พฤษภ','เมถุน','กรกฎ','สิงห์','กันย์','ตุลย์','พิจิก','ธนู','มังกร','กุมภ์','มีน']
const SIGN_COLORS = ['#e6685f','#5fae6a','#d9b94a','#4a86e8','#e08a3c','#8a8d93','#c77fb0','#9c5fd0','#5fae9c','#a87b5a','#6fb0e0','#7a6aff']

const C = 200, R_OUT = 192, R_SIGN = 168, R_HOUSE = 120, R_BODY = 96

function polar(cx, cy, r, deg) {
  const a = (deg - 90) * Math.PI / 180
  return [cx + r * Math.cos(a), cy + r * Math.sin(a)]
}

export default function NatalWheel({ chart }) {
  if (!chart || !chart.bodies) return null
  const asc = chart.ascendant?.absolute_deg ?? 0   // ASC = 0° บนวงล้อ
  const houses = chart.houses || []

  // เส้นแบ่งราศี (ทุก 30°) — offset จาก ASC
  const signLines = SIGNS.map((_, i) => asc + i * 30)
  // เส้นแบ่งบ้าน (จาก cusps)
  const cusps = (houses && houses.cusps) ? houses.cusps : []
  const houseLines = cusps.map(h => h.absolute_deg ?? 0)
  // จุดดาว
  const bodies = chart.bodies.map(b => ({ ...b, ang: b.absolute_deg }))

  const glyphs = useMemo(() => ({
    Sun:'☉', Moon:'☽', Mercury:'☿', Venus:'♀', Mars:'♂', Jupiter:'♃', Saturn:'♄',
    Uranus:'⛢', Neptune:'♆', Pluto:'♇', ASC:'ASC', MC:'MC', NorthNode:'☊', SouthNode:'☋', Chiron:'⚷'
  }), [])

  return (
    <svg viewBox="0 0 400 400" className="natal-wheel" role="img" aria-label="Natal chart wheel">
      <circle cx={C} cy={C} r={R_OUT} fill="#0c0818" stroke="var(--gold)" strokeWidth="1.5" />
      <circle cx={C} cy={C} r={R_SIGN} fill="none" stroke="var(--gold-soft)" strokeWidth="0.8" />
      <circle cx={C} cy={C} r={R_HOUSE} fill="none" stroke="var(--gold-soft)" strokeWidth="0.8" />
      <circle cx={C} cy={C} r={R_BODY} fill="#06030d" stroke="var(--gold-soft)" strokeWidth="0.6" />

      {/* ริมนอก: ชื่อราศี + สี */}
      {signLines.map((deg, i) => {
        const [x1,y1] = polar(C,C,R_SIGN,deg)
        const [x2,y2] = polar(C,C,R_OUT,deg)
        const [tx,ty] = polar(C,C,(R_SIGN+R_OUT)/2,deg+15)
        return (
          <g key={'s'+i}>
            <line x1={x1} y1={y1} x2={x2} y2={y2} stroke="var(--gold-soft)" strokeWidth="0.6" />
            <text x={tx} y={ty} fill={SIGN_COLORS[i]} fontSize="11" textAnchor="middle"
                  dominantBaseline="middle" fontFamily="Cinzel, serif">{SIGN_TH[i]}</text>
          </g>
        )
      })}

      {/* เส้นแบ่งบ้าน (ในวง R_HOUSE→R_SIGN) */}
      {houseLines.map((deg, i) => {
        const [x1,y1] = polar(C,C,R_HOUSE,deg)
        const [x2,y2] = polar(C,C,R_SIGN,deg)
        const [hx,hy] = polar(C,C,R_HOUSE-9,deg)
        return (
          <g key={'h'+i}>
            <line x1={x1} y1={y1} x2={x2} y2={y2} stroke="rgba(201,168,76,.5)" strokeWidth="0.7" />
            <text x={hx} y={hy} fill="#cbb8d6" fontSize="9" textAnchor="middle"
                  dominantBaseline="middle">{i+1}</text>
          </g>
        )
      })}

      {/* จุดดาว */}
      {bodies.map((b, i) => {
        const [x,y] = polar(C,C,R_BODY-6,b.ang)
        const g = glyphs[b.body] || b.body[0]
        const col = b.body === 'ASC' ? '#f6e4b0' : (b.body === 'Moon' ? '#cde' : (b.body==='Sun'?'#ffd97a':'#e8dcc0'))
        return (
          <g key={'b'+i}>
            <circle cx={x} cy={y} r="9" fill="#06030d" stroke={col} strokeWidth="1" />
            <text x={x} y={y} fill={col} fontSize="11" textAnchor="middle" dominantBaseline="central">{g}</text>
          </g>
        )
      })}

      {/* ศูนย์กลาง: ชื่อ */}
      <text x={C} y={C-6} fill="var(--gold-bright)" fontSize="12" textAnchor="middle"
            fontFamily="Cinzel, serif">{chart.name || ''}</text>
      <text x={C} y={C+10} fill="#cbb8d6" fontSize="9" textAnchor="middle">{chart.system==='sidereal'?'Sidereal':'Tropical'}</text>
    </svg>
  )
}
