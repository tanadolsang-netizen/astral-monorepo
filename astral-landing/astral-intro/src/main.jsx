import React, { useState, useRef, useCallback } from 'react'
import ReactDOM from 'react-dom/client'
import Intro from './Intro.jsx'
import './index.css'

const SITE_URL = '../astral-spa.html'

function App() {
  const [revealed, setRevealed] = useState(false)
  const frameRef = useRef(null)

  const onDone = useCallback(() => {
    if (frameRef.current) frameRef.current.classList.add('revealed')
    setTimeout(() => setRevealed(true), 1200)
  }, [])

  return (
    <>
      <iframe
        ref={frameRef}
        id="site-frame"
        src={SITE_URL}
        title="Astral"
        style={{ opacity: revealed ? 1 : 0 }}
      />
      {!revealed && <Intro onDone={onDone} />}
    </>
  )
}

ReactDOM.createRoot(document.getElementById('root')).render(<App />)
