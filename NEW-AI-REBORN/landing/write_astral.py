import os

html = """<!DOCTYPE html>
<html lang="th">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Astral | ระบบสุริยะ</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Cinzel:wght@400;500;600;700;800;900&family=Noto+Sans+Thai:wght@200;300;400;500;600&display=swap" rel="stylesheet">
<style>
:root{--gold:#ffd700;--purple:#c084fc;--pink:#ff6b9d;--blue:#60a5fa;--bg:#020008;--text:#f0e6d3;--text-dim:rgba(240,230,211,0.5)}
*{margin:0;padding:0;box-sizing:border-box}
html{scrollbar-width:none;-ms-overflow-style:none}
html::-webkit-scrollbar{display:none}
body{background:var(--bg);color:var(--text);font-family:'Noto Sans Thai',sans-serif;overflow-x:hidden;cursor:none}
.cursor-dot{position:fixed;width:8px;height:8px;background:var(--gold);border-radius:50%;pointer-events:none;z-index:10000;transform:translate(-50%,-50%);mix-blend-mode:difference;opacity:0}
.cursor-ring{position:fixed;width:40px;height:40px;border:1.5px solid rgba(255,215,0,0.4);border-radius:50%;pointer-events:none;z-index:9999;transform:translate(-50%,-50%);transition:transform .15s ease-out,width .3s,height .3s,opacity .3s;opacity:0}
.cursor-ring.hover{width:70px;height:70px;border-color:rgba(255,107,157,.6)}
.preloader{position:fixed;inset:0;z-index:10001;background:var(--bg);display:flex;flex-direction:column;align-items:center;justify-content:center;transition:opacity 1s,visibility 1s}
.preloader.hidden{opacity:0;visibility:hidden}
.preloader-logo{font-family:'Cinzel',serif;font-size:clamp(2.5rem,6vw,4.5rem);font-weight:900;letter-spacing:.4em;background:linear-gradient(135deg,var(--gold),var(--pink),var(--purple));-webkit-background-clip:text;-webkit-text-fill-color:transparent;background-clip:text;opacity:0;transform:translateY(30px)}
.preloader-bar-container{width:min(300px,70vw);height:2px;background:rgba(255,255,255,.1);border-radius:1px;margin-top:2rem;overflow:hidden}
.preloader-bar{height:100%;width:0%;background:linear-gradient(90deg,var(--gold),var(--pink),var(--purple));border-radius:1px;transition:width .3s}
#scene-canvas{position:fixed;top:0;left:0;width:100vw;height:100vh;z-index:0;pointer-events:none}
.aurora{position:fixed;inset:-20%;z-index:-2;background:radial-gradient(40% 50% at 20% 30%,rgba(80,20,120,.4),transparent 70%),radial-gradient(45% 55% at 80% 20%,rgba(40,10,160,.35),transparent 70%),radial-gradient(50% 60% at 60% 80%,rgba(120,30,180,.25),transparent 70%);filter:blur(80px);animation:drift 25s ease-in-out infinite alternate;pointer-events:none}
@keyframes drift{0%{transform:translate(0,0) scale(1)}50%{transform:translate(5%,-4%) scale(1.15)}100%{transform:translate(-4%,5%) scale(1.08)}}
.grain{position:fixed;inset:0;z-index:-1;opacity:.03;pointer-events:none;background-image:radial-gradient(rgba(255,255,255,.4) 1px,transparent 1px);background-size:3px 3px}
.vignette{position:fixed;inset:0;z-index:1;pointer-events:none;background:radial-gradient(ellipse at center,transparent 50%,rgba(0,0,0,.7) 100%)}
.nav{position:fixed;top:0;left:0;right:0;z-index:100;padding:1.5rem 3rem;display:flex;justify-content:space-between;align-items:center;mix-blend-mode:difference}
.nav-logo{font-family:'Cinzel',serif;font-size:1.5rem;font-weight:700;letter-spacing:.3em;color:#fff}
.nav-links{display:flex;gap:3rem;list-style:none}
.nav-links a{color:#fff;text-decoration:none;font-size:.75rem;font-weight:500;letter-spacing:.15em;text-transform:uppercase;transition:color .3s}
.nav-links a:hover{color:var(--gold)}
.section{position:relative;z-index:10;min-height:100vh;display:flex;align-items:center;justify-content:center;padding:6rem 3rem}
.hero{min-height:100vh;flex-direction:column;text-align:center}
.hero-title{font-family:'Cinzel',serif;font-size:clamp(3.5rem,10vw,8rem);font-weight:900;letter-spacing:.05em;background:linear-gradient(135deg,#fff,var(--gold),var(--pink));-webkit-background-clip:text;-webkit-text-fill-color:transparent;background-clip:text;line-height:1.1;text-shadow:0 0 60px rgba(139,92,246,.5),0 0 120px rgba(255,107,157,.3)}
.hero-subtitle{font-size:clamp(1rem,1.5vw,1.2rem);color:var(--text-dim);max-width:500px;line-height:1.8;margin-top:2rem;font-weight:300}
.hero-cta{margin-top:3rem;padding:1rem 3rem;font-family:'Noto Sans Thai',sans-serif;font-size:.85rem;font-weight:600;letter-spacing:.15em;border:1px solid var(--gold);border-radius:100px;background:transparent;color:var(--gold);cursor:none;transition:all .4s;box-shadow:0 0 30px rgba(139,92,246,.3)}
.hero-cta:hover{background:var(--gold);color:var(--bg);box-shadow:0 0 40px rgba(255,215,0,.3)}
.manifesto{flex-direction:column;text-align:center;max-width:900px}
.manifesto-text{font-family:'Cinzel',serif;font-size:clamp(1.5rem,3.5vw,2.8rem);font-weight:400;line-height:1.7;color:var(--text)}
.manifesto-sub{font-size:clamp(1rem,1.5vw,1.3rem);color:var(--gold);margin-top:2rem;font-weight:300}
.showcase-pin-wrapper{position:relative;height:300vh;z-index:10}
.showcase-pin{position:sticky;top:0;height:100vh;overflow:hidden;display:flex;align-items:center}
.showcase-track{display:flex;gap:3rem;padding-left:10vw;align-items:center;height:100%}
.showcase-card{flex-shrink:0;width:80vw;max-width:700px;height:70vh;border-radius:2rem;overflow:hidden;position:relative;display:flex;flex-direction:column;justify-content:flex-end;padding:3rem;border:1px solid rgba(255,255,255,.08);background:rgba(0,0,0,.6);backdrop-filter:blur(20px);cursor:none}
.showcase-card::before{content:'';position:absolute;inset:0;background:var(--card-grad);opacity:.6;z-index:-1}
.showcase-card-content{position:relative;z-index:2}
.showcase-card-label{font-size:.7rem;letter-spacing:.3em;text-transform:uppercase;color:var(--gold);margin-bottom:1rem}
.showcase-card-title{font-family:'Cinzel',serif;font-size:clamp(1.8rem,3vw,2.5rem);font-weight:700;margin-bottom:1rem;line-height:1.3}
.showcase-card-desc{font-size:.95rem;color:var(--text-dim);line-height:1.7;max-width:400px}
.features{flex-direction:column;text-align:center}
.features-header{margin-bottom:5rem}
.features-header h2{font-family:'Cinzel',serif;font-size:clamp(2rem,4vw,3.5rem);font-weight:700;margin-bottom:1.5rem;background:linear-gradient(135deg,#fff,var(--gold));-webkit-background-clip:text;-webkit-text-fill-color:transparent;background-clip:text;text-shadow:0 0 40px rgba(139,92,246,.4)}
.features-header p{font-size:1rem;color:var(--text-dim);max-width:500px;line-height:1.8}
.features-grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(280px,1fr));gap:1.5rem;max-width:1200px;width:100%}
.feature-card{background:rgba(255,255,255,.02);border:1px solid rgba(255,255,255,.05);border-radius:1.5rem;padding:2.5rem 2rem;transition:all .5s;cursor:none}
.feature-card:hover{background:rgba(255,255,255,.05);border-color:rgba(255,215,0,.2);transform:translateY(-5px)}
.feature-icon{font-size:2rem;margin-bottom:1.5rem;display:block}
.feature-card h3{font-family:'Cinzel',serif;font-size:1.1rem;font-weight:600;margin-bottom:.8rem}
.feature-card p{font-size:.85rem;color:var(--text-dim);line-height:1.7}
.stats{flex-direction:column;text-align:center}
.stats-header{margin-bottom:4rem}
.stats-header h2{font-family:'Cinzel',serif;font-size:clamp(2rem,4vw,3rem);font-weight:700;text-shadow:0 0 40px rgba(139,92,246,.4)}
.stats-grid{display:grid;grid-template-columns:repeat(4,1fr);gap:3rem;max-width:900px;width:100%}
.stat-item{text-align:center}
.stat-number{font-family:'Cinzel',serif;font-size:clamp(2.5rem,5vw,4rem);font-weight:800;background:linear-gradient(135deg,var(--gold),var(--pink));-webkit-background-clip:text;-webkit-text-fill-color:transparent;background-clip:text;line-height:1;margin-bottom:.5rem}
.stat-label{font-size:.8rem;color:var(--text-dim);letter-spacing:.1em}
.footer{position:relative;z-index:10;padding:4rem 3rem;border-top:1px solid rgba(255,255,255,.05);display:flex;justify-content:space-between;align-items:center;font-size:.8rem;color:var(--text-dim)}
.footer a{color:var(--gold);text-decoration:none}
.scroll-indicator{position:fixed;bottom:2rem;left:50%;transform:translateX(-50%);z-index:100;display:flex;flex-direction:column;align-items:center;gap:.5rem;color:var(--text-dim);font-size:.65rem;letter-spacing:.2em;text-transform:uppercase;animation:float 2s ease-in-out infinite}
.scroll-indicator::after{content:'';width:1px;height:40px;background:linear-gradient(to bottom,var(--gold),transparent)}
@keyframes float{0%,100%{transform:translateX(-50%) translateY(0)}50%{transform:translateX(-50%) translateY(8px)}}
@media(max-width:768px){.nav{padding:1rem 1.5rem}.nav-links{gap:1.5rem}.nav-links a{font-size:.65rem}.section{padding:4rem 1.5rem}.stats-grid{grid-template-columns:repeat(2,1fr);gap:2rem}.showcase-card{width:90vw;height:60vh}}
</style>
</head>
<body>
<div class="cursor-dot" id="cursorDot"></div>
<div class="cursor-ring" id="cursorRing"></div>
<div class="preloader" id="preloader"><div class="preloader-logo">ASTRAL</div><div class="preloader-bar-container"><div class="preloader-bar" id="preloaderBar"></div></div></div>
<canvas id="scene-canvas"></canvas>
<div class="aurora"></div><div class="grain"></div><div class="vignette"></div>
<nav class="nav"><div class="nav-logo">ASTRAL</div><ul class="nav-links"><li><a href="#manifesto">บทเปิด</a></li><li><a href="#features">สิ่งที่รออยู่</a></li></ul></nav>
<section class="section hero" id="hero"><h1 class="hero-title">Astral</h1><p class="hero-subtitle">ในเส้นทางอันกว้างใหญ่แห่งจักรวาล — ดวงดาวจะเล่าให้คุณฟัง ถ้าคุณกล้อยฟัง</p><button class="hero-cta" onclick="document.getElementById('manifesto').scrollIntoView({behavior:'smooth'})">เริ่มต้นการเดินทางของคุณ</button></section>
<section class="section manifesto" id="manifesto"><p class="manifesto-text">ก่อนที่มนุษย์จะเรียกมันว่า "โหราศาสตร์" — มันคือภาษาของดวงดาว</p><p class="manifesto-sub">และตอนนี้ ภาษานั้นกำลังรอคุณอยู่</p></section>
<div class="showcase-pin-wrapper"><div class="showcase-pin"><div class="showcase-track">
<div class="showcase-card" style="--card-grad:linear-gradient(135deg,#1a0a2e,#0d1b2a)"><div class="showcase-card-content"><div class="showcase-card-label">จุดเริ่มต้น</div><h3 class="showcase-card-title">แผนที่ดวงดาวของคุณ</h3><p class="showcase-card-desc">ทุกอย่างเริ่มต้นจากจุดเล็กๆ บนท้องฟ้า</p></div></div>
<div class="showcase-card" style="--card-grad:linear-gradient(135deg,#2e1a0a,#1a0d2e)"><div class="showcase-card-content"><div class="showcase-card-label">เมื่อดวงดาวสองดวงเดินทางมาเจอกัน</div><h3 class="showcase-card-title">ความสัมพันธ์</h3><p class="showcase-card-desc">ทำไมคนบางคนทำให้เรารู้สึกเหมือนเคยรู้จักมาก่อน</p></div></div>
<div class="showcase-card" style="--card-grad:linear-gradient(135deg,#0a2e1a,#2e0a1a)"><div class="showcase-card-content"><div class="showcase-card-label">ดวงดาวยังเคลื่อน โลกยังหมุน</div><h3 class="showcase-card-title">ดวงเคลื่อน</h3><p class="showcase-card-desc">ไม่มีวันที่ดวงดาวหยุดพัก</p></div></div>
<div class="showcase-card" style="--card-grad:linear-gradient(135deg,#1a1a2e,#2e1a2e)"><div class="showcase-card-content"><div class="showcase-card-label">ไพ่เปิดจากจักรวาล</div><h3 class="showcase-card-title">ไพ่ทาโรต์</h3><p class="showcase-card-desc">78 ใบ คือ 78 มุมมองที่ดวงดาวหยิบยื่นให้คุณ</p></div></div>
</div></div></div>
<section class="section features" id="features"><div class="features-header"><h2>สิ่งที่รอคุณอยู่</h2><p>ไม่ใช่แค่เครื่องมือ — แต่เป็นประสบการณ์ที่เปลี่ยนวิธีที่คุณมองจักรวาล</p></div><div class="features-grid">
<div class="feature-card"><span class="feature-icon">📜</span><h3>เพื่อนคู่คิด</h3><p>AI ที่เรียนรู้จากตำราโหราศาสตร์หลายพันปี</p></div>
<div class="feature-card"><span class="feature-icon">🌌</span><h3>จักรวาลในมือ</h3><p>โมเดล 3D ที่หมุนได้ ดวงดาวเคลื่อนไหวตามเวลาจริง</p></div>
<div class="feature-card"><span class="feature-icon">📖</span><h3>บันทึกชีวิตประจำวัน</h3><p>รายงานเจาะลึก 100+ หน้า</p></div>
<div class="feature-card"><span class="feature-icon">⛈️</span><h3>เสียงเรียกก่อนฝนตก</h3><p>ระบบแจ้งเตือนเมื่อดวงดาวสำคัญเคลื่อน</p></div>
</div></section>
<section class="section stats"><div class="stats-header"><h2>จักรวาลในตัวเลข</h2></div><div class="stats-grid">
<div class="stat-item"><div class="stat-number">8</div><div class="stat-label">ดาวเคละในระบบสุริยะ</div></div>
<div class="stat-item"><div class="stat-number">12</div><div class="stat-label">ราศีที่เล่าเรื่องคุณ</div></div>
<div class="stat-item"><div class="stat-number">100+</div><div class="stat-label">หน้ารายงาน</div></div>
<div class="stat-item"><div class="stat-number">∞</div><div class="stat-label">ดาวนอกระบบ</div></div>
</div></section>
<footer class="footer"><div>© 2026 Astral</div><div>ภาษาที่ดวงดาวจารซ้านไว้ให้</div></footer>
<div class="scroll-indicator">Scroll</div>
"""

