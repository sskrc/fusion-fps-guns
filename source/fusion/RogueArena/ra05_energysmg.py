# RA05 Energy SMG : boxy energy submachine gun (silhouette cues: big slab-sided receiver, long straight vertical cell ahead of the guard,
# skeletal side-folding stock).  Energy twist: box cell with glow windows, emitter coils around the solid barrel, charge strip.
from ra_lib import *

G = Gun('RA05_EnergySMG', 'energy submachine gun')
AX = 32.0                                   # bore axis height
GR = Slant((-40, -6), 18)                   # pistol grip axis
HX, HZ = -167.0, 21.0                       # stock hinge axis (vertical), just outside the right rear corner
ZU = 19.0                                   # upper receiver half width

# ------------------------------------------------------------------ upper receiver (static)
G.part('upper', 'frame', 'polymer', [
    ('add', obox(-160, 226, 10, 58, ZU, 4)),
    ('cut', box(58, 169, 40, 49, -21, -15)),                                             # charging handle track (left side)
    ('cut', box2(56, 154, 19, 29, 18, 21)),                                              # charge strip recess
    ('cut', row(5, lambda i: box2(-124 + i * 13, -117 + i * 13, 34, 50, 17.6, 21))),      # rear cooling slots
    ('cut', box2(-52, 40, 16, 36, 18.2, 21)),                                            # side panel recess
])
G.part('nose', 'frame', 'steel', [
    ('add', obox(172, 230, 8, 59, 20.5, 4.5)),
    ('add', cyl((228, AX, 0), (236, AX, 0), 15.5)),
    ('cut', row(3, lambda i: box2(180 + i * 15, 188 + i * 15, 16, 50, 19.5, 22))),
])
G.part('charge_strip', 'frame', 'glow', [('add', row(6, lambda i: box(60 + i * 15.5, 72 + i * 15.5, 22, 26, 17, 18.6)))], mirror=True)
G.part('top_rail', 'frame', 'dark', [('add', rail(-150, 222, 58, 8))])
G.part('under_rail', 'frame', 'dark', [('add', rail(108, 168, 10, 8, base=-2.0, tooth=-2.2))])
G.part('sight_rear', 'frame', 'dark', [('add', plate([(-146, 61), (-124, 61), (-124, 66), (-130, 71), (-146, 71)], 6)), ('cut', box(-147, -123, 65, 72, -2, 2))])
G.part('sight_front', 'frame', 'dark', [('add', plate([(196, 61), (216, 61), (213, 71), (203, 71)], 6)), ('cut', box(195, 217, 64, 72, -4, -1.2)),
                                        ('cut', box(195, 217, 64, 72, 1.2, 4))])

# ------------------------------------------------------------------ emitter (the barrel is a solid bar)
G.part('barrel', 'frame', 'dark', [('add', cyl((224, AX, 0), (274, AX, 0), 8.0))])
G.part('emitter_coils', 'frame', 'glow', [('add', union(*[cyl((241 + i * 11, AX, 0), (245 + i * 11, AX, 0), 11.5) for i in range(3)]))])
G.part('emitter_rods', 'frame', 'dark', [('add', union(*[cyl((230, AX + sy * 9.4, sz * 9.4), (274, AX + sy * 9.4, sz * 9.4), 2.0)
                                                         for sy in (-1, 1) for sz in (-1, 1)]))])
G.part('muzzle', 'frame', 'steel', [
    ('add', cyl((270, AX, 0), (282, AX, 0), 14.0)), ('add', cyl((268, AX, 0), (272, AX, 0), 15.5)),
    ('cut', cyl((278, AX, 0), (283, AX, 0), 6.0)),                                       # shallow recess only
])
G.part('muzzle_core', 'frame', 'glow', [('add', cyl((276, AX, 0), (278.6, AX, 0), 6.0))])

