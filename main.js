import * as THREE from 'three';
import { GLTFLoader } from 'three/addons/loaders/GLTFLoader.js';
import { OrbitControls } from 'three/addons/controls/OrbitControls.js';
import { RoomEnvironment } from 'three/addons/environments/RoomEnvironment.js';

// ---------------------------------------------------------------- coordinates
// Model space (the Fusion design): mm, +X muzzle, +Y up, +Z right side of the gun.
// three.js space (the exported GLB): metres, x = -Zm, y = Ym, z = Xm.
const mm = (x, y, z) => new THREE.Vector3(-z, y, x).multiplyScalar(0.001);
const ROT_AXIS = new THREE.Vector3(-1, 0, 0);           // model +Z axis
const MAG_DIR = [-18 / 68.41, -66 / 68.41, 0];
const MAG_CAPACITY = 7;

// which moving group every part belongs to (same data the Fusion script used)
const GROUP_OF = { slide: 'slide', extractor: 'slide', trigger: 'trigger', hammer: 'hammer', decocker: 'decocker',
  mag_body: 'magazine', mag_base: 'magazine', dummy_case: 'magazine', dummy_bullet: 'magazine', mag_catch: 'mag_catch' };
const GROUPS = {
  slide: { type: 'move', axis: [-1, 0, 0], travel: 36 },
  trigger: { type: 'rot', pivot: [72, -5, 0], angle: -22 },
  hammer: { type: 'rot', pivot: [4, -8, 0], angle: 48 },
  decocker: { type: 'rot', pivot: [33, -6.5, 0], angle: 10 },
  magazine: { type: 'move', axis: MAG_DIR, travel: 110 },
  mag_catch: { type: 'move', axis: [-1, 0, 0], travel: 2.5 },
};
// exploded view: offset (model mm) and the order parts come off
const EXPLODE = {
  mag_body: [[-31, -116, 0], 0], mag_base: [[-31, -116, 0], 0], dummy_case: [[-31, -116, 0], 0], dummy_bullet: [[-31, -116, 0], 0],
  slide: [[0, 62, 0], 1], extractor: [[0, 62, 0], 1],
  barrel: [[22, 30, 0], 2],
  grip_panel_R: [[0, 0, 46], 3], grip_panel_L: [[0, 0, -46], 3], grip_screw_R: [[0, 0, 74], 3], grip_screw_L: [[0, 0, -74], 3],
  hammer: [[-38, 16, 0], 4], decocker: [[0, 8, -44], 4], takedown_lever: [[0, 0, -40], 4], takedown_pin: [[0, 0, 34], 4],
  trigger: [[44, -20, 0], 5], trigger_guard: [[4, -34, 0], 5], mag_catch: [[-26, -14, 0], 5],
  pin_hammer_R: [[0, 0, 30], 6], pin_hammer_L: [[0, 0, -30], 6], pin_trigger_R: [[0, 0, 30], 6], pin_trigger_L: [[0, 0, -30], 6],
  frame: [[0, 0, 0], 7],
};
const LABELS = [['slide', 'SLIDE', 'スライド'], ['barrel', 'BARREL', 'バレル（中実）'], ['frame', 'FRAME', 'フレーム'],
  ['hammer', 'HAMMER', 'ハンマー'], ['trigger', 'TRIGGER', 'トリガー'], ['trigger_guard', 'GUARD', 'トリガーガード'],
  ['decocker', 'DECOCKER', 'デコッキングレバー'], ['takedown_lever', 'TAKEDOWN', 'テイクダウンレバー'],
  ['mag_body', 'MAGAZINE', 'マガジン'], ['mag_catch', 'MAG CATCH', 'マガジンキャッチ'],
  ['grip_panel_R', 'GRIP', 'グリップパネル'], ['grip_panel_L', 'GRIP', 'グリップパネル']];

