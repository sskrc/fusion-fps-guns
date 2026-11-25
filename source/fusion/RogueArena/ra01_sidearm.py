# RA01 Sidearm : standard striker-fired polymer pistol (silhouette cues: humped grip, stepped slide nose, squared guard).
from ra_lib import *

G = Gun('RA01_Sidearm', 'standard handgun')
AX = 17.0                                   # bore axis height
GR = Slant((-40, -2), 17)                   # grip / magazine axis
ZF = 12.8                                   # frame half width

# ------------------------------------------------------------------ frame (static)
G.part('frame', 'frame', 'polymer', [
    ('add', plate([(-67, 5), (106, 5), (106, -8.5), (36, -8.5), (33, -5), (-22, -5), GR.pt(6, 15.5), GR.pt(96, 15.5), GR.pt(96, -16.5),
                   GR.pt(60, -19.5), GR.pt(25, -17.5), (-69, -6), (-70, 3)], ZF)),
    ('add', plate([(-26, -5), (40, -5), (42, -12), (40, -32), (33, -40), (-33, -40), (-30, -30)], 7.0)),                # trigger guard
    ('cut', plate([(-24, -12), (34, -12), (36, -15), (34.5, -30), (30, -35), (-30.5, -35)], 15)),
    ('cut', prism('xy', GR.rect(-0.5, 97, -12.4, 12.4), -6.6, 6.6)),                                                    # magazine well
    ('cut', box(2, 20, -13, 3.5, -2.7, 2.7)),                                                                          # trigger slot
    ('cut', row(4, lambda i: box(58 + i * 11, 62.5 + i * 11, -9, -6.3, -14, 14))),                                      # accessory rail slots
    ('add', plate2([GR.pt(14, 12.5), GR.pt(90, 12.5), GR.pt(90, -13.5), GR.pt(56, -16.5), GR.pt(22, -14.5)], ZF, 14.4)),  # grip panels
    ('cut', row(9, lambda i: box2(-90, 0, -24 - i * 7.5, -22.4 - i * 7.5, 13.7, 15))),
])
G.part('barrel', 'frame', 'chrome', [('add', cyl((-20, AX, 0), (107.5, AX, 0), 6.5)), ('cut', cyl((104.5, AX, 0), (108, AX, 0), 4.3))])
G.part('slide_stop', 'frame', 'dark', [('add', prism('xy', [(-12, 3.6), (20, 3.6), (23, 0.5), (8, -2), (-12, -1)], ZF, 14.2))], mirror=True)
G.part('takedown', 'frame', 'dark', [('add', box(38, 47, -4.5, -1, ZF, 14.0))], mirror=True)
G.part('mag_paddle', 'frame', 'dark', [('add', prism('xy', [(-22, -8), (-6, -8), (-8, -11.6), (-22, -11.6)], 7.2, 9.4))], mirror=True)

# ------------------------------------------------------------------ slide
G.part('slide', 'slide', 'dark', [
    ('add', obox(-68, 107, 5.4, 27.5, 13.5, 3.2)),
    ('cut', cyl((-60, AX, 0), (108, AX, 0), 7.0)),                                       # barrel tunnel (the barrel stays with the frame)
    ('cut', box(-2, 30, 19.5, 29, 2, 15)), ('cut', box(-2, 30, 23.5, 29, -5, 3)),          # ejection port
    ('cut', box2(50, 108, 4, 30, 12.3, 15)),                                             # stepped nose
    ('cut', plate([(108, 4), (95, 4), (108, 11.5)], 15)),
    ('cut', row(6, lambda i: box2(-63 + i * 5, -60.6 + i * 5, 8.5, 24, 12.7, 15))),      # rear serrations
    ('cut', row(4, lambda i: box2(72 + i * 5, 74.4 + i * 5, 8.5, 24, 11.6, 15))),        # front serrations
])
G.part('sight_front', 'slide', 'steel', [('add', plate([(95, 27.5), (104, 27.5), (103, 30.6), (99, 30.6)], 1.8))])
G.part('sight_rear', 'slide', 'steel', [('add', plate([(-65, 27.5), (-53, 27.5), (-55, 31.2), (-65, 31.2)], 8.5)), ('cut', box(-66, -52, 29, 32, -2, 2))])
G.part('striker_flag', 'slide', 'accent', [('add', cyl((-68.7, 21, 0), (-68, 21, 0), 2.2))])

# ------------------------------------------------------------------ trigger / magazine
G.part('trigger', 'trigger', 'steel', [('add', plate([(7, 2), (13, 2), (13.6, -6), (12.6, -14), (13.6, -24), (11, -26), (8.6, -16), (7.4, -6)], 2.2))])
G.part('mag_body', 'mag', 'plate', [
    ('add', prism('xy', GR.rect(0, 96.3, -12, 12), -6.2, 6.2)),
    ('cut', row(5, lambda i: union(*[cyl(GR.pt(34 + i * 12, -6) + (z0,), GR.pt(34 + i * 12, -6) + (z1,), 1.6) for z0, z1 in ((5.4, 7), (-7, -5.4))]))),
])
G.part('mag_base', 'mag', 'polymer', [('add', prism('xy', [GR.pt(96.5, -15.5), GR.pt(96.5, 17.5), GR.pt(100, 19), GR.pt(102, 17), GR.pt(102, -15.5)], -13, 13))])

# ------------------------------------------------------------------ motion
G.group('slide', [G.move('slide', (-1, 0, 0), 38.0)])
G.group('trigger', [G.rot('trigger', (10, -1, 0), (0, 0, 1), -16.0)])
G.group('mag', [G.move('mag', GR.axis(), 125.0)])
G.mode('OPEN', slide=1.0, mag=1.0)

G.clip('Idle', 2)
G.clip('Fire', 10, trigger=[(0, 0), (0.15, 1), (0.6, 1), (1, 0)], slide=[(0.1, 0), (0.4, 1), (0.85, 0)])
G.clip('Fire_Last', 10, trigger=[(0, 0), (0.15, 1), (0.6, 1), (1, 0)], slide=[(0.1, 0), (0.4, 1)])
G.clip('Reload', 54, slide=[(0, 1), (0.82, 1), (0.92, 0)], mag=[(0.04, 0), (0.28, 1), (0.48, 1), (0.72, 0)])
G.clip('Reload_Tactical', 42, mag=[(0.05, 0), (0.36, 1), (0.58, 1), (0.92, 0)])
G.clip('Slide_Rack', 20, slide=[(0.05, 0), (0.45, 1), (0.6, 1), (0.9, 0)])
G.check()
