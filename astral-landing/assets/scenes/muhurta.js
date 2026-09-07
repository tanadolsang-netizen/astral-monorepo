/* ═══════════════════════════════════════════════════════════════
   ASTRAL — Muhurta Timeline 3D Scene
   A 3D timeline stretching into the distance with golden
   nodes representing auspicious times, scroll to travel.
   ═══════════════════════════════════════════════════════════════ */

const MuhurtaScene = (() => {
  let scene, camera, renderer, group, nodes = [], pathLine, currentMarker;
  let animId, container, hintEl;
  let disposed = false;
  let scrollProgress = 0;

  const MONTHS = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'];

  function init(containerEl) {
    disposed = false;
    container = containerEl;
    scrollProgress = 0;
    const w = container.clientWidth;
    const h = container.clientHeight;

    scene = new THREE.Scene();
    camera = new THREE.PerspectiveCamera(50, w / h, 0.1, 100);
    camera.position.set(0, 2, 8);

    renderer = new THREE.WebGLRenderer({ antialias: true, alpha: true });
    renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
    renderer.setSize(w, h);
    renderer.toneMapping = THREE.ACESFilmicToneMapping;
    container.appendChild(renderer.domElement);

    // Lights
    scene.add(new THREE.AmbientLight(0x404060, 0.5));
    const key = new THREE.PointLight(0xffd97a, 1.5, 25);
    key.position.set(0, 5, 5);
    scene.add(key);

    group = new THREE.Group();
    scene.add(group);

    // Create timeline path
    const pathPoints = [];
    for (let i = 0; i <= 100; i++) {
      const t = i / 100;
      pathPoints.push(new THREE.Vector3(
        Math.sin(t * Math.PI * 2) * 2,
        Math.cos(t * Math.PI * 4) * 0.5,
        -t * 15 + 5
      ));
    }
    const pathGeo = new THREE.BufferGeometry().setFromPoints(pathPoints);
    const pathMat = new THREE.LineBasicMaterial({ color: 0x8a7b50, transparent: true, opacity: 0.5 });
    pathLine = new THREE.Line(pathGeo, pathMat);
    group.add(pathLine);

    // Create auspicious nodes
    for (let i = 0; i < 24; i++) {
      const t = i / 24;
      const pos = getPathPoint(t);
      const isAuspicious = Math.random() > 0.4;
      const node = createNode(t, pos, isAuspicious);
      nodes.push(node);
      group.add(node.mesh);
    }

    // Current time marker
    currentMarker = new THREE.Mesh(
      new THREE.SphereGeometry(0.15, 16, 16),
      new THREE.MeshBasicMaterial({ color: 0x66ff66 })
    );
    currentMarker.position.copy(getPathPoint(0));
    group.add(currentMarker);

    // Glow ring around current
    const glowRing = new THREE.Mesh(
      new THREE.TorusGeometry(0.3, 0.02, 8, 32),
      new THREE.MeshBasicMaterial({ color: 0x66ff66, transparent: true, opacity: 0.6 })
    );
    currentMarker.add(glowRing);

    // Hint
    hintEl = document.createElement('div');
    hintEl.className = 'scene-hint';
    hintEl.textContent = 'Scroll to travel through time • Green nodes are auspicious';
    container.appendChild(hintEl);

    // Scroll handler
    container.addEventListener('wheel', onWheel, { passive: true });

    animate();
  }

  function getPathPoint(t) {
    return new THREE.Vector3(
      Math.sin(t * Math.PI * 2) * 2,
      Math.cos(t * Math.PI * 4) * 0.5,
      -t * 15 + 5
    );
  }

  function createNode(t, pos, isAuspicious) {
    const color = isAuspicious ? 0x66ff66 : 0xffcc66;
    const mesh = new THREE.Mesh(
      new THREE.SphereGeometry(isAuspicious ? 0.12 : 0.08, 12, 12),
      new THREE.MeshStandardMaterial({
        color,
        emissive: color,
        emissiveIntensity: 0.4,
        metalness: 0.6,
        roughness: 0.3
      })
    );
    mesh.position.copy(pos);
    mesh.userData = { t, isAuspicious, baseY: pos.y };

    // Glow for auspicious
    if (isAuspicious) {
      const glow = new THREE.Mesh(
        new THREE.SphereGeometry(0.2, 12, 12),
        new THREE.MeshBasicMaterial({ color, transparent: true, opacity: 0.2 })
      );
      mesh.add(glow);
    }

    return { mesh, t, isAuspicious };
  }

  function onWheel(e) {
    scrollProgress = Math.max(0, Math.min(1, scrollProgress + e.deltaY * 0.0005));
  }

  function animate() {
    if (disposed) return;
    animId = requestAnimationFrame(animate);
    const t = performance.now() * 0.001;

    // Move current marker along path
    const markerT = scrollProgress;
    currentMarker.position.copy(getPathPoint(markerT));
    currentMarker.rotation.z = t;

    // Pulse nodes
    nodes.forEach((node, i) => {
      const pulse = Math.sin(t * 2 + i) * 0.1 + 1;
      node.mesh.scale.setScalar(pulse);

      // Float
      node.mesh.position.y = node.mesh.userData.baseY + Math.sin(t + i * 0.5) * 0.05;
    });

    // Camera follows marker
    const camTarget = getPathPoint(markerT);
    camera.position.x += (camTarget.x - camera.position.x) * 0.05;
    camera.position.y += (camTarget.y + 2 - camera.position.y) * 0.05;
    camera.lookAt(camTarget);

    renderer.render(scene, camera);
  }

  function dispose() {
    disposed = true;
    cancelAnimationFrame(animId);
    nodes = [];
    container?.removeEventListener('wheel', onWheel);
    if (renderer) {
      renderer.dispose();
      container?.removeChild(renderer.domElement);
    }
    if (hintEl) hintEl.remove();
    scene = camera = renderer = group = null;
  }

  return { init, dispose };
})();
