# TALOS-IX : an original, fictional transforming rail emitter with exposed mechanics (display / game model).
# Three forms:  STOWED (compact block)  /  RAIL (telescoped barrel, stock, bipod, fins out)  /  BREACH (jaws and wings wide open).
# Pure data, no Fusion / Blender imports. Units: mm.  +X muzzle, +Y up, +Z right.  Barrel axis: y = 20.
import math

AX = 20.0


def prism(plane, pts, lo, hi):
    """plane 'xy': pts=(x,y), lo..hi along Z | 'zy': pts=(z,y), along X | 'xz': pts=(x,z), along Y"""
    return dict(k='prism', plane=plane, pts=[(float(a), float(b)) for a, b in pts], lo=float(lo), hi=float(hi))


def cyl(p1, p2, r, r2=None):
    return dict(k='cyl', p1=p1, p2=p2, r=float(r), r2=float(r if r2 is None else r2))


def box(x0, x1, y0, y1, z0, z1):
    return prism('xy', [(x0, y0), (x1, y0), (x1, y1), (x0, y1)], z0, z1)


def obox(x0, x1, y0, y1, zh, c):
    """Box along X with chamfered long edges (octagonal section), z = +-zh."""
    return prism('zy', [(-zh, y0 + c), (-zh + c, y0), (zh - c, y0), (zh, y0 + c), (zh, y1 - c), (zh - c, y1), (-zh + c, y1), (-zh, y1 - c)], x0, x1)


def csg(*ops):
    return dict(k='csg', ops=list(ops))


def gear(cx, cy, r, teeth, depth):
    pts = []
    for i in range(teeth):
        a0 = 2 * math.pi * i / teeth
        da = 2 * math.pi / teeth
        for f, rr in ((0.0, r), (0.28, r), (0.36, r + depth), (0.64, r + depth), (0.72, r)):
            pts.append((cx + rr * math.cos(a0 + f * da), cy + rr * math.sin(a0 + f * da)))
    return pts


PARTS = []


def part(n, g, m, ops, fillet=0.0, mirror=False):
    PARTS.append(dict(n=n, g=g, m=m, ops=ops, fillet=fillet, mirror=mirror))


# ------------------------------------------------------------------ RECEIVER (static)
part('receiver', 'frame', 'steel', [
    ('add', obox(-60, 80, 0, 40, 16, 4)),
    ('cut', box(-46, 66, 7, 33, 10, 20)), ('cut', box(-46, 66, 7, 33, -20, -10)),          # side pockets (mechanics live here)
    ('cut', cyl((-62, 10, 0), (32, 10, 0), 3.5)), ('cut', cyl((-62, 30, 0), (32, 30, 0), 3.5)),   # stock rod bores
    ('cut', cyl((60, AX, 0), (82, AX, 0), 6.4)),
])
part('top_rail', 'frame', 'steel', [('add', prism('xy', [(-52, 40), (72, 40)] + [p for i in range(12) for p in
     ((72 - i * 10, 43.4), (66.5 - i * 10, 43.4), (66.5 - i * 10, 41.4), (62 - i * 10, 41.4))][:-1] + [(-52, 43.4)], -6, 6))])
part('chassis', 'frame', 'steel', [('add', obox(76, 117, -14, -6.6, 12, 2.5)),
                                   ('cut', csg(*[('add', box(84 + i * 12, 91 + i * 12, -15, -4, -6, 6)) for i in range(3)]))])
part('sleeve', 'frame', 'steel', [('add', cyl((80, AX, 0), (122, AX, 0), 7.2)), ('cut', cyl((79, AX, 0), (123, AX, 0), 6.4))])
part('grip', 'frame', 'polymer', [
    ('add', prism('xy', [(-8, 0.5), (10, 0.5), (3, -68), (-1, -88), (-33, -88), (-36, -78), (-27, 0.5)], -11, 11)),
    ('int', obox(-60, 40, -100, 10, 11, 3.5)),
    ('cut', csg(*[('add', box(-40, 20, -30 - i * 9, -27 - i * 9, 9.6, 12)) for i in range(6)])),
    ('cut', csg(*[('add', box(-40, 20, -30 - i * 9, -27 - i * 9, -12, -9.6)) for i in range(6)])),
])
part('trigger_guard', 'frame', 'steel', [
    ('add', prism('xy', [(8, 1), (46, 1), (48, -6), (44, -30), (38, -36), (8, -36), (4, -28)], -4, 4)),
    ('cut', prism('xy', [(11, -3), (42, -3), (43.5, -7), (40, -27.5), (36.5, -31.5), (11, -31.5), (9, -26)], -5, 5)),
    ('cut', box(16, 30, -12, 2, -2.6, 2.6)),
])
part('trigger', 'trigger', 'chrome', [
    ('add', prism('xy', [(18.5, -5), (25.5, -5), (25, -11), (23.4, -18), (23.8, -25), (21.2, -26), (19.6, -19), (19.4, -12)], -2.2, 2.2))])
