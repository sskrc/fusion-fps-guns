// Generic viewer: viewer.html?g=<id> loads the gun's rigged GLB and turns its animation clips into buttons.
import * as THREE from 'three';
import { GLTFLoader } from 'three/addons/loaders/GLTFLoader.js';
import { OrbitControls } from 'three/addons/controls/OrbitControls.js';
import { RoomEnvironment } from 'three/addons/environments/RoomEnvironment.js';
import { GUNS, SECTIONS } from './guns.js';

const $ = id => document.getElementById(id);
const params = new URLSearchParams(location.search);
const gun = GUNS.find(g => g.id === params.get('g') && g.glb);
if (!gun) {
  $('loadText').innerHTML = 'この銃は見つかりません<br><a href="./">銃の一覧へ戻る</a>';
  throw new Error('unknown gun');
}
document.title = gun.name + ' | Fusion FPS Guns';
$('tag').textContent = SECTIONS.find(s => s.id === gun.sec).title + '  //  ' + gun.ja;
$('name').textContent = gun.name;
$('desc').textContent = gun.desc;

const LABEL = {
  Fire: '発砲', Fire_Last: '最終弾を撃つ', Fire_Burst: '3点バースト', Reload: 'リロード', Reload_Tactical: 'タクティカルリロード',
  Slide_Rack: 'スライドを引く', Selector_Switch: 'セレクター切替', Selector_Burst: 'セレクター切替', Spin: 'シリンダーを回す',
  Hammer_Cock: 'ハンマーを起こす', Stock_Extend: 'ストックを伸ばす', Stock_Collapse: 'ストックを縮める', Stock_Fold: 'ストックをたたむ',
  Stock_Unfold: 'ストックを開く', Grip_Fold: 'グリップをたたむ', Grip_Unfold: 'グリップを起こす', Sights_Up: 'サイトを起こす',
  Sights_Down: 'サイトを倒す', Pump: 'ポンプを引く', Bipod_Deploy: '二脚を展開', Bipod_Fold: '二脚をたたむ',
  Vent_Open: '冷却フラップを開く', Vent_Close: '冷却フラップを閉じる', Overheat: '過熱して排熱',
};
const label = n => LABEL[n] || n.replace(/_/g, ' ');

// ---------------------------------------------------------------- renderer / scene
const canvas = $('view');
const renderer = new THREE.WebGLRenderer({ canvas, antialias: true, alpha: true });
renderer.setPixelRatio(Math.min(devicePixelRatio, 2));
renderer.toneMapping = THREE.ACESFilmicToneMapping;
renderer.toneMappingExposure = 1.7;
const scene = new THREE.Scene();
scene.environment = new THREE.PMREMGenerator(renderer).fromScene(new RoomEnvironment(), 0.04).texture;
const camera = new THREE.PerspectiveCamera(28, 1, 0.01, 40);
const controls = new OrbitControls(camera, canvas);
controls.enableDamping = true;
controls.enablePan = false;
controls.autoRotateSpeed = 1.2;
scene.add(new THREE.HemisphereLight(0xdfe8ff, 0x20242c, 1.0));
const key = new THREE.DirectionalLight(0xfff1dd, 3.2); key.position.set(-0.5, 0.8, 0.6); scene.add(key);
const rim = new THREE.DirectionalLight(0xbfe6ff, 2.8); rim.position.set(0.7, 0.3, -0.6); scene.add(rim);

const HOME = { target: new THREE.Vector3(), size: new THREE.Vector3(1, 1, 1) };
function homeView() {
  const aspect = innerWidth / innerHeight, portrait = aspect < 1;
  const dir = (portrait ? new THREE.Vector3(-0.5, 0.2, 0.84) : new THREE.Vector3(-0.74, 0.17, 0.48)).normalize();
  const s = HOME.size, ext = s.z * Math.hypot(dir.x, dir.y) + s.x * Math.abs(dir.z);      // width the gun takes on screen
  const half = Math.tan(THREE.MathUtils.degToRad(camera.fov / 2));
  const dist = Math.max(ext * (portrait ? 1.12 : 1.5) / (2 * half * aspect), s.y * (portrait ? 2.2 : 3.3) / (2 * half)) + s.z * 0.5 * Math.abs(dir.z);
  camera.position.copy(HOME.target).addScaledVector(dir, dist);
  controls.target.copy(HOME.target);
  controls.minDistance = dist * 0.3;
  controls.maxDistance = dist * 3;
}
function resize() {
  renderer.setSize(innerWidth, innerHeight, false);
  camera.aspect = innerWidth / innerHeight;
  camera.updateProjectionMatrix();
}
addEventListener('resize', resize);
resize();

