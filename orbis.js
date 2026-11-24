import * as THREE from 'three';
import { GLTFLoader } from 'three/addons/loaders/GLTFLoader.js';
import { OrbitControls } from 'three/addons/controls/OrbitControls.js';
import { RoomEnvironment } from 'three/addons/environments/RoomEnvironment.js';
import { EffectComposer } from 'three/addons/postprocessing/EffectComposer.js';
import { RenderPass } from 'three/addons/postprocessing/RenderPass.js';
import { UnrealBloomPass } from 'three/addons/postprocessing/UnrealBloomPass.js';
import { OutputPass } from 'three/addons/postprocessing/OutputPass.js';

// Model space (the Fusion design): mm, +X muzzle, +Y up, +Z right.  three.js space: metres, x = -Zm, y = Ym, z = Xm.
const mm = (x, y, z) => new THREE.Vector3(-z, y, x).multiplyScalar(0.001);
const dir = (x, y, z) => new THREE.Vector3(-z, y, x).normalize();

const FORMS = {
  SEALED: { ja: '外装を閉じた携行形態。発射機構はロックされます。', color: 0x46e1ff, glow: 2.2, cost: 0 },
  LANCE: { ja: '外装が前方へ割れ、レールが伸びる長射程形態。細く収束したビームを撃ちます。', color: 0x46e1ff, glow: 5.0, cost: 22 },
  BLOOM: { ja: '外装と上下の顎が大きく開く広域形態。拡散する衝撃波を放ちます。', color: 0xff5ad2, glow: 6.0, cost: 38 },
};
const TRANSFORM_MS = 1500;

// ---------------------------------------------------------------- renderer / scene
const canvas = document.getElementById('view');
const renderer = new THREE.WebGLRenderer({ canvas, antialias: true });
renderer.setPixelRatio(Math.min(devicePixelRatio, 2));
renderer.toneMapping = THREE.ACESFilmicToneMapping;
renderer.toneMappingExposure = 0.95;
const scene = new THREE.Scene();
scene.background = new THREE.Color(0x05070b);
scene.fog = new THREE.Fog(0x05070b, 1.6, 4.5);
scene.environment = new THREE.PMREMGenerator(renderer).fromScene(new RoomEnvironment(), 0.04).texture;
const camera = new THREE.PerspectiveCamera(30, 1, 0.01, 30);
const controls = new OrbitControls(camera, canvas);
const HOME = { dir: new THREE.Vector3(-0.78, 0.2, 0.42).normalize(), dist: 0.95, target: new THREE.Vector3(0, -0.02, 0.1) };
const fitScale = () => Math.max(1, 1.6 / (innerWidth / innerHeight));
function homeView() { camera.position.copy(HOME.target).addScaledVector(HOME.dir, HOME.dist * fitScale()); controls.target.copy(HOME.target); }
homeView();
controls.enableDamping = true; controls.enablePan = false; controls.minDistance = 0.35; controls.maxDistance = 2.6; controls.autoRotateSpeed = 1.0;

scene.add(new THREE.HemisphereLight(0xcfe6ff, 0x101820, 0.35));
const key = new THREE.DirectionalLight(0xffffff, 1.15); key.position.set(-0.5, 0.9, 0.5); scene.add(key);
const rim = new THREE.DirectionalLight(0x46e1ff, 0.9); rim.position.set(0.8, 0.2, -0.6); scene.add(rim);
const muzzleLight = new THREE.PointLight(0x46e1ff, 0, 2.5); scene.add(muzzleLight);

const FLOOR_Y = -0.2;
const grid = new THREE.GridHelper(8, 80, 0x46e1ff, 0x1b2a38);
grid.position.y = FLOOR_Y; grid.material.transparent = true; grid.material.opacity = 0.35; scene.add(grid);
function radialTexture(stops) {
  const c = document.createElement('canvas'); c.width = c.height = 256;
  const g = c.getContext('2d'); const gr = g.createRadialGradient(128, 128, 0, 128, 128, 128);
  stops.forEach(([o, col]) => gr.addColorStop(o, col)); g.fillStyle = gr; g.fillRect(0, 0, 256, 256);
  return new THREE.CanvasTexture(c);
}
const floorGlow = new THREE.Mesh(new THREE.PlaneGeometry(1.4, 1.0), new THREE.MeshBasicMaterial({
  map: radialTexture([[0, 'rgba(255,255,255,.5)'], [1, 'rgba(255,255,255,0)']]), transparent: true, depthWrite: false,
  blending: THREE.AdditiveBlending, color: 0x46e1ff, opacity: 0.25 }));
