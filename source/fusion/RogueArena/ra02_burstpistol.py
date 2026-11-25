# RA02 Burst Pistol : select-fire machine pistol (silhouette cues: long slide on a full-size steel frame, tall extended magazine,
# slide-mounted selector lever).  Own touches: fixed ported muzzle block on the frame nose, open-top slide window.
from ra_lib import *

G = Gun('RA02_BurstPistol', 'burst machine pistol')
AX = 18.0                                   # bore axis height
GR = Slant((-40, -2), 15)                   # grip / magazine axis
ZF = 13.2                                   # frame half width
HP = (-66.0, 3.0)                           # hammer pivot
SP = (-57.0, 21.0)                          # selector pivot (rides on the slide)

# ------------------------------------------------------------------ frame (static)
G.part('frame', 'frame', 'steel', [
    ('add', plate([(-74, 5), (148, 5), (150, -6), (146, -10), (40, -10), (36, -5), (-22, -5), GR.pt(6, 15.5), GR.pt(100, 15.5),
                   GR.pt(100, -17), GR.pt(60, -19.5), GR.pt(22, -17.5), (-72, -7), (-79, -3), (-79, 2)], ZF)),
    ('add', plate([(-26, -5), (40, -5), (42, -12), (40, -32), (33, -40), (-33, -40), (-30, -30)], 7.0)),                # trigger guard
    ('cut', plate([(-24, -12), (34, -12), (36, -15), (34.5, -30), (30, -35), (-30.5, -35)], 15)),
    ('cut', prism('xy', GR.rect(-0.5, 101, -12.4, 12.4), -6.6, 6.6)),                                                   # magazine well
    ('cut', box(2, 20, -13, 3.5, -2.7, 2.7)),                                                                          # trigger slot
    ('cut', box(-82, -58.5, -3, 6, -3.2, 3.2)),                                                                        # hammer slot
    ('cut', row(5, lambda i: box(72 + i * 11, 76.5 + i * 11, -11, -7.8, -14, 14))),                                     # accessory rail slots
    ('cut', box2(44, 122, -2.2, 1.2, ZF - 1.0, ZF + 1)),                                                               # dust cover groove
])
G.part('grip_panel', 'frame', 'tan', [
    ('add', prism('xy', [GR.pt(14, 12.5), GR.pt(94, 12.5), GR.pt(94, -14), GR.pt(56, -16.5), GR.pt(22, -14.5)], ZF - 0.4, ZF + 1.7)),
    ('cut', row(10, lambda i: box(-95, 0, -24 - i * 7.5, -22.4 - i * 7.5, ZF + 0.9, ZF + 3))),
], mirror=True)
G.part('barrel', 'frame', 'chrome', [('add', cyl((-20, AX, 0), (131, AX, 0), 6.6))])
G.part('muzzle_block', 'frame', 'steel', [
    ('add', obox(129.6, 156, 4, 29, 13.4, 3.2)),
    ('cut', cyl((152, AX, 0), (157, AX, 0), 4.6)),                                       # shallow recess only: the barrel is solid
    ('cut', row(3, lambda i: box(133 + i * 4.5, 135.5 + i * 4.5, AX + 5, 31, -4.5, 4.5))),   # top ports
    ('cut', row(3, lambda i: box2(133 + i * 4.5, 135.5 + i * 4.5, AX - 2.5, AX + 2.5, 11.4, 15))),
    ('cut', plate([(157, 3), (149, 3), (157, 10)], 15)),
])
G.part('sight_front', 'frame', 'dark', [('add', plate([(146.5, 29), (155, 29), (154.5, 32.4), (150, 32.4)], 1.8))])
G.part('slide_stop', 'frame', 'dark', [('add', prism('xy', [(-12, 3.6), (20, 3.6), (23, 0.5), (8, -2), (-12, -1)], ZF, ZF + 1.2))], mirror=True)
G.part('takedown', 'frame', 'dark', [('add', box(27, 35, -3.6, -0.4, ZF, ZF + 1.0))], mirror=True)
G.part('mag_button', 'frame', 'dark', [('add', cyl((-31, -12.5, ZF - 0.3), (-31, -12.5, ZF + 1.6), 2.8))], mirror=True)
G.part('hammer_pin', 'frame', 'dark', [('add', cyl((HP[0], HP[1], -ZF - 0.5), (HP[0], HP[1], ZF + 0.5), 1.8))])