// ---------------------------------------------------------------- renderer / scene
const canvas = document.getElementById('view');
const renderer = new THREE.WebGLRenderer({ canvas, antialias: true, alpha: true });
renderer.setPixelRatio(Math.min(devicePixelRatio, 2));
renderer.toneMapping = THREE.ACESFilmicToneMapping;
renderer.toneMappingExposure = 1.9;
const scene = new THREE.Scene();
scene.environment = new THREE.PMREMGenerator(renderer).fromScene(new RoomEnvironment(), 0.04).texture;
const camera = new THREE.PerspectiveCamera(28, 1, 0.01, 10);
const HOME = { dir: new THREE.Vector3(-0.72, 0.16, 0.5).normalize(), dist: 0.43, target: new THREE.Vector3(0, -0.034, 0.07) };
const fitScale = () => Math.max(1, 1.55 / (innerWidth / innerHeight));
function homeView() { camera.position.copy(HOME.target).addScaledVector(HOME.dir, HOME.dist * fitScale()); controls.target.copy(HOME.target); }
const controls = new OrbitControls(camera, canvas);
homeView();
controls.enableDamping = true;
controls.enablePan = false;
controls.minDistance = 0.22;
controls.maxDistance = 1.6;
controls.autoRotateSpeed = 1.2;

scene.add(new THREE.HemisphereLight(0xdfe8ff, 0x20242c, 1.1));
const key = new THREE.DirectionalLight(0xfff1dd, 3.6); key.position.set(-0.5, 0.8, 0.6); scene.add(key);
const rim = new THREE.DirectionalLight(0x58c8ff, 2.4); rim.position.set(0.7, 0.3, -0.6); scene.add(rim);
const flashLight = new THREE.PointLight(0xffb060, 0, 0.9); scene.add(flashLight);

// floor: soft contact shadow + faint grid
function radialTexture(stops) {
  const c = document.createElement('canvas'); c.width = c.height = 256;
  const g = c.getContext('2d'); const gr = g.createRadialGradient(128, 128, 0, 128, 128, 128);
  stops.forEach(([o, col]) => gr.addColorStop(o, col)); g.fillStyle = gr; g.fillRect(0, 0, 256, 256);
  return new THREE.CanvasTexture(c);
}
const FLOOR_Y = -0.125;
const shadow = new THREE.Mesh(new THREE.PlaneGeometry(0.55, 0.3),
  new THREE.MeshBasicMaterial({ map: radialTexture([[0, 'rgba(0,0,0,.55)'], [1, 'rgba(0,0,0,0)']]), transparent: true, depthWrite: false }));
shadow.rotation.x = -Math.PI / 2; shadow.position.set(0, FLOOR_Y, 0.07); scene.add(shadow);
const grid = new THREE.GridHelper(1.6, 64, 0xffb020, 0x3a4250);
grid.position.y = FLOOR_Y - 0.0005; grid.material.transparent = true; grid.material.opacity = 0.16; scene.add(grid);

const gun = new THREE.Group(); scene.add(gun);          // recoil is applied to this group
const flash = new THREE.Sprite(new THREE.SpriteMaterial({
  map: radialTexture([[0, 'rgba(255,255,255,1)'], [0.25, 'rgba(255,214,130,.95)'], [0.6, 'rgba(255,120,30,.35)'], [1, 'rgba(255,90,0,0)']]),
  blending: THREE.AdditiveBlending, depthWrite: false, transparent: true }));
flash.position.copy(mm(170, 13, 0)); flash.visible = false; gun.add(flash);

// ---------------------------------------------------------------- state
const v = { slide: 0, trigger: 0, hammer: 0, decocker: 0, magazine: 0, mag_catch: 0, explode: 0, recoil: 0, cam: 0 };
let camFly = null;
const st = { mag: MAG_CAPACITY, chambered: true, hammerCocked: false, slideLocked: false, magIn: true, exploded: false, busy: false, sound: true };
const parts = {};      // name -> { obj, base, group, center }
const tweens = [];
const casings = [];
const smooth = t => t * t * (3 - 2 * t);
const linear = t => t;
function tween(key, to, ms, ease = smooth) {
  return new Promise(res => tweens.push({ key, from: v[key], to, t: 0, ms, ease, res }));
}
const wait = ms => new Promise(r => setTimeout(r, ms));
function flyTo(dir, dist, target, ms) {       // smooth camera move
  v.cam = 0;
  camFly = { p0: camera.position.clone(), t0: controls.target.clone(),
             p1: target.clone().addScaledVector(dir, dist * fitScale()), t1: target.clone() };
  return tween('cam', 1, ms).then(() => { camFly = null; });
}
const EXPLODE_VIEW = { dir: new THREE.Vector3(-0.8, 0.22, 0.42).normalize(), dist: 0.86, target: new THREE.Vector3(0, -0.02, 0.06) };

