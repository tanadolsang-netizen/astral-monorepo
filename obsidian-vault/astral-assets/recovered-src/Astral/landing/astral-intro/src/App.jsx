import { useRef, useState, useCallback } from 'react'
import Intro from './Intro.jsx'

const SITE_URL = './astral-spa.html'

export default function App(){
  const [phase, setPhase] = useState('intro') // intro -> reveal -> done
  const frameRef = useRef(null)

  const onIntroDone = useCallback(() => {
    // เปิดเผยเว็บ (iframe fade-in) แล้วซ่อน intro
    const f = frameRef.current
    if (f) f.classList.add('revealed')
    setPhase('reveal')
    // รอเฟดจบ ค่อยซ่อน intro layer
    setTimeout(() => setPhase('done'), 1300)
  }, [])

  return (
    <>
      <iframe id="site-frame" ref={frameRef} src={SITE_URL} title="Astral" />
      {phase !== 'done' && (
        <div className={'intro-root' + (phase === 'reveal' ? ' gone' : '')}>
          <Intro onDone={onIntroDone} />
        </div>
      )}
    </>
  )
}
