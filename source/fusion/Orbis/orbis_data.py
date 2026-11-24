# ORBIS-V : an original, fictional transforming energy emitter (display / game model).
# Three forms:  SEALED (closed, smooth shell)  /  LANCE (long, split shell, extended rails)  /  BLOOM (wide open).
# Pure data, no Fusion / Blender imports. Units: mm.  +X muzzle, +Y up, +Z right.
import math


# ------------------------------------------------------------------ curve helpers
def catmull(pts, n=6, closed=True):
    """Smooth polyline through pts (Catmull-Rom), n samples per span."""
    out = []
    m = len(pts)
    rng = range(m) if closed else range(m - 1)
    for i in rng:
        p0, p1, p2, p3 = (pts[(i - 1) % m] if closed or i > 0 else pts[0], pts[i], pts[(i + 1) % m],
                          pts[(i + 2) % m] if closed or i + 2 < m else pts[-1])
        for k in range(n):
            t = k / float(n)
            out.append(tuple(0.5 * ((2 * p1[j]) + (-p0[j] + p2[j]) * t + (2 * p0[j] - 5 * p1[j] + 4 * p2[j] - p3[j]) * t * t +
                                    (-p0[j] + 3 * p1[j] - 3 * p2[j] + p3[j]) * t ** 3) for j in (0, 1)))
    if not closed:
        out.append(tuple(pts[-1]))
    return out


def prism(plane, pts, lo, hi):
    """plane 'xy': pts=(x,y), lo..hi along Z | 'zy': pts=(z,y), along X | 'xz': pts=(x,z), along Y"""
    return dict(k='prism', plane=plane, pts=[(float(a), float(b)) for a, b in pts], lo=float(lo), hi=float(hi))


def cyl(p1, p2, r, r2=None):
    return dict(k='cyl', p1=p1, p2=p2, r=float(r), r2=float(r if r2 is None else r2))


def box(x0, x1, y0, y1, z0, z1):
    return prism('xy', [(x0, y0), (x1, y0), (x1, y1), (x0, y1)], z0, z1)


def csg(*ops):
    return dict(k='csg', ops=list(ops))


def slit(x, y, w, h, slant):
    return [(x, y), (x + w, y), (x + w + slant, y + h), (x + slant, y + h)]


PARTS = []


def part(n, g, m, ops, fillet=0.0, mirror=False):
    PARTS.append(dict(n=n, g=g, m=m, ops=ops, fillet=fillet, mirror=mirror))


# ------------------------------------------------------------------ SHELL (two mirrored halves)
SHELL_OUTLINE = catmull([(-56, 30), (-40, 41.5), (0, 44), (80, 44), (150, 41), (195, 34.5), (222, 25), (232, 13),
                         (224, 1), (200, -9.5), (150, -14), (72, -14), (50, -11), (41, 1), (0, 1), (-48, 1), (-57, 9), (-59, 20)], 5)
_sec = [(0.3, -14.0)]
for _i in range(1, 24):
    _t = -1 + 2 * _i / 24.0
    _sec.append((0.3 + 25.7 * (1 - abs(_t) ** 2.8) ** (1 / 2.8), 15 + 29 * _t))
_sec.append((0.3, 44.0))
_plan = [(-64, 0)] + catmull([(-64, 16), (-40, 24), (20, 27), (110, 26), (170, 20), (210, 12), (232, 4.5)], 5, closed=False) + [(238, 0)]
SHELL_CAVITY = [(-66, -3), (44, -3), (50, -12.3), (150, -12.3), (195, -8), (218, 0), (226, 14), (216, 26), (195, 32.5),
                (150, 38.8), (80, 41), (0, 41), (-40, 39), (-66, 28)]
_plan_in = [(-70, -3)] + catmull([(-70, 10.2), (0, 10.2), (150, 10.2), (185, 9.6), (205, 7), (220, 3.4), (226, 1.6)], 4, closed=False) + [(227, -3)]
_gills = [slit(62 + i * 13, 9, 5.5, 20, 9) for i in range(4)]
_gill_cut = [('add', prism('xy', g, 21.5, 32)) for g in _gills] + [('add', prism('xy', slit(150, 21, 44, 2.6, 2), 14, 32))]
_gill_glow = [('add', prism('xy', slit(63 + i * 13, 10, 3.5, 18, 8.1), 20.6, 21.6)) for i in range(4)]