function radialTexture(stops) {
  const c = document.createElement('canvas'); c.width = c.height = 256;
  const g = c.getContext('2d'); const gr = g.createRadialGradient(128, 128, 0, 128, 128, 128);
  stops.forEach(([o, col]) => gr.addColorStop(o, col)); g.fillStyle = gr; g.fillRect(0, 0, 256, 256);
  return new THREE.CanvasTexture(c);
}

// ---------------------------------------------------------------- animation bookkeeping
let mixer = null;
const entries = [];          // { name, clip, action, tracks:Set, kind, active, hold }
const buttons = [];          // { el, kind:'action'|'toggle', a, b, on }

function near(prop, a, ao, b, bo) {
  if (prop === 'quaternion') {
    const d = a[ao] * b[bo] + a[ao + 1] * b[bo + 1] + a[ao + 2] * b[bo + 2] + a[ao + 3] * b[bo + 3];
    return Math.abs(d) > 1 - 2e-6;
  }
  const tol = prop === 'position' ? 3e-5 : 1e-4;
  return Math.abs(a[ao] - b[bo]) < tol && Math.abs(a[ao + 1] - b[bo + 1]) < tol && Math.abs(a[ao + 2] - b[bo + 2]) < tol;
}

function prepare(root, clips) {
  for (const clip of clips) {
    const info = {};
    clip.tracks = clip.tracks.filter(t => {
      const p = THREE.PropertyBinding.parseTrackName(t.name);
      const node = root.getObjectByName(p.nodeName);
      if (!node || !node[p.propertyName]) return false;
      const rest = node[p.propertyName].toArray(), st = t.getValueSize(), v = t.values, n = v.length / st;
      let still = true;
      for (let i = 0; i < n && still; i++) still = near(p.propertyName, v, i * st, rest, 0);
      if (still) return false;                                   // this bone does nothing in this clip
      info[t.name] = { prop: p.propertyName, first: Array.from(v.slice(0, st)), last: Array.from(v.slice(v.length - st)),
        startRest: near(p.propertyName, v, 0, rest, 0), endRest: near(p.propertyName, v, v.length - st, rest, 0) };
      return true;
    });
    if (!clip.tracks.length) continue;                           // Idle
    const vals = Object.values(info);
    const s = vals.every(i => i.startRest), e = vals.every(i => i.endRest);
    const action = mixer.clipAction(clip);
    action.setLoop(THREE.LoopOnce, 1);
    action.clampWhenFinished = true;
    entries.push({ name: clip.name, clip, action, info, tracks: new Set(Object.keys(info)), active: false, hold: false,
      kind: s && e ? 'action' : s ? 'open' : e ? 'close' : 'action' });
  }
  // pair every "open" clip with the "close" clip that starts where it ends (fold / unfold, last shot / reload ...)
  const used = new Set();
  for (const o of entries.filter(x => x.kind === 'open')) {
    const c = entries.find(c => c.kind === 'close' && !used.has(c) && Object.entries(c.info).every(([tn, ci]) =>
      ci.startRest || (o.info[tn] && near(ci.prop, ci.first, 0, o.info[tn].last, 0))) &&
      Object.entries(o.info).every(([tn, oi]) => oi.endRest || c.info[tn]));
    if (c) used.add(c);
    // a shot or reload that ends on an equivalent pose (e.g. the cylinder one chamber on) is a one-shot action, not a toggle
    if (!c && /^(Fire|Reload|Spin)/.test(o.name)) { o.kind = 'action'; continue; }
    buttons.push({ kind: 'toggle', a: o, b: c || null, on: false });
  }
  for (const x of entries) {
    if (x.kind === 'close' && !used.has(x)) x.kind = 'action';
    if (x.kind === 'action') buttons.push({ kind: 'action', a: x });
  }
  const order = entries.map(e => e.name);
  buttons.sort((p, q) => order.indexOf(p.a.name) - order.indexOf(q.a.name));
}

