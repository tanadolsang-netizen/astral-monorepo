import { useRef, useMemo } from 'react'
import { Canvas, useFrame, useThree } from '@react-three/fiber'
import * as THREE from 'three'

/*
  Cosmic BG clone (originkit spec): full-frame WebGL nebula
  จาก domain-warped noise บน transparent canvas
  ใช้เป็นหน้าโหลด → warp ด้วย Glitter Wrap พุ่งเข้าหน้า landing
*/

const frag = `
precision highp float;
uniform float uTime;
uniform vec2 uRes;
uniform vec3 c1; uniform vec3 c2; uniform vec3 c3;

// hash / noise
float hash(vec2 p){ return fract(sin(dot(p,vec2(127.1,311.7)))*43758.5453); }
float noise(vec2 p){
  vec2 i=floor(p), f=fract(p);
  float a=hash(i), b=hash(i+vec2(1,0)), c=hash(i+vec2(0,1)), d=hash(i+vec2(1,1));
  vec2 u=f*f*(3.-2.*f);
  return mix(mix(a,b,u.x),mix(c,d,u.x),u.y);
}
float fbm(vec2 p){
  float v=0., a=.5;
  for(int i=0;i<5;i++){ v+=a*noise(p); p*=2.02; a*=.5; }
  return v;
}
void main(){
  vec2 uv=(gl_FragCoord.xy - 0.5*uRes)/uRes.y;
  uv*=2.2;
  float t=uTime*0.05;
  // domain warp
  vec2 q=vec2(fbm(uv+t), fbm(uv+vec2(5.2,1.3)-t));
  vec2 r=vec2(fbm(uv+4.0*q+vec2(1.7,9.2)+t*0.5), fbm(uv+4.0*q+vec2(8.3,2.8)-t*0.5));
  float n=fbm(uv+4.0*r);
  // สี nebula ทอง/ม่วง/คราม
  vec3 col = mix(c1, c2, clamp(n*1.4,0.,1.));
  col = mix(col, c3, clamp(length(r)*0.6,0.,1.));
  col += c1 * pow(n,3.0)*0.6;        // กระแสสว่าง
  float vig = smoothstep(1.6,0.2,length(uv));
  col *= vig;
  float alpha = clamp(n*1.2+0.05, 0.0, 1.0) * vig;
  gl_FragColor = vec4(col, alpha);
}
`

function Nebula({ speed = 1 }) {
  const mat = useRef()
  const { size, viewport } = useThree()
  const uniforms = useMemo(() => ({
    uTime: { value: 0 },
    uRes: { value: new THREE.Vector2(size.width, size.height) },
    c1: { value: new THREE.Color('#c9a84c') },
    c2: { value: new THREE.Color('#5a3d8c') },
    c3: { value: new THREE.Color('#2a3d8c') }
  }), [])
  useFrame((_, dt) => { if (mat.current) mat.current.uniforms.uTime.value += dt * speed })
  return (
    <mesh>
      <planeGeometry args={[20, 20]} />
      <shaderMaterial ref={mat} transparent depthWrite={false} uniforms={uniforms}
        vertexShader={`void main(){gl_Position=vec4(position.xy,0.,1.);}`} fragmentShader={frag} />
    </mesh>
  )
}

export default function CosmicBG({ speed = 1 }) {
  return (
    <Canvas orthographic camera={{ position: [0, 0, 1] }} dpr={[1, 2]} gl={{ antialias: true, alpha: true }}
      style={{ position: 'absolute', inset: 0 }}>
      <Nebula speed={speed} />
    </Canvas>
  )
}