# ------------------------------------------------------------------ slide
G.part('slide', 'slide', 'dark', [
    ('add', obox(-72, 128.6, 5.4, 29, 13.8, 3.2)),
    ('cut', cyl((-64, AX, 0), (130, AX, 0), 7.1)),                                       # barrel tunnel (the barrel stays with the frame)
    ('cut', box(-73, -20, 4, 26, -3.2, 3.2)),                                            # hammer channel
    ('cut', box(-2, 30, 20.5, 31, 2, 15)), ('cut', box(-2, 30, 24.5, 31, -5, 3)),          # ejection port
    ('cut', box(52, 112, 24, 31, -3.6, 3.6)),                                            # open top window over the barrel
    ('cut', row(7, lambda i: box2(-44 + i * 5, -41.6 + i * 5, 9, 25, 13.0, 15))),         # rear serrations
    ('cut', box2(46, 122, 8.5, 12, 13.0, 15)),                                           # long side flute
    ('cut', row(4, lambda i: box2(98 + i * 6, 101 + i * 6, 14.5, 24, 13.0, 15))),         # front serrations
])
G.part('sight_rear', 'slide', 'steel', [('add', plate([(-70, 29), (-58, 29), (-60, 32.6), (-70, 32.6)], 8.5)), ('cut', box(-71, -57, 30.4, 33, -2, 2))])
G.part('selector_pin', 'slide', 'steel', [('add', cyl((SP[0], SP[1], 13), (SP[0], SP[1], 16.9), 1.5))], mirror=True)
G.part('selector', 'selector', 'accent', [
    ('add', cyl((SP[0], SP[1], 14.2), (SP[0], SP[1], 16.2), 4.2)),
    ('add', box(SP[0], SP[0] + 12, SP[1] - 1.6, SP[1] + 1.6, 14.2, 16.6)),
], mirror=True)

# ------------------------------------------------------------------ hammer / trigger / magazine
G.part('hammer', 'hammer', 'steel', [
    ('add', plate([(-69, 1), (-63, 4), (-64.5, 21), (-67, 23.5), (-79, 25), (-80.5, 22.5), (-72.5, 19.5), (-71.5, 8), (-70, 2)], 2.7)),
    ('add', cyl((HP[0], HP[1], -2.7), (HP[0], HP[1], 2.7), 4.0)),
])
G.part('trigger', 'trigger', 'steel', [('add', plate([(7, 2), (13, 2), (13.6, -6), (12.6, -14), (13.6, -24), (11, -26), (8.6, -16), (7.4, -6)], 2.2))])
G.part('mag_body', 'mag', 'dark', [
    ('add', prism('xy', GR.rect(0, 128, -12, 12), -6.2, 6.2)),
    ('cut', row(3, lambda i: plate2(GR.rect(106 + i * 6, 108.5 + i * 6, -13, 13), 5.6, 7))),
])
G.part('mag_base', 'mag', 'polymer', [('add', prism('xy', [GR.pt(128.3, -14.5), GR.pt(128.3, 17), GR.pt(132, 19), GR.pt(135, 17), GR.pt(135, -14.5)], -8.5, 8.5))])

# ------------------------------------------------------------------ motion
G.group('slide', [G.move('slide', (-1, 0, 0), 40.0)])
G.group('selector', [G.move('slide', (-1, 0, 0), 40.0), G.rot('selector', (SP[0], SP[1], 0), (0, 0, 1), -40.0)], mirror=True)
G.group('hammer', [G.rot('hammer', (HP[0], HP[1], 0), (0, 0, 1), 45.0)])
G.group('trigger', [G.rot('trigger', (10, -1, 0), (0, 0, 1), -16.0)])
G.group('mag', [G.move('mag', GR.axis(), 160.0)])
G.mode('OPEN', slide=1.0, mag=1.0, hammer=1.0)
G.mode('BURST', selector=1.0, hammer=1.0)

G.clip('Idle', 2)
G.clip('Fire', 10, trigger=[(0, 0), (0.15, 1), (0.6, 1), (1, 0)], slide=[(0.2, 0), (0.45, 1), (0.85, 0)],
       hammer=[(0, 0), (0.12, 1), (0.2, 0), (0.25, 0), (0.45, 1), (0.85, 1), (1, 0)])
G.clip('Fire_Burst', 26, selector=[(0, 1), (1, 1)], trigger=[(0, 0), (0.06, 1), (0.9, 1), (1, 0)],
       slide=[(0.08, 0), (0.18, 1), (0.32, 0), (0.38, 0), (0.48, 1), (0.62, 0), (0.68, 0), (0.78, 1), (0.92, 0)],
       hammer=[(0, 0), (0.05, 1), (0.08, 0), (0.1, 0), (0.18, 1), (0.34, 1), (0.37, 0), (0.4, 0), (0.48, 1), (0.64, 1), (0.67, 0), (0.7, 0),
               (0.78, 1), (0.92, 1), (1, 0)])
G.clip('Reload', 54, slide=[(0, 1), (0.82, 1), (0.92, 0)], mag=[(0.04, 0), (0.28, 1), (0.48, 1), (0.72, 0)], hammer=[(0, 1), (1, 1)])
G.clip('Slide_Rack', 20, slide=[(0.05, 0), (0.45, 1), (0.6, 1), (0.9, 0)], hammer=[(0.05, 0), (0.4, 1), (0.9, 1), (1, 0)])
G.clip('Selector_Switch', 10, selector=[(0, 0), (0.45, 1), (0.55, 1), (1, 0)])
G.check()
