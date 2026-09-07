import { useRef, useEffect } from 'react'
import * as THREE from 'three'
import gsap from 'gsap'

const SITE_URL = './astral-spa.html'

export default function App() {
  const mountRef = useRef(null)
  const frameRef = useRef(null)

  useEffect(() => {
    const mount = mountRef.current
    if (!mount) return

    // ── Renderer ──
    const renderer = new THREE.WebGLRenderer({ antialias: true, alpha: true })
    renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2))
    renderer.setSize(window.innerWidth, window.innerHeight)
    renderer.toneMapping = THREE.ACESFilmicToneMapping
    renderer.toneMappingExposure = 1.2
    mount.appendChild(renderer.domElement)

    // ── Scene & Camera ──
    const scene = new THREE.Scene()
    const camera = new THREE.PerspectiveCamera(60, window.innerWidth / window.innerHeight, 0.1, 100)
    camera.position.set(0, 0, 6)

    // ── Lights ──
    const ambient = new THREE.AmbientLight(0x404060, 0.6)
    scene.add(ambient)
    const pointLight = new THREE.PointLight(0xffd97a, 2.5, 30)
    pointLight.position.set(0, 0, 6)
    scene.add(pointLight)
    const rimLight = new THREE.PointLight(0x8b7bff, 1.5, 20)
    rimLight.position.set(-5, 3, -3)
    scene.add(rimLight)

    // ── Starfield ──
    const starGeo = new THREE.BufferGeometry()
    const starCount = 3000
    const starPos = new Float32Array(starCount * 3)
    for (let i = 0; i < starCount * 3; i += 3) {
      starPos[i] = (Math.random() - 0.5) * 80
      starPos[i + 1] = (Math.random() - 0.5) * 80
      starPos[i + 2] = (Math.random() - 0.5) * 80
    }
    starGeo.setAttribute('position', new THREE.BufferAttribute(starPos, 3))
    const starMat = new THREE.PointsMaterial({ color: 0xffffff, size: 0.08, transparent: true, opacity: 0.8 })
    const stars = new THREE.Points(starGeo, starMat)
    scene.add(stars)

    // ── Logo Group ──
    const logoGroup = new THREE.Group()
    logoGroup.scale.set(0, 0, 0)
    scene.add(logoGroup)

    // Icosahedron core
    const coreGeo = new THREE.IcosahedronGeometry(1.1, 0)
    const coreMat = new THREE.MeshStandardMaterial({
      color: 0xc9a84c, emissive: 0x9a7b34, emissiveIntensity: 0.6,
      metalness: 0.8, roughness: 0.3
    })
    const core = new THREE.Mesh(coreGeo, coreMat)
    logoGroup.add(core)

    // Torus ring
    const ringGeo = new THREE.TorusGeometry(1.9, 0.04, 16, 80)
    const ringMat = new THREE.MeshStandardMaterial({
      color: 0xf6e4b0, emissive: 0xc9a84c, emissiveIntensity: 0.8
    })
    const ring = new THREE.Mesh(ringGeo, ringMat)
    ring.rotation.x = Math.PI / 2.2
    logoGroup.add(ring)

    // Glow sphere
    const glowGeo = new THREE.SphereGeometry(2.6, 24, 24)
    const glowMat = new THREE.MeshBasicMaterial({
      color: 0xffd97a, transparent: true, opacity: 0,
      blending: THREE.AdditiveBlending, depthWrite: false
    })
    const glow = new THREE.Mesh(glowGeo, glowMat)
    logoGroup.add(glow)

    // ── Animation ──
    let animId
    const clock = new THREE.Clock()
    const animate = () => {
      animId = requestAnimationFrame(animate)
      const dt = clock.getDelta()
      const t = clock.getElapsedTime()

      ring.rotation.z += dt * 0.4
      logoGroup.rotation.y = Math.sin(t * 0.3) * 0.15
      logoGroup.rotation.x = Math.sin(t * 0.2) * 0.05
      stars.rotation.y += dt * 0.02

      renderer.render(scene, camera)
    }
    animate()

    // ── GSAP Timeline ──
    const tl = gsap.timeline()
    tl.to(logoGroup.scale, { x: 1, y: 1, z: 1, duration: 1.1, ease: 'back.out(1.6)' })
      .to(glowMat, { opacity: 0.9, duration: 0.8 }, '-=0.3')
      .to({}, { duration: 0.8 }) // pause
      .to(logoGroup.position, { z: 6, duration: 0.7, ease: 'power3.in' })
      .to(logoGroup.scale, { x: 6, y: 6, z: 6, duration: 0.7, ease: 'power3.in' }, '<')
      .to(glowMat, { opacity: 0, duration: 0.5 }, '<')
      .to(camera.position, { z: 1.2, duration: 0.7, ease: 'power3.in' }, '<')
      .to(camera, { fov: 30, duration: 0.7, ease: 'power3.in', onUpdate: () => camera.updateProjectionMatrix() }, '<')
      .add(() => {
        // Reveal iframe + fade intro
        if (frameRef.current) frameRef.current.classList.add('revealed')
        mount.classList.add('gone')
      })

    // ── Resize ──
    const onResize = () => {
      camera.aspect = window.innerWidth / window.innerHeight
      camera.updateProjectionMatrix()
      renderer.setSize(window.innerWidth, window.innerHeight)
    }
    window.addEventListener('resize', onResize)

    return () => {
      cancelAnimationFrame(animId)
      window.removeEventListener('resize', onResize)
      renderer.dispose()
      mount.removeChild(renderer.domElement)
    }
  }, [])

  return (
    <>
      <iframe ref={frameRef} id="site-frame" src={SITE_URL} title="Astral" />
      <div ref={mountRef} className="intro-root" />
    </>
  )
}
