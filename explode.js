// Shared "exploded view" helpers.  three.js space: x = across the gun, y = up, z = along the barrel.
import * as THREE from 'three';

// items: [{ box: THREE.Box3 }]  ->  adds .offset (Vector3) and .delay (0..1) to every item.
// The biggest piece stays put; everything else moves away from the gun's centre, sideways / up-down first, then along the barrel.
export function planExplode(items, spread = 1) {
  const all = new THREE.Box3();
  items.forEach(i => all.union(i.box));
  const C = all.getCenter(new THREE.Vector3()), S = all.getSize(new THREE.Vector3());
  const vol = b => { const s = b.getSize(new THREE.Vector3()); return Math.max(s.x, 1e-4) * Math.max(s.y, 1e-4) * Math.max(s.z, 1e-4); };
  let base = items[0];
  items.forEach(i => { if (vol(i.box) > vol(base.box)) base = i; });
  const bc = base.box.getCenter(new THREE.Vector3());
  for (const i of items) {
    const off = new THREE.Vector3();
    if (i !== base) {
      const c = i.box.getCenter(new THREE.Vector3()), d = c.clone().sub(C), db = c.clone().sub(bc);
      if (Math.abs(d.x) > Math.max(0.0015, 0.12 * S.x)) off.x = Math.sign(d.x) * (Math.abs(d.x) * 1.4 + 0.9 * S.x + 0.02);
      const dy = Math.abs(db.y) > 0.04 * S.y ? db.y : d.y;
      if (Math.abs(dy) > 0.03 * S.y) off.y = dy * 0.8 + Math.sign(dy) * 0.3 * S.y;
      off.z = d.z * 0.32;
      if (!off.x && !off.y) off.z += (Math.sign(d.z) || 1) * 0.16 * S.z;      // on the centre line: slide out along the barrel
      if (off.length() < 0.02 * S.length()) off.y = 0.32 * S.y;
      off.multiplyScalar(spread);
    }
    i.offset = off;
  }
  const far = Math.max(...items.map(i => i.offset.length()), 1e-6);
  items.forEach(i => { i.delay = i === base ? 0 : 1 - i.offset.length() / far; });      // outer pieces leave first
  return { center: C, size: S };
}

// progress of one piece for overall progress k (0..1): staggered start, smooth stop
export function pieceK(k, delay) {
  const t = Math.min(1, Math.max(0, (k * 1.5 - delay * 0.5)));
  return t * t * (3 - 2 * t);
}

// Split a mesh into its connected pieces (one piece per separately modelled solid). Returns plain Meshes sharing the vertex buffers.
export function splitMesh(mesh) {
  const g = mesh.geometry, pos = g.attributes.position, n = pos.count;
  const index = g.index ? g.index.array : Uint32Array.from({ length: n }, (_, i) => i);
  const parent = new Uint32Array(n), weld = new Map();
  for (let i = 0; i < n; i++) {                       // weld vertices that only differ by UV / normal seams
    const key = Math.round(pos.getX(i) * 1e5) + ',' + Math.round(pos.getY(i) * 1e5) + ',' + Math.round(pos.getZ(i) * 1e5);
    const j = weld.get(key);
    if (j === undefined) { weld.set(key, i); parent[i] = i; } else parent[i] = j;
  }
  const find = a => { while (parent[a] !== a) { parent[a] = parent[parent[a]]; a = parent[a]; } return a; };
  for (let t = 0; t < index.length; t += 3) {
    const a = find(index[t]), b = find(index[t + 1]), c = find(index[t + 2]);
    if (b !== a) parent[b] = a;
    if (c !== a) parent[find(c)] = a;
  }
  const groups = new Map();
  for (let t = 0; t < index.length; t += 3) {
    const r = find(index[t]);
    let arr = groups.get(r);
    if (!arr) groups.set(r, arr = []);
    arr.push(index[t], index[t + 1], index[t + 2]);
  }
  const M = mesh.isSkinnedMesh ? mesh.bindMatrix : mesh.matrixWorld, v = new THREE.Vector3(), out = [];
  for (const idx of groups.values()) {
    const geo = new THREE.BufferGeometry();
    for (const name of ['position', 'normal', 'uv', 'uv1', 'tangent', 'color']) if (g.attributes[name]) geo.setAttribute(name, g.attributes[name]);
    geo.setIndex(idx);
    const box = new THREE.Box3();
    for (const i of idx) box.expandByPoint(v.fromBufferAttribute(pos, i).applyMatrix4(M));
    const piece = new THREE.Mesh(geo, mesh.material);
    piece.matrixAutoUpdate = false;
    piece.frustumCulled = false;
    out.push({ mesh: piece, base: M.clone(), box });
  }
  return out;
}