part('cell', 'frame', 'steel', [('add', obox(50, 76, -34, -0.2, 9, 2.5)), ('cut', box(55, 71, -28, -8, 7.5, 10)), ('cut', box(55, 71, -28, -8, -10, -7.5))])
part('cell_glow', 'frame', 'glow', [('add', box(56, 70, -27, -9, 7.0, 7.8))], mirror=True)
part('rear_fins', 'frame', 'chrome', [('add', box(-56 + i * 5, -53.5 + i * 5, 40, 47 - abs(i - 2) * 1.2, -11, 11)) for i in range(5)])
# inside the side pockets
part('pocket_glow', 'frame', 'glow', [('add', box(-42, 62, 18.5, 21.5, 10.0, 10.25))], mirror=True)
part('piston', 'frame', 'chrome', [('add', cyl((-42, 28, 13), (-4, 28, 13), 2.7)), ('add', cyl((-44, 28, 13), (-40, 28, 13), 3.4)),
                                   ('add', cyl((-8, 28, 13), (-4, 28, 13), 3.4))], mirror=True)
part('rod', 'rod', 'chrome', [('add', cyl((-3.6, 28, 13), (30, 28, 13), 1.4)), ('add', cyl((27, 28, 13), (31, 28, 13), 2.4))], mirror=True)
part('gear', 'gear', 'chrome', [('add', prism('xy', gear(51, 17, 7.6, 12, 1.8), 10.6, 13.4)), ('cut', cyl((51, 17, 9), (51, 17, 15), 2.2)),
                                ('cut', csg(*[('add', cyl((51 + 4.6 * math.cos(a), 17 + 4.6 * math.sin(a), 9), (51 + 4.6 * math.cos(a), 17 + 4.6 * math.sin(a), 15), 1.3))
                                              for a in (0.5, 2.07, 3.64, 5.21)]))], mirror=True)
part('gear_axle', 'frame', 'steel', [('add', cyl((51, 17, 10), (51, 17, 14.2), 1.9))], mirror=True)
part('fins', 'fins', 'chrome', [('add', box(4 + i * 6.5, 6.4 + i * 6.5, 8, 24, 10.45, 16)) for i in range(5)] +
     [('add', box(3, 33, 14, 18, 10.45, 11.5))], mirror=True)

# ------------------------------------------------------------------ WINGS (side armour, hinged along the top edge)
_wing = [(-48, 5), (-44, 1.5) if False else (-48, 5), (64, 5), (68, 9), (68, 40.4), (-48, 40.4)]
_wing = [(-48, 8), (-44, 4.6), (64, 4.6), (68, 8.6), (68, 40.4), (-48, 40.4)]
part('wing', 'wing', 'plate', [
    ('add', prism('xy', _wing, 16.6, 19.2)),
    ('cut', csg(*[('add', prism('xy', [(-30 + i * 9, 10), (-25 + i * 9, 10), (-21 + i * 9, 22), (-26 + i * 9, 22)], 15, 21)) for i in range(5)])),
    ('add', csg(*[('add', cyl((x, y, 19.0), (x, y, 20.2), 1.7)) for x, y in ((-43, 35.5), (62, 35.5), (-43, 11.5), (62, 12), (10, 35.5))])),
], mirror=True)
part('wing_stripe', 'wing', 'hazard', [('add', prism('xy', [(26, 8), (58, 8), (62, 12), (62, 16), (30, 16)], 19.2, 19.7))], mirror=True)
part('wing_pin', 'frame', 'chrome', [('add', cyl((-40, 40.5, 16.5), (60, 40.5, 16.5), 1.3))], mirror=True)

# ------------------------------------------------------------------ BARREL GROUP
part('inner_barrel', 'inner', 'chrome', [('add', cyl((70, AX, 0), (202, AX, 0), 6.0)), ('cut', cyl((198, AX, 0), (203, AX, 0), 4.4))])
part('inner_glow', 'inner', 'glow', [('add', cyl((196.5, AX, 0), (198.4, AX, 0), 4.3))] +
     [('add', csg(('add', cyl((x, AX, 0), (x + 2.4, AX, 0), 6.5)), ('cut', cyl((x - 1, AX, 0), (x + 3.4, AX, 0), 5.9)))) for x in (140, 156, 172, 188)])


