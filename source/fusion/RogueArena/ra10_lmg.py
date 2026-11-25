# RA10 LMG : ultralight belt-fed machine gun (silhouette cues: unbroken full-length top rail over a side-opening feed cover,
# soft ammunition pouch hanging under the receiver, slim fluted barrel with a carry handle, sliding carbine stock).
from ra_lib import *

G = Gun('RA10_LMG', 'light machine gun')
AX = 36.0                                   # bore axis height
GR = Slant((-40, -6), 18)                   # pistol grip axis
BP = (385.0, 9.0)                           # bipod hinge (x, y)
CH = (27.0, -19.2)                          # feed cover hinge line (y, z) : lower outer edge, left side

# ------------------------------------------------------------------ receiver + handguard (static)
G.part('receiver', 'frame', 'steel', [
    ('add', obox(-110, 212, 10, 52, 15, 4)),
    ('cut', box(48, 142, 31, 45, -16, -11)),                                             # feed tray recess (under the side cover)
    ('cut', box(58, 192, 37.5, 44.5, 13, 16)),                                           # charging handle track (right side)
    ('cut', box(68, 132, 17, 31, 13.8, 16)),                                             # ejection port recess
    ('cut', row(4, lambda i: box2(-96 + i * 16, -86 + i * 16, 22, 40, 14, 16))),
])
G.part('port_door', 'frame', 'dark', [('add', box(70, 130, 18.5, 29.5, 13.4, 14.1))])
G.part('feed_tray', 'frame', 'plate', [('add', box(50, 140, 33, 43, -12.4, -10.5)), ('cut', row(8, lambda i: box(55 + i * 10.5, 59 + i * 10.5, 34.5, 41.5, -13, -11.6)))])
G.part('cover_hinge', 'frame', 'dark', [('add', union(*[box(x, x + 16, 22.5, 26.4, -19.2, -14.5) for x in (48, 87, 126)]))])
G.part('cover_pin', 'frame', 'plate', [('add', cyl((44, 26.6, -17.6), (146, 26.6, -17.6), 1.5))])
G.part('handguard', 'frame', 'polymer', [
    ('add', obox(208, 400, 17, 52, 13, 4)),
    ('cut', row(5, lambda i: box2(224 + i * 34, 248 + i * 34, 31, 39, 9.5, 15))),          # side slots
    ('cut', row(5, lambda i: box2(224 + i * 34, 248 + i * 34, 21.5, 25.5, 11.6, 15))),
    ('cut', cyl((392, AX, 0), (401, AX, 0), 12.5)),
])
G.part('top_rail', 'frame', 'dark', [('add', rail(-106, 398, 51.5, 7.5, base=2.5))])
G.part('housing', 'frame', 'polymer', [
    ('add', slab([(-110, 12), (34, 12), (34, -8), (-60, -8), (-110, 2)], 13, 2.5)),
    ('add', plate([(-28, -8), (22, -8), (22, -36), (16, -40), (-36, -40)], 6)),            # trigger guard
    ('cut', plate([(-24, -11), (19, -11), (19, -34), (15, -37), (-32, -37)], 15)),
    ('cut', box(-4, 14, -12, 6, -2.7, 2.7)),                                              # trigger slot
])
G.part('grip', 'frame', 'polymer', [
    ('add', plate([(-22, -7.9), GR.pt(8, 14), GR.pt(86, 14), GR.pt(90, 10), GR.pt(90, -15), GR.pt(40, -17), (-62, -7.9)], 12)),
    ('add', plate2([GR.pt(14, 11), GR.pt(82, 11), GR.pt(82, -12), GR.pt(20, -13)], 12, 13.5)),
    ('cut', row(8, lambda i: box2(-80, -20, -24 - i * 8, -22.2 - i * 8, 12.8, 14))),
])
G.part('selector', 'frame', 'accent', [('add', cyl((-18, 3, 13), (-18, 3, 14.6), 4.2)), ('add', box(-17, -6, 1.6, 4.4, 13, 14.6))], mirror=True)
G.part('pins', 'frame', 'dark', [('add', union(*[cyl((x, y, 14.6), (x, y, 15.5), 2.2) for x, y in ((-98, 16), (180, 16), (20, 16))]))], mirror=True)
G.part('pouch_bracket', 'frame', 'dark', [
    ('add', box(36, 176, 2, 11, -27, 27)),
    ('cut', box(38.5, 173.5, 0, 7.6, -25, 25)),                                           # pouch socket (blind at the top)
    ('cut', row(5, lambda i: box2(48 + i * 26, 64 + i * 26, 3.5, 6.5, 24, 28))),
])
G.part('barrel', 'frame', 'dark', [
    ('add', cyl((205, AX, 0), (640, AX, 0), 10.0)),
    ('cut', union(*[cyl((476, AX + 11.6 * math.sin(a), 11.6 * math.cos(a)), (624, AX + 11.6 * math.sin(a), 11.6 * math.cos(a)), 3.2)
                    for a in [math.radians(30 + 60 * k) for k in range(6)]])),              # flutes
])
G.part('barrel_nut', 'frame', 'steel', [('add', cyl((398, AX, 0), (410, AX, 0), 13.5)), ('add', cyl((410, AX, 0), (418, AX, 0), 13.5, 10.5))])
G.part('carry_collar', 'frame', 'steel', [('add', obox(438, 462, AX - 13, AX + 15, 12, 4.5))])
G.part('carry_handle', 'frame', 'polymer', [
    ('add', plate([(441, AX + 13), (459, AX + 13), (468, AX + 39), (450, AX + 39)], 4)),
    ('add', cyl((424, AX + 40, 0), (512, AX + 40, 0), 6.5)),
    ('cut', row(6, lambda i: tube((476 + i * 6, AX + 40, 0), (478 + i * 6, AX + 40, 0), 7.5, 5.7))),
])
G.part('flash_hider', 'frame', 'steel', [
    ('add', cyl((634, AX, 0), (672, AX, 0), 12.5)), ('add', cyl((630, AX, 0), (637, AX, 0), 13.5)),
    ('cut', cyl((667.5, AX, 0), (673, AX, 0), 5.5)),                                     # shallow recess only: the barrel is solid
    ('cut', row(3, lambda i: box(643 + i * 7.5, 647 + i * 7.5, AX - 3, AX + 3, -14, 14))),
    ('cut', row(3, lambda i: box(643 + i * 7.5, 647 + i * 7.5, AX + 7, AX + 14, -3, 3))),
])
G.part('stock_spine', 'frame', 'dark', [('add', cyl((-205, 30, 0), (-108, 30, 0), 10)), ('add', obox(-116, -108, 11, 51, 16, 4))])
G.part('bipod_mount', 'frame', 'dark', [('add', box(372, 398, 2, 19, -15.5, 15.5)), ('cut', box(360, 410, -2, 8, -9, 9))])
G.part('bipod_pin', 'frame', 'plate', [('add', cyl((BP[0], BP[1], -26), (BP[0], BP[1], 26), 2.2))])
G.part('sight_rear', 'frame', 'dark', [('add', plate([(-98, 54), (-76, 54), (-78, 63), (-98, 63)], 6.5)), ('cut', box(-100, -74, 57.5, 64, -2.2, 2.2))])
G.part('sight_front', 'frame', 'dark', [('add', plate([(366, 54), (392, 54), (390, 63), (372, 63)], 6.5)), ('cut', box(360, 396, 57.5, 64, -5, -1.2)),
                                        ('cut', box(360, 396, 57.5, 64, 1.2, 5))])

