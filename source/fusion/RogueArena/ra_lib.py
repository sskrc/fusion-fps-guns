# RogueArena weapon set : shared shape helpers, materials and the Gun container used by every raNN_*.py module.
# Pure data, no Fusion / Blender imports. Units: mm.  +X muzzle, +Y up, +Z right.
# Every gun is an original fictional design (display / game model): solid barrel, no internals, no markings.
import math

CLEAR = 0.35      # minimum gap between parts that move relative to each other (touching faces count as interference)


# ------------------------------------------------------------------ shapes
def prism(plane, pts, lo, hi):
    """plane 'xy': pts=(x,y), lo..hi along Z | 'zy': pts=(z,y), along X | 'xz': pts=(x,z), along Y"""
    return dict(k='prism', plane=plane, pts=[(float(a), float(b)) for a, b in pts], lo=float(min(lo, hi)), hi=float(max(lo, hi)))


def cyl(p1, p2, r, r2=None):
    return dict(k='cyl', p1=tuple(float(v) for v in p1), p2=tuple(float(v) for v in p2), r=float(r), r2=float(r if r2 is None else r2))


def csg(*ops):
    return dict(k='csg', ops=list(ops))


def union(*shapes):
    return csg(*[('add', s) for s in shapes])


def box(x0, x1, y0, y1, z0, z1):
    return prism('xy', [(x0, y0), (x1, y0), (x1, y1), (x0, y1)], z0, z1)


def box2(x0, x1, y0, y1, z0, z1):
    """The box and its mirror image in Z (for cuts / details on both sides of one part)."""
    return union(box(x0, x1, y0, y1, z0, z1), box(x0, x1, y0, y1, -z1, -z0))


def plate(pts, zh):
    """Side profile (x,y) extruded symmetrically to z = +-zh."""
    return prism('xy', pts, -zh, zh)


def plate2(pts, z0, z1):
    return union(prism('xy', pts, z0, z1), prism('xy', pts, -z1, -z0))


def obox(x0, x1, y0, y1, zh, c):
    """Box along X with chamfered long edges (octagonal section), z = +-zh."""
    return prism('zy', [(-zh, y0 + c), (-zh + c, y0), (zh - c, y0), (zh, y0 + c), (zh, y1 - c), (zh - c, y1), (-zh + c, y1), (-zh, y1 - c)], x0, x1)


def tbox(x0, x1, y0, y1, zh, c):
    """Box along X with only the two top long edges chamfered."""
    return prism('zy', [(-zh, y0), (zh, y0), (zh, y1 - c), (zh - c, y1), (-zh + c, y1), (-zh, y1 - c)], x0, x1)


def slab(pts, zh, c):
    """Side profile plate whose top-most and bottom-most long edges are chamfered by c."""
    xs = [p[0] for p in pts]
    ys = [p[1] for p in pts]
    return csg(('add', plate(pts, zh)), ('int', obox(min(xs) - 1, max(xs) + 1, min(ys), max(ys), zh, c)))


def tube(p1, p2, r_out, r_in):
    d = [b - a for a, b in zip(p1, p2)]
    n = math.sqrt(sum(v * v for v in d))
    e = [v / n for v in d]
    q1 = [a - v for a, v in zip(p1, e)]
    q2 = [b + v for b, v in zip(p2, e)]
    return csg(('add', cyl(p1, p2, r_out)), ('cut', cyl(q1, q2, r_in)))


def row(n, fn):
    """Union of fn(0) .. fn(n-1); handy as one 'cut' of repeated slots."""
    return union(*[fn(i) for i in range(n)])


def rail(x0, x1, y, zh=7.5, pitch=10.0, base=2.0, tooth=2.2):
    """Slotted accessory rail on top of height y (teeth along X). Returns one prism."""
    top, mid, w = y + base + tooth, y + base, pitch * 0.55
    pts = [(x0, y), (x1, y)]
    x = x1
    while True:
        xe = max(x - w, x0)
        pts += [(x, top), (xe, top)]
        if x - pitch <= x0 + 1e-6:
            if xe > x0 + 1e-6:
                pts += [(xe, mid), (x0, mid)]
            break
        pts += [(xe, mid), (x - pitch, mid)]
        x -= pitch
    return prism('xy', pts, -zh, zh)


def ngon(cx, cy, r, n, rot=0.0):
    return [(cx + r * math.cos(rot + 2 * math.pi * i / n), cy + r * math.sin(rot + 2 * math.pi * i / n)) for i in range(n)]


class Slant:
    """2-D frame in the XY plane for slanted things (grips, magazines): s runs along the axis, t across it (forward)."""

    def __init__(self, base, deg):
        a = math.radians(deg)                       # deg = lean back from straight down
        self.base = base
        self.d = (-math.sin(a), -math.cos(a))       # s : down (and back)
        self.n = (math.cos(a), -math.sin(a))        # t : forward

    def pt(self, s, t):
        return (self.base[0] + s * self.d[0] + t * self.n[0], self.base[1] + s * self.d[1] + t * self.n[1])

    def rect(self, s0, s1, t0, t1):
        return [self.pt(s0, t0), self.pt(s0, t1), self.pt(s1, t1), self.pt(s1, t0)]

    def axis(self):
        return (self.d[0], self.d[1], 0.0)


