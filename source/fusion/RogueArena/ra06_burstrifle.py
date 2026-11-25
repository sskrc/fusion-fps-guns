# RA06 Burst Rifle : polymer burst-fire rifle (silhouette cues: tall carry handle with a built-in optic bridging the receiver,
# long vented handguard, curved box magazine, skeletal side-folding stock).
from ra_lib import *

G = Gun('RA06_BurstRifle', 'burst rifle')
AX = 34.0                                   # bore axis height
GR = Slant((-40, -6), 18)                   # pistol grip axis
MG = Slant((78, 2), -6)                    # magazine axis (leans forward)
HX, HZ = -167.0, 20.0                       # stock hinge axis (vertical), just outside the right rear corner
ZU = 18.0                                   # receiver half width
OY = 100.0                                  # optic axis height

# ------------------------------------------------------------------ receiver + handguard (static)
G.part('upper', 'frame', 'olive', [
    ('add', obox(-160, 130, 8, 60, ZU, 4)),
    ('cut', box(-40, 90, 56, 61, -4, 4)),                                                # charging handle groove (top)
    ('cut', box(20, 72, 36, 47, 16.6, 20)),                                              # ejection port recess
    ('cut', row(4, lambda i: box2(-128 + i * 12, -122 + i * 12, 30, 50, 16.8, 20))),      # rear grooves
    ('cut', box2(-70, 8, 16, 30, 17.2, 20)),
])
G.part('port_door', 'frame', 'dark', [('add', box(22, 70, 37.5, 45.5, 16.2, 16.7))])
G.part('handguard', 'frame', 'olive', [
    ('add', obox(128, 370, 12, 56, 17, 5)),
    ('cut', row(6, lambda i: box2(146 + i * 36, 170 + i * 36, 38, 45, 15, 19))),          # vents, upper row
    ('cut', row(6, lambda i: box2(146 + i * 36, 170 + i * 36, 23, 30, 15, 19))),          # vents, lower row
    ('cut', row(5, lambda i: box(164 + i * 36, 188 + i * 36, 53, 58, -3.5, 3.5))),        # top vents
    ('cut', cyl((362, AX, 0), (371, AX, 0), 11.0)),
])
G.part('handguard_liner', 'frame', 'dark', [('add', obox(136, 364, 14, 54.6, 15.6, 5))])
G.part('under_lug', 'frame', 'dark', [('add', rail(150, 230, 12, 7, base=-2.0, tooth=-2.2))])
G.part('barrel', 'frame', 'dark', [('add', cyl((360, AX, 0), (572, AX, 0), 7.5)), ('add', cyl((368, AX, 0), (384, AX, 0), 9.5)),
                                   ('add', cyl((468, AX, 0), (478, AX, 0), 9.2))])
G.part('muzzle', 'frame', 'steel', [
    ('add', cyl((568, AX, 0), (602, AX, 0), 9.5)), ('add', cyl((566, AX, 0), (572, AX, 0), 10.8)),
    ('cut', cyl((597.5, AX, 0), (603, AX, 0), 4.4)),                                     # shallow recess only: the barrel is solid
    ('cut', row(4, lambda i: box(577 + i * 6, 580 + i * 6, AX - 2.5, AX + 2.5, -11, 11))),
    ('cut', row(4, lambda i: box(577 + i * 6, 580 + i * 6, AX + 5.5, AX + 11, -2.5, 2.5))),
])

# ------------------------------------------------------------------ carry handle with built-in optic (static)
G.part('carry_handle', 'frame', 'polymer', [
    ('add', slab([(-142, 58), (-130, 84), (-112, 90), (72, 90), (102, 84), (129, 58)], 9, 2.5)),
    ('cut', plate([(-114, 57), (-104, 80), (82, 80), (104, 57)], 12)),                    # hand window (the charging handle runs below it)
])
G.part('optic', 'frame', 'dark', [
    ('add', obox(-78, 36, 88, 112, 11.5, 4)),
    ('add', cyl((30, OY, 0), (46, OY, 0), 11.0)),
    ('cut', cyl((42, OY, 0), (47, OY, 0), 9.0)),
    ('cut', cyl((-79, OY, 0), (-75, OY, 0), 7.5)),
    ('add', tbox(-70, 26, 111.5, 115, 3.2, 1)),                                          # backup sight rib
    ('cut', box(-71, 27, 113.2, 116, -1, 1)),
    ('cut', row(3, lambda i: box2(-50 + i * 24, -36 + i * 24, 94, 106, 10.6, 13))),
])
G.part('optic_lens', 'frame', 'lens', [('add', cyl((41, OY, 0), (43.2, OY, 0), 9.0)), ('add', cyl((-76.2, OY, 0), (-74, OY, 0), 7.5))])
G.part('optic_knob', 'frame', 'steel', [('add', cyl((-20, OY, 9.5), (-20, OY, 15.5), 5.0))], mirror=True)