part('shell', 'shell', 'armor', [
    ('add', prism('xy', SHELL_OUTLINE, 0.3, 28)),
    ('int', prism('zy', _sec, -70, 245)),
    ('int', prism('xz', _plan, -30, 60)),
    ('cut', csg(('add', prism('xy', SHELL_CAVITY, -2, 10.2)), ('int', prism('xz', _plan_in, -30, 60)))),
    ('cut', box(-70, 104, 38, 60, -2, 3.6)),               # slot for the crest
    ('cut', csg(*_gill_cut)),
], mirror=True)
part('shell_gills', 'shell', 'glow', _gill_glow, mirror=True)
part('shell_eye', 'shell', 'glow', [('add', prism('xy', slit(151, 21.4, 42, 1.8, 2), 13.2, 14.2))], mirror=True)

# ------------------------------------------------------------------ CORE (static)
part('core', 'frame', 'core', [
    ('add', prism('zy', [(-9.5, 2), (-7.5, 0), (7.5, 0), (9.5, 2), (9.5, 25.5), (7.5, 27.5), (-7.5, 27.5), (-9.5, 25.5)], -40, 58)),
    ('cut', cyl((-41, 8, 0), (14, 8, 0), 3.5)), ('cut', cyl((-41, 21, 0), (14, 21, 0), 3.5)),      # tail rods slide in here
    ('add', prism('xy', [(-37, 27), (-21, 27), (-24, 39.4), (-35, 39.4)], -2.4, 2.4)),                  # crest pylon
])
part('crest_pin', 'frame', 'dark', [('add', cyl((-30, 42, -3.7), (-30, 42, 3.7), 1.6))])
part('barrel', 'frame', 'dark', [('add', cyl((50, 14, 0), (188, 14, 0), 7.0)),
                                 ('cut', cyl((185, 14, 0), (189, 14, 0), 5.6))])
part('lens', 'frame', 'glow', [('add', cyl((183.5, 14, 0), (185.3, 14, 0), 5.4))])
for _i, _x in enumerate((84, 112, 140)):
    part('coil_%d' % _i, 'frame', 'glow', [('add', cyl((_x, 14, 0), (_x + 3, 14, 0), 7.5)), ('cut', cyl((_x - 1, 14, 0), (_x + 4, 14, 0), 6.9))])
part('core_strip', 'frame', 'glow', [('add', box(-30, 50, 9.5, 12, 9.4, 9.9))], mirror=True)
part('core_strip_b', 'frame', 'glow', [('add', box(-30, 50, 17, 18.2, 9.4, 9.9))], mirror=True)

GRIP = catmull([(22, 0), (18, -30), (11, -70), (6, -104), (-12, -110), (-34, -106), (-33, -70), (-27, -35), (-24, -12), (-26, 0)], 5)
part('grip', 'frame', 'polymer', [
    ('add', prism('xy', GRIP, -13, 13)),
    ('int', prism('zy', [(-13 * math.cos(math.radians(a)) ** 0.6 if math.cos(math.radians(a)) > 0 else 13 * (-math.cos(math.radians(a))) ** 0.6,
                          -52 + 62 * math.sin(math.radians(a))) for a in range(0, 360, 10)], -50, 40)),
    ('cut', box(-60, 60, 0.5, 20, -20, 20)),
], fillet=1.5)
part('grip_inlay', 'frame', 'glow', [('add', prism('xy', slit(-14, -88, 3, 60, 14), 12.2, 13.3))], mirror=True)
part('trigger_guard', 'frame', 'core', [
    ('add', prism('xy', catmull([(19, 1), (46, 1), (49, -14), (45, -31), (35, -38), (20, -36), (15, -24)], 4), -4, 4)),
    ('cut', prism('xy', catmull([(23, -3), (43, -3), (45, -14), (41.5, -27.5), (34, -33.5), (23, -32), (20, -22)], 4), -5, 5)),
    ('cut', box(26, 40, -12, 2, -2.6, 2.6)),
], fillet=1.0)
part('trigger', 'trigger', 'dark', [
    ('add', prism('xy', [(28.5, -5), (35.5, -5), (35, -11), (33.4, -18), (33.8, -25), (31.2, -26), (29.6, -19), (29.4, -12)], -2.2, 2.2)),
], fillet=0.7)

