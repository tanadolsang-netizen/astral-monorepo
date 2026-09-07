import { useRef, useEffect, useMemo, useState } from 'react'
import { Canvas, useFrame, useThree } from '@react-three/fiber'
import { Text, Billboard, Environment, Lightformer } from '@react-three/drei'
import { EffectComposer, Bloom, Vignette } from '@react-three/postprocessing'
import * as THREE from 'three'
import gsap from 'gsap'

const GOLD = '#c9a84c'
const GOLD_BRIGHT = '#f6e4b0'
const GOLD_DEEP = '#8a6a24'

/* ── ambient hum: two detuned sine oscillators through a lowpass, no audio file needed ── */
function useAmbientHum() {
  useEffect(() => {
    let handle
    try {
      const Ctx = window.AudioContext || window.webkitAudioContext
      const ctx = new Ctx()
      const gain = ctx.createGain()
      const filter = ctx.createBiquadFilter()
      filter.type = 'lowpass'
      filter.frequency.value = 420
      const osc1 = ctx.createOscillator()
      const osc2 = ctx.createOscillator()
      osc1.type = 'sine'; osc1.frequency.value = 55
      osc2.type = 'sine'; osc2.frequency.value = 55.6
      osc1.connect(filter); osc2.connect(filter); filter.connect(gain); gain.connect(ctx.destination)
      gain.gain.value = 0
      osc1.start(); osc2.start()
      gain.gain.linearRampToValueAtTime(0.035, ctx.currentTime + 2.5)
      const resume = () => { if (ctx.state === 'suspended') ctx.resume() }
      window.addEventListener('pointerdown', resume, { once: true })
      window.addEventListener('keydown', resume, { once: true })
      handle = { ctx, gain, osc1, osc2, resume }
    } catch {
      // Web Audio unavailable — skip the hum silently.
    }
    return () => {
      if (!handle) return
      const { ctx, gain, osc1, osc2, resume } = handle
      window.removeEventListener('pointerdown', resume)
      window.removeEventListener('keydown', resume)
      try {
        gain.gain.cancelScheduledValues(ctx.currentTime)
        gain.gain.linearRampToValueAtTime(0, ctx.currentTime + 0.4)
        setTimeout(() => { osc1.stop(); osc2.stop(); ctx.close() }, 450)
      } catch {
        /* already closed */
      }
    }
  }, [])
}

/* ── custom-shader starfield: 5000 points, per-star twinkle, additive soft dots ── */
const STAR_VERTEX = /* glsl */ `
  attribute float aScale;
  attribute float aPhase;
  attribute float aSpeed;
  uniform float uTime;
  uniform float uPixelRatio;
  varying float vTwinkle;
  void main() {
    vTwinkle = 0.5 + 0.5 * sin(uTime * aSpeed + aPhase);
    vec4 mvPosition = modelViewMatrix * vec4(position, 1.0);
    gl_PointSize = aScale * uPixelRatio * (45.0 / -mvPosition.z);
    gl_Position = projectionMatrix * mvPosition;
  }
`
const STAR_FRAGMENT = /* glsl */ `
  uniform float uOpacity;
  uniform vec3 uColor;
  varying float vTwinkle;
  void main() {
    float d = length(gl_PointCoord - 0.5);
    float alpha = smoothstep(0.5, 0.0, d);
    gl_FragColor = vec4(uColor, alpha * alpha * vTwinkle * uOpacity);
  }
`

/* ── soft radial glow quad (no hard rectangle edges) used behind the logo ── */
const GLOW_VERTEX = /* glsl */ `
  varying vec2 vUv;
  void main() {
    vUv = uv;
    gl_Position = projectionMatrix * modelViewMatrix * vec4(position, 1.0);
  }
`
const GLOW_FRAGMENT = /* glsl */ `
  uniform vec3 uColor;
  uniform float uOpacity;
  varying vec2 vUv;
  void main() {
    float d = length(vUv - 0.5) * 2.0;
    float alpha = smoothstep(1.0, 0.0, d);
    gl_FragColor = vec4(uColor, alpha * alpha * uOpacity);
  }
`

