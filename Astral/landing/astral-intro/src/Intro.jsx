import { useRef, useEffect, useState } from 'react'
import { Canvas, useFrame, useThree } from '@react-three/fiber'
import { Text, Stars, Float, Billboard, useTexture } from '@react-three/drei'
import * as THREE from 'three'
import gsap from 'gsap'

/* ── โลโก้ ASTRA + ดาว (รูปทรง 3D ประกอบเข้าตัวอักษร) ── */
function LogoMark({ ready, onWarp }) {
  const group = useRef()
  const ring = useRef()
  const glow = useRef()
  const mat = useRef()

  useFrame((s, dt) => {
    if (ring.current) ring.current.rotation.z += dt * 0.4
    if (group.current) group.current.rotation.y = Math.sin(s.clock.elapsedTime * 0.3) * 0.15
  })

  // timeline: ประกอบ (scale 0->1) -> เรืองแสง -> takeoff warp
  useEffect(() => {
    if (!ready) return
    const g = group.current
    const tl = gsap.timeline()
    tl.fromTo(g.scale, { x: 0, y: 0, z: 0 }, { x: 1, y: 1, z: 1, duration: 1.1, ease: 'back.out(1.6)' })
      .to(glow.current.material, { opacity: 0.9, duration: 0.8 }, '-=0.3')
      .to({}, { duration: 0.8 }) // หยุดให้คนดูโลโก้
      .add(() => setTakeoff(true))
    return () => tl.kill()
  }, [ready])

  const [takeoff, setTakeoff] = useState(false)
  // เมื่อ takeoff: โลโก้พุ่งเข้าหากล้อง (warp) แล้วเรียก onWarp
  useEffect(() => {
    if (!takeoff) return
    const g = group.current
    const tl = gsap.timeline({ onComplete: onWarp })
    tl.to(g.position, { z: 6, duration: 0.7, ease: 'power3.in' })
      .to(g.scale, { x: 6, y: 6, z: 6, duration: 0.7, ease: 'power3.in' }, '<')
      .to(glow.current.material, { opacity: 0, duration: 0.5 }, '<')
    return () => tl.kill()
  }, [takeoff, onWarp])

  return (
    <group ref={group} scale={0}>
      {/* ดาว 8 แฉก (monogram) */}
      <mesh rotation={[0, 0, 0]}>
        <icosahedronGeometry args={[1.1, 0]} />
        <meshStandardMaterial ref={mat} color="#c9a84c" emissive="#9a7b34" emissiveIntensity={0.6} metalness={0.8} roughness={0.3} />
      </mesh>
      {/* วงแหวนหมุนรอบ */}
      <mesh ref={ring} rotation={[Math.PI / 2.2, 0, 0]}>
        <torusGeometry args={[1.9, 0.04, 16, 80]} />
        <meshStandardMaterial color="#f6e4b0" emissive="#c9a84c" emissiveIntensity={0.8} />
      </mesh>
      {/* เรืองแสง */}
      <mesh ref={glow}>
        <sphereGeometry args={[2.6, 24, 24]} />
        <meshBasicMaterial color="#ffd97a" transparent opacity={0} blending={THREE.AdditiveBlending} depthWrite={false} />
      </mesh>
      {/* ตัวอักษร ASTRAL */}
      <Billboard position={[0, 0, 0]}>
        <Text fontSize={0.62} color="#f6e4b0" anchorX="center" anchorY="middle"
              outlineWidth={0.01} outlineColor="#9a7b34" position={[0, 0, 1.25]}>
          ASTRAL
        </Text>
      </Billboard>
    </group>
  )
}

/* ── กล้อง warp (ดึงจาก Canvas ผ่าน Context) ── */
function Rig({ active }) {
  const { camera } = useThree()
  useEffect(() => {
    if (!active) return
    const tl = gsap.timeline()
    tl.to(camera.position, { z: 1.2, duration: 0.7, ease: 'power3.in' })
      .to(camera, { fov: 30, duration: 0.7, ease: 'power3.in', onUpdate: () => camera.updateProjectionMatrix() }, '<')
    return () => tl.kill()
  }, [active, camera])
  return null
}

function Scene({ onWarp }) {
  const [ready, setReady] = useState(false)
  const [takeoff, setTakeoff] = useState(false)
  useEffect(() => { const t = setTimeout(() => setReady(true), 300); return () => clearTimeout(t) }, [])

  return (
    <>
      <color attach="background" args={['#05030c']} />
      <ambientLight intensity={0.6} />
      <pointLight position={[0, 0, 6]} intensity={2.2} color="#ffd97a" />
      <Stars radius={80} depth={50} count={4000} factor={4} saturation={0} fade speed={1} />
      <Float speed={1.2} rotationIntensity={0.3} floatIntensity={0.4}>
        <LogoMark
          ready={ready}
          onWarp={onWarp}
        />
      </Float>
      <Rig active={takeoff} />
      {/* ข้อความ PREPARE FOR TAKEOFF เป็น Html overlay ต่างหาก (DOM) */}
    </>
  )
}

export default function Intro({ onDone }) {
  const [showText, setShowText] = useState(false)
  useEffect(() => { const t = setTimeout(() => setShowText(true), 1600); return () => clearTimeout(t) }, [])

  return (
    <div style={{ position: 'relative', width: '100%', height: '100%' }}>
      <Canvas camera={{ position: [0, 0, 6], fov: 60 }} dpr={[1, 2]} gl={{ antialias: true }}>
        <Scene onWarp={onDone} />
      </Canvas>
      {/* ข้อความบรรยาย */}
      <div style={{
        position: 'absolute', bottom: '14%', left: 0, right: 0, textAlign: 'center',
        color: '#c9a84c', fontFamily: 'Cinzel, serif', letterSpacing: '6px',
        opacity: showText ? 1 : 0, transition: 'opacity 0.8s ease', pointerEvents: 'none'
      }}>
        <div style={{ fontSize: 14 }}>✦ PREPARE FOR TAKEOFF ✦</div>
        <div style={{ fontSize: 11, opacity: 0.7, marginTop: 6, letterSpacing: 3 }}>THE COSMIC SYSTEM</div>
      </div>
    </div>
  )
}