# ------------------------------------------------------------------ lower receiver, grip, guard (static)
G.part('lower', 'frame', 'polymer', [
    ('add', slab([(-160, 12), (98, 12), (98, -34), (36, -34), (34, -8), (-60, -8), (-160, 2)], 16, 2.5)),
    ('cut', box(43.5, 88.5, -36, 6.4, -11.5, 11.5)),                                     # cell well (blind at the top)
    ('add', plate([(-28, -8), (36, -8), (36, -38), (30, -42), (-36, -42)], 6)),          # trigger guard
    ('cut', plate([(-24, -11), (33, -11), (33, -36), (29, -39), (-32, -39)], 17)),
    ('cut', box(-4, 14, -12, 6, -2.7, 2.7)),                                             # trigger slot
    ('cut', row(4, lambda i: box2(46, 96, -30 + i * 7, -27 + i * 7, 15, 17))),            # well ribs
])
G.part('grip', 'frame', 'polymer', [
    ('add', plate([(-22, -7.9), GR.pt(8, 14), GR.pt(86, 14), GR.pt(90, 10), GR.pt(90, -15), GR.pt(40, -17), (-62, -7.9)], 12)),
    ('add', plate2([GR.pt(14, 11), GR.pt(82, 11), GR.pt(82, -12), GR.pt(20, -13)], 12, 13.5)),
    ('cut', row(8, lambda i: box2(-80, -20, -24 - i * 8, -22.2 - i * 8, 12.8, 14))),
])
G.part('selector', 'frame', 'accent', [('add', cyl((-18, 3, 16), (-18, 3, 17.6), 4.2)), ('add', box(-17, -6, 1.6, 4.4, 16, 17.6))], mirror=True)
G.part('cell_catch', 'frame', 'dark', [('add', box(20, 32, -4, 2, 16, 17.4))], mirror=True)
G.part('pins', 'frame', 'steel', [('add', union(*[cyl((x, y, 15.8), (x, y, 16.5), 2.2) for x, y in ((-140, 6), (-50, 0), (92, 6))]))], mirror=True)
G.part('hinge_block', 'frame', 'steel', [('add', union(*[s for y0, y1 in ((14, 24), (44, 54)) for s in (
    cyl((HX, y0, HZ), (HX, y1, HZ), 5.0), box(HX, -159, y0, y1, HZ - 5, HZ + 5))]))])
G.part('hinge_pin', 'frame', 'chrome', [('add', cyl((HX, 13, HZ), (HX, 55, HZ), 2.0))])

# ------------------------------------------------------------------ folding stock
G.part('stock_frame', 'stock', 'steel', [
    ('add', slab([(-161, 54), (-392, 54), (-400, 48), (-400, -22), (-392, -28), (-378, -22), (-215, 14), (-161, 14)], 9, 2.5)),
    ('cut', plate([(-192, 45), (-380, 45), (-380, -10), (-222, 24), (-192, 24)], 12)),    # skeleton window
    ('add', box(-172, -161, 24.4, 43.6, -9, HZ)),                                        # hinge arm
    ('add', cyl((HX, 24.4, HZ), (HX, 43.6, HZ), 5.0)),
    ('cut', row(3, lambda i: box2(-188 + i * 8, -184 + i * 8, 18, 50, 8, 10))),
])
G.part('stock_cheek', 'stock', 'polymer', [('add', tbox(-350, -215, 53, 58, 8, 3))])
G.part('butt_pad', 'stock', 'polymer', [('add', plate([(-399.5, 52), (-406, 48), (-406, -22), (-399.5, -27)], 10))])

# ------------------------------------------------------------------ moving parts
G.part('charge_handle', 'charge', 'plate', [('add', box(150, 166, 40.4, 48.6, -24, -15.4)), ('add', cyl((158, 44.5, -32), (158, 44.5, -23), 6.0))])
G.part('trigger', 'trigger', 'steel', [('add', plate([(1, 1), (7, 1), (7.6, -10), (6.6, -18), (7.6, -28), (5, -30), (2.6, -20), (1.4, -10)], 2.2))])
G.part('cell_body', 'mag', 'plate', [
    ('add', box(44, 88, -150, 6, -11, 11)),
    ('cut', row(4, lambda i: plate2([(50, -62 - i * 22), (82, -54 - i * 22), (82, -44 - i * 22), (50, -52 - i * 22)], 9.6, 12))),   # glow windows
    ('cut', box2(43, 89, -146, -142, 10.2, 12)),
])
G.part('cell_core', 'mag', 'glow', [('add', box(48, 84, -138, -42, -10.3, 10.3))])
G.part('cell_base', 'mag', 'polymer', [('add', obox(41, 91, -157, -150, 13, 2))])

# ------------------------------------------------------------------ motion
G.group('charge', [G.move('charge', (-1, 0, 0), 80.0)])
G.group('trigger', [G.rot('trigger', (4, -3, 0), (0, 0, 1), -15.0)])
G.group('mag', [G.move('mag', (0, -1, 0), 200.0)])
G.group('stock', [G.rot('stock', (HX, 34, HZ), (0, 1, 0), 178.0)])
G.mode('OPEN', mag=1.0, charge=1.0)
G.mode('FOLDED', stock=1.0)

G.clip('Idle', 2)
G.clip('Fire', 8, trigger=[(0, 0), (0.15, 1), (0.6, 1), (1, 0)])
G.clip('Reload', 66, mag=[(0.04, 0), (0.3, 1), (0.46, 1), (0.72, 0)], charge=[(0.76, 0), (0.86, 1), (0.9, 1), (0.97, 0)])
G.clip('Stock_Fold', 24, stock=[(0, 0), (1, 1)])
G.clip('Stock_Unfold', 24, stock=[(0, 1), (1, 0)])
G.check()
