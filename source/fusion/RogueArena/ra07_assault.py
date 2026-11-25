# RA07 Assault Rifle : modular carbine (silhouette cues: tall slab-sided monolithic upper, full-length top rail, boot-shaped sliding stock).
from ra_lib import *

G = Gun('RA07_AssaultRifle', 'assault rifle')
AX = 34.0                                   # bore axis height
GR = Slant((-40, -6), 18)                   # pistol grip axis
MG = Slant((56, 5), -6)                     # magazine axis (leans forward)

# ------------------------------------------------------------------ upper receiver + handguard (static)
G.part('upper', 'frame', 'tan', [
    ('add', obox(-110, 250, 12, 52, 16, 4)),
    ('cut', box(62, 166, 40, 45, 13, 17)),                                               # charging handle track (right side)
    ('cut', box(20, 72, 25, 35.5, 14.6, 17)),                                            # ejection port recess
    ('cut', row(5, lambda i: box2(176 + i * 14, 184 + i * 14, 27, 41, 12, 17))),          # handguard vents
    ('cut', cyl((236, AX, 0), (251, AX, 0), 9.5)),
])
G.part('port_door', 'frame', 'dark', [('add', box(22, 70, 26.5, 34, 14.2, 14.7))])
G.part('top_rail', 'frame', 'dark', [('add', rail(-106, 246, 52, 8))])
G.part('under_rail', 'frame', 'dark', [('add', rail(130, 246, 12, 8, base=-2.0, tooth=-2.2))])
G.part('side_rail', 'frame', 'dark', [('add', row(8, lambda i: box(172 + i * 9.5, 177 + i * 9.5, 18, 26, 16, 18.6)))], mirror=True)
G.part('barrel', 'frame', 'dark', [('add', cyl((238, AX, 0), (432, AX, 0), 8.0)), ('add', cyl((250, AX, 0), (262, AX, 0), 9.2))])
G.part('gas_block', 'frame', 'steel', [('add', obox(292, 316, AX - 10, AX + 16, 9, 3)), ('add', cyl((250, AX + 11, 0), (294, AX + 11, 0), 3.6))])
G.part('muzzle', 'frame', 'steel', [
    ('add', cyl((430, AX, 0), (464, AX, 0), 10.5)), ('add', cyl((428, AX, 0), (434, AX, 0), 11.5)),
    ('cut', cyl((459.5, AX, 0), (465, AX, 0), 4.6)),                                     # shallow recess only: the barrel is solid
    ('cut', row(3, lambda i: box(439 + i * 7, 443 + i * 7, AX - 3, AX + 3, -12, 12))),
    ('cut', row(3, lambda i: box(439 + i * 7, 443 + i * 7, AX + 6, AX + 12, -3, 3))),
])

# ------------------------------------------------------------------ lower receiver, grip, guard (static)
G.part('lower', 'frame', 'polymer', [
    ('add', slab([(-110, 12), (94, 12), (98, -30), (22, -30), (20, -8), (-60, -8), (-110, 2)], 14, 2.5)),
    ('cut', prism('xy', MG.rect(-1, 46, -29.5, 29.5), -11, 11)),                           # magazine well (blind at the top)
    ('add', plate([(-28, -8), (22, -8), (22, -36), (16, -40), (-36, -40)], 6)),            # trigger guard
    ('cut', plate([(-24, -11), (19, -11), (19, -34), (15, -37), (-32, -37)], 15)),
    ('cut', box(-4, 14, -12, 6, -2.7, 2.7)),                                              # trigger slot
])
G.part('grip', 'frame', 'polymer', [
    ('add', plate([(-22, -7.9), GR.pt(8, 14), GR.pt(86, 14), GR.pt(90, 10), GR.pt(90, -15), GR.pt(40, -17), (-62, -7.9)], 12)),
    ('add', plate2([GR.pt(14, 11), GR.pt(82, 11), GR.pt(82, -12), GR.pt(20, -13)], 12, 13.5)),
    ('cut', row(8, lambda i: box2(-80, -20, -24 - i * 8, -22.2 - i * 8, 12.8, 14))),
])
G.part('selector', 'frame', 'accent', [('add', cyl((-18, 3, 14), (-18, 3, 15.6), 4.2)), ('add', box(-17, -6, 1.6, 4.4, 14, 15.6))], mirror=True)
G.part('mag_catch', 'frame', 'dark', [('add', box(30, 42, -4, 2, 14, 15.4))], mirror=True)
G.part('pins', 'frame', 'steel', [('add', union(*[cyl((x, y, 13.8), (x, y, 14.5), 2.2) for x, y in ((-96, 6), (84, 6), (-50, 0))]))], mirror=True)

