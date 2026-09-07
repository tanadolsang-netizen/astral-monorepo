/* ═══════════════════════════════════════════════════════════════
   ASTRAL — Natal Wheel 3D Scene
   A golden astrological wheel with 12 zodiac segments,
   rotating 3D ring with orbiting planets.
   ═══════════════════════════════════════════════════════════════ */

const NatalWheel = (() => {
  let scene, camera, renderer, wheel, planets = [], zodiacMeshes = [];
  let animId, container, hintEl;
  let disposed = false;

  const ZODIAC = [
    { sym: '♈', name: 'Aries' }, { sym: '♉', name: 'Taurus' },
    { sym: '♊', name: 'Gemini' }, { sym: '♋', name: 'Cancer' },
    { sym: '♌', name: 'Leo' }, { sym: '♍', name: 'Virgo' },
    { sym: '♎', name: 'Libra' }, { sym: '♏', name: 'Scorpio' },
    { sym: '♐', name: 'Sagittarius' }, { sym: '♑', name: 'Capricorn' },
    { sym: '♒', name: 'Aquarius' }, { sym: '♓', name: 'Pisces' }
  ];

  const PLANETS = [
    { name: 'Sun', color: 0xffd97a, size: 0.32, speed: 0.15, radius: 2.2 },
    { name: 'Moon', color: 0xdcdcdc, size: 0.22, speed: 0.35, radius: 2.7 },
    { name: 'Mercury', color: 0xc9a84c, size: 0.16, speed: 0.6, radius: 3.1 },
    { name: 'Venus', color: 0xff9966, size: 0.20, speed: 0.45, radius: 3.5 },
    { name: 'Mars', color: 0xcc4444, size: 0.18, speed: 0.3, radius: 3.9 },
    { name: 'Jupiter', color: 0xddaa77, size: 0.26, speed: 0.12, radius: 4.4 },
    { name: 'Saturn', color: 0xccbb88, size: 0.24, speed: 0.08, radius: 4.9 }
  ];

  function init(containerEl) {
    disposed = false;
    container = containerEl;
    const w = container.clientWidth;
    const h = container.clientHeight;

    scene = new THREE.Scene();
    camera = new THREE.PerspectiveCamera(50, w / h, 0.1, 100);
    camera.position.set(0, 3.5, 8);
    camera.lookAt(0, 0, 0);

    renderer = new THREE.WebGLRenderer({ antialias: true, alpha: true });
    renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
    renderer.setSize(w, h);
    renderer.toneMapping = THREE.ACESFilmicToneMapping;
    container.appendChild(renderer.domElement);

    // Lights
    scene.add(new THREE.AmbientLight(0x404060, 0.5));
    const key = new THREE.PointLight(0xffd97a, 1.8, 20);
    key.position.set(3, 5, 4);
    scene.add(key);
    const rim = new THREE.PointLight(0x8b7bff, 0.8, 15);
    rim.position.set(-4, 2, -3);
    scene.add(rim);

    // Build wheel
    wheel = new THREE.Group();
    scene.add(wheel);

    // Outer ring
    const outerRing = new THREE.Mesh(
      new THREE.TorusGeometry(5.5, 0.04, 16, 100),
      new THREE.MeshStandardMaterial({ color: 0xc9a84c, emissive: 0x9a7b34, emissiveIntensity: 0.4, metalness: 0.8, roughness: 0.3 })
    );
    wheel.add(outerRing);

    // Zodiac segments
    const segGeo = new THREE.RingGeometry(4.8, 5.5, 32);
    ZODIAC.forEach((z, i) => {
      const mat = new THREE.MeshStandardMaterial({
        color: i % 2 === 0 ? 0x1a1228 : 0x161024,
        side: THREE.DoubleSide,
        transparent: true,
        opacity: 0.85
      });
      const seg = new THREE.Mesh(segGeo, mat);
      seg.rotation.z = (i / 12) * Math.PI * 2;
      seg.rotation.x = -Math.PI / 2;
      wheel.add(seg);
      zodiacMeshes.push(seg);
    });

    // Zodiac symbols (using sprites with canvas texture)
    ZODIAC.forEach((z, i) => {
      const tex = makeTextTexture(z.sym, 64, '#c9a84c');
      const spriteMat = new THREE.SpriteMaterial({ map: tex, transparent: true });
      const sprite = new THREE.Sprite(spriteMat);
      const angle = (i / 12) * Math.PI * 2 + Math.PI / 12;
      sprite.position.set(Math.cos(angle) * 5.15, 0, Math.sin(angle) * 5.15);
      sprite.scale.set(0.5, 0.5, 1);
      wheel.add(sprite);
    });

    // Inner rings
    [2.9, 3.7, 4.6].forEach((r, i) => {
      const ring = new THREE.Mesh(
        new THREE.TorusGeometry(r, 0.015, 8, 80),
        new THREE.MeshStandardMaterial({ color: 0x8a7b50, transparent: true, opacity: 0.4 })
      );
      ring.rotation.x = Math.PI / 2;
      wheel.add(ring);
    });

    // Core sphere
    const core = new THREE.Mesh(
      new THREE.SphereGeometry(0.6, 24, 24),
      new THREE.MeshStandardMaterial({ color: 0xffd97a, emissive: 0xc9a84c, emissiveIntensity: 0.6, metalness: 0.9, roughness: 0.2 })
    );
    wheel.add(core);

    // Planets
    PLANETS.forEach(p => {
      const mesh = new THREE.Mesh(
        new THREE.SphereGeometry(p.size, 16, 16),
        new THREE.MeshStandardMaterial({ color: p.color, emissive: p.color, emissiveIntensity: 0.3, metalness: 0.7, roughness: 0.3 })
      );
      mesh.userData = { ...p, angle: Math.random() * Math.PI * 2 };
      scene.add(mesh);
      planets.push(mesh);

      // Orbit ring
      const orbit = new THREE.Mesh(
        new THREE.TorusGeometry(p.radius, 0.008, 8, 80),
        new THREE.MeshBasicMaterial({ color: p.color, transparent: true, opacity: 0.15 })
      );
      orbit.rotation.x = Math.PI / 2;
      scene.add(orbit);
    });

    // Hint text
    hintEl = document.createElement('div');
    hintEl.className = 'scene-hint';
    hintEl.textContent = 'Click a planet to see its meaning';
    container.appendChild(hintEl);

    // Click handler
    const raycaster = new THREE.Raycaster();
    const mouse = new THREE.Vector2();
    renderer.domElement.addEventListener('click', (e) => {
      const rect = renderer.domElement.getBoundingClientRect();
      mouse.x = ((e.clientX - rect.left) / rect.width) * 2 - 1;
      mouse.y = -((e.clientY - rect.top) / rect.height) * 2 + 1;
      raycaster.setFromCamera(mouse, camera);
      const hits = raycaster.intersectObjects(planets);
      if (hits.length > 0) {
        const p = hits[0].object.userData;
        showPlanetInfo(p);
      }
    });

    animate();
  }

  function makeTextTexture(text, size, color) {
    const canvas = document.createElement('canvas');
    canvas.width = canvas.height = size;
    const ctx = canvas.getContext('2d');
    ctx.fillStyle = color;
    ctx.font = `bold ${size * 0.7}px serif`;
    ctx.textAlign = 'center';
    ctx.textBaseline = 'middle';
    ctx.fillText(text, size / 2, size / 2);
    return new THREE.CanvasTexture(canvas);
  }

  function showPlanetInfo(p) {
    if (!hintEl) return;
    hintEl.textContent = `${p.name} — orbiting at ${p.radius.toFixed(1)} AU`;
    hintEl.style.opacity = '1';
    clearTimeout(hintEl._t);
    hintEl._t = setTimeout(() => { hintEl.style.opacity = '0.5'; }, 2500);
  }

  function animate() {
    if (disposed) return;
    animId = requestAnimationFrame(animate);
    const t = performance.now() * 0.001;

    // Rotate wheel slowly
    wheel.rotation.y = t * 0.05;

    // Orbit planets
    planets.forEach(p => {
      p.userData.angle += p.userData.speed * 0.01;
      p.position.x = Math.cos(p.userData.angle) * p.userData.radius;
      p.position.z = Math.sin(p.userData.angle) * p.userData.radius;
      p.position.y = Math.sin(t * 0.5 + p.userData.radius) * 0.15;
    });

    renderer.render(scene, camera);
  }

  function dispose() {
    disposed = true;
    cancelAnimationFrame(animId);
    planets = [];
    zodiacMeshes = [];
    if (renderer) {
      renderer.dispose();
      container?.removeChild(renderer.domElement);
    }
    if (hintEl) hintEl.remove();
    scene = camera = renderer = wheel = null;
  }

  return { init, dispose };
})();
