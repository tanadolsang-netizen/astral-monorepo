import { useRef, useMemo, useEffect } from 'react'
import { Canvas, useFrame } from '@react-three/fiber'
import * as THREE from 'three'

const GLYPHS = ['☉','☽','☿','♀','♂','♃','♄','♅','♆','♇','⚭','⚮']

function makeCardTexture(card, glyph, flipped) {
  const c = document.createElement('canvas'); c.width = 256; c.height = 420
  const x = c.getContext('2d')
  const g = x.createLinearGradient(0, 0, 0, 420)
  g.addColorStop(0, '#f6f0e2'); g.addColorStop(1, '#e7dcc2'); x.fillStyle = g; x.fillRect(0, 0, 256, 420)
  x.strokeStyle = '#9a7b34'; x.lineWidth = 8; x.strokeRect(14, 14, 228, 392)
  x.strokeStyle = 'rgba(154,123,52,.5)'; x.lineWidth = 2; x.strokeRect(26, 26, 204, 368)
  x.fillStyle = '#2e2818'; x.textAlign = 'center'; x.font = 'bold 22px Cinzel, serif'
  x.fillText(card, 128, 200)
  x.font = '64px serif'; x.fillStyle = '#9a7b34'; x.fillText(glyph, 128, 290)
  if (flipped) { x.font = '12px serif'; x.fillStyle = '#7a1f2b'; x.fillText('reversed', 128, 360) }
  const t = new THREE.CanvasTexture(c); t.anisotropy = 4; return t
}

function Cards({ cards }) {
  const ref = useRef()
  const stateRef = useRef([])
  const { meshes, mats } = useMemo(() => {
    const n = Math.max(3, cards.length || 3)
    const ms = [], mt = []
    for (let i = 0; i < n; i++) {
      const card = cards[i] || {}
      const nm = (card.card ? card.card.replace(' of ', ' แห่ง ') : 'ไพ่')
      const gph = GLYPHS[i % 12]
      const texF = makeCardTexture(nm, gph, false)
      const texB = makeCardTexture(nm, gph, true)
      const front = new THREE.MeshStandardMaterial({ map: texF, roughness: .6, metalness: .2 })
      const back = new THREE.MeshStandardMaterial({ map: texB, roughness: .6, metalness: .2 })
      mt.push(front, back)
      ms.push({ geo: new THREE.BoxGeometry(1.5, 2.5, 0.06), front, back, name: nm })
      stateRef.current[i] = { target: Math.PI, cur: Math.PI }
    }
    return { meshes: ms, mats: mt }
  }, [cards])

  useFrame(() => {
    stateRef.current.forEach((s, i) => {
      s.cur += (s.target - s.cur) * 0.12
      if (ref.current && ref.current.children[i]) ref.current.children[i].rotation.y = s.cur
    })
  })

  useEffect(() => {
    const t = setTimeout(() => stateRef.current.forEach(s => s.target = 0), 500)
    window.__flipTarot3D = (i) => { if (stateRef.current[i]) stateRef.current[i].target = stateRef.current[i].target > Math.PI/2 ? Math.PI : 0 }
    return () => { clearTimeout(t); window.__flipTarot3D = null }
  }, [])

  return (
    <group ref={ref}>
      {meshes.map((m, i) => (
        <mesh key={i} position={[(i - (meshes.length-1)/2) * 1.95, 0, 0]} geometry={m.geo} rotation={[0, Math.PI, 0]}>
          <meshStandardMaterial attach="material-0" map={m.back} />
          <meshStandardMaterial attach="material-1" map={m.back} />
          <meshStandardMaterial attach="material-2" map={m.back} />
          <meshStandardMaterial attach="material-3" map={m.back} />
          <meshStandardMaterial attach="material-4" map={m.front} />
          <meshStandardMaterial attach="material-5" map={m.front} />
        </mesh>
      ))}
    </group>
  )
}

export default function Tarot3D({ cards }) {
  return (
    <Canvas camera={{ position: [0, 0, 9], fov: 50 }} dpr={[1, 2]} gl={{ antialias: true, alpha: true }}>
      <ambientLight intensity={0.9} />
      <directionalLight position={[3, 5, 6]} intensity={0.8} color="#ffe9b0" />
      <Cards cards={cards} />
    </Canvas>
  )
}