def _prong(y0, y1, sign):
    ops = [('add', obox(85, 216, y0, y1, 8, 2.2)),
           ('cut', csg(*[('add', box(98 + i * 19, 110 + i * 19, y0 - 1, y1 + 1, -3.4, 3.4)) for i in range(6)])),
           ('cut', prism('xy', [(216.5, y1 + 1), (200, y1 + 1), (216.5, y1 - 7)] if sign > 0 else [(216.5, y0 - 1), (200, y0 - 1), (216.5, y0 + 7)], -9, 9))]
    return ops


part('prong_u', 'prong_u', 'steel', _prong(27.5, 38.5, 1))
part('prong_u_glow', 'prong_u', 'glow', [('add', box(92, 210, 27.42, 28.1, -7.2, -4.4)), ('add', box(92, 210, 27.42, 28.1, 4.4, 7.2))])
part('prong_d', 'prong_d', 'steel', _prong(1.5, 12.5, -1))
part('prong_d_glow', 'prong_d', 'glow', [('add', box(92, 210, 11.9, 12.58, -7.2, -4.4)), ('add', box(92, 210, 11.9, 12.58, 4.4, 7.2))])
part('claw', 'claw', 'plate', [
    ('add', prism('xy', [(88, 14), (150, 14), (192, 18.5), (192, 21.5), (150, 26), (88, 26)], 9, 12.4)),
    ('cut', csg(*[('add', box(104 + i * 16, 112 + i * 16, 17, 23, 8, 13)) for i in range(3)])),
], mirror=True)
part('claw_edge', 'claw', 'hazard', [('add', prism('xy', [(152, 14.6), (190, 18.7), (190, 19.6), (152, 16.2)], 12.4, 12.9))], mirror=True)

# ------------------------------------------------------------------ STOCK / SIGHT / BIPOD
part('stock_rods', 'stock', 'chrome', [('add', cyl((-74, 10, 0), (30, 10, 0), 3.0)), ('add', cyl((-74, 30, 0), (30, 30, 0), 3.0))])
part('stock_butt', 'stock', 'steel', [
    ('add', prism('xy', [(-61, -14), (-61, 44), (-70, 44), (-78, 36), (-78, -6), (-72, -14)], -12, 12)),
    ('int', obox(-90, -50, -20, 50, 12, 3)),
    ('cut', box(-80, -66, 14, 26, -13, 13)),
])
part('stock_pad', 'stock', 'polymer', [('add', prism('xy', [(-78, 35), (-81.5, 32), (-81.5, -2), (-78, -5)], -11, 11))])
part('sight', 'sight', 'steel', [
    ('add', prism('xy', [(-20.8, 43.7), (12, 43.7), (12, 46.4), (-20.8, 46.4)], -5, 5)),
    ('cut', box(-4, 8, 42, 48, -2.6, 2.6)),
])
part('sight_glow', 'sight', 'glow', [('add', box(8.2, 11.6, 44.4, 45.7, -3.4, 3.4))])
part('sight_pin', 'frame', 'chrome', [('add', cyl((-20, 45, -5.6), (-20, 45, 5.6), 1.2))])
part('leg', 'leg', 'steel', [
    ('add', prism('xy', [(121, -10.8), (212, -10.8), (216, -8.4), (212, -6), (121, -6)], 8.6, 13)),
    ('cut', csg(*[('add', box(134 + i * 18, 146 + i * 18, -12, -5, 10, 11.6)) for i in range(4)])),
], mirror=True)
part('leg_foot', 'leg', 'polymer', [('add', box(210, 218, -12, -4.8, 7.8, 13.8))], mirror=True)
part('leg_pin', 'frame', 'chrome', [('add', cyl((123, -8.4, 8), (123, -8.4, 13.6), 1.4))], mirror=True)