// ---------------------------------------------------------------- sound (synthesised, no files)
let actx = null, master = null, reverb = null;
function audio() {
  if (!actx) {
    actx = new (window.AudioContext || window.webkitAudioContext)();
    master = actx.createDynamicsCompressor();
    master.threshold.value = -14; master.knee.value = 8; master.ratio.value = 8; master.attack.value = 0.001; master.release.value = 0.18;
    master.connect(actx.destination);
    // synthetic outdoor tail: early slap-back reflections + a long decaying, darkening noise tail
    const len = Math.floor(actx.sampleRate * 1.8), ir = actx.createBuffer(2, len, actx.sampleRate);
    for (let ch = 0; ch < 2; ch++) {
      const d = ir.getChannelData(ch); let lp = 0;
      for (let i = 0; i < len; i++) {
        const t = i / actx.sampleRate;
        const k = 0.5 * Math.exp(-t * 9);                    // tail gets darker over time
        lp += (Math.random() * 2 - 1 - lp) * (0.06 + k);
        d[i] = lp * Math.exp(-t * 3.4) * 1.6;
      }
      for (const [t, g] of [[0.031, 0.7], [0.067, 0.5], [0.118, 0.38], [0.21, 0.26], [0.34, 0.17]]) {
        const i0 = Math.floor((t + ch * 0.004) * actx.sampleRate);
        for (let i = 0; i < 90; i++) d[i0 + i] += (Math.random() * 2 - 1) * g * (1 - i / 90);
      }
    }
    reverb = actx.createConvolver(); reverb.buffer = ir;
    const wet = actx.createGain(); wet.gain.value = 0.5;
    reverb.connect(wet).connect(master);
  }
  if (actx.state === 'suspended') actx.resume();
  return actx;
}
function noiseBuffer(a, dur) {
  const n = Math.floor(a.sampleRate * dur), buf = a.createBuffer(1, n, a.sampleRate), d = buf.getChannelData(0);
  for (let i = 0; i < n; i++) d[i] = Math.random() * 2 - 1;
  return buf;
}
function drive(a, amount) {              // soft clipper: gives the blast its saturated, "loud" character
  const ws = a.createWaveShaper(), c = new Float32Array(1024);
  for (let i = 0; i < 1024; i++) { const x = i / 511.5 - 1; c[i] = Math.tanh(x * amount); }
  ws.curve = c; ws.oversample = '4x';
  return ws;
}
// short filtered noise hit (mechanical clicks, slide, magazine)
function noise(dur, freq, gain, q = 0.7, type = 'lowpass', delay = 0) {
  if (!st.sound) return;
  const a = audio(), t0 = a.currentTime + delay;
  const src = a.createBufferSource(); src.buffer = noiseBuffer(a, dur);
  const f = a.createBiquadFilter(); f.type = type; f.frequency.value = freq; f.Q.value = q;
  const g = a.createGain(); g.gain.setValueAtTime(gain, t0); g.gain.exponentialRampToValueAtTime(0.0005, t0 + dur);
  src.connect(f).connect(g).connect(master); src.start(t0);
}
function thump(freq, dur, gain, delay = 0) {
  if (!st.sound) return;
  const a = audio(), t0 = a.currentTime + delay, o = a.createOscillator(), g = a.createGain();
  o.frequency.setValueAtTime(freq, t0); o.frequency.exponentialRampToValueAtTime(38, t0 + dur);
  g.gain.setValueAtTime(gain, t0); g.gain.exponentialRampToValueAtTime(0.0005, t0 + dur);
  o.connect(g).connect(master); o.start(t0); o.stop(t0 + dur + 0.02);
}
function gunshot() {
  if (!st.sound) return;
  const a = audio(), t = a.currentTime;
  const bus = a.createGain(); bus.gain.value = 1;
  bus.connect(master); bus.connect(reverb);
  // 1) muzzle crack: a few milliseconds of full-band noise with an instant attack
  const crack = a.createBufferSource(); crack.buffer = noiseBuffer(a, 0.03);
  const cg = a.createGain(); cg.gain.setValueAtTime(2.6, t); cg.gain.exponentialRampToValueAtTime(0.001, t + 0.022);
  const chp = a.createBiquadFilter(); chp.type = 'highpass'; chp.frequency.value = 900;
  crack.connect(chp).connect(cg).connect(drive(a, 3)).connect(bus); crack.start(t);
  // 2) blast body: saturated noise whose low-pass sweeps down quickly
  const body = a.createBufferSource(); body.buffer = noiseBuffer(a, 0.5);
  const lp = a.createBiquadFilter(); lp.type = 'lowpass'; lp.Q.value = 0.8;
  lp.frequency.setValueAtTime(6500, t); lp.frequency.exponentialRampToValueAtTime(420, t + 0.16);
  const bg = a.createGain(); bg.gain.setValueAtTime(2.2, t); bg.gain.exponentialRampToValueAtTime(0.25, t + 0.07);
  bg.gain.exponentialRampToValueAtTime(0.001, t + 0.42);
  body.connect(lp).connect(bg).connect(drive(a, 4)).connect(bus); body.start(t);
  // 3) low pressure thump
  const o = a.createOscillator(), og = a.createGain(); o.type = 'sine';
  o.frequency.setValueAtTime(190, t); o.frequency.exponentialRampToValueAtTime(42, t + 0.13);
  og.gain.setValueAtTime(1.5, t); og.gain.exponentialRampToValueAtTime(0.001, t + 0.2);
  o.connect(og).connect(bus); o.start(t); o.stop(t + 0.22);
  // 4) action noise: slide hitting the rear and closing again
  noise(0.03, 2600, 0.5, 3, 'bandpass', 0.045);
  noise(0.04, 1900, 0.55, 3, 'bandpass', 0.125);
  thump(260, 0.04, 0.2, 0.125);
}
const sfx = {
  shot: gunshot,
  click() { noise(0.03, 4200, 0.6, 5, 'bandpass'); noise(0.02, 1500, 0.3, 3, 'bandpass', 0.004); },
  slide() { noise(0.05, 2400, 0.55, 3, 'bandpass'); thump(240, 0.05, 0.18); },
  mag() { noise(0.06, 1300, 0.6, 3, 'bandpass'); thump(140, 0.07, 0.3); },
};

