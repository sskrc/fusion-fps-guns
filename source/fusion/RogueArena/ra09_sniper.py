# RA09 Sniper : heavy anti-materiel rifle (silhouette cues: very long fluted recoiling barrel with an arrowhead two-chamber brake,
# long boxy pressed-steel receiver with a full top rail, big box magazine ahead of the guard, plain hooked butt).
from ra_lib import *

G = Gun('RA09_Sniper', 'anti-materiel sniper rifle')
AX = 40.0                                   # bore axis height
GR = Slant((-40, -6), 18)                   # pistol grip axis
SY = 114.0                                  # scope axis height
BP = (538.0, 14.0)                          # bipod hinge (x, y)

# ------------------------------------------------------------------ receiver + barrel shroud (static)
G.part('upper', 'frame', 'steel', [
    ('add', slab([(-250, 18), (330, 18), (352, 25), (560, 25), (560, 61), (544, 66), (-250, 66)], 19, 4)),
    ('cut', cyl((215, AX, 0), (561, AX, 0), 13.9)),                                       # barrel tunnel (blind at the rear)
    ('cut', box(150, 300, 43.5, 50.5, 17, 21)),                                          # charging handle track (right side)
    ('cut', box(58, 142, 34, 52, 17.6, 21)),                                             # ejection port recess
    ('cut', box2(-228, -30, 28, 58, 18.2, 21)),                                          # pressed side panels
    ('cut', box(-20, 140, 28, 58, -21, -18.2)),
    ('cut', row(6, lambda i: box2(366 + i * 30, 386 + i * 30, 35.5, 44.5, 12, 21))),     # shroud vents
    ('cut', row(6, lambda i: box2(366 + i * 30, 386 + i * 30, 52, 56, 17.8, 21))),
])
G.part('port_door', 'frame', 'dark', [('add', box(61, 139, 36, 50, 17.2, 17.8))])
G.part('top_rail', 'frame', 'dark', [('add', rail(-244, 540, 65.5, 8, base=2.5))])
G.part('shroud_band', 'frame', 'dark', [('add', obox(546, 564, 23, 63, 20.5, 5)), ('cut', cyl((540, AX, 0), (570, AX, 0), 13.9))])
G.part('rear_cap', 'frame', 'dark', [('add', obox(-256, -244, 14, 68, 20.5, 5))])
G.part('lower', 'frame', 'steel', [
    ('add', slab([(-250, 20), (330, 20), (322, 2), (134, 2), (130, -22), (40, -22), (38, -8), (-70, -8), (-250, 0)], 17, 2.5)),
    ('add', plate([(-28, -8), (40, -8), (40, -40), (34, -44), (-36, -44)], 6)),            # trigger guard
    ('cut', plate([(-24, -11), (36, -11), (36, -38), (32, -41), (-32, -41)], 20)),
    ('cut', box(46, 124, -23, 12, -12, 12)),                                              # magazine well (blind at the top)
    ('cut', box(-4, 14, -12, 6, -2.7, 2.7)),                                              # trigger slot
    ('cut', row(5, lambda i: box2(160 + i * 30, 176 + i * 30, 6, 15, 16, 18))),
])
G.part('grip', 'frame', 'polymer', [
    ('add', plate([(-22, -7.9), GR.pt(8, 14), GR.pt(86, 14), GR.pt(90, 10), GR.pt(90, -15), GR.pt(40, -17), (-62, -7.9)], 12)),
    ('add', plate2([GR.pt(14, 11), GR.pt(82, 11), GR.pt(82, -12), GR.pt(20, -13)], 12, 13.5)),
    ('cut', row(8, lambda i: box2(-80, -20, -24 - i * 8, -22.2 - i * 8, 12.8, 14))),
])
G.part('butt', 'frame', 'steel', [
    ('add', slab([(-246, 64), (-318, 64), (-328, 56), (-328, -32), (-320, -38), (-298, -38), (-288, -14), (-262, -9), (-246, -1)], 18, 3.5)),
    ('cut', box2(-316, -262, 6, 50, 16.6, 19)),
])
G.part('butt_pad', 'frame', 'polymer', [('add', plate([(-327.5, 60), (-340, 54), (-340, -30), (-327.5, -36)], 16))])
G.part('selector', 'frame', 'accent', [('add', cyl((-18, 6, 17), (-18, 6, 18.6), 4.2)), ('add', box(-17, -6, 4.6, 7.4, 17, 18.6))], mirror=True)
G.part('mag_catch', 'frame', 'dark', [('add', box(112, 126, -14, 0, 16.5, 18.4))], mirror=True)
G.part('pins', 'frame', 'dark', [('add', union(*[cyl((x, y, 16.8), (x, y, 17.6), 2.6) for x, y in ((-230, 8), (300, 10), (-60, 0), (140, 12))]))], mirror=True)