# ------------------------------------------------------------------ motion
_S, _C = math.sin(math.radians(20)), math.cos(math.radians(20))
GROUPS = dict(
    frame=dict(steps=[]),
    wing=dict(mirror=True, steps=[dict(dof='wing', type='rot', pivot=(0, 40.5, 16.5), axis=(1, 0, 0), angle=-70.0)]),
    fins=dict(mirror=True, steps=[dict(dof='vent', type='move', axis=(0, 0, 1), travel=18.0)]),
    rod=dict(mirror=True, steps=[dict(dof='extend', type='move', axis=(1, 0, 0), travel=10.0)]),
    gear=dict(mirror=True, steps=[dict(dof='extend', type='rot', pivot=(51, 17, 12), axis=(0, 0, 1), angle=300.0)]),
    inner=dict(steps=[dict(dof='extend', type='move', axis=(1, 0, 0), travel=60.0)]),
    prong_u=dict(steps=[dict(dof='split', type='move', axis=(0, 1, 0), travel=4.0), dict(dof='extend', type='move', axis=(1, 0, 0), travel=120.0),
                        dict(dof='pitch', type='rot', pivot=(90, 30, 0), axis=(0, 0, 1), angle=16.0)]),
    prong_d=dict(steps=[dict(dof='split', type='move', axis=(0, -1, 0), travel=4.0), dict(dof='extend', type='move', axis=(1, 0, 0), travel=120.0),
                        dict(dof='pitch', type='rot', pivot=(90, 10, 0), axis=(0, 0, 1), angle=-16.0)]),
    claw=dict(mirror=True, steps=[dict(dof='claw', type='rot', pivot=(88, 20, 9), axis=(0, 1, 0), angle=-28.0)]),
    stock=dict(steps=[dict(dof='stock', type='move', axis=(-1, 0, 0), travel=70.0)]),
    sight=dict(steps=[dict(dof='sight', type='rot', pivot=(-20, 45, 0), axis=(0, 0, 1), angle=90.0)]),
    leg=dict(mirror=True, steps=[dict(dof='legs', type='rot', pivot=(123, -8.4, 10.8), axis=(0, _S, _C), angle=-80.0)]),
    trigger=dict(steps=[dict(dof='trigger', type='rot', pivot=(22, -5, 0), axis=(0, 0, 1), angle=-18.0)]),
)
DOFS = ['wing', 'vent', 'split', 'extend', 'pitch', 'claw', 'stock', 'sight', 'legs', 'trigger']
MODES = dict(
    STOWED=dict(),
    RAIL=dict(wing=0.85, vent=1.0, split=1.0, extend=1.0, pitch=0.0, claw=0.2, stock=1.0, sight=1.0, legs=1.0),
    BREACH=dict(wing=1.25, vent=1.0, split=1.6, extend=0.35, pitch=1.0, claw=1.0, stock=0.5, sight=0.0, legs=1.0),
)
WINDOWS = dict(wing=(0.0, 0.3), stock=(0.1, 0.5), split=(0.2, 0.45), vent=(0.3, 0.6), legs=(0.3, 0.75), extend=(0.35, 0.8),
               pitch=(0.62, 0.95), claw=(0.5, 0.9), sight=(0.6, 0.9), trigger=(0, 1))


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
            k = math.sin(math.pi * min(1.0, u / 0.35)) if u < 0.35 else 0.0
            k2 = _smooth(min(1.0, u / 0.12)) * (1 - _smooth((u - 0.12) / 0.6))
            for d, amt in pulse.items():
                st[d] += amt * (k2 if d != 'trigger' else k)
        return st
    return f


FPS = 30
FIRE = dict(RAIL=dict(extend=-0.16, split=0.25, stock=-0.06, trigger=1.0), BREACH=dict(pitch=0.14, claw=0.12, wing=0.05, trigger=1.0))
CLIPS = [
    ('Idle_Stowed', 2, _hold('STOWED')), ('Idle_Rail', 2, _hold('RAIL')), ('Idle_Breach', 2, _hold('BREACH')),
    ('Stowed_to_Rail', 54, _transition('STOWED', 'RAIL', True)), ('Rail_to_Stowed', 54, _transition('RAIL', 'STOWED', False)),
    ('Stowed_to_Breach', 54, _transition('STOWED', 'BREACH', True)), ('Breach_to_Stowed', 54, _transition('BREACH', 'STOWED', False)),
    ('Rail_to_Breach', 42, _transition('RAIL', 'BREACH', True)), ('Breach_to_Rail', 42, _transition('BREACH', 'RAIL', False)),
    ('Fire_Rail', 24, _hold('RAIL', FIRE['RAIL'])), ('Fire_Breach', 24, _hold('BREACH', FIRE['BREACH'])),
]


def clip_state(clip, frame):
    name, n, f = clip
    return f(frame / float(max(1, n - 1)))


MATERIALS = dict(
    steel=dict(rgb=(54, 58, 64), metal=1.0, rough=0.42),
    plate=dict(rgb=(150, 155, 160), metal=0.75, rough=0.48),
    chrome=dict(rgb=(196, 198, 202), metal=1.0, rough=0.22),
    hazard=dict(rgb=(240, 176, 18), metal=0.2, rough=0.5),
    polymer=dict(rgb=(17, 17, 19), metal=0.0, rough=0.72),
    glow=dict(rgb=(255, 150, 40), metal=0.0, rough=0.35, emit=1.0),
)