floorGlow.rotation.x = -Math.PI / 2; floorGlow.position.set(0, FLOOR_Y + 0.001, 0.1); scene.add(floorGlow);

const composer = new EffectComposer(renderer);
composer.addPass(new RenderPass(scene, camera));
const bloom = new UnrealBloomPass(new THREE.Vector2(1, 1), 0.55, 0.45, 1.0);
composer.addPass(bloom);
composer.addPass(new OutputPass());

const gun = new THREE.Group(); scene.add(gun);

// ---------------------------------------------------------------- beam / burst effects
const fx = new THREE.Group(); scene.add(fx);
const glowTex = radialTexture([[0, 'rgba(255,255,255,1)'], [0.3, 'rgba(255,255,255,.6)'], [1, 'rgba(255,255,255,0)']]);
const addMat = (color, opacity = 1) => new THREE.MeshBasicMaterial({ color, transparent: true, opacity, blending: THREE.AdditiveBlending, depthWrite: false, side: THREE.DoubleSide });
const beamGeo = new THREE.CylinderGeometry(1, 1, 1, 24, 1, true); beamGeo.rotateX(Math.PI / 2); beamGeo.translate(0, 0, 0.5);   // along +z, base at origin
const beamCore = new THREE.Mesh(beamGeo, addMat(0xffffff)), beamHalo = new THREE.Mesh(beamGeo, addMat(0x46e1ff, 0.55));
const muzzleSprite = new THREE.Sprite(new THREE.SpriteMaterial({ map: glowTex, blending: THREE.AdditiveBlending, depthWrite: false, transparent: true, color: 0x46e1ff }));
const chargeSprite = muzzleSprite.clone(); chargeSprite.material = muzzleSprite.material.clone();
const rings = [0, 1, 2, 3].map(() => new THREE.Mesh(new THREE.TorusGeometry(1, 0.035, 10, 64), addMat(0xff5ad2)));
const cone = new THREE.Mesh(new THREE.ConeGeometry(1, 1, 40, 1, true).rotateX(-Math.PI / 2).translate(0, 0, 0.5), addMat(0xff5ad2, 0.35));
[beamCore, beamHalo, muzzleSprite, chargeSprite, cone, ...rings].forEach(m => { m.visible = false; fx.add(m); });
const shots = [];     // active effect animations: {t, dur, update(k)}

// ---------------------------------------------------------------- state
let rig = null;
const parts = {};                 // name -> { obj, base, group }
const dof = {};                   // current DOF values
const st = { form: 'SEALED', busy: false, energy: 100, charge: 0, sound: true, label: '待機' };
const tweens = [];
const smooth = t => { t = Math.min(1, Math.max(0, t)); return t * t * (3 - 2 * t); };
const wait = ms => new Promise(r => setTimeout(r, ms));
function run(ms, fn) { return new Promise(res => tweens.push({ t: 0, ms, fn, res })); }     // fn(k) with k in 0..1
let material = null, glowNow = 2.2, glowColor = new THREE.Color(0x46e1ff), pulse = 0;

