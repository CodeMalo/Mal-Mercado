/* ════════════════════════════════════════════════════════════════
   fondo.js — Mal Mercado
   Fondo 3D: la cámara VUELA sobre la línea de precio de una acción.
   Subidas en verde, bajadas en rojo. Starfield + bloom. El scroll de
   la página avanza el recorrido. Adaptado (de un hero cósmico React con
   Three.js) al stack estático del sitio. Sin build: Three.js por CDN.
   ════════════════════════════════════════════════════════════════ */
import * as THREE from "three";
import { EffectComposer } from "three/addons/postprocessing/EffectComposer.js";
import { RenderPass } from "three/addons/postprocessing/RenderPass.js";
import { UnrealBloomPass } from "three/addons/postprocessing/UnrealBloomPass.js";

const canvas = document.getElementById("fondo");
if (canvas) boot();

function boot() {
  const reduce = matchMedia("(prefers-reduced-motion: reduce)").matches;
  // Si no hay WebGL, dejamos el degradado CSS de respaldo y salimos.
  let ok = false;
  try { ok = !!(canvas.getContext("webgl2") || canvas.getContext("webgl")); } catch (e) {}
  if (!ok) { canvas.style.display = "none"; return; }

  const VERDE = 0x3ef08c, ROJO = 0xff5a4d, NEG = 0x07090d;
  const W = () => window.innerWidth || document.documentElement.clientWidth || 1280;
  const H = () => window.innerHeight || document.documentElement.clientHeight || 720;

  const scene = new THREE.Scene();
  scene.fog = new THREE.FogExp2(NEG, 0.0019);

  const camera = new THREE.PerspectiveCamera(72, W() / H(), 0.1, 4000);

  const renderer = new THREE.WebGLRenderer({ canvas, antialias: true, alpha: true, powerPreference: "high-performance" });
  renderer.setSize(W(), H());
  renderer.setPixelRatio(Math.min(window.devicePixelRatio, 1.75));
  renderer.toneMapping = THREE.ACESFilmicToneMapping;
  renderer.toneMappingExposure = 1.05;

  // ── Serie de precio (camino determinista con tendencia + ruido) ──
  const N = 300, STEP = 12;
  const pts = [];
  let y = 0, trend = 0.5, seed = 20260711;
  const rnd = () => { seed = (seed * 9301 + 49297) % 233280; return seed / 233280; };
  for (let i = 0; i < N; i++) {
    trend += (rnd() - 0.5) * 0.34;
    trend = Math.max(-1.25, Math.min(1.3, trend));
    y += trend * 3.1 + (rnd() - 0.5) * 3.2;
    y *= 0.994;                                   // reversión suave a la media
    const x = Math.sin(i * 0.06) * 26 + Math.sin(i * 0.021) * 14;
    pts.push(new THREE.Vector3(x, y, -i * STEP));
  }
  const curve = new THREE.CatmullRomCurve3(pts, false, "catmullrom", 0.5);
  const DIV = 1600;
  const cpts = curve.getPoints(DIV);

  // ── Línea de precio con color por dirección (verde sube / rojo baja) ──
  const up = new THREE.Color(VERDE), dn = new THREE.Color(ROJO);
  const mkColors = () => {
    const col = new Float32Array(cpts.length * 3);
    for (let i = 0; i < cpts.length; i++) {
      const prev = cpts[Math.max(0, i - 1)];
      const c = cpts[i].y >= prev.y - 0.001 ? up : dn;
      col[i * 3] = c.r; col[i * 3 + 1] = c.g; col[i * 3 + 2] = c.b;
    }
    return col;
  };
  const lineGeo = new THREE.BufferGeometry().setFromPoints(cpts);
  lineGeo.setAttribute("color", new THREE.BufferAttribute(mkColors(), 3));
  scene.add(new THREE.Line(lineGeo, new THREE.LineBasicMaterial({ vertexColors: true, transparent: true, opacity: 0.98 })));

  // Puntos-glow sobre la línea (semillas del bloom)
  const glowGeo = new THREE.BufferGeometry().setFromPoints(cpts.filter((_, i) => i % 10 === 0));
  const gcol = new Float32Array(Math.ceil(cpts.length / 10) * 3);
  cpts.filter((_, i) => i % 10 === 0).forEach((p, i) => {
    const prev = cpts[Math.max(0, i * 10 - 1)]; const c = p.y >= prev.y ? up : dn;
    gcol[i * 3] = c.r; gcol[i * 3 + 1] = c.g; gcol[i * 3 + 2] = c.b;
  });
  glowGeo.setAttribute("color", new THREE.BufferAttribute(gcol, 3));
  scene.add(new THREE.Points(glowGeo, new THREE.PointsMaterial({ size: 6, vertexColors: true, transparent: true, opacity: 0.9, depthWrite: false, blending: THREE.AdditiveBlending })));

  // ── "Velas": barras verticales tenues de la línea a una base ──
  const baseY = Math.min(...pts.map((p) => p.y)) - 60;
  const barPos = [], barCol = [];
  for (let i = 0; i < cpts.length; i += 8) {
    const p = cpts[i], prev = cpts[Math.max(0, i - 1)];
    const c = p.y >= prev.y ? up : dn;
    barPos.push(p.x, p.y, p.z, p.x, baseY, p.z);
    barCol.push(c.r, c.g, c.b, 0, 0, 0);
  }
  const barGeo = new THREE.BufferGeometry();
  barGeo.setAttribute("position", new THREE.Float32BufferAttribute(barPos, 3));
  barGeo.setAttribute("color", new THREE.Float32BufferAttribute(barCol, 3));
  scene.add(new THREE.LineSegments(barGeo, new THREE.LineBasicMaterial({ vertexColors: true, transparent: true, opacity: 0.14 })));

  // ── Starfield (partículas de fondo para profundidad "cósmica") ──
  const SN = 1700, sp = new Float32Array(SN * 3);
  for (let i = 0; i < SN; i++) {
    sp[i * 3] = (Math.random() - 0.5) * 1800;
    sp[i * 3 + 1] = (Math.random() - 0.5) * 1000;
    sp[i * 3 + 2] = -Math.random() * N * STEP;
  }
  const starGeo = new THREE.BufferGeometry();
  starGeo.setAttribute("position", new THREE.BufferAttribute(sp, 3));
  scene.add(new THREE.Points(starGeo, new THREE.PointsMaterial({ color: 0x9fb6c9, size: 1.7, transparent: true, opacity: 0.45, depthWrite: false })));

  // ── Rejilla-piso para dar sensación de recorrido ──
  const grid = new THREE.GridHelper(N * STEP, 70, 0x114a30, 0x0b241a);
  grid.position.y = baseY;
  grid.material.transparent = true; grid.material.opacity = 0.12;
  scene.add(grid);

  // ── Bloom ──
  const composer = new EffectComposer(renderer);
  composer.addPass(new RenderPass(scene, camera));
  const bloom = new UnrealBloomPass(new THREE.Vector2(W(), H()), 0.95, 0.55, 0.18);
  composer.addPass(bloom);

  // ── Scroll → avance sobre la curva ──
  let target = 0, curP = 0;
  const onScroll = () => {
    const max = document.documentElement.scrollHeight - H();
    target = max > 0 ? Math.min(window.scrollY / max, 1) : 0;
  };
  window.addEventListener("scroll", onScroll, { passive: true });
  onScroll();

  const clock = new THREE.Clock();
  const smooth = { x: pts[0].x, y: pts[0].y + 30, z: 60 };
  function animate() {
    requestAnimationFrame(animate);
    const t = clock.getElapsedTime();
    curP += (target - curP) * 0.055;
    // avance = scroll + deriva lenta automática (a menos que reduce-motion)
    const along = Math.min(0.006 + curP * 0.9 + (reduce ? 0 : (t * 0.004) % 0.09), 0.988);
    const p = curve.getPointAt(along);
    const ahead = curve.getPointAt(Math.min(along + 0.014, 0.999));
    // cámara ligeramente por encima/detrás de la línea, mirando hacia adelante
    const tx = p.x - 8, ty = p.y + 30, tz = p.z + 66;
    smooth.x += (tx - smooth.x) * 0.08;
    smooth.y += (ty - smooth.y) * 0.08;
    smooth.z += (tz - smooth.z) * 0.08;
    const fx = Math.sin(t * 0.25) * 3, fy = Math.cos(t * 0.2) * 2;
    camera.position.set(smooth.x + fx, smooth.y + fy, smooth.z);
    camera.lookAt(ahead.x, ahead.y + 8, ahead.z);
    composer.render();
  }
  animate();

  const fit = () => {
    camera.aspect = W() / H(); camera.updateProjectionMatrix();
    renderer.setSize(W(), H()); composer.setSize(W(), H()); bloom.setSize(W(), H());
  };
  window.addEventListener("resize", fit);
  window.addEventListener("load", fit);
  setTimeout(fit, 300); setTimeout(fit, 1200);   // corrige si el tamaño inicial fue 0
}
