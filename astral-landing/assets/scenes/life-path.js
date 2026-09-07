/* ═══════════════════════════════════════════════════════════════
   ASTRAL — Life Path 3D Scene
   A winding 3D path through stars with planetary transit
   markers, current position, and glowing intensity.
   ═══════════════════════════════════════════════════════════════ */

const LifePath = (() => {
  let scene, camera, renderer, group, pathMarkers = [], path;
  let animId, container, hintEl;
  let disposed = false;
  let currentT = 0;

  const TRANSITS = [
    { name: 'Jupiter Return', year: 0, desc: 'A year of growth and expansion' },
    { name: 'Saturn Opposition', year: 3, desc: 'A time of responsibility and testing' },
    { name: 'Chiron Return', year: 7, desc: 'Healing old wounds and rediscovering purpose' },
    { name: 'Uranus Opposition', year: 12, desc: 'Breaking free from old patterns' },
    { name: 'Neptune Square', year: 16, desc: 'Spiritual awakening and confusion' },
    { name: 'Pluto Square', year: 20, desc: 'Deep transformation and rebirth' },
    { name: 'Second Jupiter Return', year: 24, desc: 'A new cycle of wisdom and expansion' }
  ];

  function init(containerEl) {
    disposed = false;
    container = containerEl;
    currentT = 0;
    const w = container.clientWidth;
    const h = container.clientHeight;

    scene = new THREE.Scene();
    camera = new THREE.PerspectiveCamera(50, w / h, 0.1, 100);
    camera.position.set(0, 3, 10);

    renderer = new THREE.WebGLRenderer({ antialias: true, alpha: true });
    renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
    renderer.setSize(w, h);
    renderer.toneMapping = THREE.ACESFilmicToneMapping;
    container.appendChild(renderer.domElement);

    // Lights
    scene.add(new THREE.AmbientLight(0x404060, 0.5));
    const key = new THREE.PointLight(0xffd97a, 1.5, 25);
    key.position.set(3, 5, 5);
    scene.add(key);
    const rim = new THREE.PointLight(0x8b7bff, 0.8, 15);
    rim.position.set(-3, 2, -3);
    scene.add(rim);

    group = new THREE.Group();
    scene.add(group);

    // Create winding path
    const pathPoints = [];
    const pathCount = 200;
    for (let i = 0; i <= pathCount; i++) {
      const t = i / pathCount;
      pathPoints.push(getPathPos(t));
    }
    const pathGeo = new THREE.BufferGeometry().setFromPoints(pathPoints);
    const pathMat = new THREE.LineBasicMaterial({ color: 0x8a7b50, transparent: true, opacity: 0.4 });
    path = new THREE.Line(pathGeo, pathMat);
    group.add(path);

    // Path glow (using a thicker mesh)
    const glowGeo = new THREE.TubeGeometry(new THREE.CatmullRomCurve3(pathPoints), 200, 0.08, 8, false);
    const glowMat = new THREE.MeshBasicMaterial({ color: 0xc9a84c, transparent: true, opacity: 0.15 });
    const glowMesh = new THREE.Mesh(glowGeo, glowMat);
    group.add(glowMesh);

    // Create transit markers
    TRANSITS.forEach((transit, i) => {
      const t = transit.year / 24;
      const pos = getPathPos(t);
      const marker = createMarker(transit, t, pos, i);
      pathMarkers.push(marker);
      group.add(marker.mesh);
    });

    // Starfield background
    const starGeo = new THREE.BufferGeometry();
    const sCount = 1000;
    const sPos = new Float32Array(sCount * 3);
    for (let i = 0; i < sCount; i++) {
      sPos[i * 3] = (Math.random() - 0.5) * 50;
      sPos[i * 3 + 1] = (Math.random() - 0.5) * 30;
      sPos[i * 3 + 2] = (Math.random() - 0.5) * 50;
    }
    starGeo.setAttribute('position', new THREE.BufferAttribute(sPos, 3));
    const starMat = new THREE.PointsMaterial({ color: 0xffffff, size: 0.08, transparent: true, opacity: 0.7, blending: THREE.AdditiveBlending });
    scene.add(new THREE.Points(starGeo, starMat));

    // Current position indicator
    const indicator = new THREE.Mesh(
      new THREE.SphereGeometry(0.2, 16, 16),
      new THREE.MeshBasicMaterial({ color: 0x66ff66 })
    );
    indicator.position.copy(getPathPos(0));
    group.add(indicator);
    group.userData.indicator = indicator;

    // Light beam from indicator
    const beamGeo = new THREE.CylinderGeometry(0.05, 0.15, 3, 8);
    const beamMat = new THREE.MeshBasicMaterial({ color: 0x66ff66, transparent: true, opacity: 0.3 });
    const beam = new THREE.Mesh(beamGeo, beamMat);
    beam.position.y = 1.5;
    indicator.add(beam);

    // Hint
    hintEl = document.createElement('div');
    hintEl.className = 'scene-hint';
    hintEl.textContent = 'Click markers to see transit meanings';
    container.appendChild(hintEl);

    // Click handler
    const raycaster = new THREE.Raycaster();
    const mouse = new THREE.Vector2();
    renderer.domElement.addEventListener('click', (e) => {
      const rect = renderer.domElement.getBoundingClientRect();
      mouse.x = ((e.clientX - rect.left) / rect.width) * 2 - 1;
      const my = -((e.clientY - rect.top) / rect.height) * 2 + 1;
      mouse.y = my;
      raycaster.setFromCamera(mouse, camera);
      const hits = raycaster.intersectObjects(pathMarkers.map(m => m.mesh), true);
      if (hits.length > 0) {
        let obj = hits[0].object;
        while (obj.parent && !obj.userData.transit) obj = obj.parent;
        if (obj.userData.transit) showTransitInfo(obj.userData.transit);
      }
    });

    animate();
  }

  function getPathPos(t) {
    return new THREE.Vector3(
      Math.sin(t * Math.PI * 3) * 4,
      Math.cos(t * Math.PI * 2) * 1.5 + t * 2,
      -t * 20 + 10
    );
  }

  function createMarker(transit, t, pos, index) {
    const intensity = 0.5 + Math.random() * 0.5;
    const color = new THREE.Color().setHSL(0.1 + intensity * 0.1, 0.8, 0.6);

    const mesh = new THREE.Mesh(
      new THREE.SphereGeometry(0.15 + intensity * 0.15, 16, 16),
      new THREE.MeshStandardMaterial({
        color,
        emissive: color,
        emissiveIntensity: 0.3 + intensity * 0.5,
        metalness: 0.7,
        roughness: 0.3
      })
    );
    mesh.position.copy(pos);
    mesh.userData = { transit, t, intensity, index };

    // Outer glow
    const glow = new THREE.Mesh(
      new THREE.SphereGeometry(0.3 + intensity * 0.2, 12, 12),
      new THREE.MeshBasicMaterial({ color, transparent: true, opacity: 0.15 + intensity * 0.15 })
    );
    mesh.add(glow);

    return { mesh, transit, t, intensity };
  }

  function showTransitInfo(transit) {
    if (!hintEl) return;
    hintEl.textContent = `${transit.name} (Year ${transit.year}): ${transit.desc}`;
    hintEl.style.opacity = '1';
    clearTimeout(hintEl._t);
    hintEl._t = setTimeout(() => { hintEl.style.opacity = '0.5'; }, 3500);
  }

  function animate() {
    if (disposed) return;
    animId = requestAnimationFrame(animate);
    const t = performance.now() * 0.001;

    // Pulse markers based on intensity
    pathMarkers.forEach((marker, i) => {
      const pulse = 1 + Math.sin(t * 2 + i) * 0.2 * marker.intensity;
      marker.mesh.scale.setScalar(pulse);
    });

    // Move indicator slowly along path
    currentT = (currentT + 0.0003) % 1;
    const indicator = group.userData.indicator;
    if (indicator) {
      indicator.position.copy(getPathPos(currentT));
      indicator.rotation.y = t * 2;
    }

    // Slow camera sway
    camera.position.x = Math.sin(t * 0.1) * 1.5;
    camera.lookAt(getPathPos(currentT));

    renderer.render(scene, camera);
  }

  function dispose() {
    disposed = true;
    cancelAnimationFrame(animId);
    pathMarkers = [];
    if (renderer) {
      renderer.dispose();
      container?.removeChild(renderer.domElement);
    }
    if (hintEl) hintEl.remove();
    scene = camera = renderer = group = null;
  }

  return { init, dispose };
})();