# ------------------------------------------------------------------ sliding stock
G.part('stock', 'stock', 'polymer', [
    ('add', slab([(-160, 44), (-290, 44), (-298, 38), (-298, -30), (-288, -36), (-270, -24), (-230, 10), (-160, 16)], 12.5, 3)),
    ('cut', cyl((-246, 30, 0), (-159, 30, 0), 10.6)),                                    # tunnel for the spine tube
    ('cut', plate([(-250, 6), (-288, 6), (-288, -22), (-274, -14)], 15)),                # skeleton window
    ('cut', row(4, lambda i: box2(-228 + i * 15, -220 + i * 15, 36, 41, 11.4, 14))),
])
G.part('cheek', 'stock', 'tan', [('add', tbox(-284, -172, 43.5, 49, 9, 3))])
G.part('butt_pad', 'stock', 'polymer', [('add', plate([(-297.6, 40), (-304, 36), (-304, -27), (-297.6, -32)], 11.5))])
G.part('stock_latch', 'stock', 'accent', [('add', box(-200, -186, 13.5, 17, -5, 5))])

# ------------------------------------------------------------------ side feed cover (left), charging handle, trigger
G.part('feed_cover', 'cover', 'steel', [
    ('add', prism('xy', [(42, 27), (148, 27), (148, 44), (144, 48), (46, 48), (42, 44)], -19.2, -15.5)),
    ('add', prism('xy', [(50, 31), (140, 31), (140, 42), (137, 45), (53, 45), (50, 42)], -20.6, -19)),
    ('cut', row(6, lambda i: box(58 + i * 13, 64 + i * 13, 34, 42, -22, -19.9))),
])
G.part('cover_latch', 'cover', 'accent', [('add', box(86, 104, 45.3, 47.5, -20.2, -19))])
G.part('charge_handle', 'charge', 'plate', [('add', box(172, 182, 38.1, 43.9, 13.5, 22)), ('add', cyl((177, 41, 20), (177, 41, 27), 4))])
G.part('trigger', 'trigger', 'steel', [('add', plate([(1, 1), (7, 1), (7.6, -10), (6.6, -18), (7.6, -28), (5, -30), (2.6, -20), (1.4, -10)], 2.2))])

