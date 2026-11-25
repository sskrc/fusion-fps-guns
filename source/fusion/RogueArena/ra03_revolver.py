# RA03 Revolver : heavy hand cannon (silhouette cues: barrel in line with the BOTTOM chamber, tall slab-sided angular shroud with a rib
# above the barrel, cylinder that swings up and out on a top-hinged crane).  Own touches: short top rail, recessed slanted vents.
from ra_lib import *

G = Gun('RA03_Revolver', 'heavy revolver')
AX = 14.0                                   # bore axis (= bottom chamber)
CY, CR, CH = 27.0, 21.0, 13.0               # cylinder axis height, radius, chamber circle radius
X0, X1 = 8.6, 50.0                          # cylinder rear / front face
PV = (53.0, -8.0)                           # crane hinge axis (y, z), runs along X in the left edge of the top strap
ZF = 11.0                                   # frame half width
GR = Slant((-34, -4), 22)                   # grip axis
HP = (-14.0, 36.0)                          # hammer pivot


def ring(n, rad, r, xa, xb, off):
    """n cylinders along X, evenly spaced on a circle of radius rad around the cylinder axis (off = angle of the first, deg)."""
    out = []
    for i in range(n):
        a = math.radians(off + 360.0 / n * i)
        y, z = CY + rad * math.sin(a), rad * math.cos(a)
        out.append(cyl((xa, y, z), (xb, y, z), r))
    return union(*out)


# ------------------------------------------------------------------ frame (static)
G.part('frame', 'frame', 'steel', [
    ('add', plate([(-12, -8), (64, -8), (72, 2), (56, 2), (56, 57), (-8, 57), (-22, 46), (-27, 22), (-34, 8), GR.pt(8, -16), GR.pt(80, -17),
                   GR.pt(86, -12), GR.pt(86, 12), GR.pt(10, 13)], ZF)),
    ('add', cyl((0.5, CY, 0), (7.5, CY, 0), 19.5)),                                       # recoil shield
    ('cut', box(7.5, 57, 4, 49, -25, 25)),                                               # cylinder window
    ('cut', box(50, 57, 48, 58, -25, -2.5)),                                             # notch for the crane knuckle
    ('cut', union(*[prism('zy', [(s * (ZF + 0.1), 53), (s * (ZF + 0.1), 57.1), (s * (ZF - 4), 57.1)], -30, 57) for s in (1, -1)])),  # strap chamfers
    ('add', plate([(-18, -8), (40, -8), (42, -14), (40, -34), (33, -41), (-30, -41), (-28, -30)], 6.0)),                # trigger guard
    ('cut', plate([(-16, -12), (34, -12), (36, -16), (34.5, -31), (30, -36), (-27, -36)], 15)),
    ('cut', box(-4, 14, -13, 2.5, -2.7, 2.7)),                                           # trigger slot
    ('cut', box(-45, -7, 30, 60, -3.2, 3.2)),                                            # hammer slot
])
G.part('shroud', 'frame', 'dark', [
    ('add', slab([(56, 1), (166, 1), (172, 7), (172, 26), (164, 31), (56, 31)], 10, 3)),                # barrel housing (bore low)
    ('cut', cyl((166, AX, 0), (173, AX, 0), 8.6)),                                       # muzzle counterbore
    ('cut', box2(62, 150, 13, 15, 9.0, 11)),                                             # side flute
    ('add', cyl((50.6, AX, 0), (57, AX, 0), 5.0)),                                       # barrel stub facing the bottom chamber
])
G.part('rib', 'frame', 'steel', [
    ('add', slab([(56, 29), (164, 29), (153, 50), (104, 57), (56, 57)], 7.5, 3)),
    ('cut', row(4, lambda i: plate([(68 + i * 21, 34), (79 + i * 21, 34), (85 + i * 21, 47), (74 + i * 21, 47)], 9))),   # vent slots
])
G.part('rib_core', 'frame', 'dark', [('add', plate([(62, 32), (150, 32), (146, 48), (62, 49)], 3.5))])   # closes the vents (no see-through)
G.part('barrel', 'frame', 'chrome', [('add', cyl((150, AX, 0), (175, AX, 0), 6.4)), ('cut', cyl((171.5, AX, 0), (176, AX, 0), 4.6))])
G.part('top_rail', 'frame', 'dark', [('add', rail(12, 102, 57, 4.5))])
G.part('under_rail', 'frame', 'steel', [('add', rail(96, 148, 1, 6, base=-2.0, tooth=-2.2))])
G.part('sight_front', 'frame', 'steel', [('add', plate([(136, 52.3), (150, 50.3), (149, 58.5), (143, 58.5)], 1.6))])
G.part('sight_rear', 'frame', 'steel', [('add', plate([(-8, 57), (6, 57), (6, 61), (-6, 61)], 7)), ('cut', box(-9, 7, 58.8, 62, -1.6, 1.6))])
G.part('crane_pin', 'frame', 'dark', [('add', cyl((44, PV[0], PV[1]), (56.2, PV[0], PV[1]), 1.6))])
G.part('hammer_pin', 'frame', 'dark', [('add', cyl((HP[0], HP[1], -ZF - 0.4), (HP[0], HP[1], ZF + 0.4), 1.8))])
G.part('latch', 'frame', 'dark', [('add', prism('xy', [(-21, 23), (-7, 23), (-5, 27), (-7, 31), (-21, 31)], -ZF - 1.6, -ZF + 0.3))])
G.part('mark', 'frame', 'accent', [('add', box(-13, -5, 40.5, 42.5, ZF - 0.3, ZF + 0.4))], mirror=True)
G.part('screws', 'frame', 'dark', [('add', union(*[cyl((x, y, ZF - 0.3), (x, y, ZF + 0.5), 2.0) for x, y in ((30, -2), (-12, 10), (62, -3))]))], mirror=True)
G.part('grip_panel', 'frame', 'tan', [
    ('add', prism('xy', [GR.pt(10, 11), GR.pt(40, 13.5), GR.pt(82, 12), GR.pt(87, 5), GR.pt(86, -17), GR.pt(50, -19.5), GR.pt(20, -16), GR.pt(8, -12)], ZF - 0.4, ZF + 3.2)),
    ('cut', row(8, lambda i: box(-100, 0, -24 - i * 8, -22.5 - i * 8, ZF + 2.4, ZF + 4))),
], mirror=True)
G.part('grip_cap', 'frame', 'dark', [('add', plate([GR.pt(85.8, -13.5), GR.pt(85.8, 13), GR.pt(89, 12), GR.pt(89, -12.5)], ZF + 1.2))])

