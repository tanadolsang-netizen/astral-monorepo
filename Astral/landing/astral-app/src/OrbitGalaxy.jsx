import { useRef, useState, useMemo } from 'react'
import { useFrame } from '@react-three/fiber'
import * as THREE from 'three'

/* ── ระบบวงโคจรดาว (BlueYard Orbit Systems — Galaxy) ──
   โหนดบนวงโคจรโคจรได้ คลิก/แตะดูข้อมูล + ไปหน้าฟีเจอร์นั้น
   ใส่ใน <Canvas> เดียวกับ CosmicScene (single WebGL context) */

export const ORBIT_NODES = [
  { id:'natal',    label:'ดวงชะตา',  color:'#ffd97a', r:2.4, speed:0.20, phase:0.0,
    desc:'วันเกิดของท่าน คือเข็มทิศชี้ทางมาเกิด — เราจะบอกว่าท่านมีของดีซ่อนที่ไหน และอุปสรรคที่ฟ้าฝากมาให้ฝ่าฟัน' },
  { id:'tarot',    label:'ไพ่ทาโรต์', color:'#ff7ab0', r:3.1, speed:0.16, phase:1.1,
    desc:'จั่วไพ่ 78 ใบจากสำนักโบราณ — สิ่งที่ออกมาไม่ใช่คำทำนายเลื่อนลอย แต่เป็นเสียงที่สะท้อนสิ่งที่ท่านกังวลอยู่ในใจ' },
  { id:'synastry', label:'ดูคู่',     color:'#7a6aff', r:3.9, speed:0.13, phase:2.3,
    desc:'เมื่อดวงท่านไปพบดวงเขา หรือดวงเธอ จะเกิดกระแสไฟบางอย่าง — เราจะบอกว่าสองดวงนี้ช่วยกันหรือต้องระวังเรื่องใด' },
  { id:'vedic',    label:'เวดิก',    color:'#55b6ff', r:4.8, speed:0.10, phase:3.5,
    desc:'มองผ่านตำราโบราณอินเดีย ดาวจะเลื่อนไปตำแหน่งที่แท้จริงตามฤดูกาล — เห็นธาตุที่ท่านเกิดมาและหน้าที่ที่ฟ้าฝากไว้' },
  { id:'muhurta',  label:'มูฮูร์ตะ',  color:'#c9a84c', r:5.7, speed:0.08, phase:4.7,
    desc:'มีเรื่องสำคัญจะทำใช่ไหม — เราจะหาชั่วโมงที่ดาวยืนรับรอง ให้สิ่งที่ท่านเริ่มตั้งต้นนั้นเป็นสิริมงคล' },
  { id:'life',     label:'ชีวิตคุณ',  color:'#9affc4', r:6.6, speed:0.06, phase:5.9,
    desc:'ดาวไม่หยุดหมุน และแต่ละรอบที่มันผ่าน จะพาเหตุการณ์ใหม่มา — เราจะบอกท่านล่วงหน้าว่าเมื่อไหร่ควรก้าวไป' },
]

function Ring({ radius, color }) {
  const geo = useMemo(() => new THREE.RingGeometry(radius - 0.012, radius + 0.012, 160), [radius])
  return (
    <mesh geometry={geo} rotation={[-Math.PI / 2, 0, 0]}>
      <meshBasicMaterial color={color} transparent opacity={0.20} side={THREE.DoubleSide} toneMapped={false} />
    </mesh>
  )
}

function Node({ node, onSelect, selected }) {
  const grp = useRef()
  const [hovered, setHovered] = useState(false)
  const labelTex = useMemo(() => makeLabelTexture(node.label, node.color), [node.label, node.color])
  useFrame((s) => {
    const t = s.clock.elapsedTime
    const a = node.phase + t * node.speed
    if (grp.current) grp.current.position.set(Math.cos(a) * node.r, 0, Math.sin(a) * node.r)
  })
  const active = hovered || selected
  return (
    <group ref={grp}>
      <mesh
        onPointerOver={(e) => { e.stopPropagation(); setHovered(true); document.body.style.cursor = 'pointer' }}
        onPointerOut={() => { setHovered(false); document.body.style.cursor = 'auto' }}
        onClick={(e) => { e.stopPropagation(); onSelect(node) }}>
        <sphereGeometry args={[active ? 0.30 : 0.22, 24, 24]} />
        <meshBasicMaterial color={node.color} toneMapped={false} />
      </mesh>
      <mesh scale={active ? 1.9 : 1.4}>
        <sphereGeometry args={[0.22, 16, 16]} />
        <meshBasicMaterial color={node.color} transparent opacity={active ? 0.30 : 0.12}
          blending={THREE.AdditiveBlending} depthWrite={false} toneMapped={false} />
      </mesh>
      {/* ป้ายชื่อแบบ billboard (sprite — เรนเดอร์ใน WebGL context เดียว) */}
      <sprite scale={active ? [1.5, 0.42, 1] : [1.2, 0.34, 1]}>
        <spriteMaterial map={labelTex} transparent depthWrite={false} toneMapped={false} />
      </sprite>
    </group>
  )
}

/* สร้าง texture ป้ายชื่อจาก canvas 2D (รันครั้งเดียวต่อโหนด) */
function makeLabelTexture(text, color) {
  const c = document.createElement('canvas')
  c.width = 256; c.height = 64
  const ctx = c.getContext('2d')
  ctx.font = "600 30px 'Cinzel', serif"
  ctx.textAlign = 'center'; ctx.textBaseline = 'middle'
  ctx.shadowColor = color; ctx.shadowBlur = 14
  ctx.fillStyle = '#f6f0e2'
  ctx.fillText(text, 128, 34)
  const tex = new THREE.CanvasTexture(c)
  tex.minFilter = THREE.LinearFilter
  return tex
}

export default function OrbitGalaxy({ onSelect, selectedId, rotate = true }) {
  const root = useRef()
  useFrame((s, dt) => {
    if (rotate && root.current) root.current.rotation.y += dt * 0.04   // หมุนทั้งระบบค่อยๆ
  })
  return (
    <group ref={root} position={[0, -0.6, 0]}>
      {ORBIT_NODES.map((n) => <Ring key={'r' + n.id} radius={n.r} color={n.color} />)}
      {/* ดวงอาทิตย์ศูนย์กลาง (หลุมดำแสง) */}
      <mesh>
        <sphereGeometry args={[0.55, 32, 32]} />
        <meshBasicMaterial color="#ffe9b0" toneMapped={false} />
      </mesh>
      <mesh scale={2.2}>
        <sphereGeometry args={[0.55, 24, 24]} />
        <meshBasicMaterial color="#ffd97a" transparent opacity={0.18}
          blending={THREE.AdditiveBlending} depthWrite={false} toneMapped={false} />
      </mesh>
      {ORBIT_NODES.map((n) => (
        <Node key={n.id} node={n} onSelect={onSelect} selected={selectedId === n.id} />
      ))}
    </group>
  )
}