# Part 2: Scripts
scripts = """
<script src="https://unpkg.com/three@0.128.0/build/three.min.js"></script>
<script src="https://unpkg.com/three@0.128.0/examples/js/postprocessing/EffectComposer.js"></script>
<script src="https://unpkg.com/three@0.128.0/examples/js/postprocessing/RenderPass.js"></script>
<script src="https://unpkg.com/three@0.128.0/examples/js/postprocessing/UnrealBloomPass.js"></script>
<script src="https://unpkg.com/three@0.128.0/examples/js/postprocessing/ShaderPass.js"></script>
<script src="https://unpkg.com/three@0.128.0/examples/js/shaders/CopyShader.js"></script>
<script src="https://unpkg.com/three@0.128.0/examples/js/shaders/LuminosityHighPassShader.js"></script>
<script src="https://cdnjs.cloudflare.com/ajax/libs/gsap/3.12.2/gsap.min.js"></script>
<script src="https://cdnjs.cloudflare.com/ajax/libs/gsap/3.12.2/ScrollTrigger.min.js"></script>
<script src="https://cdn.jsdelivr.net/gh/studio-freight/lenis@1.0.29/bundled/lenis.min.js"></script>
<script>
window.addEventListener('error',(e)=>{console.warn('Global error:',e.message);return true});
window.addEventListener('unhandledrejection',(e)=>{console.warn('Unhandled:',e.reason);return true});

const hasGSAP=typeof gsap!=='undefined'&&gsap.registerPlugin;
const hasThree=typeof THREE!=='undefined';

// Cursor
const cursorDot=document.getElementById('cursorDot');
const cursorRing=document.getElementById('cursorRing');
let mouseX=0,mouseY=0,ringX=0,ringY=0;
document.addEventListener('mousemove',(e)=>{mouseX=e.clientX;mouseY=e.clientY;cursorDot.style.left=mouseX+'px';cursorDot.style.top=mouseY+'px'});
function animateCursor(){ringX+=(mouseX-ringX)*0.15;ringY+=(mouseY-ringY)*.15;cursorRing.style.left=ringX+'px';cursorRing.style.top=ringY+'px';requestAnimationFrame(animateCursor)}animateCursor();
setTimeout(()=>{cursorDot.style.opacity='1';cursorRing.style.opacity='1'},500);

// Preloader
const preloaderBar=document.getElementById('preloaderBar');
const preloader=document.getElementById('preloader');
let progress=0;
function updatePreloader(){progress+=Math.random()*15+5;if(progress>100)progress=100;preloaderBar.style.width=progress+'%';if(progress<100){setTimeout(updatePreloader,200)}else{setTimeout(()=>{preloader.classList.add('hidden');if(hasGSAP){gsap.from('.hero-title',{opacity:0,y:60,duration:1.5,ease:'power3.out'});gsap.from('.hero-subtitle',{opacity:0,y:40,duration:1.5,delay:.2,ease:'power3.out'});gsap.from('.hero-cta',{opacity:0,y:40,duration:1.2,delay:.4,ease:'power3.out'})}},500)}}
setTimeout(updatePreloader,300);

// THREE.JS
const canvas=document.getElementById('scene-canvas');
const renderer=new THREE.WebGLRenderer({canvas,antialias:true,alpha:true,powerPreference:'high-performance'});
renderer.setPixelRatio(Math.min(window.devicePixelRatio,2));
renderer.setSize(window.innerWidth,window.innerHeight);
const scene=new THREE.Scene();
scene.background=new THREE.Color(0x020008);
scene.fog=new THREE.FogExp2(0x020008,.0015);
const camera=new THREE.PerspectiveCamera(60,window.innerWidth/window.innerHeight,.1,3000);
camera.position.set(0,40,120);
renderer.toneMapping=THREE.ACESFilmicToneMapping;
renderer.toneMappingExposure=1.4;

let useComposer=false,composer=null;
try{const renderScene=new THREE.RenderPass(scene,camera);const bloomPass=new THREE.UnrealBloomPass(new THREE.Vector2(window.innerWidth,window.innerHeight),1.8,.5,.9);bloomPass.threshold=.2;bloomPass.strength=1.2;bloomPass.radius=.6;composer=new THREE.EffectComposer(renderer);composer.addPass(renderScene);composer.addPass(bloomPass);useComposer=true}catch(e){console.warn('Bloom unavailable')}

// Star texture
function createStarTexture(){const c=document.createElement('canvas');c.width=128;c.height=128;const ctx=c.getContext('2d');const g=ctx.createRadialGradient(64,64,0,64,64,64);g.addColorStop(0,'rgba(255,255,255,1)');g.addColorStop(.1,'rgba(255,255,255,.95)');g.addColorStop(.25,'rgba(230,220,255,.7)');g.addColorStop(.45,'rgba(200,170,255,.35)');g.addColorStop(.7,'rgba(140,100,220,.12)');g.addColorStop(1,'rgba(0,0,0,0)');ctx.fillStyle=g;ctx.fillRect(0,0,128,128);return new THREE.CanvasTexture(c)}
const starTexture=createStarTexture();

// Nebula
function createNebulaTexture(){const c=document.createElement('canvas');c.width=1024;c.height=1024;const ctx=c.getContext('2d');const bg=ctx.createRadialGradient(512,512,0,512,512,700);bg.addColorStop(0,'rgba(30,5,60,.8)');bg.addColorStop(.25,'rgba(20,3,40,.6)');bg.addColorStop(.5,'rgba(10,1,20,.4)');bg.addColorStop(.75,'rgba(5,0,10,.2)');bg.addColorStop(1,'rgba(0,0,0,0)');ctx.fillStyle=bg;ctx.fillRect(0,0,1024,1024);for(let i=0;i<30;i++){const x=Math.random()*1024,y=Math.random()*1024,r=100+Math.random()*300;const cols=['rgba(80,30,180,.1)','rgba(60,20,150,.09)','rgba(100,40,200,.08)','rgba(50,10,120,.08)','rgba(120,50,220,.07)'];const g=ctx.createRadialGradient(x,y,0,x,y,r);g.addColorStop(0,cols[i%cols.length]);g.addColorStop(1,'rgba(0,0,0,0)');ctx.fillStyle=g;ctx.fillRect(0,0,1024,1024)}return new THREE.CanvasTexture(c)}
const nebulaTexture=createNebulaTexture();
const nebulaMat=new THREE.MeshBasicMaterial({map:nebulaTexture,transparent:true,blending:THREE.AdditiveBlending,depthWrite:false,opacity:.7});
const nebula=new THREE.Mesh(new THREE.PlaneGeometry(2000,2000),nebulaMat);nebula.position.z=-600;scene.add(nebula);
const nebula2=new THREE.Mesh(new THREE.PlaneGeometry(1200,1200),nebulaMat.clone());nebula2.material.opacity=.5;nebula2.position.z=-300;nebula2.rotation.z=Math.PI/3;scene.add(nebula2);
const nebula3=new THREE.Mesh(new THREE.PlaneGeometry(800,800),nebulaMat.clone());nebula3.material.opacity=.3;nebula3.position.z=-100;nebula3.rotation.z=-Math.PI/5;scene.add(nebula3);

// STARFIELD - deep space layers
const starLayers=[];
[{count:5000,size:1.5,spread:800,speedX:.00008,speedY:.00004,color:0xffffff,opacity:.9},{count:3000,size:2.5,spread:600,speedX:.00015,speedY:.00008,color:0xe0d0ff,opacity:.85},{count:1500,size:4,spread:400,speedX:.0003,speedY:.00015,color:0xc8b0ff,opacity:.8},{count:500,size:6,spread:250,speedX:.0005,speedY:.00025,color:0xa080ff,opacity:.7}].forEach((cfg)=>{
  const geo=new THREE.BufferGeometry();const pos=new Float32Array(cfg.count*3);const col=new Float32Array(cfg.count*3);const base=new THREE.Color(cfg.color);
  for(let i=0;i<cfg.count;i++){pos[i*3]=(Math.random()-.5)*cfg.spread*2;pos[i*3+1]=(Math.random()-.5)*cfg.spread*2;pos[i*3+2]=(Math.random()-.5)*cfg.spread*1.5;const v=.12;col[i*3]=base.r+(Math.random()-.5)*v;col[i*3+1]=base.g+(Math.random()-.5)*v;col[i*3+2]=base.b+(Math.random()-.5)*v}
  geo.setAttribute('position',new THREE.BufferAttribute(pos,3));geo.setAttribute('color',new THREE.BufferAttribute(col,3));
  const mat=new THREE.PointsMaterial({size:cfg.size,map:starTexture,transparent:true,blending:THREE.AdditiveBlending,depthWrite:false,vertexColors:true,opacity:cfg.opacity,sizeAttenuation:true});
  const stars=new THREE.Points(geo,mat);scene.add(stars);starLayers.push({mesh:stars,config:cfg})
});

// DUST PARTICLES
const dustGeo=new THREE.BufferGeometry();
const dustCount=2000;
const dustPos=new Float32Array(dustCount*3);
for(let i=0;i<dustCount;i++){dustPos[i*3]=(Math.random()-.5)*400;dustPos[i*3+1]=(Math.random()-.5)*400;dustPos[i*3+2]=(Math.random()-.5)*400}
dustGeo.setAttribute('position',new THREE.BufferAttribute(dustPos,3));
const dustMat=new THREE.PointsMaterial({size:.8,color:0x8866aa,transparent:true,opacity:.4,blending:THREE.AdditiveBlending,depthWrite:false});
const dust=new THREE.Points(dustGeo,dustMat);scene.add(dust);

// SOLAR SYSTEM
const ambientLight=new THREE.AmbientLight(0x111122,.5);scene.add(ambientLight);
const sunLight=new THREE.PointLight(0xffeebb,3,500);sunLight.position.set(0,0,0);scene.add(sunLight);

// Sun with cinematic glow
const sunGeo=new THREE.SphereGeometry(8,64,64);
const sunMat=new THREE.MeshBasicMaterial({color:0xffee88});
const sun=new THREE.Mesh(sunGeo,sunMat);scene.add(sun);

// Sun layers
const sunGlow1=new THREE.Mesh(new THREE.SphereGeometry(14,32,32),new THREE.MeshBasicMaterial({color:0xffcc44,transparent:true,opacity:.25,blending:THREE.AdditiveBlending,depthWrite:false}));scene.add(sunGlow1);
const sunGlow2=new THREE.Mesh(new THREE.SphereGeometry(22,32,32),new THREE.MeshBasicMaterial({color:0xff8833,transparent:true,opacity:.12,blending:THREE.AdditiveBlending,depthWrite:false}));scene.add(sunGlow2);
const sunGlow3=new THREE.Mesh(new THREE.SphereGeometry(35,32,32),new THREE.MeshBasicMaterial({color:0xff5522,transparent:true,opacity:.06,blending:THREE.AdditiveBlending,depthWrite:false}));scene.add(sunGlow3);

// Lens flare
const flareGeo=new THREE.PlaneGeometry(30,30);
const flareMat=new THREE.MeshBasicMaterial({color:0xffddaa,transparent:true,opacity:.15,blending:THREE.AdditiveBlending,depthWrite:false});
for(let i=0;i<5;i++){const flare=new THREE.Mesh(flareGeo,flareMat.clone());flare.position.set((Math.random()-.5)*60,(Math.random()-.5)*60,-50);flare.scale.setScalar(.5+Math.random()*1.5);scene.add(flare)}

// Planets
const planetsData=[
  {radius:1,distance:28,speed:.012,color:0xa0a0a0,name:'Mercury'},
  {radius:1.8,distance:42,speed:.009,color:0xe8b849,name:'Venus'},
  {radius:2,distance:58,speed:.007,color:0x5588cc,name:'Earth'},
  {radius:1.5,distance:75,speed:.005,color:0xcc4422,name:'Mars'},
  {radius:5,distance:105,speed:.003,color:0xddbb88,name:'Jupiter'},
  {radius:4.2,distance:140,speed:.002,color:0xccaa77,rings:true,name:'Saturn'},
  {radius:3,distance:180,speed:.0015,color:0x88aacc,name:'Uranus'},
  {radius:2.8,distance:220,speed:.001,color:0x4466cc,name:'Neptune'}
];
const planetMeshes=[];
planetsData.forEach((p)=>{
  const mesh=new THREE.Mesh(new THREE.SphereGeometry(p.radius,48,48),new THREE.MeshStandardMaterial({color:p.color,roughness:.7,metalness:.3}));
  mesh.userData={distance:p.distance,speed:p.speed,angle:Math.random()*Math.PI*2,inclination:(Math.random()-.5)*.15};
  scene.add(mesh);planetMeshes.push(mesh);
  if(p.rings){const ring=new THREE.Mesh(new THREE.RingGeometry(p.radius*1.5,p.radius*2.5,64),new THREE.MeshBasicMaterial({color:0xbbaa88,side:THREE.DoubleSide,transparent:true,opacity:.6}));ring.rotation.x=Math.PI/2.8;mesh.add(ring)}
  const orbitGeo=new THREE.BufferGeometry();const pts=[];for(let i=0;i<=256;i++){const a=(i/256)*Math.PI*2;pts.push(new THREE.Vector3(Math.cos(a)*p.distance,0,Math.sin(a)*p.distance))}orbitGeo.setFromPoints(pts);scene.add(new THREE.Line(orbitGeo,new THREE.LineBasicMaterial({color:0x221133,transparent:true,opacity:.2})))});

// ASTEROID BELT
const asteroidGeo=new THREE.BufferGeometry();
const asteroidCount=800;
const asteroidPos=new Float32Array(asteroidCount*3);
for(let i=0;i<asteroidCount;i++){const angle=Math.random()*Math.PI*2;const r=90+Math.random()*20;asteroidPos[i*3]=Math.cos(angle)*r;asteroidPos[i*3+1]=(Math.random()-.5)*8;asteroidPos[i*3+2]=Math.sin(angle)*r}
asteroidGeo.setAttribute('position',new THREE.BufferAttribute(asteroidPos,3));
const asteroidMat=new THREE.PointsMaterial({size:1.2,color:0x665544,transparent:true,opacity:.6,blending:THREE.AdditiveBlending,depthWrite:false});
const asteroids=new THREE.Points(asteroidGeo,asteroidMat);scene.add(asteroids);

// COMET
const cometGroup=new THREE.Group();
const cometCore=new THREE.Mesh(new THREE.SphereGeometry(1.5,16,16),new THREE.MeshBasicMaterial({color:0xaaddff}));
cometGroup.add(cometCore);
const cometTailGeo=new THREE.BufferGeometry();
const tailPts=new Float32Array(100*3);
for(let i=0;i<100;i++){tailPts[i*3]=i*.5;tailPts[i*3+1]=(Math.random()-.5)*i*.1;tailPts[i*3+2]=(Math.random()-.5)*i*.1}
cometTailGeo.setAttribute('position',new THREE.BufferAttribute(tailPts,3));
const cometTail=new THREE.Points(cometTailGeo,new THREE.PointsMaterial({size:2,color:0x88ccff,transparent:true,opacity:.5,blending:THREE.AdditiveBlending,depthWrite:false}));
cometGroup.add(cometTail);
cometGroup.position.set(150,20,0);
scene.add(cometGroup);

// Animation
let scrollY=0;window.addEventListener('scroll',()=>{scrollY=window.scrollY||window.pageYOffset||0});
let lastFrameTime=0;const clock=new THREE.Clock();
let cameraAngle=0;

function animate(ts){requestAnimationFrame(animate);const now=ts||performance.now();if(lastFrameTime&&now-lastFrameTime<1000/60)return;lastFrameTime=now;
  try{const t=clock.getElapsedTime()||0;
    // Cinematic camera orbit
    cameraAngle+=.0003;
    const camRadius=130+Math.sin(t*.1)*20;
    camera.position.x=Math.sin(cameraAngle)*camRadius+mouseX*.5;
    camera.position.z=Math.cos(cameraAngle)*camRadius-scrollY*.03;
    camera.position.y=35+Math.sin(t*.15)*15+mouseY*.3;
    camera.lookAt(0,0,0);

    // Sun pulse
    const pulse=1+Math.sin(t*1.5)*.06;
    sunGlow1.scale.set(pulse,pulse,pulse);
    sunGlow2.scale.set(pulse*1.1,pulse*1.1,pulse*1.1);
    sunGlow3.scale.set(pulse*1.2,pulse*1.2,pulse*1.2);
    sunLight.intensity=2.5+Math.sin(t*2)*.5;

    // Planet orbits
    planetMeshes.forEach(m=>{m.userData.angle+=m.userData.speed;m.position.x=Math.cos(m.userData.angle)*m.userData.distance;m.position.z=Math.sin(m.userData.angle)*m.userData.distance;m.position.y=Math.sin(m.userData.angle)*m.userData.distance*m.userData.inclination;m.rotation.y+=.01});

    // Asteroid belt rotation
    asteroids.rotation.y+=.0005;

    // Comet orbit
    const cometAngle=t*.05;
    cometGroup.position.x=Math.cos(cometAngle)*180;
    cometGroup.position.z=Math.sin(cometAngle)*180;
    cometGroup.position.y=20+Math.sin(cometAngle*2)*30;
    cometGroup.rotation.y=-cometAngle+Math.PI/2;

    // Nebula parallax
    if(nebula){nebula.position.x=mouseX*.01;nebula.position.y=-mouseY*.01;nebula.rotation.z+=.00005}
    if(nebula2){nebula2.position.x=mouseX*.03;nebula2.position.y=-mouseY*.03;nebula2.rotation.z+=.00008}
    if(nebula3){nebula3.position.x=mouseX*.05;nebula3.position.y=-mouseY*.05;nebula3.rotation.z+=.0001}

    // Starfield drift
    starLayers.forEach(l=>{if(!l||!l.mesh||!l.mesh.geometry)return;const p=l.mesh.geometry.attributes.position.array;const sx=l.config.speedX,sy=l.config.speedY;for(let i=0;i<p.length;i+=3){p[i]+=sx*60;p[i+1]+=sy*60;if(p[i]>l.config.spread)p[i]=-l.config.spread;if(p[i]<-l.config.spread)p[i]=l.config.spread;if(p[i+1]>l.config.spread)p[i+1]=-l.config.spread;if(p[i+1]<-l.config.spread)p[i+1]=l.config.spread}l.mesh.geometry.attributes.position.needsUpdate=true});

    // Dust drift
    const dp=dust.geometry.attributes.position.array;for(let i=0;i<dp.length;i+=3){dp[i]+=.02;dp[i+1]+=.01;if(dp[i]>200)dp[i]=-200;if(dp[i+1]>200)dp[i+1]=-200}dust.geometry.attributes.position.needsUpdate=true;

    if(useComposer&&composer)composer.render();else renderer.render(scene,camera);
  }catch(e){console.warn('Frame error:',e.message);try{renderer.render(scene,camera)}catch(e2){}}
}animate(0);

// GSAP Scroll
if(hasGSAP){gsap.registerPlugin(ScrollTrigger);
  gsap.to('.hero',{y:-100,opacity:.3,ease:'none',scrollTrigger:{trigger:'.hero',start:'top top',end:'bottom top',scrub:true}});
  const sw=document.querySelector('.showcase-pin-wrapper'),st=document.querySelector('.showcase-track');
  if(sw&&st){gsap.to(st,{x:-(st.scrollWidth-window.innerWidth),ease:'none',scrollTrigger:{trigger:sw,start:'top top',end:'bottom bottom',scrub:1,pin:'.showcase-pin',anticipatePin:1}})}
  gsap.from('.manifesto-text',{opacity:0,y:60,duration:1.5,ease:'power3.out',scrollTrigger:{trigger:'.manifesto',start:'top 75%',end:'top 35%',scrub:1}});
  gsap.from('.manifesto-sub',{opacity:0,y:40,duration:1.2,ease:'power3.out',scrollTrigger:{trigger:'.manifesto',start:'top 65%',end:'top 30%',scrub:1}});
  gsap.from('.feature-card',{opacity:0,y:50,duration:.8,stagger:.1,ease:'power3.out',scrollTrigger:{trigger:'.features',start:'top 75%',end:'top 35%',scrub:1}});
  gsap.from('.stat-item',{opacity:0,y:40,duration:.8,stagger:.15,ease:'power3.out',scrollTrigger:{trigger:'.stats',start:'top 75%',end:'top 35%',scrub:1}});
  gsap.from('.footer',{opacity:0,duration:1,scrollTrigger:{trigger:'.footer',start:'top 95%'}});
}

window.addEventListener('resize',()=>{camera.aspect=window.innerWidth/window.innerHeight;camera.updateProjectionMatrix();renderer.setSize(window.innerWidth,window.innerHeight);if(composer&&composer.setSize)composer.setSize(window.innerWidth,window.innerHeight)});
</script>
</body>
</html>
"""

with open('astral-solar.html', 'w', encoding='utf-8') as f:
    f.write(html + scripts)
print('OK:', len(html + scripts), 'bytes')
