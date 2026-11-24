# P230-style compact pistol: display / game model only.
# Solid barrel (shallow muzzle dimple only), no chamber, no firing mechanism, no maker markings.
# Pure data (no Fusion / Blender imports). Units: mm.  +X muzzle, +Y up, +Z right side.
# Origin: rear face of the slide (x=0), top of the frame deck (y=0), centre plane (z=0).
import math

BORE_Y = 13.0
SLIDE_TRAVEL = 36.0
MAG_DIR = (-18.0 / 68.41, -66.0 / 68.41, 0.0)     # magazine insert/remove direction (down the grip)


def arc(cx, cy, r, a0, a1, n):
    return [(cx + r * math.cos(math.radians(a0 + (a1 - a0) * i / n)),
             cy + r * math.sin(math.radians(a0 + (a1 - a0) * i / n))) for i in range(n + 1)]


def prism(plane, pts, lo, hi):
    """plane 'xy': pts=(x,y), lo..hi along Z | 'zy': pts=(z,y), along X | 'xz': pts=(x,z), along Y"""
    return dict(k='prism', plane=plane, pts=[(float(a), float(b)) for a, b in pts], lo=float(lo), hi=float(hi))


def cyl(p1, p2, r, r2=None):
    return dict(k='cyl', p1=p1, p2=p2, r=float(r), r2=float(r if r2 is None else r2))


def box(x0, x1, y0, y1, z0, z1):
    return prism('xy', [(x0, y0), (x1, y0), (x1, y1), (x0, y1)], z0, z1)


def csg(*ops):
    return dict(k='csg', ops=list(ops))


def slide_section(off=0.0):
    """Slide cross-section (z,y): flat lower sides, tapered upper sides, round top."""
    w, w2 = 10.5 - off, 8.2 - off
    r = math.hypot(w2, 19.0 - 12.6)
    a = math.degrees(math.atan2(19.0 - 12.6, w2))
    return [(-w, -3.0 if off else 0.0), (w, -3.0 if off else 0.0), (w, 10.0)] + arc(0, 12.6, r, a, 180 - a, 12) + [(-w, 10.0)]


PARTS = []


def part(n, g, m, ops, fillet=0.0, mirror=False):
    PARTS.append(dict(n=n, g=g, m=m, ops=ops, fillet=fillet, mirror=mirror))


# ------------------------------------------------------------------ SLIDE
_serr = [('add', prism('xy', [(7 + i * 2.7, 2.5), (8.3 + i * 2.7, 2.5), (12.3 + i * 2.7, 20), (11 + i * 2.7, 20)], -12, 12))
         for i in range(12)]
_serr.append(('cut', prism('zy', slide_section(0.6), -5, 60)))

part('slide', 'slide', 'steel', [
    ('add', prism('xy', [(0, 0), (145, 0), (155.5, 3.2), (160, 9), (160, 20.5), (158, 22.6), (150, 23),
                         (22, 23), (8, 22.2), (0, 19.5)], -11, 11)),
    ('int', prism('zy', slide_section(), -5, 165)),
    ('int', prism('xz', [(-1, -10.5), (124, -10.5), (160.5, -8.3), (160.5, 8.3), (124, 10.5), (-1, 10.5)], -5, 30)),
    # inner cavity (open at the bottom), front wall 4 mm
    ('cut', prism('zy', [(-8, -1), (8, -1), (8, 17.2), (5.6, 19.8), (-5.6, 19.8), (-8, 17.2)], 52, 118)),
    # front part of the cavity keeps a closed floor, so nothing is visible from below ahead of the frame
    ('cut', prism('zy', [(-8, 2.2), (8, 2.2), (8, 17.2), (5.6, 19.8), (-5.6, 19.8), (-8, 17.2)], 117.9, 156)),
    ('cut', cyl((150, BORE_Y, 0), (162, BORE_Y, 0), 6.55)),
    # hammer slot and low clearance channel under the breech block
    ('cut', box(-1, 46, -1, 16.5, -3.6, 3.6)),
    ('cut', box(-1, 53, -1, 7.5, -3.6, 3.6)),
    # ejection port, right side + top
    ('cut', box(53, 79, 11.5, 25, 0.5, 12)),
    ('cut', csg(*_serr)),
    # sights
    ('add', prism('xy', [(145, 22.6), (154, 22.6), (154, 25.6), (150.5, 25.6)], -1.6, 1.6)),
    ('add', prism('zy', [(-6.5, 21.5), (6.5, 21.5), (6.5, 24.4), (5.5, 26), (1.6, 26), (1.6, 23.6),
                         (-1.6, 23.6), (-1.6, 26), (-5.5, 26), (-6.5, 24.4)], 5, 14)),
])
part('extractor', 'slide', 'steel_dark', [('add', box(38, 53.5, 12.6, 15.4, 9.6, 10.9))])