// ---------------------------------------------------------------- sound (synthesised)
let actx = null, master = null, reverb = null;
function audio() {
  if (!actx) {
    actx = new (window.AudioContext || window.webkitAudioContext)();
    master = actx.createDynamicsCompressor(); master.threshold.value = -16; master.ratio.value = 6; master.connect(actx.destination);
    const len = Math.floor(actx.sampleRate * 2.2), ir = actx.createBuffer(2, len, actx.sampleRate);
    for (let ch = 0; ch < 2; ch++) { const d = ir.getChannelData(ch); for (let i = 0; i < len; i++) d[i] = (Math.random() * 2 - 1) * Math.pow(1 - i / len, 3.2); }
    reverb = actx.createConvolver(); reverb.buffer = ir;
    const wet = actx.createGain(); wet.gain.value = 0.35; reverb.connect(wet).connect(master);
  }
  if (actx.state === 'suspended') actx.resume();
  return actx;
}
function tone(type, f0, f1, dur, gain, delay = 0, wet = true) {
  if (!st.sound) return;
  const a = audio(), t = a.currentTime + delay, o = a.createOscillator(), g = a.createGain();
  o.type = type; o.frequency.setValueAtTime(f0, t); o.frequency.exponentialRampToValueAtTime(Math.max(20, f1), t + dur);
  g.gain.setValueAtTime(0.0001, t); g.gain.exponentialRampToValueAtTime(gain, t + Math.min(0.03, dur / 4)); g.gain.exponentialRampToValueAtTime(0.0001, t + dur);
  o.connect(g); g.connect(master); if (wet) g.connect(reverb); o.start(t); o.stop(t + dur + 0.05);
}
function hiss(dur, freq, gain, delay = 0, type = 'bandpass', q = 2) {
  if (!st.sound) return;
  const a = audio(), t = a.currentTime + delay, n = Math.floor(a.sampleRate * dur), buf = a.createBuffer(1, n, a.sampleRate), d = buf.getChannelData(0);
  for (let i = 0; i < n; i++) d[i] = Math.random() * 2 - 1;
  const src = a.createBufferSource(); src.buffer = buf;
  const f = a.createBiquadFilter(); f.type = type; f.frequency.value = freq; f.Q.value = q;
  const g = a.createGain(); g.gain.setValueAtTime(gain, t); g.gain.exponentialRampToValueAtTime(0.0005, t + dur);
  src.connect(f).connect(g); g.connect(master); g.connect(reverb); src.start(t);
}
const sfx = {
  transform() { tone('sawtooth', 90, 240, 1.3, 0.09); tone('sine', 420, 900, 1.2, 0.05); [0.05, 0.42, 0.78, 1.25].forEach(d => hiss(0.05, 2400, 0.3, d)); tone('sine', 1300, 1700, 0.18, 0.12, 1.35); },
  charge(ms) { tone('sine', 180, 1500, ms / 1000, 0.16, 0, false); tone('sawtooth', 60, 520, ms / 1000, 0.05, 0, false); },
  lance() { tone('sawtooth', 2600, 110, 0.5, 0.5); tone('square', 1400, 60, 0.32, 0.22); hiss(0.4, 5200, 0.6, 0, 'highpass', 0.7); tone('sine', 150, 38, 0.6, 0.7); },
  bloom() { tone('sine', 220, 30, 1.1, 0.95); tone('sawtooth', 700, 50, 0.8, 0.3); hiss(0.9, 900, 0.75, 0, 'lowpass', 0.6); hiss(0.25, 4200, 0.4, 0, 'highpass', 0.7); },
  deny() { tone('square', 220, 180, 0.12, 0.16, 0, false); tone('square', 170, 140, 0.16, 0.16, 0.14, false); },
};

