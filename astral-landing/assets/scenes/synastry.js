/* ═══════════════════════════════════════════════════════════════
   ASTRAL — Synastry 3D Scene
   Two golden orbits intersecting (representing two people),
   aspect lines in 3D space, flowing particles.
   ═══════════════════════════════════════════════════════════════ */

const SynastryScene = (() => {
  let scene, camera, renderer, group, orbitA, orbitB, particles = [], aspectLines = [];
  let animId, container;
  let disposed = false;

  const ASPECT_COLORS = [
    0x66ff66, // conjunction
    0x66b3ff, // trine
    0xff6666, // square
    0xffcc66, // opposition
    0xcc88ff  // sextile
  ];

  function init(containerEl) {
    disposed = false;
    container = containerEl;
    const w = container.clientWidth;
    const h = container.clientHeight;

    scene = new THREE.Scene();
    camera = new THREE.PerspectiveCamera(50, w / h, 0.1, 100);
    camera.position.set(0, 4, 9);

    renderer = new THREE.WebGLRenderer({ antialias: true, alpha: true });
    renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
    renderer.setSize(w, h);
    renderer.toneMapping = THREE.ACESFilmicToneMapping;
    container.appendChild(renderer.domElement);

    // Lights
    scene.add(new THREE.AmbientLight(0x404060, 0.5));
    const key = new THREE.PointLight(0xffd97a, 1.5, 20);
    key.position.set(4, 5, 4);
    scene.add(key);

    group = new THREE.Group();
    scene.add(group);

    // Two orbits
    orbitA = createOrbit(3.0, 0.02, 0xffd97a, [0.2, 0.1, 0]);
    orbitB = createOrbit(3.0, 0.02, 0x88bbff, [-0.2, -0.1, 0.3]);
    group.add(orbitA.group);
    group.add(orbitB.group);

    // Person cores
    const coreA = new THREE.Mesh(
      new THREE.SphereGeometry(0.3, 20, 20),
      new THREE.MeshStandardMaterial({ color: 0xffd97a, emissive: 0xc9a84c, emissiveIntensity: 0.5, metalness: 0.8, roughness: 0.2 })
    );
    coreA.position.copy(orbitA.points[0]);
    group.add(coreA);

    const coreB = new THREE.Mesh(
      new THREE.SphereGeometry(0.3, 20, 20),
      new THREE.MeshStandardMaterial({ color: 0x88bbff, emissive: 0x4488cc, emissiveIntensity: 0.5, metalness: 0.8, roughness: 0.2 })
    );
    coreB.position.copy(orbitB.points[50]);
    group.add(coreB);

    // Aspect lines
    for (let i = 0; i < 30; i++) {
      const idxA = Math.floor(Math.random() * 100);
      const idxB = Math.floor(Math.random() * 100);
      const color = ASPECT_COLORS[Math.floor(Math.random() * ASPECT_COLORS.length)];
      const line = createAspectLine(orbitA.points[idxA], orbitB.points[idxB], color);
      aspectLines.push(line);
      group.add(line);
    }

    // Flowing particles
    for (let i = 0; i < 200; i++) {
      const p = createParticle(orbitA, orbitB);
      particles.push(p);
      group.add(p.mesh);
    }

    animate();
  }

  function createOrbit(radius, thickness, color, rotation) {
    const points = [];
    for (let i = 0; i < 100; i++) {
      const t = (i / 100) * Math.PI * 2;
      points.push(new THREE.Vector3(
        Math.cos(t) * radius,
        Math.sin(t * 2) * 0.3,
        Math.sin(t) * radius
      ));
    }
    const geo = new THREE.BufferGeometry().setFromPoints(points);
    const mat = new THREE.LineBasicMaterial({ color, transparent: true, opacity: 0.7 });
    const line = new THREE.Line(geo, mat);
    line.rotation.set(...rotation);
    return { group: line, points, rotation, radius };
  }

  function createAspectLine(start, end, color) {
    const geo = new THREE.BufferGeometry().setFromPoints([start, end]);
    const mat = new THREE.LineBasicMaterial({ color, transparent: true, opacity: 0.4 + Math.random() * 0.4 });
    return new THREE.Line(geo, mat);
  }

  function createParticle(orbitA, orbitB) {
    const mesh = new THREE.Mesh(
      new THREE.SphereGeometry(0.04, 8, 8),
      new THREE.MeshBasicMaterial({ color: Math.random() > 0.5 ? 0xffd97a : 0x88bbff })
    );
    return { mesh, t: Math.random(), speed: 0.002 + Math.random() * 0.004, orbitA, orbitB };
  }

  function animate() {
    if (disposed) return;
    animId = requestAnimationFrame(animate);
    const t = performance.now() * 0.001;

    group.rotation.y = t * 0.05;

    // Animate particles flowing between orbits
    particles.forEach(p => {
      p.t += p.speed;
      if (p.t > 1) p.t = 0;
      const aIdx = Math.floor(p.t * 99);
      const bIdx = Math.floor(((p.t + 0.5) % 1) * 99);
      p.mesh.position.lerpVectors(p.orbitA.points[aIdx], p.orbitB.points[bIdx], Math.sin(p.t * Math.PI));
    });

    // Pulse aspect lines
    aspectLines.forEach((line, i) => {
      line.material.opacity = 0.3 + Math.sin(t * 2 + i) * 0.3;
    });

    camera.position.x = Math.sin(t * 0.1) * 2;
    camera.lookAt(0, 0, 0);

    renderer.render(scene, camera);
  }

  function dispose() {
    disposed = true;
    cancelAnimationFrame(animId);
    particles = [];
    aspectLines = [];
    if (renderer) {
      renderer.dispose();
      container?.removeChild(renderer.domElement);
    }
    scene = camera = renderer = group = null;
  }

  return { init, dispose };
})();