# ------------------------------------------------------------------ BARREL (fixed to frame, SOLID)
part('barrel', 'frame', 'steel_bright', [
    ('add', cyl((56, BORE_Y, 0), (160.6, BORE_Y, 0), 6.2)),
    ('add', prism('zy', [(-7.6, 4), (7.6, 4), (7.6, 17), (5.2, 19.4), (-5.2, 19.4), (-7.6, 17)], 56, 80)),
    ('add', box(56, 80, -1, 8, -5, 5)),
    ('cut', cyl((157.6, BORE_Y, 0), (162, BORE_Y, 0), 4.5)),          # 3 mm dimple, barrel is not bored
])

# ------------------------------------------------------------------ FRAME
FRAME_OUTLINE = [(-1, -0.2), (128, -0.2), (126.5, -6), (120, -11), (98, -12), (47, -12), (45, -20), (27, -86), (-10, -86),
                 (-12, -78), (-9.5, -50), (-8.5, -28), (-9.5, -18), (-11.5, -11), (-9, -6), (-4, -2.5)]
MAG_PROFILE = [(19.5, -1.5), (47.5, -1.5), (24.4, -86.4), (-3.6, -86.4)]
_well = [(18.3, 1.5), (48.7, 1.5), (22.1, -96), (-8.3, -96)]

part('frame', 'frame', 'alloy', [
    ('add', prism('xy', FRAME_OUTLINE, -10.5, 10.5)),
    ('int', prism('zy', [(-10.5, 0.5), (10.5, 0.5), (10.5, -10.5), (8, -14), (8, -90), (-8, -90), (-8, -14),
                         (-10.5, -10.5)], -30, 140)),
    ('cut', prism('xy', _well, -6.1, 6.1)),
    ('cut', box(-14, 12, -6, 1, -3.4, 3.4)),            # hammer slot (upper, open to the rear)
    ('cut', box(-8.5, 12, -14, -5.9, -3.4, 3.4)),       # hammer slot (lower)
    ('cut', box(58, 82, -17, -2.5, -3.6, 3.6)),         # trigger slot
])
part('trigger_guard', 'frame', 'alloy', [
    ('add', prism('xy', [(46, -11)] + arc(85, -24.75, 13.75, 90, -90, 14) + [(54, -38.5), (41.2, -36), (43.5, -24)],
                  -5, 5)),
    ('cut', prism('xy', [(50, -13.5)] + arc(84.5, -24, 10.5, 90, -90, 14) + [(55.5, -34.5), (47.5, -31.5), (48.2, -22)],
                  -6, 6)),
    ('cut', box(58, 82, -17, -2.5, -3.6, 3.6)),
], fillet=1.2)

_panel = [(42, -17), (26, -83), (-8.5, -83), (-10.4, -76), (-8, -50), (-7, -30), (-6.5, -22), (0, -19.5), (22, -15.5)]
part('grip_panel', 'frame', 'polymer', [
    ('add', prism('xy', _panel, 7.5, 15)),
    ('int', cyl((24.2, 1.6, -41.5), (-5.0, -105.4, -41.5), 56.0)),
], fillet=1.2, mirror=True)
part('grip_screw', 'frame', 'steel_dark', [('add', cyl((10, -50, 13.4), (10, -50, 15.0), 2.6)),
                                           ('cut', box(7, 13, -50.4, -49.6, 14.5, 15.5))], mirror=True)
# pins and take-down lever
part('pin_hammer', 'frame', 'steel_dark', [('add', cyl((4, -8, 10.3), (4, -8, 10.9), 1.8))], mirror=True)
part('pin_trigger', 'frame', 'steel_dark', [('add', cyl((72, -5, 10.3), (72, -5, 10.9), 1.6))], mirror=True)
part('takedown_lever', 'frame', 'steel', [
    ('add', cyl((88, -6, -10.3), (88, -6, -12.4), 3.2)),
    ('add', prism('xy', [(88, -3.6), (88, -8.4), (74, -7.6), (72.8, -5.8), (74, -4.2)], -12.1, -10.3)),
])
part('takedown_pin', 'frame', 'steel_dark', [('add', cyl((88, -6, 10.3), (88, -6, 11.1), 2.3))])