// ---------------------------------------------------------------- part placement from the rig definition
const _m = new THREE.Matrix4(), _t = new THREE.Matrix4();
function groupMatrix(group, out) {
  out.identity();
  for (const s of rig.groups[group].steps) {
    const v = dof[s.dof] || 0;
    if (s.type === 'move') { const p = mm(...s.axis).multiplyScalar(s.travel * v); out.multiply(_t.makeTranslation(p.x, p.y, p.z)); }
    else {
      const pv = mm(...s.pivot);
      out.multiply(_t.makeTranslation(pv.x, pv.y, pv.z));
      out.multiply(_t.makeRotationAxis(dir(...s.axis), THREE.MathUtils.degToRad(s.angle * v)));
      out.multiply(_t.makeTranslation(-pv.x, -pv.y, -pv.z));
    }
  }
  return out;
}
function placeParts() {
  const cache = {};
  for (const name in parts) {
    const p = parts[name];
    const g = cache[p.group] || (cache[p.group] = groupMatrix(p.group, new THREE.Matrix4()));
    p.obj.matrix.multiplyMatrices(g, p.base);
    p.obj.matrixWorldNeedsUpdate = true;
  }
}
function muzzleWorld(out) {            // front of the emitter ring, wherever the rails currently are
  const railX = 184.6 + (dof.rail || 0) * 115;
  return gun.localToWorld(out.copy(mm(railX + 6, 14, 0)));
}
// the same staggered schedule the exported animation clips use
function transitionState(from, to, u) {
  const opening = !(to === 'SEALED' || (from === 'BLOOM' && to === 'LANCE'));
  const A = rig.modes[from], B = rig.modes[to], out = {};
  for (const d of rig.dofs) {
    const [w0, w1] = rig.windows[d];
    const k = opening ? smooth((u - w0) / (w1 - w0)) : 1 - smooth(((1 - u) - w0) / (w1 - w0));
    out[d] = (A[d] || 0) + ((B[d] || 0) - (A[d] || 0)) * k;
  }
  return out;
}

// ---------------------------------------------------------------- actions
async function guarded(fn) { if (st.busy || !rig) return; st.busy = true; try { await fn(); } finally { st.busy = false; st.label = '待機'; updateHud(); } }
const setForm = to => guarded(async () => {
  if (to === st.form) return;
  const from = st.form;
  st.label = '変形中'; st.form = to; updateHud(); setHint('');
  sfx.transform();
  const g0 = glowNow, c0 = glowColor.clone(), c1 = new THREE.Color(FORMS[to].color);
  await run(TRANSFORM_MS, k => {
    Object.assign(dof, transitionState(from, to, k));
    glowNow = g0 + (FORMS[to].glow - g0) * smooth(k) + Math.sin(k * Math.PI) * 3;
    glowColor.copy(c0).lerp(c1, smooth(k));
  });
  Object.assign(dof, transitionState(from, to, 1));
  setHint(to === 'SEALED' ? '' : '<b>SPACE</b> でチャージして発射');
});
const fire = () => guarded(async () => {
  const F = FORMS[st.form];
  if (st.form === 'SEALED') { sfx.deny(); setHint('封鎖形態では発射できません。<b>2</b> か <b>3</b> で展開してください。'); return; }
  if (st.energy < F.cost) { sfx.deny(); setHint('エネルギー不足です。回復を待ってください。'); return; }
  const base = { ...dof }, chargeMs = st.form === 'LANCE' ? 700 : 950;
  st.label = 'チャージ'; updateHud(); sfx.charge(chargeMs);
  chargeSprite.visible = true; chargeSprite.material.color.set(F.color);
  await run(chargeMs, k => {
    st.charge = k * 100; pulse = k * 6;
    dof.trigger = smooth(Math.min(1, k * 4));
    muzzleWorld(chargeSprite.position); chargeSprite.scale.setScalar(0.02 + 0.09 * k * (0.85 + 0.15 * Math.sin(k * 60)));
    muzzleLight.position.copy(chargeSprite.position); muzzleLight.color.set(F.color); muzzleLight.intensity = k * 1.5;
    $('chargeN').textContent = Math.round(st.charge) + '%'; $('chargeBar').style.width = st.charge + '%';
  });
  chargeSprite.visible = false;
  st.energy -= F.cost; st.label = '発射'; updateHud();
  const origin = muzzleWorld(new THREE.Vector3());
  if (st.form === 'LANCE') {
    sfx.lance();
    [beamCore, beamHalo, muzzleSprite].forEach(m => { m.visible = true; m.position.copy(origin); });
    muzzleSprite.material.color.set(F.color);
    shots.push({ t: 0, dur: 0.55, update(k) {
      const a = 1 - smooth(k), w = 0.006 + 0.012 * (1 - k);
      beamCore.scale.set(w * 0.45, w * 0.45, 12); beamHalo.scale.set(w * 1.8, w * 1.8, 12);
      beamCore.material.opacity = a; beamHalo.material.opacity = 0.6 * a;
      muzzleSprite.scale.setScalar(0.28 * (1 - k * 0.6)); muzzleSprite.material.opacity = a;
      muzzleLight.intensity = 6 * a;
    }, end() { [beamCore, beamHalo, muzzleSprite].forEach(m => m.visible = false); muzzleLight.intensity = 0; } });
    await run(420, k => {                      // recoil of the mechanism (same pulse as the Fire_Lance clip)
      const p = smooth(Math.min(1, k / 0.15)) * (1 - smooth((k - 0.15) / 0.7));
      dof.rail = base.rail - 0.22 * p; dof.shell_yaw = base.shell_yaw + 0.12 * p; dof.tail = base.tail + 0.2 * p;
      pulse = 8 * (1 - k);
    });
  } else {
    sfx.bloom();
    cone.visible = muzzleSprite.visible = true; cone.position.copy(origin); muzzleSprite.position.copy(origin);
    muzzleSprite.material.color.set(F.color);
    rings.forEach(r => { r.visible = true; r.position.copy(origin); });
    shots.push({ t: 0, dur: 1.1, update(k) {
      const a = 1 - smooth(k);
      rings.forEach((r, i) => { const kk = Math.max(0, k * 1.3 - i * 0.12); r.position.z = origin.z + kk * 2.4; r.scale.setScalar(0.03 + kk * 0.95); r.material.opacity = Math.max(0, 1 - kk) * 0.9; });
      cone.scale.set(0.9 * k + 0.05, 0.9 * k + 0.05, 2.2 * k + 0.1); cone.material.opacity = 0.4 * a;
      muzzleSprite.scale.setScalar(0.5 * (1 - k * 0.5)); muzzleSprite.material.opacity = a;
      muzzleLight.intensity = 9 * a;
    }, end() { cone.visible = muzzleSprite.visible = false; rings.forEach(r => r.visible = false); muzzleLight.intensity = 0; } });
    await run(620, k => {
      const p = smooth(Math.min(1, k / 0.15)) * (1 - smooth((k - 0.15) / 0.7));
      dof.beak = base.beak + 0.14 * p; dof.jaw = base.jaw + 0.14 * p; dof.shell_yaw = base.shell_yaw + 0.1 * p; dof.crest = base.crest + 0.12 * p;
      pulse = 10 * (1 - k);
    });
  }
  Object.assign(dof, base); dof.trigger = 0; pulse = 0; st.charge = 0;
  $('chargeN').textContent = '0%'; $('chargeBar').style.width = '0%';
});

