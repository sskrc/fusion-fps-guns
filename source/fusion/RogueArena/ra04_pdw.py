# RA04 PDW : high-rate compact personal defence weapon (silhouette cues: very compact boxy polymer body with the magazine inside the
# pistol grip, folding vertical foregrip under the front, two-rod retractable stock, full top rail with flip sights).
from ra_lib import *

G = Gun('RA04_PDW', 'compact PDW')
AX = 26.0                                   # bore axis height
GR = Slant((-34, -8), 8)                    # pistol grip / magazine axis
ZB = 18.0                                   # body half width
RY, RZ = 38.0, 13.0                         # stock rod axis (y, |z|)
FP = (120.0, 0.0)                           # foregrip pivot
WELL = GR.rect(-30, 94, -13.4, 13.4)

# ------------------------------------------------------------------ body (static)
G.part('body', 'frame', 'olive', [
    ('add', slab([(-140, -2), (-140, 52), (176, 52), (182, 46), (182, 16), (177, 11), (106, 11), (102, -8), (-58, -8), (-66, -2)], ZB, 4)),
    ('add', plate([(-18, -8), (40, -8), (44, -12), (40, -34), (34, -40), (-22, -40)], 6)),                 # trigger guard
    ('cut', plate([(-15, -11), (36, -11), (38, -14), (35, -33), (31, -37), (-19, -37)], 20)),
    ('add', plate2([(113, 12), (113, 0), (115, -5), (120, -7), (125, -5), (127, 0), (127, 12)], 7.6, 12)),  # foregrip hinge ears
    ('cut', prism('xy', WELL, -8.6, 8.6)),                                                # magazine well (blind at the top)
    ('cut', box(-4, 14, -12, 6, -2.7, 2.7)),                                              # trigger slot
    ('cut', union(cyl((-141, RY, RZ), (89, RY, RZ), 4.0), cyl((-141, RY, -RZ), (89, RY, -RZ), 4.0))),   # stock rod bores
    ('cut', box(-141, -88, 45, 50, -5, 5)),                                               # charging handle tunnel
    ('cut', box(10, 56, 16, 32, 15.5, 19)),                                               # ejection port recess (right side)
    ('cut', row(5, lambda i: box2(118 + i * 11, 125 + i * 11, 30, 42, 16.2, 19))),         # front vents
    ('cut', row(6, lambda i: box2(-128 + i * 9, -123 + i * 9, 6, 30, 16.8, 19))),          # rear grooves
    ('cut', cyl((170, AX, 0), (183, AX, 0), 8.5)),                                        # muzzle recess
])
G.part('grip', 'frame', 'polymer', [
    ('add', plate([GR.pt(-2, 18), GR.pt(88, 18), GR.pt(93, 14), GR.pt(93, -17), GR.pt(40, -19), GR.pt(-2, -18)], 13)),
    ('cut', prism('xy', WELL, -8.6, 8.6)),
    ('add', plate2([GR.pt(10, 15), GR.pt(86, 15), GR.pt(86, -15), GR.pt(14, -15.5)], 13, 14.4)),
    ('cut', row(9, lambda i: box2(-70, -5, -26 - i * 8, -24.4 - i * 8, 13.7, 15))),
])
G.part('top_cover', 'frame', 'polymer', [
    ('add', prism('zy', [(-18.5, 44.5), (18.5, 44.5), (18.5, 48.3), (14.3, 52.5), (-14.3, 52.5), (-18.5, 48.3)], -139.8, 174)),
    ('cut', box(-141, -88, 45, 50, -5, 5)),                                               # charging handle tunnel
])
G.part('top_rail', 'frame', 'dark', [('add', rail(-136, 176, 52, 8))])
G.part('side_rail', 'frame', 'dark', [('add', row(5, lambda i: box(112 + i * 9.5, 117 + i * 9.5, 16, 24, ZB - 0.2, ZB + 2.6)))], mirror=True)
G.part('sight_lug', 'frame', 'dark', [('add', union(box(-130, -124, 54, 60, 6.6, 8), box(163.5, 169.5, 54, 60, 6.6, 8)))], mirror=True)
G.part('selector', 'frame', 'accent', [('add', cyl((-8, 1, ZB - 0.3), (-8, 1, ZB + 1.2), 4.0)), ('add', box(-8, 3, -0.3, 2.3, ZB - 0.3, ZB + 1.7))], mirror=True)
G.part('pins', 'frame', 'steel', [('add', union(*[cyl((x, y, ZB - 0.3), (x, y, ZB + 0.5), 2.2) for x, y in ((-112, 0), (66, 2), (92, 22), (-76, 36))]))], mirror=True)
G.part('muzzle', 'frame', 'steel', [
    ('add', cyl((168, AX, 0), (190, AX, 0), 6.5)), ('add', cyl((184, AX, 0), (190, AX, 0), 7.6)),
    ('cut', cyl((186, AX, 0), (191, AX, 0), 4.2)),                                        # shallow recess only: the barrel is solid
    ('cut', row(2, lambda i: box(175 + i * 4.5, 177.5 + i * 4.5, AX - 2, AX + 2, -9, 9))),
])
G.part('foregrip_pin', 'frame', 'steel', [('add', cyl((FP[0], FP[1], -12.4), (FP[0], FP[1], 12.4), 2.0))])