function stopEntry(e) { e.action.stop(); e.active = false; e.hold = false; }
function clearConflicts(e) {            // nothing else may drive the same bones
  for (const o of entries) {
    if (o === e || !o.active) continue;
    if ([...e.tracks].some(t => o.tracks.has(t))) {
      stopEntry(o);
      const b = buttons.find(b => b.kind === 'toggle' && (b.a === o || b.b === o));
      if (b) b.on = false;
    }
  }
}
function start(e, hold) {
  clearConflicts(e);
  e.action.reset().play();
  e.active = true; e.hold = hold;
}
function press(b) {
  if (b.kind === 'action') { start(b.a, false); }
  else if (!b.on) { start(b.a, true); b.on = true; }
  else {
    b.on = false;
    stopEntry(b.a);
    if (b.b) start(b.b, false);
  }
  refresh();
}
function resetPose() {
  entries.forEach(stopEntry);
  buttons.forEach(b => { b.on = false; });
  refresh();
}
function refresh() {
  for (const b of buttons) {
    const playing = (b.a.active && b.a.action.isRunning()) || (b.b && b.b.active && b.b.action.isRunning());
    b.el.classList.toggle('playing', !!playing);
    b.el.classList.toggle('on', b.kind === 'toggle' && b.on);
    b.text.textContent = b.kind === 'toggle' && b.on ? (b.b ? label(b.b.name) : label(b.a.name) + '（戻す）') : label(b.a.name);
  }
  const now = entries.filter(e => e.active && e.action.isRunning()).map(e => label(e.name));
  $('sNow').textContent = now.length ? now.join(' / ') : '—';
}

// ---------------------------------------------------------------- load
new GLTFLoader().loadAsync(gun.glb).then(gltf => {
  const root = gltf.scene;
  scene.add(root);
  // rest-pose bounds straight from the geometry (Box3.setFromObject on a skinned mesh needs an updated skeleton)
  const box = new THREE.Box3();
  root.updateMatrixWorld(true);
  root.traverse(o => {
    if (!o.isMesh) return;
    o.frustumCulled = false;
    o.geometry.computeBoundingBox();
    box.union(o.isSkinnedMesh ? o.geometry.boundingBox : o.geometry.boundingBox.clone().applyMatrix4(o.matrixWorld));
  });
  const size = box.getSize(new THREE.Vector3()), mid = box.getCenter(new THREE.Vector3());
  HOME.target.copy(mid);
  HOME.size.copy(size);
  homeView();
  const floorY = box.min.y - size.y * 0.12;
  const shadow = new THREE.Mesh(new THREE.PlaneGeometry(size.z * 1.5, size.z * 0.5 + 0.1),
    new THREE.MeshBasicMaterial({ map: radialTexture([[0, 'rgba(0,0,0,.5)'], [1, 'rgba(0,0,0,0)']]), transparent: true, depthWrite: false }));
  shadow.rotation.x = -Math.PI / 2; shadow.rotation.z = Math.PI / 2;
  shadow.position.set(mid.x, floorY, mid.z);
  scene.add(shadow);
  $('sLen').textContent = Math.round(size.z * 1000) + ' mm';
  $('sHgt').textContent = Math.round(size.y * 1000) + ' mm';

  mixer = new THREE.AnimationMixer(root);
  prepare(root, gltf.animations);
  mixer.addEventListener('finished', ev => {
    const e = entries.find(e => e.action === ev.action);
    if (e && !e.hold) stopEntry(e);          // ends in the rest pose, so releasing the bones does not pop
    refresh();
  });
  const nav = $('actions');
  buttons.forEach((b, i) => {
    b.el = document.createElement('button');
    b.el.innerHTML = `<kbd>${i < 9 ? i + 1 : ''}</kbd><span></span>`;
    if (i >= 9) b.el.querySelector('kbd').remove();
    b.text = b.el.querySelector('span');
    b.el.addEventListener('click', () => press(b));
    nav.appendChild(b.el);
  });
  $('sClips').textContent = buttons.length ? entries.length + ' 種' : 'なし';
  if (!buttons.length) document.querySelector('.hint').innerHTML = 'ドラッグで回転、ホイールでズーム。<br>このモデルに可動部はありません。';
  refresh();
  $('loading').classList.add('done');
  window.__v = { gun, entries, buttons, press, resetPose, root, mixer, size };
}).catch(err => {
  console.error(err);
  $('loadText').innerHTML = 'モデルを読み込めませんでした<br><a href="./">銃の一覧へ戻る</a>';
});

// ---------------------------------------------------------------- input / loop
$('btnRotate').addEventListener('click', () => { controls.autoRotate = !controls.autoRotate; $('btnRotate').classList.toggle('on', controls.autoRotate); });
$('btnReset').addEventListener('click', resetPose);
$('btnView').addEventListener('click', homeView);
addEventListener('keydown', ev => {
  if (ev.repeat || ev.metaKey || ev.ctrlKey || ev.altKey) return;
  const i = '123456789'.indexOf(ev.key);
  if (i >= 0 && buttons[i]) press(buttons[i]);
});

const clock = new THREE.Clock();
function tick() {
  const dt = Math.min(clock.getDelta(), 0.1);
  if (mixer) mixer.update(dt);
  controls.update();
  renderer.render(scene, camera);
}
if (params.get('test')) setInterval(tick, 33);            // the test harness runs with the tab hidden, where rAF is paused
else renderer.setAnimationLoop(tick);