// ---------------------------------------------------------------- HUD
const $ = id => document.getElementById(id);
function setHint(html) { $('hint').innerHTML = html; }
function updateHud() {
  const F = FORMS[st.form], col = '#' + new THREE.Color(F.color).getHexString();
  document.documentElement.style.setProperty('--acc', col);
  $('modeName').textContent = st.form; $('modeJa').textContent = F.ja; $('sState').textContent = st.label;
  document.querySelectorAll('#modes button').forEach(b => b.classList.toggle('on', b.dataset.mode === st.form));
  $('btnFire').disabled = st.form === 'SEALED';
}
function syncTools() {
  $('btnRotate').classList.toggle('on', controls.autoRotate);
  $('btnSound').classList.toggle('on', st.sound); $('btnSound').textContent = st.sound ? 'サウンド ON' : 'サウンド OFF';
}
const ACTIONS = { fire, rotate() { controls.autoRotate = !controls.autoRotate; syncTools(); }, sound() { st.sound = !st.sound; syncTools(); }, view() { homeView(); } };
document.querySelectorAll('button[data-act]').forEach(b => b.addEventListener('click', () => ACTIONS[b.dataset.act]()));
document.querySelectorAll('button[data-mode]').forEach(b => b.addEventListener('click', () => setForm(b.dataset.mode)));
addEventListener('keydown', e => {
  if (e.repeat || e.ctrlKey || e.metaKey || e.altKey) return;
  const k = e.key.toLowerCase();
  if (k === ' ' || k === 'f') { e.preventDefault(); fire(); }
  else if (k === '1') setForm('SEALED'); else if (k === '2') setForm('LANCE'); else if (k === '3') setForm('BLOOM');
});