# ------------------------------------------------------------------ moving parts
G.part('foregrip', 'fgrip', 'polymer', [
    ('add', cyl((FP[0], FP[1], -7), (FP[0], FP[1], 7), 6.0)),
    ('add', box(114, 126, -9, 0, -7, 7)),
    ('add', plate([(110, -8), (130, -8), (130, -60), (127, -66), (113, -66), (110, -60)], 9)),
    ('cut', row(5, lambda i: box2(105, 135, -22 - i * 8, -20.4 - i * 8, 8.3, 10))),
])
G.part('stock_rod', 'stock', 'steel', [('add', cyl((-142, RY, RZ), (85, RY, RZ), 3.5))], mirror=True)
G.part('buttplate', 'stock', 'olive', [('add', slab([(-147, -2), (-140.5, -2), (-140.5, 43.5), (-147, 43.5)], 17, 2))])
G.part('butt_pad', 'stock', 'polymer', [('add', plate([(-147, -1), (-147, 42.5), (-150, 39.5), (-150, 2)], 15))])
G.part('charge_handle', 'charge', 'steel', [
    ('add', box(-138, -92, 45.4, 49.6, -4.5, 4.5)),
    ('add', box(-146.5, -140.6, 44.6, 50.6, -15, 15)),
    ('cut', box2(-147, -144, 44, 51, 6, 12)),
])
G.part('bolt', 'bolt', 'steel', [('add', box(33, 55.5, 16.5, 31.5, 15.9, 17.2))])
G.part('trigger', 'trigger', 'steel', [('add', plate([(1, 1), (7, 1), (7.6, -10), (6.6, -18), (7.6, -28), (5, -30), (2.6, -20), (1.4, -10)], 2.2))])
G.part('mag_body', 'mag', 'dark', [
    ('add', prism('xy', GR.rect(-29, 114, -13, 13), -8.2, 8.2)),
    ('cut', row(2, lambda i: plate2(GR.rect(100 + i * 5, 102 + i * 5, -14, 14), 7.6, 9))),
])
G.part('mag_base', 'mag', 'polymer', [('add', prism('xy', [GR.pt(114.3, -15), GR.pt(114.3, 15.5), GR.pt(118, 17), GR.pt(120.5, 15.5), GR.pt(120.5, -15)], -10.5, 10.5))])
G.part('sight_rear', 'sight_r', 'dark', [('add', plate([(-128.2, 57.2), (-101, 57.2), (-101, 58.8), (-107, 60.4), (-128.2, 60.4)], 6)), ('cut', box(-105, -100, 56, 61, -2, 2))])
G.part('sight_front', 'sight_f', 'dark', [('add', plate([(167.7, 57.2), (145, 57.2), (145, 58.8), (151, 60.4), (167.7, 60.4)], 5)), ('cut', box(144, 149, 56, 61, -1.6, 1.6))])

# ------------------------------------------------------------------ motion
G.group('mag', [G.move('mag', GR.axis(), 150.0)])
G.group('trigger', [G.rot('trigger', (4, -3, 0), (0, 0, 1), -15.0)])
G.group('bolt', [G.move('bolt', (-1, 0, 0), 22.0)])
G.group('charge', [G.move('charge', (-1, 0, 0), 35.0)])
G.group('stock', [G.move('stock', (-1, 0, 0), 200.0)])
G.group('fgrip', [G.rot('grip', (FP[0], FP[1], 0), (0, 0, 1), 90.0)])
G.group('sight_r', [G.rot('sights', (-127, 58.8, 0), (0, 0, 1), 90.0)])
G.group('sight_f', [G.rot('sights', (166.5, 58.8, 0), (0, 0, 1), -90.0)])
G.mode('OPEN', mag=1.0, charge=1.0, bolt=1.0)
G.mode('EXTENDED', stock=1.0, sights=1.0)
G.mode('FOLDED', grip=1.0)

G.clip('Idle', 2)
G.clip('Fire', 6, trigger=[(0, 0), (0.2, 1), (0.6, 1), (1, 0)], bolt=[(0.1, 0), (0.45, 1), (0.9, 0)])
G.clip('Reload', 60, mag=[(0.04, 0), (0.28, 1), (0.46, 1), (0.7, 0)], charge=[(0.76, 0), (0.86, 1), (0.9, 1), (0.97, 0)],
       bolt=[(0.76, 0), (0.86, 1), (0.9, 1), (0.97, 0)])
G.clip('Stock_Extend', 18, stock=[(0, 0), (1, 1)])
G.clip('Stock_Collapse', 18, stock=[(0, 1), (1, 0)])
G.clip('Grip_Fold', 14, grip=[(0, 0), (1, 1)])
G.clip('Grip_Unfold', 14, grip=[(0, 1), (1, 0)])
G.check()
