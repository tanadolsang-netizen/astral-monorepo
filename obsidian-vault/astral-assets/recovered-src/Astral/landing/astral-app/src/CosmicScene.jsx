import { useRef, useMemo } from 'react'
import { useFrame } from '@react-three/fiber'
import { Stars, Cloud, Float } from '@react-three/drei'
import * as THREE from 'three'

/* ── Partikel field ระบบสุริยะ (จุดเรืองแสงเล็กๆ) ── */
function ParticleField({ zoom }) {
  const N = 6000
  const geo = useMemo(() => {
    const g = new THREE.BufferGeometry()
    const pos = new Float32Array(N * 3)
    const col = new Float32Array(N * 3)
    const c1 = new THREE.Color('#ffe9b0'), c2 = new THREE.Color('#9a7b34'),
          c3 = new THREE.Color('#7a6aff'), c4 = new THREE.Color('#55b6ff')
    for (let i = 0; i < N; i++) {
      const r = Math.pow(Math.random(), 0.6) * 9
      const a = r * 0.5 + Math.random() * Math.PI * 2
      const spiral = Math.sin(r * 0.4) * 0.6
      pos[i*3]   = Math.cos(a + spiral) * r
      pos[i*3+1] = (Math.random() - 0.5) * 1.2 * (1 - r/9)
      pos[i*3+2] = Math.sin(a + spiral) * r
      const t = Math.min(1, r/9)
      const c = c1.clone().lerp(c2, t).lerp(c3, Math.max(0,(r-4)/5)).lerp(c4, Math.random()*0.3)
      col[i*3]=c.r; col[i*3+1]=c.g; col[i*3+2]=c.b
    }
    g.setAttribute('position', new THREE.BufferAttribute(pos, 3))
    g.setAttribute('color', new THREE.BufferAttribute(col, 3))
    return g
  }, [])
  const pts = useRef()
  useFrame((s) => { if (pts.current) pts.current.rotation.y = s.clock.elapsedTime * 0.03 })
  const z = zoom?.current ?? 0
  return (
    <points ref={pts} geometry={geo}>
      <pointsMaterial size={0.06} vertexColors transparent opacity={0.9 - z*0.5}
        blending={THREE.AdditiveBlending} depthWrite={false} />
    </points>
  )
}

/* ── ดวงอาทิตย์ (zoom เข้าเมื่อ scroll ท้าย) ── */
function SolarCore({ zoom }) {
  const ref = useRef()
  useFrame(() => {
    const z = zoom?.current ?? 0
    if (ref.current) {
      const sc = 1 + z * 2.4
      ref.current.scale.set(sc, sc, sc)
      ref.current.material.opacity = 0.4 + z * 0.5
    }
  })
  return (
    <mesh ref={ref} position={[0, 0, -2]}>
      <sphereGeometry args={[1.6, 32, 32]} />
      <meshBasicMaterial color="#ffd97a" transparent blending={THREE.AdditiveBlending} depthWrite={false} />
    </mesh>
  )
}

export default function CosmicScene({ zoomRef }) {
  return (
    <>
      <color attach="background" args={['#06030d']} />
      <ambientLight intensity={0.5} />
      <pointLight position={[0, 0, 6]} intensity={1.8} color="#ffd97a" />
      {/* ดาราพื้นหลัง */}
      <Stars radius={90} depth={60} count={5000} factor={4} saturation={0} fade speed={0.6} />
      {/* เมฆระบบจักรวาล (แทน Vanta clouds แบบ 3D) */}
      <Float speed={0.4} rotationIntensity={0.15} floatIntensity={0.3}>
        <Cloud position={[-4, 2, -6]} args={[6, 2, 2]} color="#3a2a5e" opacity={0.35} speed={0.2} />
        <Cloud position={[5, -3, -8]} args={[8, 3, 3]} color="#2a1d40" opacity={0.3} speed={0.15} />
      </Float>
      <ParticleField zoom={zoomRef} />
      <SolarCore zoom={zoomRef} />
    </>
  )
}