// ---------------------------------------------------------------- loop
function resize() {
  renderer.setSize(innerWidth, innerHeight, false); composer.setSize(innerWidth, innerHeight);
  camera.aspect = innerWidth / innerHeight; camera.fov = innerWidth < 900 ? 42 : 30; camera.updateProjectionMatrix();
}
addEventListener('resize', resize); resize();
const clock = new THREE.Clock();
const TEST = new URLSearchParams(location.search).has('test');      // timer-driven loop, for checking while the tab is not painted
const nextFrame = () => (TEST ? setTimeout(frame, 16) : requestAnimationFrame(frame));
let time = 0;
function frame() {
  const dt = Math.min(clock.getDelta(), TEST ? 2 : 0.05); time += dt;
  for (let i = tweens.length - 1; i >= 0; i--) {
    const t = tweens[i]; t.t += dt * 1000; const k = Math.min(1, t.t / t.ms);
    t.fn(k); if (k >= 1) { tweens.splice(i, 1); t.res(); }
  }
  for (let i = shots.length - 1; i >= 0; i--) {
    const s = shots[i]; s.t += dt; const k = Math.min(1, s.t / s.dur);
    s.update(k); if (k >= 1) { s.end(); shots.splice(i, 1); }
  }
  if (!st.busy && st.energy < 100) { st.energy = Math.min(100, st.energy + dt * 9); }
  $('energyN').textContent = Math.round(st.energy) + '%'; $('energyBar').style.width = st.energy + '%';
  if (material) {
    material.emissive.copy(glowColor);
    material.emissiveIntensity = glowNow * (0.92 + 0.08 * Math.sin(time * 3.1)) + pulse;
    rim.color.copy(glowColor); floorGlow.material.color.copy(glowColor);
    floorGlow.material.opacity = Math.min(0.6, 0.08 + 0.025 * glowNow + 0.03 * pulse);
  }
  if (rig) placeParts();
  controls.update();
  composer.render();
  nextFrame();
}

// ---------------------------------------------------------------- load
Promise.all([fetch('./assets/ORBIS_rig.json').then(r => r.json()), new GLTFLoader().loadAsync('./assets/ORBIS_parts.glb')]).then(([r, gltf]) => {
  rig = r; rig.dofs.forEach(d => { dof[d] = 0; });
  gun.add(gltf.scene); gltf.scene.updateMatrixWorld(true);
  gltf.scene.traverse(o => {
    if (!o.isMesh) return;
    o.matrixAutoUpdate = false;
    parts[o.name] = { obj: o, base: o.matrix.clone(), group: rig.part_group[o.name] || 'frame' };
    if (!material) {
      material = o.material; material.envMapIntensity = 0.55;
      // turn the baked (cyan) emission map into a neutral mask so each form can tint the glow
      const img = material.emissiveMap && material.emissiveMap.image;
      if (img) {
        const c = document.createElement('canvas'); c.width = img.width; c.height = img.height;
        const g = c.getContext('2d'); g.drawImage(img, 0, 0);
        const d = g.getImageData(0, 0, c.width, c.height), px = d.data;
        for (let i = 0; i < px.length; i += 4) { const m = Math.max(px[i], px[i + 1], px[i + 2]); px[i] = px[i + 1] = px[i + 2] = m; }
        g.putImageData(d, 0, 0);
        const tex = new THREE.CanvasTexture(c); tex.flipY = false; tex.colorSpace = THREE.SRGBColorSpace;
        tex.wrapS = material.emissiveMap.wrapS; tex.wrapT = material.emissiveMap.wrapT;
        material.emissiveMap = tex;
      }
      material.needsUpdate = true;
    }
    o.material = material;
  });
  window.__orbis = { parts, st, dof, setForm, fire, rig };
  updateHud(); syncTools(); setHint('<b>2</b> か <b>3</b> で変形');
  $('loading').classList.add('done'); setTimeout(() => { $('loading').style.display = 'none'; }, 700);
  frame();
}).catch(err => { $('loading').firstElementChild.textContent = 'MODEL LOAD FAILED'; console.error(err); });