function StarField({ matRef }) {
  const COUNT = 5200
  const [positions, scales, phases, speeds] = useMemo(() => {
    const pos = new Float32Array(COUNT * 3)
    const scale = new Float32Array(COUNT)
    const phase = new Float32Array(COUNT)
    const speed = new Float32Array(COUNT)
    for (let i = 0; i < COUNT; i++) {
      const r = 22 + Math.random() * 75
      const theta = Math.random() * Math.PI * 2
      const phi = Math.acos(2 * Math.random() - 1)
      pos[i * 3] = r * Math.sin(phi) * Math.cos(theta)
      pos[i * 3 + 1] = r * Math.sin(phi) * Math.sin(theta)
      pos[i * 3 + 2] = r * Math.cos(phi)
      scale[i] = 1.1 + Math.random() * 2.4
      phase[i] = Math.random() * Math.PI * 2
      speed[i] = 0.4 + Math.random() * 1.8
    }
    return [pos, scale, phase, speed]
  }, [])

  useFrame((state) => {
    if (matRef.current) matRef.current.uniforms.uTime.value = state.clock.elapsedTime
  })

  return (
    <points>
      <bufferGeometry>
        <bufferAttribute attach="attributes-position" args={[positions, 3]} />
        <bufferAttribute attach="attributes-aScale" args={[scales, 1]} />
        <bufferAttribute attach="attributes-aPhase" args={[phases, 1]} />
        <bufferAttribute attach="attributes-aSpeed" args={[speeds, 1]} />
      </bufferGeometry>
      <shaderMaterial
        ref={matRef}
        transparent
        depthWrite={false}
        blending={THREE.AdditiveBlending}
        vertexShader={STAR_VERTEX}
        fragmentShader={STAR_FRAGMENT}
        uniforms={{
          uTime: { value: 0 },
          uOpacity: { value: 0 },
          uPixelRatio: { value: Math.min(window.devicePixelRatio, 2) },
          uColor: { value: new THREE.Color('#fff3d6') },
        }}
      />
    </points>
  )
}

/* ── golden icosahedron core: assembles via GSAP scale, spins continuously ── */
function GoldCore({ groupRef, glowRef }) {
  const meshRef = useRef()
  useFrame((_, dt) => {
    if (!meshRef.current) return
    meshRef.current.rotation.y += dt * 0.18
    meshRef.current.rotation.x += dt * 0.05
  })
  return (
    <group ref={groupRef} scale={0}>
      <mesh ref={meshRef}>
        <icosahedronGeometry args={[1, 0]} />
        <meshStandardMaterial color="#d9b25f" emissive={GOLD_DEEP} emissiveIntensity={0.32} metalness={0.92} roughness={0.28} />
      </mesh>
      <mesh ref={glowRef} scale={1.7}>
        <sphereGeometry args={[1, 24, 24]} />
        <meshBasicMaterial color="#ffdf9b" transparent opacity={0} blending={THREE.AdditiveBlending} depthWrite={false} />
      </mesh>
    </group>
  )
}

/* ── three Saturn-like rings at different tilts, independent spin speeds ── */
const RING_DEFS = [
  { radius: 1.7, tube: 0.02, tilt: [Math.PI / 2.4, 0, 0], color: GOLD_BRIGHT, spin: 0.32 },
  { radius: 2.05, tube: 0.015, tilt: [Math.PI / 2.1, 0.5, 0.1], color: GOLD, spin: -0.22 },
  { radius: 2.42, tube: 0.012, tilt: [Math.PI / 1.75, -0.35, 0.25], color: '#8f7233', spin: 0.48 },
]

function OrbitRings({ ringRefs }) {
  useFrame((_, dt) => {
    RING_DEFS.forEach((def, i) => {
      const r = ringRefs[i].current
      if (r) r.rotation.z += dt * def.spin
    })
  })
  return (
    <>
      {RING_DEFS.map((def, i) => (
        <mesh key={i} ref={ringRefs[i]} rotation={def.tilt}>
          <torusGeometry args={[def.radius, def.tube, 16, 100]} />
          <meshStandardMaterial color={def.color} emissive={def.color} emissiveIntensity={0.3} transparent opacity={0} />
        </mesh>
      ))}
    </>
  )
}