// ---------------------------------------------------------------- per-frame part placement
const _m = new THREE.Matrix4(), _t = new THREE.Matrix4(), _p = new THREE.Vector3();
function hammerValue() { const t = Math.min(1, v.slide / 0.3); return Math.max(v.hammer, smooth(t)); }   // the slide pushes the hammer down
function groupMatrix(group, out) {
  out.identity();
  const g = GROUPS[group]; if (!g) return out;
  const val = group === 'hammer' ? hammerValue() : v[group];
  if (g.type === 'move') { _p.copy(mm(...g.axis)).multiplyScalar(g.travel * val); out.makeTranslation(_p.x, _p.y, _p.z); }
  else {
    const pv = mm(...g.pivot);
    out.makeTranslation(pv.x, pv.y, pv.z);
    out.multiply(_t.makeRotationAxis(ROT_AXIS, THREE.MathUtils.degToRad(g.angle * val)));
    out.multiply(_t.makeTranslation(-pv.x, -pv.y, -pv.z));
  }
  return out;
}
const STAGES = 8;
function explodeAmount(order) { return smooth(THREE.MathUtils.clamp(v.explode * (STAGES + 2.5) - order, 0, 2.5) / 2.5); }
function placeParts() {
  for (const name in parts) {
    const p = parts[name];
    groupMatrix(p.group, _m);
    const ex = EXPLODE[name];
    if (ex && v.explode > 0) {
      _p.copy(mm(...ex[0])).multiplyScalar(explodeAmount(ex[1]));
      _m.premultiply(_t.makeTranslation(_p.x, _p.y, _p.z));
    }
    p.obj.matrix.copy(_m).multiply(p.base);
    p.obj.matrixWorldNeedsUpdate = true;
  }
  const hasRound = st.mag > 0;
  if (parts.dummy_case) parts.dummy_case.obj.visible = parts.dummy_bullet.obj.visible = hasRound;
  gun.rotation.x = -0.16 * v.recoil;
  gun.position.set(0, 0.004 * v.recoil, -0.012 * v.recoil);
}