# ------------------------------------------------------------------ BEAK / JAW (centre pieces, hidden inside the sealed shell)
part('beak', 'beak', 'core', [
    ('add', prism('xy', [(58, 28.5), (198, 28.5), (197, 29.8), (185, 33.0), (150, 37.6), (100, 39.6), (58, 40)], -9.5, 9.5)),
    ('int', prism('xz', catmull([(50, -9.5), (150, -9.5), (185, -7.5), (199, -3), (199, 3), (185, 7.5), (150, 9.5), (50, 9.5)], 3), 20, 50)),
])
part('beak_glow', 'beak', 'glow', [('add', box(72, 186, 28.42, 29.2, -3, 3))])
part('jaw', 'jaw', 'core', [
    ('add', prism('xy', [(58, -0.7), (213, -0.7), (212, -1.6), (190, -8), (150, -11.8), (58, -11.8)], -9.5, 9.5)),
    ('int', prism('xz', catmull([(50, -9.5), (150, -9.5), (190, -7.5), (214, -3), (214, 3), (190, 7.5), (150, 9.5), (50, 9.5)], 3), -20, 5)),
])
part('jaw_glow', 'jaw', 'glow', [('add', box(72, 190, -1.5, -0.62, -3, 3))])

# ------------------------------------------------------------------ CREST / RAILS / TAIL
part('crest', 'crest', 'armor', [
    ('add', prism('xy', catmull([(-30, 41.4), (30, 41.4), (92, 41.4), (89, 45.5), (45, 50.5), (-8, 52), (-33, 47.5)], 4), -3, 3)),
])
part('crest_glow', 'crest', 'glow', [('add', prism('xy', [(-20, 45), (70, 45), (66, 46.6), (-20, 46.6)], -3.25, 3.25))])
part('rail_upper', 'rail', 'dark', [('add', prism('zy', [(-6, 22.3), (6, 22.3), (6, 26), (4.5, 27.4), (-4.5, 27.4), (-6, 26)], 58.4, 187))])
part('rail_lower', 'rail', 'dark', [('add', prism('zy', [(-6, 5.7), (6, 5.7), (6, 2), (4.5, 0.6), (-4.5, 0.6), (-6, 2)], 58.4, 187))])
part('muzzle_ring', 'rail', 'core', [('add', cyl((170, 14, 0), (184, 14, 0), 9.2)), ('cut', cyl((167, 14, 0), (187, 14, 0), 7.5))])
part('muzzle_glow', 'rail', 'glow', [('add', cyl((183.2, 14, 0), (184.6, 14, 0), 8.8)), ('cut', cyl((182, 14, 0), (186, 14, 0), 7.9))])
part('tail', 'tail', 'core', [
    ('add', prism('xy', catmull([(-41, 3), (-41, 16), (-41, 28.5), (-58, 29.5), (-76, 24), (-80, 13), (-70, 3.5)], 4), -9, 9)),
    ('cut', box(-41.3, 0, -10, 40, -12, 12)),
])
part('tail_rod_a', 'tail', 'dark', [('add', cyl((-60, 8, 0), (11, 8, 0), 3.0))])
part('tail_rod_b', 'tail', 'dark', [('add', cyl((-60, 21, 0), (11, 21, 0), 3.0))])
part('tail_glow', 'tail', 'glow', [('add', cyl((-80.6, 14, 0), (-78, 14, 0), 4.2))])