# carry handle (on the shroud) + bipod mount
G.part('carry_handle', 'frame', 'polymer', [
    ('add', plate([(352, 68), (366, 93), (474, 93), (488, 68), (474, 68), (464, 86), (376, 86), (366, 68)], 6)),
    ('add', obox(374, 466, 84.5, 94.5, 8, 2.5)),
])
G.part('bipod_mount', 'frame', 'dark', [('add', box(520, 556, 5, 25.5, -23.5, 23.5)), ('cut', box(510, 566, 0, 12, -14, 14))])
G.part('bipod_pin', 'frame', 'plate', [('add', cyl((BP[0], BP[1], -36), (BP[0], BP[1], 36), 2.6))])

# ------------------------------------------------------------------ telescopic sight (static, on the rail)
G.part('scope_mount', 'frame', 'steel', [
    ('add', union(*[obox(x, x + 22, 68, SY + 6, 11, 4) for x in (-12, 96)])),
    ('add', box(-12, 118, 68, 76, -9, 9)),
    ('cut', box(12, 94, 70.5, 77, -6, 6)),
])
G.part('scope_tube', 'frame', 'dark', [
    ('add', cyl((-76, SY, 0), (150, SY, 0), 15)),
    ('add', cyl((-105, SY, 0), (-63, SY, 0), 19.5)), ('add', cyl((-64, SY, 0), (-50, SY, 0), 19.5, 15.2)),        # ocular bell
    ('add', cyl((122, SY, 0), (151, SY, 0), 15.2, 22)), ('add', cyl((150, SY, 0), (226, SY, 0), 22)),              # objective bell
    ('add', cyl((-108, SY, 0), (-99, SY, 0), 21)), ('add', cyl((217, SY, 0), (228, SY, 0), 23.2)),
    ('cut', cyl((-110, SY, 0), (-103, SY, 0), 17)), ('cut', cyl((222, SY, 0), (230, SY, 0), 20)),
    ('add', obox(38, 70, SY - 17, SY + 17, 17, 6)),                                                                # turret saddle
])
G.part('scope_lens', 'frame', 'lens', [('add', cyl((-103.5, SY, 0), (-101, SY, 0), 17.6)), ('add', cyl((219, SY, 0), (222.5, SY, 0), 20.6))])
G.part('scope_turrets', 'frame', 'steel', [
    ('add', cyl((54, SY + 16, 0), (54, SY + 31, 0), 9)), ('add', cyl((54, SY, 16), (54, SY, 31), 9)), ('add', cyl((54, SY, -16), (54, SY, -27), 10.5)),
    ('cut', row(2, lambda i: tube((54, SY + 21 + i * 4, 0), (54, SY + 22.6 + i * 4, 0), 10, 8.2))),
])
G.part('scope_mark', 'frame', 'accent', [('add', cyl((54, SY + 30.6, 0), (54, SY + 31.6, 0), 4.5))])