# ------------------------------------------------------------------ materials (keys are shared by all guns; wear is keyed on the names)
MATERIALS = dict(
    steel=dict(rgb=(58, 61, 66), metal=1.0, rough=0.42),        # parkerised receiver steel
    dark=dict(rgb=(26, 27, 30), metal=1.0, rough=0.38),         # blued / black oxide
    plate=dict(rgb=(142, 147, 152), metal=0.8, rough=0.46),     # bare alloy
    chrome=dict(rgb=(196, 198, 202), metal=1.0, rough=0.22),
    polymer=dict(rgb=(19, 19, 21), metal=0.0, rough=0.7),
    tan=dict(rgb=(146, 122, 88), metal=0.0, rough=0.68),        # sand polymer
    olive=dict(rgb=(66, 72, 52), metal=0.0, rough=0.66),
    accent=dict(rgb=(214, 62, 30), metal=0.1, rough=0.5),       # RogueArena signal red-orange paint
    lens=dict(rgb=(12, 20, 30), metal=0.6, rough=0.08),
    glow=dict(rgb=(60, 220, 255), metal=0.0, rough=0.35, emit=1.0),     # energy weapons
)


# ------------------------------------------------------------------ the gun container (same interface the pipeline scripts expect)
def _smooth(t):
    t = max(0.0, min(1.0, t))
    return t * t * (3 - 2 * t)


def track(keys, u):
    """keys = [(u0, v0), (u1, v1), ...] ascending; smooth interpolation, held before / after."""
    if u <= keys[0][0]:
        return keys[0][1]
    for (u0, v0), (u1, v1) in zip(keys, keys[1:]):
        if u <= u1:
            return v0 + (v1 - v0) * _smooth((u - u0) / (u1 - u0)) if u1 > u0 else v1
    return keys[-1][1]


class Gun:
    FPS = 30

    def __init__(self, name, title):
        self.NAME, self.TITLE = name, title
        self.PARTS, self.GROUPS, self.DOFS = [], dict(frame=dict(steps=[])), []
        self.MODES, self.WINDOWS, self.CLIPS = dict(READY={}), {}, []
        self.MATERIALS = MATERIALS

    # geometry
    def part(self, n, g, m, ops, mirror=False):
        assert m in MATERIALS, m
        assert n not in [p['n'] for p in self.PARTS], n
        self.PARTS.append(dict(n=n, g=g, m=m, ops=ops, fillet=0.0, mirror=mirror))

    # motion
    def move(self, dof, axis, travel):
        self._dof(dof)
        return dict(dof=dof, type='move', axis=tuple(axis), travel=float(travel))

    def rot(self, dof, pivot, axis, angle):
        self._dof(dof)
        return dict(dof=dof, type='rot', pivot=tuple(pivot), axis=tuple(axis), angle=float(angle))

    def _dof(self, dof):
        if dof not in self.DOFS:
            self.DOFS.append(dof)
            self.WINDOWS[dof] = (0.0, 1.0)

    def group(self, name, steps, mirror=False):
        self.GROUPS[name] = dict(steps=list(steps), mirror=True) if mirror else dict(steps=list(steps))

    def mode(self, name, **st):
        self.MODES[name] = st

    def clip(self, name, frames, **tracks):
        for d in tracks:
            assert d in self.DOFS, d
        dofs = list(self.DOFS)

        def f(u, tracks=tracks):
            return {d: (track(tracks[d], u) if d in tracks else 0.0) for d in dofs}
        self.CLIPS.append((name, frames, f))

    def check(self):
        for p in self.PARTS:
            assert p['g'] in self.GROUPS, (p['n'], p['g'])
            assert bool(p['mirror']) or not self.GROUPS[p['g']].get('mirror'), 'mirrored group needs mirrored parts: ' + p['n']
        return self

    # pipeline interface
    def expanded_groups(self):
        out = {}
        for name, g in self.GROUPS.items():
            if not g.get('mirror'):
                out[name] = dict(steps=[dict(s) for s in g['steps']])
                continue
            out[name + '_R'] = dict(steps=[dict(s) for s in g['steps']])
            left = []
            for s in g['steps']:
                s2 = dict(s)
                s2['axis'] = (s['axis'][0], s['axis'][1], -s['axis'][2])
                if s['type'] == 'rot':
                    s2['pivot'] = (s['pivot'][0], s['pivot'][1], -s['pivot'][2])
                    s2['angle'] = -s['angle']
                left.append(s2)
            out[name + '_L'] = dict(steps=left)
        return out

    def clip_state(self, clip, frame):
        name, n, f = clip
        return f(frame / float(max(1, n - 1)))