# ------------------------------------------------------------------ stock : fixed spine + sliding boot
G.part('stock_spine', 'frame', 'dark', [('add', box(-200, -110, 18, 44, -8, 8)), ('add', box(-122, -110, 12, 50, -15, 15))])
G.part('stock', 'stock', 'tan', [
    ('add', slab([(-160, 48), (-304, 48), (-312, 42), (-312, -26), (-302, -34), (-284, -22), (-236, 8), (-160, 13)], 13, 3)),
    ('cut', box(-246, -159, 17.6, 44.4, -8.4, 8.4)),                                     # tunnel for the spine
    ('cut', plate([(-256, 6), (-296, 6), (-296, -18), (-284, -12)], 15)),                # skeleton window
    ('cut', row(4, lambda i: box2(-232 + i * 14, -224 + i * 14, 24, 38, 11.8, 14))),
])
G.part('cheek', 'stock', 'polymer', [('add', tbox(-290, -170, 48, 53, 9, 3))])
G.part('butt_pad', 'stock', 'polymer', [('add', plate([(-312.3, 41), (-318, 37), (-318, -22), (-312.3, -25.5)], 12))])

# ------------------------------------------------------------------ moving parts
G.part('charge_handle', 'charge', 'steel', [('add', box(150, 162, 40.4, 44.6, 13.4, 24)), ('add', cyl((156, 42.5, 22), (156, 42.5, 27), 4))])
G.part('trigger', 'trigger', 'steel', [('add', plate([(1, 1), (7, 1), (7.6, -10), (6.6, -18), (7.6, -28), (5, -30), (2.6, -20), (1.4, -10)], 2.2))])
G.part('mag_body', 'mag', 'polymer', [
    ('add', plate([MG.pt(0, -29), MG.pt(0, 29), MG.pt(72, 29), MG.pt(152, 46), MG.pt(156, -12), MG.pt(72, -29)], 10.4)),
    ('cut', row(3, lambda i: plate2([MG.pt(64 + i * 24, 22 + i * 5), MG.pt(68 + i * 24, 22 + i * 5.2), MG.pt(72 + i * 24, -20 + i * 5.2),
                                     MG.pt(68 + i * 24, -20 + i * 5)], 9.6, 11))),
])
G.part('mag_floor', 'mag', 'tan', [('add', plate([MG.pt(152.4, 49), MG.pt(156.4, -15), MG.pt(161, -15), MG.pt(157, 49)], 12))])
G.part('sight_rear', 'sight_r', 'dark', [('add', plate([(-97.5, 57), (-70, 57), (-70, 59), (-76, 60.5), (-97.5, 60.5)], 6)), ('cut', box(-74, -69, 56, 61, -2, 2))])
G.part('sight_front', 'sight_f', 'dark', [('add', plate([(313, 50.6), (290, 50.6), (290, 52.4), (296, 54), (313, 54)], 5)), ('cut', box(289, 294, 50, 55, -1.6, 1.6))])

# ------------------------------------------------------------------ motion
G.group('charge', [G.move('charge', (-1, 0, 0), 85.0)])
G.group('trigger', [G.rot('trigger', (4, -3, 0), (0, 0, 1), -15.0)])
G.group('mag', [G.move('mag', MG.axis(), 180.0)])
G.group('stock', [G.move('stock', (1, 0, 0), 36.0)])
G.group('sight_r', [G.rot('sights', (-96, 58.75, 0), (0, 0, 1), 90.0)])
G.group('sight_f', [G.rot('sights', (311.5, 52.3, 0), (0, 0, 1), -90.0)])
G.mode('OPEN', mag=1.0, charge=1.0, sights=1.0)
G.mode('COMPACT', stock=1.0)

G.clip('Idle', 2)
G.clip('Fire', 8, trigger=[(0, 0), (0.15, 1), (0.6, 1), (1, 0)], charge=[(0.1, 0), (0.4, 0.5), (0.85, 0)])
G.clip('Reload', 66, mag=[(0.04, 0), (0.28, 1), (0.46, 1), (0.7, 0)], charge=[(0.76, 0), (0.86, 1), (0.9, 1), (0.97, 0)])
G.clip('Stock_Collapse', 18, stock=[(0, 0), (1, 1)])
G.clip('Stock_Extend', 18, stock=[(0, 1), (1, 0)])
G.clip('Sights_Up', 16, sights=[(0, 0), (1, 1)])
G.clip('Sights_Down', 16, sights=[(0, 1), (1, 0)])
G.check()