// ---------------------------------------------------------------- effects
const casingGeo = new THREE.CylinderGeometry(0.0047, 0.0047, 0.017, 14);
const casingMat = new THREE.MeshStandardMaterial({ color: 0xd9a441, metalness: 1, roughness: 0.28 });
function ejectCasing() {
  const m = new THREE.Mesh(casingGeo, casingMat);
  m.position.copy(gun.localToWorld(mm(64, 19, 9)));
  m.rotation.set(Math.PI / 2, 0, Math.random());
  scene.add(m);
  casings.push({ m, vel: new THREE.Vector3(-0.75 - Math.random() * 0.3, 1.1 + Math.random() * 0.3, -0.35 - Math.random() * 0.2),
    spin: new THREE.Vector3(Math.random() * 22, Math.random() * 16, Math.random() * 22), life: 0, bounced: false });
}
function muzzleFlash() {
  flash.visible = true; flash.scale.setScalar(0.07 + Math.random() * 0.03); flash.material.rotation = Math.random() * 6.28;
  flashLight.position.copy(gun.localToWorld(mm(175, 15, 0))); flashLight.intensity = 2.2;
  const fx = document.getElementById('flashfx'); fx.style.transition = 'none'; fx.style.opacity = 1;
  setTimeout(() => { flash.visible = false; flashLight.intensity = 0; fx.style.transition = 'opacity .25s'; fx.style.opacity = 0; }, 55);
  v.recoil = 1;
}

// ---------------------------------------------------------------- actions
async function guarded(fn) {
  if (st.busy) return; st.busy = true;
  try { await fn(); } finally { st.busy = false; updateHud(); }
}
async function cycleSlideAfterShot() {
  await tween('slide', 1, 45, linear);
  st.hammerCocked = true; v.hammer = 1;
  if (st.magIn && st.mag > 0) { st.mag--; st.chambered = true; updateHud(); await tween('slide', 0, 75); }
  else if (st.magIn) { st.slideLocked = true; await tween('slide', 0.92, 40); }
  else { await tween('slide', 0, 75); }
}
const fire = () => guarded(async () => {
  if (st.exploded || st.slideLocked) { if (st.slideLocked) { sfx.click(); setHint('スライドが後退したままです。<b>R</b> でリロードしてください。'); } return; }
  if (!st.hammerCocked) await Promise.all([tween('trigger', 1, 150), tween('hammer', 0.85, 150)]);   // double action
  else await tween('trigger', 1, 45);
  await tween('hammer', 0, 22, linear);
  st.hammerCocked = false;
  if (st.chambered) {
    st.chambered = false;
    sfx.shot(); muzzleFlash(); ejectCasing();
    await cycleSlideAfterShot();
    setHint(st.slideLocked ? '弾切れです。<b>R</b> でリロード。' : '');
  } else {
    sfx.click();
    setHint('薬室が空です。<b>S</b> でスライドを引くか、<b>R</b> でリロード。');
  }
  await tween('trigger', st.hammerCocked ? 0.55 : 0, 110);
});
async function magOut() {
  sfx.mag();
  await tween('mag_catch', 1, 90);
  tween('mag_catch', 0, 260);
  await tween('magazine', 1.3, 360);
  st.magIn = false;
}
async function magIn() {
  st.mag = MAG_CAPACITY; updateHud();
  tween('mag_catch', 1, 200).then(() => tween('mag_catch', 0, 120));
  await tween('magazine', 0, 300);
  sfx.mag();
  st.magIn = true;
}
const toggleMag = () => guarded(async () => { if (st.exploded) return; if (st.magIn) await magOut(); else await magIn(); });
async function rackInner() {
  sfx.slide();
  if (st.slideLocked) {
    st.slideLocked = false;
    await tween('slide', 1, 60);
  } else {
    await tween('slide', 1, 190);
    if (st.chambered) { st.chambered = false; ejectCasing(); }
    st.hammerCocked = true; v.hammer = 1;
    await wait(70);
  }
  if (st.magIn && st.mag > 0) { st.mag--; st.chambered = true; updateHud(); sfx.slide(); await tween('slide', 0, 80); }
  else if (st.magIn) { st.slideLocked = true; await tween('slide', 0.92, 50); }
  else { sfx.slide(); await tween('slide', 0, 80); }
  await tween('trigger', st.hammerCocked ? 0.55 : 0, 80);
}
const rack = () => guarded(async () => { if (st.exploded) return; await rackInner(); setHint(''); });
const reload = () => guarded(async () => {
  if (st.exploded) return;
  if (st.magIn) { await magOut(); await wait(260); }
  await magIn();
  if (st.slideLocked) { await wait(160); await rackInner(); }
  setHint('');
});
const decock = () => guarded(async () => {
  if (st.exploded || !st.hammerCocked) return;
  await tween('decocker', 1, 110);
  sfx.click();
  await Promise.all([tween('hammer', 0, 90), tween('trigger', 0, 160)]);
  st.hammerCocked = false;
  await tween('decocker', 0, 180);
});
const toggleExplode = () => guarded(async () => {
  if (!st.exploded) {
    st.exploded = true; updateHud();
    if (st.slideLocked) { st.slideLocked = false; await tween('slide', 0, 200); }
    controls.autoRotate = false; syncTools();
    sfx.mag(); setHint('');
    flyTo(EXPLODE_VIEW.dir, EXPLODE_VIEW.dist, EXPLODE_VIEW.target, 1600);
    await tween('explode', 1, 2200, linear);
  } else {
    flyTo(HOME.dir, HOME.dist, HOME.target, 1500);
    await tween('explode', 0, 1700, linear);
    sfx.slide();
    st.exploded = false;
  }
});

