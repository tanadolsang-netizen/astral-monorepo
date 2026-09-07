/* ═══════════════════════════════════════════════════════════════
   ASTRAL — Tarot Cards 3D Scene
   78 tarot cards floating in a spiral, click to flip,
   golden cosmic card backs, selected cards glow.
   ═══════════════════════════════════════════════════════════════ */

const TarotScene = (() => {
  let scene, camera, renderer, group, cards = [];
  let animId, container, hintEl;
  let disposed = false;
  let selectedCards = [];

  const MAJOR_ARCANA = [
    { name: 'The Fool', desc: 'New beginnings, innocence' },
    { name: 'The Magician', desc: 'Manifestation, power' },
    { name: 'The High Priestess', desc: 'Intuition, mystery' },
    { name: 'The Empress', desc: 'Abundance, fertility' },
    { name: 'The Emperor', desc: 'Authority, structure' },
    { name: 'The Hierophant', desc: 'Tradition, beliefs' },
    { name: 'The Lovers', desc: 'Love, harmony' },
    { name: 'The Chariot', desc: 'Willpower, victory' },
    { name: 'Strength', desc: 'Courage, patience' },
    { name: 'The Hermit', desc: 'Soul-searching, guidance' },
    { name: 'Wheel of Fortune', desc: 'Change, cycles' },
    { name: 'Justice', desc: 'Fairness, truth' },
    { name: 'The Hanged Man', desc: 'Surrender, letting go' },
    { name: 'Death', desc: 'Transformation, endings' },
    { name: 'Temperance', desc: 'Balance, moderation' },
    { name: 'The Devil', desc: 'Bondage, materialism' },
    { name: 'The Tower', desc: 'Upheaval, revelation' },
    { name: 'The Star', desc: 'Hope, renewal' },
    { name: 'The Moon', desc: 'Illusion, fear' },
    { name: 'The Sun', desc: 'Joy, success' },
    { name: 'Judgement', desc: 'Rebirth, reckoning' },
    { name: 'The World', desc: 'Completion, accomplishment' }
  ];

  function init(containerEl) {
    disposed = false;
    container = containerEl;
    selectedCards = [];
    const w = container.clientWidth;
    const h = container.clientHeight;

    scene = new THREE.Scene();
    camera = new THREE.PerspectiveCamera(50, w / h, 0.1, 100);
    camera.position.set(0, 0, 8);

    renderer = new THREE.WebGLRenderer({ antialias: true, alpha: true });
    renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
    renderer.setSize(w, h);
    renderer.toneMapping = THREE.ACESFilmicToneMapping;
    container.appendChild(renderer.domElement);

    // Lights
    scene.add(new THREE.AmbientLight(0x606080, 0.6));
    const key = new THREE.PointLight(0xffd97a, 1.5, 20);
    key.position.set(3, 5, 5);
    scene.add(key);
    const rim = new THREE.PointLight(0x8b7bff, 0.8, 15);
    rim.position.set(-3, -2, -3);
    scene.add(rim);

    group = new THREE.Group();
    scene.add(group);

    // Create cards in a spiral
    const totalCards = 22;
    for (let i = 0; i < totalCards; i++) {
      const angle = (i / totalCards) * Math.PI * 4;
      const radius = 1.5 + (i / totalCards) * 3;
      const y = (i - totalCards / 2) * 0.15;

      const cardData = MAJOR_ARCANA[i] || { name: `Card ${i + 1}`, desc: 'A mysterious card' };
      const card = createCard(cardData, i);
      card.position.set(Math.cos(angle) * radius, y, Math.sin(angle) * radius);
      card.rotation.y = -angle + Math.PI / 2;
      card.rotation.x = Math.sin(i * 0.5) * 0.1;
      cards.push(card);
      group.add(card);
    }

    // Particles
    const particleGeo = new THREE.BufferGeometry();
    const pCount = 500;
    const pPos = new Float32Array(pCount * 3);
    for (let i = 0; i < pCount; i++) {
      pPos[i * 3] = (Math.random() - 0.5) * 20;
      pPos[i * 3 + 1] = (Math.random() - 0.5) * 15;
      pPos[i * 3 + 2] = (Math.random() - 0.5) * 20;
    }
    particleGeo.setAttribute('position', new THREE.BufferAttribute(pPos, 3));
    const particleMat = new THREE.PointsMaterial({ color: 0xffd97a, size: 0.05, transparent: true, opacity: 0.6, blending: THREE.AdditiveBlending });
    const particles = new THREE.Points(particleGeo, particleMat);
    scene.add(particles);

    // Hint
    hintEl = document.createElement('div');
    hintEl.className = 'scene-hint';
    hintEl.textContent = 'Click cards to reveal their meaning';
    container.appendChild(hintEl);

    // Click handler
    const raycaster = new THREE.Raycaster();
    const mouse = new THREE.Vector2();
    renderer.domElement.addEventListener('click', (e) => {
      const rect = renderer.domElement.getBoundingClientRect();
      mouse.x = ((e.clientX - rect.left) / rect.width) * 2 - 1;
      mouse.y = -((e.clientY - rect.top) / rect.height) * 2 + 1;
      raycaster.setFromCamera(mouse, camera);
      const hits = raycaster.intersectObjects(cards, true);
      if (hits.length > 0) {
        let cardObj = hits[0].object;
        while (cardObj.parent && !cardObj.userData.cardData) cardObj = cardObj.parent;
        if (cardObj.userData.cardData) flipCard(cardObj);
      }
    });

    animate();
  }

  function createCard(data, index) {
    const cardGroup = new THREE.Group();
    cardGroup.userData = { cardData: data, flipped: false, index };

    // Card back (golden cosmic design)
    const backGeo = new THREE.PlaneGeometry(1.0, 1.6);
    const backTex = createCardBackTexture(data.name);
    const backMat = new THREE.MeshStandardMaterial({ map: backTex, side: THREE.BackSide, metalness: 0.7, roughness: 0.3 });
    const back = new THREE.Mesh(backGeo, backMat);
    back.position.z = -0.01;
    cardGroup.add(back);

    // Card front
    const frontTex = createCardFrontTexture(data.name, data.desc);
    const frontMat = new THREE.MeshStandardMaterial({ map: frontTex, side: THREE.FrontSide });
    const front = new THREE.Mesh(backGeo.clone(), frontMat);
    front.position.z = 0.01;
    cardGroup.add(front);

    // Glow
    const glowGeo = new THREE.PlaneGeometry(1.1, 1.7);
    const glowMat = new THREE.MeshBasicMaterial({ color: 0xffd97a, transparent: true, opacity: 0, side: THREE.DoubleSide });
    const glow = new THREE.Mesh(glowGeo, glowMat);
    cardGroup.add(glow);

    return cardGroup;
  }

  function createCardBackTexture(name) {
    const canvas = document.createElement('canvas');
    canvas.width = 200;
    canvas.height = 320;
    const ctx = canvas.getContext('2d');

    // Background gradient
    const grad = ctx.createLinearGradient(0, 0, 200, 320);
    grad.addColorStop(0, '#1a1228');
    grad.addColorStop(0.5, '#0d0820');
    grad.addColorStop(1, '#1a1228');
    ctx.fillStyle = grad;
    ctx.fillRect(0, 0, 200, 320);

    // Border
    ctx.strokeStyle = '#c9a84c';
    ctx.lineWidth = 3;
    ctx.strokeRect(10, 10, 180, 300);

    // Inner border
    ctx.strokeStyle = '#8a7b50';
    ctx.lineWidth = 1;
    ctx.strokeRect(18, 18, 164, 284);

    // Stars
    for (let i = 0; i < 40; i++) {
      ctx.fillStyle = `rgba(201, 168, 76, ${0.3 + Math.random() * 0.7})`;
      ctx.beginPath();
      ctx.arc(20 + Math.random() * 160, 20 + Math.random() * 280, 0.5 + Math.random() * 2, 0, Math.PI * 2);
      ctx.fill();
    }

    // Center symbol
    ctx.fillStyle = '#c9a84c';
    ctx.font = 'bold 48px serif';
    ctx.textAlign = 'center';
    ctx.textBaseline = 'middle';
    ctx.fillText('✦', 100, 140);
    ctx.font = '14px serif';
    ctx.fillText(name, 100, 190);

    return new THREE.CanvasTexture(canvas);
  }

  function createCardFrontTexture(name, desc) {
    const canvas = document.createElement('canvas');
    canvas.width = 200;
    canvas.height = 320;
    const ctx = canvas.getContext('2d');

    // Background
    ctx.fillStyle = '#fdfaf1';
    ctx.fillRect(0, 0, 200, 320);

    // Border
    ctx.strokeStyle = '#c9a84c';
    ctx.lineWidth = 3;
    ctx.strokeRect(8, 8, 184, 304);

    // Name
    ctx.fillStyle = '#3b3324';
    ctx.font = 'bold 16px serif';
    ctx.textAlign = 'center';
    ctx.fillText(name, 100, 40);

    // Description
    ctx.font = '12px sans-serif';
    ctx.fillStyle = '#5a4a28';
    const words = desc.split(' ');
    let line = '';
    let y = 80;
    for (const word of words) {
      const test = line + word + ' ';
      if (ctx.measureText(test).width > 160) {
        ctx.fillText(line.trim(), 100, y);
        line = word + ' ';
        y += 18;
      } else {
        line = test;
      }
    }
    ctx.fillText(line.trim(), 100, y);

    // Large symbol
    ctx.fillStyle = '#c9a84c';
    ctx.font = '60px serif';
    ctx.fillText('🔮', 100, 200);

    return new THREE.CanvasTexture(canvas);
  }

  function flipCard(card) {
    if (card.userData.flipping) return;
    card.userData.flipping = true;

    const isFlipped = card.userData.flipped;
    const targetRot = isFlipped ? 0 : Math.PI;

    // Animate flip
    const start = performance.now();
    const dur = 600;
    function step() {
      const t = Math.min(1, (performance.now() - start) / dur);
      const eased = 1 - Math.pow(1 - t, 3);
      card.rotation.y = isFlipped ? Math.PI - eased * Math.PI : eased * Math.PI;

      // Glow when revealed
      const glow = card.children[2];
      if (glow) glow.material.opacity = isFlipped ? 0 : Math.sin(eased * Math.PI) * 0.3;

      if (t < 1) requestAnimationFrame(step);
      else {
        card.userData.flipped = !isFlipped;
        card.userData.flipping = false;

        // Show hint
        if (card.userData.flipped && hintEl) {
          hintEl.textContent = `${card.userData.cardData.name}: ${card.userData.cardData.desc}`;
          hintEl.style.opacity = '1';
          clearTimeout(hintEl._t);
          hintEl._t = setTimeout(() => { hintEl.style.opacity = '0.5'; }, 3000);
        }
      }
    }
    step();
  }

  function animate() {
    if (disposed) return;
    animId = requestAnimationFrame(animate);
    const t = performance.now() * 0.001;

    // Gentle float
    cards.forEach((card, i) => {
      if (!card.userData.flipping) {
        card.position.y += Math.sin(t * 0.8 + i * 0.5) * 0.002;
        card.rotation.z = Math.sin(t * 0.3 + i) * 0.02;
      }
    });

    group.rotation.y = t * 0.05;
    renderer.render(scene, camera);
  }

  function dispose() {
    disposed = true;
    cancelAnimationFrame(animId);
    cards = [];
    selectedCards = [];
    if (renderer) {
      renderer.dispose();
      container?.removeChild(renderer.domElement);
    }
    if (hintEl) hintEl.remove();
    scene = camera = renderer = group = null;
  }

  return { init, dispose };
})();
