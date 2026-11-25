# RA11 Energy LMG : bullpup energy machine gun (silhouette cues: cell behind the pistol grip, smooth swooping one-piece shell with an
# integrated optic hump, oversized guard that flows into the fore-end).  Energy twist: glowing cell, radiator flaps, emitter rings.
from ra_lib import *

G = Gun('RA11_EnergyLMG', 'energy light machine gun')
AX = 39.0                                   # emitter axis height
GR = Slant((-40, -6), 16)                   # pistol grip axis
OY = 72.0                                   # optic axis height
ZS = 22.0                                   # shell half width
FH = (55.0, 24.0)                           # cooling flap hinge line (y, z) : upper outer edge

# ------------------------------------------------------------------ one-piece shell (static)
G.part('shell', 'frame', 'polymer', [
    ('add', plate([(-262, -10), (-262, 44), (-250, 55), (-170, 64), (-120, 66), (-66, 88), (48, 88), (104, 66), (300, 66), (338, 52), (338, 26),
                   (300, 10), (150, 2), (-70, -6), (-76, -36), (-176, -40), (-244, -24)], ZS)),
    ('int', union(obox(-270, -120, -41, 66, ZS, 6), obox(-121, 104, -110, 88, ZS, 6), obox(103, 345, 0, 66, ZS, 7))),
    ('cut', box(-162, -88, -45, 30, -14, 14)),                                           # cell well (blind at the top)
    ('cut', row(4, lambda i: box2(-146 + i * 11, -138 + i * 11, -5, 15, 17.5, 23))),      # charge gauge slots (blind)
    ('cut', box(-4, 14, -12, 10, -2.7, 2.7)),                                            # trigger slot
    ('cut', box(14, 104, 55, 62, -23, -19)),                                             # charging handle track (left side)
    ('cut', cyl((-140, OY, 0), (-74.5, OY, 0), 9)), ('cut', cyl((62.5, OY, 0), (130, OY, 0), 9)),      # optic channel ends
    ('cut', box2(150, 290, 28, 56, 17, 23)),                                             # radiator bays (under the flaps)
    ('cut', row(6, lambda i: box2(158 + i * 22, 172 + i * 22, 15, 22, 19.5, 23))),        # lower cooling slits
    ('cut', row(5, lambda i: box2(-226 + i * 14, -218 + i * 14, 38, 50, 20.6, 23))),
])
G.part('side_panel', 'frame', 'steel', [
    ('add', prism('xy', [(-236, -20), (-240, 24), (-218, 34), (-112, 34), (-90, 20), (-84, -31), (-180, -33)], 21.5, 23.8)),
    ('cut', box(-150, -100, -9, 19, 20, 25)),
], mirror=True)
G.part('hump_panel', 'frame', 'steel', [('add', prism('xy', [(-64, 66), (-52, 82), (40, 82), (58, 70), (52, 65), (-40, 65)], 21.5, 23.6)),
                                        ('cut', row(4, lambda i: box(-30 + i * 16, -22 + i * 16, 69, 78, 22.6, 25)))], mirror=True)
G.part('accent_mark', 'frame', 'accent', [('add', prism('xy', [(-58, 67.5), (-52, 76), (-46, 76), (-52, 67.5)], 23.2, 24.2))], mirror=True)
G.part('top_rail', 'frame', 'dark', [('add', rail(-58, 40, 87.5, 6.5, base=2.5))])
G.part('fore_rail', 'frame', 'dark', [('add', rail(128, 290, 65.5, 6.5, base=2.5))])
G.part('optic_lens', 'frame', 'lens', [('add', cyl((-77, OY, 0), (-73.5, OY, 0), 8.8)), ('add', cyl((61.5, OY, 0), (65, OY, 0), 8.8))])
G.part('butt_pad', 'frame', 'steel', [('add', plate([(-261.6, 43), (-269, 38), (-269, -5), (-261.6, -9)], 19))])
G.part('grip', 'frame', 'polymer', [
    ('add', plate([(-22, -3), GR.pt(8, 14), GR.pt(86, 14), GR.pt(90, 10), GR.pt(90, -15), GR.pt(40, -17), (-66, -3)], 13)),
    ('add', plate2([GR.pt(14, 11), GR.pt(82, 11), GR.pt(82, -12), GR.pt(20, -13)], 13, 14.5)),
    ('cut', row(8, lambda i: box2(-84, -20, -24 - i * 8, -22.2 - i * 8, 13.8, 15))),
])
G.part('guard', 'frame', 'polymer', [
    ('add', plate([(-24, -3), (150, 5), (134, -26), (92, -66), (-46, -96), (-54, -92)], 7)),
    ('cut', plate([(-30, -9), (128, -2.5), (119, -24), (86, -60), (-44, -89.5), (-50, -84)], 9)),
    ('cut', box(-4, 14, -14, 8, -2.7, 2.7)),
])
G.part('selector', 'frame', 'accent', [('add', cyl((-20, 12, ZS), (-20, 12, ZS + 1.6), 4.2)), ('add', box(-19, -8, 10.6, 13.4, ZS, ZS + 1.6))], mirror=True)

