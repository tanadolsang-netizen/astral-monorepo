import { useRef, useMemo } from 'react'
import { Canvas, useFrame } from '@react-three/fiber'
import * as THREE from 'three'

/*
  Glitter Wrap clone (originkit spec):
  particleCount, density, starSize, focalDepth, turbulence, brightness,
  glitterIntensity, trailAmount, reverse, speed, color1/2/3
  → starfield warp tunnel ที่ใช้ตอน transition ระหว่าง view
*/

function Warp({ active, onDone, props }) {
  const {
    particleCount = 500, density = 100, starSize = 20, focalDepth = 8,
    turbulence = 0, brightness = 100, glitterIntensity = 3, trailAmount = 0.6,
    reverse = false, speed = 5, color1 = '#ffe9b0', color2 = '#c9a84c', color3 = '#7a6aff'
  } = props || {}

  const N = Math.min(1000, particleCount)
  const stars = useMemo(() => {
    const arr = []
    const cols = [new THREE.Color(color1), new THREE.Color(color2), new THREE.Color(color3)]
    for (let i = 0; i < N; i++) {
      const ang = Math.random() * Math.PI * 2
      const rad = Math.random() * density
      arr.push({
        x: Math.cos(ang) * rad, y: Math.sin(ang) * rad, z: Math.random() * 1000,
        c: cols[i % 3], s: (Math.random() * 0.6 + 0.4),
        tw: Math.random() * 100, sp: 0.6 + Math.random() * 0.8
      })
    }
    return arr
  }, [N, density, color1, color2, color3])

  const ptsRef = useRef()
  const matRef = useRef()
  const tRef = useRef(0)
  const doneRef = useRef(false)

  useFrame((_, dt) => {
    tRef.current += dt
    const t = tRef.current
    if (ptsRef.current) {
      const pos = ptsRef.current.geometry.attributes.position.array
      const col = ptsRef.current.geometry.attributes.color.array
      const sz = ptsRef.current.geometry.attributes.aSize.array
      const glit = ptsRef.current.geometry.attributes.aGlit.array
      for (let i = 0; i < N; i++) {
        const st = stars[i]
        // warp: z ลดลงเรื่อยๆ (reverse → เพิ่ม) ผ่าน focalDepth
        let z = st.z - t * speed * st.sp * 60
        if (!reverse) { while (z < 1) z += 1000 } else { while (z > 1000) z -= 1000 }
        // turbulence wobble
        const wob = turbulence ? Math.sin(t * 2 + st.tw) * turbulence * 12 : 0
        const sc = focalDepth * 60 / (z + focalDepth * 6)
        pos[i*3]   = (st.x + wob) * sc
        pos[i*3+1] = (st.y + wob) * sc
        pos[i*3+2] = -z * 0.01
        const tw = 0.6 + 0.4 * Math.sin(t * 6 + st.tw)
        const gl = glitterIntensity > 0 ? (Math.random() < glitterIntensity * 0.004 ? 2.2 : 1) : 1
        col[i*3]   = st.c.r * tw * gl
        col[i*3+1] = st.c.g * tw * gl
        col[i*3+2] = st.c.b * tw * gl
        sz[i] = starSize * 0.01 * sc * st.s
        glit[i] = gl
      }
      ptsRef.current.geometry.attributes.position.needsUpdate = true
      ptsRef.current.geometry.attributes.color.needsUpdate = true
      ptsRef.current.geometry.attributes.aSize.needsUpdate = true
    }
    if (matRef.current) matRef.current.opacity = (brightness / 100)
    // จบ warp หลัง ~0.9s
    if (active && !doneRef.current && t > 0.9) { doneRef.current = true; onDone && onDone() }
  })

  const geo = useMemo(() => {
    const g = new THREE.BufferGeometry()
    g.setAttribute('position', new THREE.BufferAttribute(new Float32Array(N * 3), 3))
    g.setAttribute('color', new THREE.BufferAttribute(new Float32Array(N * 3), 3))
    g.setAttribute('aSize', new THREE.BufferAttribute(new Float32Array(N), 1))
    g.setAttribute('aGlit', new THREE.BufferAttribute(new Float32Array(N), 1))
    return g
  }, [N])

  return (
    <points ref={ptsRef} geometry={geo}>
      <pointsMaterial ref={matRef} size={starSize * 0.02} vertexColors transparent
        blending={THREE.AdditiveBlending} depthWrite={false} opacity={brightness/100}
        sizeAttenuation />
    </points>
  )
}

export default function GlitterWarp({ active, onDone, props }) {
  return (
    <Canvas orthographic camera={{ position: [0, 0, 100], zoom: 1, near: 0.1 }} dpr={[1, 2]}
      gl={{ antialias: true, alpha: true, preserveDrawingBuffer: false }}>
      <Warp active={active} onDone={onDone} props={props} />
    </Canvas>
  )
}
