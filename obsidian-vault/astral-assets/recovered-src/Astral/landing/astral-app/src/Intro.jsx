import { useState, useRef, useEffect } from 'react'
import CosmicBG from './CosmicBG.jsx'
import GlitterWarp from './GlitterWarp.jsx'

/*
  Intro: Cosmic BG nebula (หน้าโหลด) → คลิก/อัตโนมัติ → Glitter Wrap warp พุ่งเข้าหน้า landing
*/
export default function Intro({ onDone }) {
  const [phase, setPhase] = useState('cosmic') // cosmic -> warp -> done
  const doneRef = useRef(false)

  // อัตโนมัตินำไป warp หลัง 3.2s (หรือคลิกเพื่อเร็วขึ้น)
  useEffect(() => {
    if (phase !== 'cosmic') return
    const t = setTimeout(() => setPhase('warp'), 3200)
    return () => clearTimeout(t)
  }, [phase])

  const startWarp = () => { if (phase === 'cosmic') setPhase('warp') }

  const onWarpDone = () => {
    if (doneRef.current) return
    doneRef.current = true
    setPhase('done')
    onDone && onDone()
  }

  // safety: ถ้า warp ไม่เรียก onDone (headless context ล้น) ให้บังคับจบใน 2.5s
  useEffect(() => {
    if (phase !== 'warp') return
    const t = setTimeout(() => onWarpDone(), 2500)
    return () => clearTimeout(t)
  }, [phase])

  if (phase === 'done') return null

  return (
    <div onClick={startWarp} style={{
      position: 'fixed', inset: 0, zIndex: 100, cursor: phase === 'cosmic' ? 'pointer' : 'default',
      background: '#05030c', overflow: 'hidden'
    }}>
      {/* Cosmic BG nebula (หายตอน warp เพื่อคืน WebGL context) */}
      <div style={{ position: 'absolute', inset: 0, opacity: phase === 'warp' ? 0 : 1, transition: 'opacity .4s', display: phase === 'warp' ? 'none' : 'block' }}>
        <CosmicBG speed={phase === 'cosmic' ? 1 : 0.2} />
      </div>

      {/* โลโก้ Astral + ข้อความ */}
      <div style={{
        position: 'absolute', inset: 0, display: 'flex', flexDirection: 'column',
        alignItems: 'center', justifyContent: 'center', pointerEvents: 'none',
        opacity: phase === 'warp' ? 0 : 1, transition: 'opacity .35s, transform .5s',
        transform: phase === 'warp' ? 'scale(1.6)' : 'scale(1)'
      }}>
        <div style={{ fontFamily: 'Cinzel, serif', fontSize: 'clamp(40px,8vw,84px)', fontWeight: 700,
          color: '#f6e4b0', letterSpacing: '8px', textShadow: '0 0 30px rgba(201,168,76,.6)' }}>ASTRAL</div>
        <div style={{ marginTop: 14, fontSize: 13, letterSpacing: 6, color: '#c9a84c', opacity: .85 }}>
          ✦ PREPARE FOR TAKEOFF ✦</div>
        <div style={{ marginTop: 6, fontSize: 11, letterSpacing: 3, color: '#8a7b9e' }}>THE COSMIC SYSTEM</div>
      </div>

      {/* Glitter Wrap warp พุ่งเข้าหน้า landing */}
      {phase === 'warp' && (
        <div style={{ position: 'absolute', inset: 0 }}>
          <GlitterWarp active onDone={onWarpDone} props={{
            particleCount: 800, density: 130, starSize: 28, focalDepth: 11,
            turbulence: 1.8, brightness: 100, glitterIntensity: 5, trailAmount: 0.8,
            reverse: false, speed: 9, color1: '#ffe9b0', color2: '#c9a84c', color3: '#7a6aff'
          }} />
        </div>
      )}
    </div>
  )
}