# ------------------------------------------------------------------ recoiling barrel + brake
G.part('barrel', 'barrel', 'dark', [
    ('add', cyl((250, AX, 0), (1004, AX, 0), 13.2)),
    ('cut', union(*[cyl((610, AX + 14.6 * math.sin(a), 14.6 * math.cos(a)), (975, AX + 14.6 * math.sin(a), 14.6 * math.cos(a)), 4.2)
                    for a in [math.radians(30 + 60 * k) for k in range(6)]])),              # flutes
])
G.part('brake', 'barrel', 'steel', [
    ('add', prism('xz', [(1004, -14), (1012, -33), (1026, -33), (1050, -18), (1054, -29), (1068, -29), (1102, -14),
                         (1102, 14), (1068, 29), (1054, 29), (1050, 18), (1026, 33), (1012, 33), (1004, 14)], AX - 15, AX + 15)),
    ('int', obox(990, 1110, AX - 15, AX + 15, 34, 5)),
    ('add', cyl((992, AX, 0), (1008, AX, 0), 16)),
    ('cut', box(1015, 1037, AX - 10, AX + 10, -40, 40)),                                  # two open chambers
    ('cut', box(1056, 1080, AX - 10, AX + 10, -40, 40)),
    ('cut', cyl((1097.5, AX, 0), (1103, AX, 0), 7.5)),                                    # shallow recess only: the barrel is solid
])

# ------------------------------------------------------------------ bipod (mirrored; rest = folded forward under the barrel)
G.part('bipod_leg', 'bipod', 'dark', [
    ('add', prism('xy', [(530, 9), (760, 10.5), (760, 17.5), (530, 19)], 24.5, 33.5)),
    ('cut', row(5, lambda i: box(580 + i * 32, 600 + i * 32, 12.5, 15.5, 31.5, 35))),
], mirror=True)
G.part('bipod_foot', 'bipod', 'polymer', [('add', prism('xy', [(756, 8), (776, 6), (780, 14), (776, 22), (756, 20)], 23.5, 34.5))], mirror=True)

# ------------------------------------------------------------------ other moving parts
G.part('charge_handle', 'charge', 'plate', [('add', box(280, 292, 44.2, 49.8, 17.5, 28)), ('add', cyl((286, 47, 26), (286, 47, 34), 5))])
G.part('trigger', 'trigger', 'dark', [('add', plate([(1, 1), (7, 1), (7.6, -10), (6.6, -18), (7.6, -28), (5, -30), (2.6, -20), (1.4, -10)], 2.2))])
G.part('mag_body', 'mag', 'dark', [
    ('add', plate([(46.5, 11.5), (123.5, 11.5), (123.5, -108), (119, -114), (46.5, -114)], 11.5)),
    ('cut', row(3, lambda i: box2(60 + i * 20, 68 + i * 20, -104, -34, 10.5, 12))),
])
G.part('mag_floor', 'mag', 'steel', [('add', plate([(44.5, -114.4), (121, -114.4), (126, -108), (127, -118), (123, -121), (44.5, -121)], 13))])

# ------------------------------------------------------------------ motion
G.group('barrel', [G.move('barrel', (-1, 0, 0), 30.0)])
G.group('charge', [G.move('charge', (-1, 0, 0), 112.0)])
G.group('trigger', [G.rot('trigger', (4, -3, 0), (0, 0, 1), -15.0)])
G.group('mag', [G.move('mag', (0, -1, 0), 170.0)])
G.group('bipod', [G.rot('bipod', (BP[0], 22.0, 24.5), (1, 0, 0), -14.0), G.rot('bipod', (BP[0], BP[1], 0), (0, 0, 1), -82.0)], mirror=True)
G.mode('OPEN', mag=1.0, charge=1.0, barrel=1.0)
G.mode('DEPLOYED', bipod=1.0)

G.clip('Idle', 2)
G.clip('Fire', 16, trigger=[(0, 0), (0.12, 1), (0.5, 1), (1, 0)], barrel=[(0.08, 0), (0.28, 1), (0.9, 0)])
G.clip('Reload', 76, mag=[(0.04, 0), (0.28, 1), (0.46, 1), (0.7, 0)], charge=[(0.76, 0), (0.86, 1), (0.9, 1), (0.97, 0)])
G.clip('Bipod_Deploy', 20, bipod=[(0, 0), (1, 1)])
G.clip('Bipod_Fold', 20, bipod=[(0, 1), (1, 0)])
G.check()