// ---------------------------------------------------------------- HUD
const $ = id => document.getElementById(id);
const pips = $('pips');
for (let i = 0; i < MAG_CAPACITY; i++) pips.appendChild(document.createElement('i'));
function setHint(html) { $('hint').innerHTML = html; }
function updateHud() {
  $('ammoN').textContent = st.mag;
  $('ammoN').classList.toggle('empty', st.mag === 0 && !st.chambered);
  $('ammoPlus').textContent = st.chambered ? '+1' : '+0';
  [...pips.children].forEach((el, i) => el.classList.toggle('on', i < st.mag));
  const set = (id, text, cls) => { const e = $(id); e.textContent = text; e.className = cls || ''; };
  set('sChamber', st.chambered ? '装填' : '空', st.chambered ? 'hot' : '');
  set('sHammer', st.hammerCocked ? 'コック / SA' : 'ダウン / DA', st.hammerCocked ? 'hot' : '');
  set('sSlide', st.slideLocked ? 'ホールドオープン' : '閉鎖', st.slideLocked ? 'warn' : '');
  set('sMag', st.magIn ? '装着' : '取り外し', st.magIn ? '' : 'warn');
  $('magLabel').textContent = st.magIn ? 'マガジンを抜く' : 'マガジンを入れる';
  $('rackLabel').textContent = st.slideLocked ? 'スライドを戻す' : 'スライドを引く';
  $('explodeLabel').textContent = st.exploded ? '組み立てる' : '分解する';
  $('btnExplode').classList.toggle('on', st.exploded);
  document.querySelectorAll('#actions button').forEach(b => { if (b.dataset.act !== 'explode') b.disabled = st.exploded; });
}
function syncTools() {
  $('btnRotate').classList.toggle('on', controls.autoRotate);
  $('btnSound').classList.toggle('on', st.sound);
  $('btnSound').textContent = st.sound ? 'サウンド ON' : 'サウンド OFF';
}
const ACTIONS = { fire, mag: toggleMag, reload, rack, decock, explode: toggleExplode,
  rotate() { controls.autoRotate = !controls.autoRotate; syncTools(); },
  sound() { st.sound = !st.sound; syncTools(); },
  view() { homeView(); } };
document.querySelectorAll('button[data-act]').forEach(b => b.addEventListener('click', () => ACTIONS[b.dataset.act]()));
const KEYS = { ' ': 'fire', f: 'fire', m: 'mag', r: 'reload', s: 'rack', d: 'decock', x: 'explode' };
addEventListener('keydown', e => {
  if (e.repeat || e.ctrlKey || e.metaKey || e.altKey) return;
  const a = KEYS[e.key.toLowerCase()];
  if (a) { e.preventDefault(); ACTIONS[a](); }
});