# radiators, slits, emitter
G.part('radiator', 'frame', 'glow', [('add', box2(152, 288, 29.5, 54.5, 16, 18.6))])
G.part('radiator_fins', 'frame', 'steel', [('add', row(9, lambda i: box2(158 + i * 15, 162 + i * 15, 28.5, 55.5, 16.5, 20)))])
G.part('gauge_glow', 'frame', 'glow', [('add', box2(-148, -102, -7, 17, 16.5, 18.6))])
G.part('slit_glow', 'frame', 'glow', [('add', box2(154, 292, 14, 23, 18, 20.3))])
G.part('flap_hinge', 'frame', 'steel', [('add', union(*[box(x, x + 14, 56.6, 59.6, 21.5, 25.2) for x in (156, 213, 270)]))], mirror=True)
G.part('flap_pin', 'frame', 'plate', [('add', cyl((153, 56.3, 24), (287, 56.3, 24), 1.3))], mirror=True)
G.part('nose_cap', 'frame', 'steel', [('add', obox(328, 346, 21, 57, 19, 7)), ('add', cyl((344, AX, 0), (356, AX, 0), 16, 12.5))])
G.part('emitter_barrel', 'frame', 'dark', [('add', cyl((340, AX, 0), (466, AX, 0), 12))])
G.part('emitter_core', 'frame', 'glow', [('add', cyl((386, AX, 0), (452, AX, 0), 15))])
G.part('emitter_rings', 'frame', 'steel', [('add', union(*[cyl((x, AX, 0), (x + 7, AX, 0), 19.5) for x in (380, 400, 420, 440)])),
                                           ('add', union(*[cyl((x + 7, AX, 0), (x + 10, AX, 0), 19.5, 16) for x in (380, 400, 420, 440)]))])
G.part('muzzle_cap', 'frame', 'steel', [('add', cyl((458, AX, 0), (480, AX, 0), 14.5)), ('add', cyl((450, AX, 0), (460, AX, 0), 17, 14.5)),
                                        ('cut', cyl((475.5, AX, 0), (481, AX, 0), 9)),                              # shallow recess only: solid emitter
                                        ('cut', row(3, lambda i: tube((462 + i * 4.5, AX, 0), (464 + i * 4.5, AX, 0), 16, 13.6)))])
G.part('muzzle_glow', 'frame', 'glow', [('add', cyl((474, AX, 0), (476.5, AX, 0), 8.8))])

# ------------------------------------------------------------------ cooling flaps (mirrored, hinged along X at the upper edge)
G.part('flap', 'flap', 'steel', [
    ('add', prism('xy', [(151, 29), (289, 29), (289, 55), (151, 55)], 20.6, 24)),
    ('cut', row(5, lambda i: box(162 + i * 25, 174 + i * 25, 34, 48, 19, 26))),            # louvre slits
], mirror=True)
G.part('flap_rib', 'flap', 'dark', [('add', prism('xy', [(153, 30), (287, 30), (287, 32.5), (153, 32.5)], 23.6, 25.2)),
                                    ('add', prism('xy', [(153, 50.5), (287, 50.5), (287, 53), (153, 53)], 23.6, 25.2))], mirror=True)

# ------------------------------------------------------------------ energy cell (behind the grip), charging handle, trigger
G.part('cell_body', 'mag', 'steel', [
    ('add', box(-161.5, -88.5, -72, 29.5, -13.5, 13.5)),
    ('cut', box2(-150, -100, -64, -44, 12, 14)),
])
G.part('cell_glow', 'mag', 'glow', [('add', box(-150.5, -99.5, -64.5, -43.5, -12.7, 12.7))])
G.part('cell_cap', 'mag', 'dark', [('add', obox(-164, -86, -80, -71.6, 16, 3))])
G.part('cell_tab', 'mag', 'accent', [('add', box(-134, -116, -83, -79.6, -5, 5))])
G.part('charge_handle', 'charge', 'plate', [('add', box(88, 98, 55.6, 61.4, -29, -19.5)), ('add', cyl((93, 58.5, -27), (93, 58.5, -34), 4.2))])
G.part('trigger', 'trigger', 'steel', [('add', plate([(1, 1), (7, 1), (7.6, -10), (6.6, -18), (7.6, -28), (5, -30), (2.6, -20), (1.4, -10)], 2.2))])

# ------------------------------------------------------------------ motion
G.group('flap', [G.rot('flap', (0, FH[0], FH[1]), (1, 0, 0), -40.0)], mirror=True)
G.group('mag', [G.move('mag', (0, -1, 0), 130.0)])
G.group('charge', [G.move('charge', (-1, 0, 0), 68.0)])
G.group('trigger', [G.rot('trigger', (4, -3, 0), (0, 0, 1), -15.0)])
G.mode('OPEN', mag=1.0, charge=1.0)
G.mode('VENT', flap=1.0)

G.clip('Idle', 2)
G.clip('Fire', 6, trigger=[(0, 0), (0.2, 1), (0.7, 1), (1, 0)], flap=[(0, 0), (0.4, 0.15), (1, 0)])
G.clip('Reload', 70, mag=[(0.04, 0), (0.3, 1), (0.48, 1), (0.72, 0)], charge=[(0.78, 0), (0.87, 1), (0.91, 1), (0.98, 0)])
G.clip('Vent_Open', 14, flap=[(0, 0), (1, 1)])
G.clip('Vent_Close', 22, flap=[(0, 1), (1, 0)])
G.clip('Overheat', 64, flap=[(0, 0), (0.07, 1), (0.55, 1), (1, 0)])
G.check()