# ------------------------------------------------------------------ lower receiver, grip, guard (static)
G.part('lower', 'frame', 'polymer', [
    ('add', slab([(-160, 10), (116, 10), (120, -30), (44, -30), (42, -8), (-60, -8), (-160, 2)], 15, 2.5)),
    ('cut', prism('xy', MG.rect(-1, 46, -29.5, 29.5), -11, 11)),                          # magazine well (blind at the top)
    ('add', plate([(-28, -8), (44, -8), (44, -36), (38, -40), (-36, -40)], 6)),           # trigger guard
    ('cut', plate([(-24, -11), (41, -11), (41, -34), (37, -37), (-32, -37)], 16)),
    ('cut', box(-4, 14, -12, 6, -2.7, 2.7)),                                             # trigger slot
])
G.part('grip', 'frame', 'polymer', [
    ('add', plate([(-22, -7.9), GR.pt(8, 14), GR.pt(86, 14), GR.pt(90, 10), GR.pt(90, -15), GR.pt(40, -17), (-62, -7.9)], 12)),
    ('add', plate2([GR.pt(14, 11), GR.pt(82, 11), GR.pt(82, -12), GR.pt(20, -13)], 12, 13.5)),
    ('cut', row(8, lambda i: box2(-80, -20, -24 - i * 8, -22.2 - i * 8, 12.8, 14))),
])
G.part('mag_catch', 'frame', 'dark', [('add', box(54, 66, -4, 2, 15, 16.4))], mirror=True)
G.part('pins', 'frame', 'steel', [('add', union(*[cyl((x, y, 14.8), (x, y, 15.5), 2.2) for x, y in ((-140, 5), (106, 4), (-50, 0))]))], mirror=True)
G.part('hinge_block', 'frame', 'steel', [('add', union(*[s for y0, y1 in ((14, 24), (44, 54)) for s in (
    cyl((HX, y0, HZ), (HX, y1, HZ), 5.0), box(HX, -159, y0, y1, HZ - 5, HZ + 5))]))])
G.part('hinge_pin', 'frame', 'chrome', [('add', cyl((HX, 13, HZ), (HX, 55, HZ), 2.0))])

# ------------------------------------------------------------------ folding stock
G.part('stock_frame', 'stock', 'olive', [
    ('add', slab([(-161, 56), (-390, 56), (-400, 50), (-400, -30), (-392, -36), (-378, -30), (-232, 12), (-161, 12)], 9, 2.5)),
    ('cut', plate([(-196, 46), (-380, 46), (-380, -15), (-240, 25), (-196, 25)], 12)),    # skeleton window
    ('add', box(-172, -161, 24.4, 43.6, -9, HZ)),                                        # hinge arm
    ('add', cyl((HX, 24.4, HZ), (HX, 43.6, HZ), 5.0)),
    ('cut', row(3, lambda i: box2(-190 + i * 8, -186 + i * 8, 17, 51, 8, 10))),
])
G.part('stock_cheek', 'stock', 'polymer', [('add', tbox(-360, -210, 55, 60, 8, 3))])
G.part('butt_pad', 'stock', 'polymer', [('add', plate([(-399.5, 54), (-406, 50), (-406, -30), (-399.5, -35)], 10))])

# ------------------------------------------------------------------ moving parts
G.part('charge_handle', 'charge', 'steel', [('add', box(64, 80, 56.4, 66, -3.6, 3.6)), ('add', box(67, 77, 62, 66, -12, 12))])
G.part('trigger', 'trigger', 'steel', [('add', plate([(1, 1), (7, 1), (7.6, -10), (6.6, -18), (7.6, -28), (5, -30), (2.6, -20), (1.4, -10)], 2.2))])
G.part('selector', 'selector', 'accent', [('add', box2(-17, -5, 1.6, 4.4, 15.4, 17)), ('add', cyl((-18, 3, 15.4), (-18, 3, 17), 4.2)),
                                           ('add', cyl((-18, 3, -17), (-18, 3, -15.4), 4.2))])      # both sides
G.part('mag_body', 'mag', 'polymer', [
    ('add', plate([MG.pt(0, -29), MG.pt(0, 29), MG.pt(60, 29), MG.pt(96, 34), MG.pt(126, 45), MG.pt(148, 58), MG.pt(160, 2), MG.pt(134, -12),
                   MG.pt(98, -23), MG.pt(60, -29)], 10.4)),
    ('cut', plate2([MG.pt(66, 22), MG.pt(96, 27), MG.pt(124, 38), MG.pt(141, 48), MG.pt(149, 10), MG.pt(130, -4), MG.pt(98, -16), MG.pt(66, -22)], 9.6, 12)),
])
G.part('mag_floor', 'mag', 'olive', [('add', plate([MG.pt(147.3, 59.9), MG.pt(160.1, -0.1), MG.pt(165.3, 1.0), MG.pt(152.5, 61)], 12))])

# ------------------------------------------------------------------ motion
G.group('charge', [G.move('charge', (-1, 0, 0), 90.0)])
G.group('trigger', [G.rot('trigger', (4, -3, 0), (0, 0, 1), -15.0)])
G.group('selector', [G.rot('selector', (-18, 3, 0), (0, 0, 1), -50.0)])
G.group('mag', [G.move('mag', MG.axis(), 190.0)])
G.group('stock', [G.rot('stock', (HX, 34, HZ), (0, 1, 0), 178.0)])
G.mode('OPEN', mag=1.0, charge=1.0, selector=1.0)
G.mode('FOLDED', stock=1.0)

G.clip('Idle', 2)
G.clip('Fire', 8, trigger=[(0, 0), (0.15, 1), (0.6, 1), (1, 0)], charge=[(0.1, 0), (0.4, 0.3), (0.85, 0)])
G.clip('Fire_Burst', 16, trigger=[(0, 0), (0.08, 1), (0.85, 1), (1, 0)],
       charge=[(0.05, 0), (0.17, 0.3), (0.3, 0), (0.33, 0), (0.45, 0.3), (0.58, 0), (0.61, 0), (0.73, 0.3), (0.88, 0)])
G.clip('Reload', 66, mag=[(0.04, 0), (0.28, 1), (0.46, 1), (0.7, 0)], charge=[(0.76, 0), (0.86, 1), (0.9, 1), (0.97, 0)])
G.clip('Selector_Burst', 8, selector=[(0, 0), (1, 1)])
G.clip('Stock_Fold', 24, stock=[(0, 0), (1, 1)])
G.clip('Stock_Unfold', 24, stock=[(0, 1), (1, 0)])
G.check()