# ------------------------------------------------------------------ motion
# A group moves by a chain of steps; each step is driven by one named DOF (0 = sealed form).
GROUPS = dict(
    frame=dict(steps=[]),
    shell=dict(mirror=True, steps=[
        dict(dof='shell_out', type='move', axis=(0, 0, 1), travel=14.0),
        dict(dof='shell_fwd', type='move', axis=(1, 0, 0), travel=55.0),
        dict(dof='shell_yaw', type='rot', pivot=(-45, 0, 12), axis=(0, 1, 0), angle=-18.0)]),
    crest=dict(steps=[dict(dof='crest', type='rot', pivot=(-30, 42, 0), axis=(0, 0, 1), angle=24.0)]),
    beak=dict(steps=[dict(dof='beak', type='rot', pivot=(60, 34, 0), axis=(0, 0, 1), angle=22.0)]),
    jaw=dict(steps=[dict(dof='jaw', type='rot', pivot=(60, -6, 0), axis=(0, 0, 1), angle=-30.0)]),
    rail=dict(steps=[dict(dof='rail', type='move', axis=(1, 0, 0), travel=115.0)]),
    tail=dict(steps=[dict(dof='tail', type='move', axis=(-1, 0, 0), travel=40.0)]),
    trigger=dict(steps=[dict(dof='trigger', type='rot', pivot=(32, -5, 0), axis=(0, 0, 1), angle=-18.0)]),
)
DOFS = ['shell_out', 'shell_fwd', 'shell_yaw', 'crest', 'beak', 'jaw', 'rail', 'tail', 'trigger']
MODES = dict(
    SEALED=dict(),
    LANCE=dict(shell_out=1.0, shell_fwd=1.0, shell_yaw=0.3, crest=1.0, beak=0.15, jaw=0.25, rail=1.0, tail=1.0),
    BLOOM=dict(shell_out=1.4, shell_fwd=-0.3, shell_yaw=1.0, crest=1.3, beak=1.0, jaw=1.0, rail=0.25, tail=0.4),
)
# when each DOF moves inside a transition (fractions of the clip); closing plays the same schedule backwards
WINDOWS = dict(shell_out=(0.0, 0.3), shell_yaw=(0.2, 0.7), shell_fwd=(0.2, 0.65), tail=(0.15, 0.5), rail=(0.4, 0.85),
               crest=(0.45, 0.9), beak=(0.5, 0.92), jaw=(0.5, 0.92), trigger=(0, 1))


def expanded_groups():
    """Groups as actually rigged: mirrored groups become <name>_R and <name>_L."""
    out = {}
    for name, g in GROUPS.items():
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


def _smooth(t):
    t = max(0.0, min(1.0, t))
    return t * t * (3 - 2 * t)


def _transition(a, b, opening):
    A, B = MODES[a], MODES[b]

    def f(u):
        st = {}
        for d in DOFS:
            w0, w1 = WINDOWS[d]
            k = _smooth((u - w0) / (w1 - w0)) if opening else 1 - _smooth(((1 - u) - w0) / (w1 - w0))
            st[d] = A.get(d, 0.0) + (B.get(d, 0.0) - A.get(d, 0.0)) * k
        return st
    return f


def _hold(mode, pulse=None):
    M = MODES[mode]

    def f(u):
        st = {d: M.get(d, 0.0) for d in DOFS}
        if pulse:
            k = math.sin(math.pi * min(1.0, u / 0.35)) if u < 0.35 else 0.0     # quick kick, then settle
            k2 = _smooth(min(1.0, u / 0.12)) * (1 - _smooth((u - 0.12) / 0.6))
            for d, amt in pulse.items():
                st[d] += amt * (k2 if d != 'trigger' else k)
        return st
    return f


FPS = 30
# (name, frames, function u in [0,1] -> {dof: value})
CLIPS = [
    ('Idle_Sealed', 2, _hold('SEALED')), ('Idle_Lance', 2, _hold('LANCE')), ('Idle_Bloom', 2, _hold('BLOOM')),
    ('Sealed_to_Lance', 45, _transition('SEALED', 'LANCE', True)), ('Lance_to_Sealed', 45, _transition('LANCE', 'SEALED', False)),
    ('Sealed_to_Bloom', 45, _transition('SEALED', 'BLOOM', True)), ('Bloom_to_Sealed', 45, _transition('BLOOM', 'SEALED', False)),
    ('Lance_to_Bloom', 36, _transition('LANCE', 'BLOOM', True)), ('Bloom_to_Lance', 36, _transition('BLOOM', 'LANCE', False)),
    ('Fire_Lance', 24, _hold('LANCE', dict(rail=-0.22, shell_yaw=0.12, tail=0.2, trigger=1.0))),
    ('Fire_Bloom', 24, _hold('BLOOM', dict(beak=0.14, jaw=0.14, shell_yaw=0.1, crest=0.12, trigger=1.0))),
]


def clip_state(clip, frame):
    name, n, f = clip
    return f(frame / float(max(1, n - 1)))


MATERIALS = dict(
    armor=dict(rgb=(228, 231, 236), metal=0.15, rough=0.32),
    core=dict(rgb=(46, 50, 58), metal=0.9, rough=0.42),
    dark=dict(rgb=(20, 21, 24), metal=1.0, rough=0.35),
    polymer=dict(rgb=(18, 18, 20), metal=0.0, rough=0.7),
    glow=dict(rgb=(70, 225, 255), metal=0.0, rough=0.35, emit=1.0),
)