/* ── ASTRAL wordmark: troika Text w/ a gold-gradient material patched via onBeforeCompile, plus a pulsing glow plane ── */
function LogoMark({ material, glowRef }) {
  const glowUniforms = useMemo(() => ({
    uColor: { value: new THREE.Color('#ffdf9b') },
    uOpacity: { value: 0 },
  }), [])
  useFrame((state) => {
    const g = glowRef.current
    if (g?.userData.active) {
      glowUniforms.uOpacity.value = 0.22 + Math.sin(state.clock.elapsedTime * 2.2) * 0.1
    }
  })
  return (
    <Billboard position={[0, -2.3, 0]}>
      <mesh ref={glowRef} scale={[3.6, 1.2, 1]}>
        <planeGeometry args={[1, 1]} />
        <shaderMaterial
          transparent
          depthWrite={false}
          blending={THREE.AdditiveBlending}
          vertexShader={GLOW_VERTEX}
          fragmentShader={GLOW_FRAGMENT}
          uniforms={glowUniforms}
        />
      </mesh>
      <Text
        material={material}
        font="/fonts/Cinzel-SemiBold.ttf"
        fontSize={0.5}
        letterSpacing={0.22}
        anchorX="center"
        anchorY="middle"
      >
        ASTRAL
      </Text>
    </Billboard>
  )
}