// part labels (exploded view)
const labelEls = LABELS.map(([part, en, ja]) => {
  const el = document.createElement('div'); el.className = 'label';
  el.innerHTML = `<span>${ja}</span><em>${en}</em>`;
  $('labels').appendChild(el);
  return { part, el };
});
function placeLabels() {
  const show = v.explode > 0.82;
  for (const { part, el } of labelEls) {
    const p = parts[part];
    if (!p) continue;
    _p.copy(p.center).applyMatrix4(p.obj.matrixWorld).project(camera);
    el.style.left = ((_p.x * 0.5 + 0.5) * innerWidth) + 'px';
    el.style.top = ((-_p.y * 0.5 + 0.5) * innerHeight) + 'px';
    el.classList.toggle('show', show && _p.z < 1);
  }
}

// ---------------------------------------------------------------- loop
function resize() {
  renderer.setSize(innerWidth, innerHeight, false);
  camera.aspect = innerWidth / innerHeight;
  camera.fov = innerWidth < 820 ? 40 : 28;
  camera.updateProjectionMatrix();
}
addEventListener('resize', resize); resize();
const clock = new THREE.Clock();
// ?test=1 keeps the simulation running on timers, so it can be checked while the tab is not being painted
const TEST = new URLSearchParams(location.search).has('test');
const nextFrame = () => (TEST ? setTimeout(frame, 16) : requestAnimationFrame(frame));
function frame() {
  const dt = Math.min(clock.getDelta(), TEST ? 2 : 0.05);
  for (let i = tweens.length - 1; i >= 0; i--) {
    const t = tweens[i]; t.t += dt * 1000;
    const k = Math.min(1, t.t / t.ms);
    v[t.key] = t.from + (t.to - t.from) * t.ease(k);
    if (k >= 1) { tweens.splice(i, 1); t.res(); }
  }
  if (camFly) { camera.position.lerpVectors(camFly.p0, camFly.p1, v.cam); controls.target.lerpVectors(camFly.t0, camFly.t1, v.cam); }
  v.recoil += (0 - v.recoil) * Math.min(1, dt * 11);
  for (let i = casings.length - 1; i >= 0; i--) {
    const c = casings[i]; c.life += dt;
    c.vel.y -= 9.8 * 0.45 * dt;
    c.m.position.addScaledVector(c.vel, dt);
    c.m.rotation.x += c.spin.x * dt; c.m.rotation.y += c.spin.y * dt; c.m.rotation.z += c.spin.z * dt;
    if (c.m.position.y < FLOOR_Y + 0.005 && c.vel.y < 0) {
      c.m.position.y = FLOOR_Y + 0.005; c.vel.y *= -0.35; c.vel.x *= 0.5; c.vel.z *= 0.5; c.spin.multiplyScalar(0.4);
      if (!c.bounced) { c.bounced = true; noise(0.03, 5200, 0.12, 6, 'bandpass'); }
    }
    if (c.life > 6) { scene.remove(c.m); casings.splice(i, 1); }
  }
  placeParts();
  controls.update();
  gun.updateMatrixWorld(true);
  placeLabels();
  renderer.render(scene, camera);
  nextFrame();
}

// ---------------------------------------------------------------- load
new GLTFLoader().load('./assets/P230_parts.glb', gltf => {
  gun.add(gltf.scene);
  gltf.scene.updateMatrixWorld(true);
  gltf.scene.traverse(o => {
    if (!o.isMesh) return;
    o.material.envMapIntensity = 1.9;
    o.matrixAutoUpdate = false;
    o.geometry.computeBoundingBox();
    parts[o.name] = { obj: o, base: o.matrix.clone(), group: GROUP_OF[o.name] || null,
      center: o.geometry.boundingBox.getCenter(new THREE.Vector3()) };
  });
  window.__p230 = { parts, st, v, ACTIONS };      // handy for debugging from the console
  updateHud(); syncTools();
  setHint('<b>SPACE</b> で発砲。初弾はダブルアクション、2発目以降はシングルアクションです。');
  $('loading').classList.add('done');
  setTimeout(() => { $('loading').style.display = 'none'; }, 700);
  frame();
}, undefined, err => { $('loading').firstElementChild.textContent = 'MODEL LOAD FAILED'; console.error(err); });