# ------------------------------------------------------------------ TRIGGER / HAMMER / DECOCKER
part('trigger', 'trigger', 'steel', [
    ('add', prism('xy', [(67.5, -5.6), (76.5, -5.6), (76.5, -9), (73.8, -16), (72.8, -23), (73.8, -30.5), (70.6, -31.5),
                         (68.4, -24), (68.4, -15), (66.8, -9)], -3, 3)),
], fillet=1.0)
part('hammer', 'hammer', 'steel', [
    ('add', prism('xy', [(0, -12), (8, -12), (9, -3), (7.6, 6), (5.2, 11.5), (2, 14.6), (-3, 16), (-6.8, 13.6),
                         (-6.8, 10.2), (-2.4, 8.6), (-0.6, 3), (-1, -4)], -3, 3)),
    ('cut', prism('xy', [(-7.5, 13.2), (-6.2, 13.2), (-6.2, 12.6), (-7.5, 12.6)], -4, 4)),
    ('cut', prism('xy', [(-7.5, 11.8), (-6.2, 11.8), (-6.2, 11.2), (-7.5, 11.2)], -4, 4)),
], fillet=0.8)
part('decocker', 'decocker', 'steel', [
    ('add', prism('xy', [(22, -3.5), (36, -3.5), (38, -6.5), (36, -9.5), (24, -10), (12, -12.5), (8, -12), (7, -9),
                         (10, -6.5)], -12.6, -10.3)),
    ('add', prism('xy', [(7, -9), (8, -12.5), (15, -12), (16, -7.6), (10, -6.5)], -14.4, -10.3)),
    ('add', cyl((33, -6.5, -10.3), (33, -6.5, -13.2), 2.2)),
])

# ------------------------------------------------------------------ MAGAZINE (+ heel catch)
part('mag_body', 'magazine', 'steel_mag', [
    ('add', prism('xy', MAG_PROFILE, -5.6, 5.6)),
    ('cut', prism('xy', [(24.5, 0), (49.5, 0), (48, -7.5), (26.5, -7.5)], -3.9, 3.9)),
])
part('mag_base', 'magazine', 'polymer', [
    ('add', prism('xy', [(-3.4, -86.4), (26, -86.4), (33, -88), (34.2, -91), (31.5, -93.5), (-2.6, -93.5), (-4, -91)],
                  -8.2, 8.2)),
], fillet=1.2)
part('dummy_case', 'magazine', 'brass', [('add', cyl((24.5, -5.3, 0), (37, -5.3, 0), 4.6))])
part('dummy_bullet', 'magazine', 'copper', [('add', cyl((37, -5.3, 0), (42.5, -5.3, 0), 4.5, 2.4))])
part('mag_catch', 'mag_catch', 'steel', [
    ('add', prism('xy', [(-9.6, -84.5), (-3.8, -84.5), (-5.7, -91.5), (-7.6, -93.3), (-11.6, -91)], -4.5, 4.5)),
], fillet=0.8)

# ------------------------------------------------------------------ motion definition (for the rig)
GROUPS = dict(
    frame=dict(type='static'),
    slide=dict(type='translate', axis=(-1, 0, 0), travel=SLIDE_TRAVEL),
    trigger=dict(type='rotate', pivot=(72, -5, 0), axis=(0, 0, 1), angle=-22.0),
    hammer=dict(type='rotate', pivot=(4, -8, 0), axis=(0, 0, 1), angle=48.0),
    decocker=dict(type='rotate', pivot=(33, -6.5, 0), axis=(0, 0, 1), angle=10.0),
    magazine=dict(type='translate', axis=MAG_DIR, travel=110.0),
    mag_catch=dict(type='translate', axis=(-1, 0, 0), travel=2.5),
)

MATERIALS = dict(
    steel=dict(rgb=(34, 36, 40), metal=1.0, rough=0.32),
    steel_dark=dict(rgb=(22, 23, 26), metal=1.0, rough=0.4),
    steel_bright=dict(rgb=(150, 152, 156), metal=1.0, rough=0.28),
    steel_mag=dict(rgb=(70, 72, 76), metal=1.0, rough=0.35),
    alloy=dict(rgb=(28, 29, 32), metal=0.9, rough=0.5),
    polymer=dict(rgb=(14, 14, 15), metal=0.0, rough=0.7),
    brass=dict(rgb=(200, 160, 70), metal=1.0, rough=0.3),
    copper=dict(rgb=(190, 110, 70), metal=1.0, rough=0.35),
)