# ------------------------------------------------------------------ cylinder + crane
G.part('cylinder', 'cyl', 'plate', [
    ('add', cyl((X0, CY, 0), (X1, CY, 0), CR)),
    ('cut', ring(6, CR + 3.5, 7.0, 25, X1 + 1, -60)),                                    # flutes (between the chambers)
    ('cut', ring(6, CH, 5.0, X1 - 3, X1 + 1, -90)),                                      # chamber mouths : shallow recesses only
    ('cut', ring(6, CH, 5.4, X0 - 1, X0 + 3.5, -90)),
    ('cut', ring(6, CR + 0.6, 1.8, 12, 16, -90)),                                        # stop notches
])
G.part('ejector', 'cyl', 'steel', [('add', cyl((8.0, CY, 0), (X0 + 0.1, CY, 0), 7.0))])
G.part('crane', 'crane', 'steel', [
    ('add', cyl((50.5, PV[0], PV[1]), (55.5, PV[0], PV[1]), 3.5)),
    ('add', prism('zy', [(-4.75, 54.0), (3.25, 28.0), (-3.25, 26.0), (-11.25, 52.0)], 50.5, 55.5)),
    ('add', cyl((50.5, CY, 0), (55.5, CY, 0), 5.5)),
])

# ------------------------------------------------------------------ hammer / trigger
G.part('hammer', 'hammer', 'steel', [
    ('add', plate([(-17, 33), (-11, 36), (-10, 52), (-13, 55), (-27, 57), (-29, 54), (-19, 50), (-20, 36)], 2.7)),
    ('add', cyl((HP[0], HP[1], -2.7), (HP[0], HP[1], 2.7), 4.0)),
])
G.part('trigger', 'trigger', 'steel', [('add', plate([(1, 1), (7, 1), (7.6, -10), (6.6, -18), (7.6, -28), (5, -30), (2.6, -20), (1.4, -10)], 2.2))])

# ------------------------------------------------------------------ motion
SWING = G.rot('crane', (0, PV[0], PV[1]), (1, 0, 0), 100.0)
G.group('crane', [SWING])
G.group('cyl', [SWING, G.rot('spin', (0, CY, 0), (1, 0, 0), 360.0)])          # spin axis rides on the crane
G.group('hammer', [G.rot('hammer', (HP[0], HP[1], 0), (0, 0, 1), 40.0)])
G.group('trigger', [G.rot('trigger', (4, -3, 0), (0, 0, 1), -15.0)])
G.mode('OPEN', crane=1.0, spin=1.0 / 12)
G.mode('COCKED', hammer=1.0, trigger=0.4)

S6 = 1.0 / 6
G.clip('Idle', 2)
G.clip('Fire', 14, trigger=[(0, 0), (0.3, 1), (0.6, 1), (1, 0)], hammer=[(0, 0), (0.3, 1), (0.38, 0)], spin=[(0, 0), (0.28, S6), (1, S6)])
G.clip('Reload', 60, crane=[(0.05, 0), (0.25, 1), (0.75, 1), (0.95, 0)], spin=[(0.3, 0), (0.7, 3 * S6)])
G.clip('Spin', 30, crane=[(0, 1), (1, 1)], spin=[(0, 0), (1, 1)])
G.clip('Hammer_Cock', 12, hammer=[(0, 0), (0.8, 1), (1, 1)], spin=[(0, 0), (0.8, S6), (1, S6)])
G.check()