/* ── choreography: builds refs, wires the master GSAP timeline, drives the cinematic camera orbit + warp ── */
function Experience({ setPhase, onDone }) {
  const { camera } = useThree()

  const starMatRef = useRef()
  const coreGroupRef = useRef()
  const coreGlowRef = useRef()
  const ringRefs = [useRef(), useRef(), useRef()]
  const logoGlowRef = useRef()
  const bloomRef = useRef()
  const orbit = useRef({ angle: 0.6, radius: 6.4, warping: false })

  const logoMaterial = useMemo(() => {
    const mat = new THREE.MeshStandardMaterial({
      color: GOLD_BRIGHT,
      emissive: GOLD,
      emissiveIntensity: 0.45,
      metalness: 0.5,
      roughness: 0.35,
      transparent: true,
      opacity: 0,
    })
    mat.onBeforeCompile = (shader) => {
      shader.vertexShader = shader.vertexShader
        .replace('#include <common>', '#include <common>\nvarying vec3 vGradPos;')
        .replace('#include <begin_vertex>', '#include <begin_vertex>\nvGradPos = position;')
      shader.fragmentShader = shader.fragmentShader
        .replace('#include <common>', '#include <common>\nvarying vec3 vGradPos;')
        .replace(
          '#include <dithering_fragment>',
          `#include <dithering_fragment>
          gl_FragColor.rgb = mix(vec3(0.788, 0.659, 0.298), vec3(0.965, 0.894, 0.690), clamp(vGradPos.x * 0.6 + 0.55, 0.0, 1.0));`
        )
    }
    return mat
  }, [])

  useFrame(() => {
    if (orbit.current.warping) return
    orbit.current.angle += 0.0022
    const { angle, radius } = orbit.current
    camera.position.x = Math.sin(angle) * radius
    camera.position.z = Math.cos(angle) * radius
    camera.position.y = 0.6 + Math.sin(angle * 0.5) * 0.4
    camera.lookAt(0, 0, 0)
  })

  useEffect(() => {
    const ctx = gsap.context(() => {
      const tl = gsap.timeline({ delay: 0.2 })

      // 1. stars fade in
      tl.to(starMatRef.current.uniforms.uOpacity, { value: 1, duration: 1.6, ease: 'power1.out' }, 0)
        // 2. icosahedron assembles from scale 0, back ease
        .to(coreGroupRef.current.scale, { x: 1, y: 1, z: 1, duration: 1.3, ease: 'back.out(1.7)' }, 0.5)
        .to(coreGlowRef.current.material, { opacity: 0.32, duration: 1.0 }, 0.9)
        // 3. rings fade in (they're already spinning via useFrame)
        .to(ringRefs[0].current.material, { opacity: 0.6, duration: 1.0 }, 1.0)
        .to(ringRefs[1].current.material, { opacity: 0.5, duration: 1.0 }, 1.15)
        .to(ringRefs[2].current.material, { opacity: 0.4, duration: 1.0 }, 1.3)
        // 4. logo fades in with glow pulse
        .to(logoMaterial, { opacity: 1, duration: 0.9 }, 2.1)
        .call(() => { logoGlowRef.current.userData.active = true }, [], 2.1)
        .call(() => setPhase('orbit'), [], 2.1)
        // 5. camera already orbiting continuously — hold on the scene
        // 6. after 4s total: "prepare for takeoff"
        .call(() => setPhase('takeoffText'), [], 4.0)
        // 7. warp zoom into the core
        .addLabel('warp', 5.6)
        .call(() => { orbit.current.warping = true }, [], 'warp')
        .to(camera.position, { x: 0, y: 0, z: 0.55, duration: 1.05, ease: 'power3.in' }, 'warp')
        .to(camera, { fov: 18, duration: 1.05, ease: 'power3.in', onUpdate: () => camera.updateProjectionMatrix() }, 'warp')
        .to(coreGroupRef.current.scale, { x: 9, y: 9, z: 9, duration: 1.05, ease: 'power3.in' }, 'warp')
        .to(bloomRef.current, { intensity: 4, duration: 1.05 }, 'warp')
        .call(() => setPhase('flash'), [], 'warp+=0.65')
        .call(() => onDone && onDone(), [], 'warp+=1.1')
    })
    return () => ctx.revert()
  }, [camera, logoMaterial, onDone, setPhase])

  return (
    <>
      <color attach="background" args={['#05030c']} />
      <ambientLight intensity={0.4} />
      <pointLight position={[0, 0, 6]} intensity={1.1} color="#ffd97a" />
      <pointLight position={[-4, 2, -3]} intensity={0.4} color="#8b7bff" />

      <Environment resolution={64}>
        <Lightformer intensity={0.9} color="#ffdca8" position={[0, 3, 2]} scale={[4, 1, 1]} />
        <Lightformer intensity={0.4} color="#6a5acd" position={[-3, -2, -3]} rotation={[0, Math.PI / 3, 0]} scale={[3, 1, 1]} />
      </Environment>

      <StarField matRef={starMatRef} />
      <GoldCore groupRef={coreGroupRef} glowRef={coreGlowRef} />
      <OrbitRings ringRefs={ringRefs} />
      <LogoMark material={logoMaterial} glowRef={logoGlowRef} />

      <EffectComposer multisampling={0}>
        <Bloom ref={bloomRef} intensity={0.6} luminanceThreshold={0.35} luminanceSmoothing={0.3} mipmapBlur />
        <Vignette eskil={false} offset={0.15} darkness={0.85} />
      </EffectComposer>
    </>
  )
}

export default function Intro({ onDone }) {
  const [phase, setPhase] = useState('boot')
  useAmbientHum()

  return (
    <div className="intro-root">
      <Canvas camera={{ position: [0, 0.6, 6.4], fov: 55 }} dpr={[1, 2]} gl={{ antialias: true, powerPreference: 'high-performance' }}>
        <Experience setPhase={setPhase} onDone={onDone} />
      </Canvas>

      <div className={`intro-overlay ${phase === 'takeoffText' || phase === 'flash' ? 'show' : ''}`}>
        <div className="intro-overlay-title">✦ PREPARE FOR TAKEOFF ✦</div>
        <div className="intro-overlay-sub">THE COSMIC SYSTEM</div>
      </div>

      <div className={`intro-flash ${phase === 'flash' ? 'active' : ''}`} />
    </div>
  )
}