# ------------------------------------------------------------------ ammunition pouch (hangs in the bracket socket)
G.part('pouch', 'mag', 'olive', [
    ('add', prism('zy', [(-23, 6.8), (23, 6.8), (23, 0), (27, -9), (28.5, -80), (23, -118), (-23, -118), (-28.5, -80), (-27, -9), (-23, 0)], 40, 172)),
    ('int', plate([(40, 8), (172, 8), (172, -96), (160, -118), (52, -118), (40, -96)], 32)),
])
G.part('pouch_flap', 'mag', 'tan', [
    ('add', prism('zy', [(-28.2, -6), (28.2, -6), (29.6, -14), (29.9, -30), (-29.9, -30), (-29.6, -14)], 38.8, 173.2)),
    ('cut', box(30, 182, -18.5, -16.5, -40, 40)),
])
G.part('pouch_strap', 'mag', 'tan', [('add', prism('zy', [(-30.6, -29), (30.6, -29), (30.6, -80), (25, -119.6), (-25, -119.6), (-30.6, -80)], 99, 113))])
G.part('pouch_buckle', 'mag', 'dark', [('add', box2(97.5, 114.5, -58, -50, 30.2, 32))])

# ------------------------------------------------------------------ bipod (mirrored; rest = folded forward under the barrel)
G.part('bipod_leg', 'bipod', 'dark', [
    ('add', prism('xy', [(378, 5), (566, 6), (566, 12), (378, 13)], 16.5, 23.5)),
    ('cut', row(4, lambda i: box(420 + i * 34, 442 + i * 34, 7.7, 10.3, 22, 25))),
], mirror=True)
G.part('bipod_foot', 'bipod', 'polymer', [('add', prism('xy', [(562, 4), (578, 3), (582, 9), (578, 15), (562, 14)], 15.7, 24.3))], mirror=True)

# ------------------------------------------------------------------ motion
G.group('stock', [G.move('stock', (1, 0, 0), 36.0)])
G.group('cover', [G.rot('cover', (0, CH[0], CH[1]), (1, 0, 0), -112.0)])
G.group('charge', [G.move('charge', (-1, 0, 0), 104.0)])
G.group('trigger', [G.rot('trigger', (4, -3, 0), (0, 0, 1), -15.0)])
G.group('mag', [G.move('mag', (0, -1, 0), 170.0)])
G.group('bipod', [G.rot('bipod', (BP[0], 15.0, 16.5), (1, 0, 0), -16.0), G.rot('bipod', (BP[0], BP[1], 0), (0, 0, 1), -82.0)], mirror=True)
G.mode('OPEN', cover=1.0, mag=1.0, charge=1.0)
G.mode('DEPLOYED', bipod=1.0, stock=1.0)

G.clip('Idle', 2)
G.clip('Fire', 6, trigger=[(0, 0), (0.2, 1), (0.7, 1), (1, 0)], charge=[(0.1, 0), (0.45, 0.25), (0.9, 0)])
G.clip('Reload', 96, cover=[(0.03, 0), (0.16, 1), (0.66, 1), (0.8, 0)], mag=[(0.18, 0), (0.34, 1), (0.46, 1), (0.64, 0)],
       charge=[(0.83, 0), (0.9, 1), (0.93, 1), (0.99, 0)])
G.clip('Bipod_Deploy', 18, bipod=[(0, 0), (1, 1)])
G.clip('Bipod_Fold', 18, bipod=[(0, 1), (1, 0)])
G.clip('Stock_Collapse', 16, stock=[(0, 0), (1, 1)])
G.clip('Stock_Extend', 16, stock=[(0, 1), (1, 0)])
G.check()
