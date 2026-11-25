# RA08 Shotgun : pump / semi combat shotgun (silhouette cues: perforated heat shield over the barrel, chunky ribbed pump fore-end
# on a tube magazine, over-the-top folding metal stock with a hook-shaped butt).
from ra_lib import *

G = Gun('RA08_Shotgun', 'combat shotgun')
AX = 30.0                                   # bore axis height
TY = 3.0                                    # tube magazine axis height
GR = Slant((-40, -6), 18)                   # pistol grip axis
PX, PY = -138.0, 41.0                       # stock hinge axis (across the receiver)
ZR = 18.0                                   # receiver half width
ZA = 18.6                                   # inner face of the stock arms


def holes(a_deg, x0, n, pitch):
    a = math.radians(a_deg)
    return union(*[cyl((x0 + i * pitch, AX, 0), (x0 + i * pitch, AX + 21 * math.cos(a), 21 * math.sin(a)), 4.0) for i in range(n)])


# ------------------------------------------------------------------ receiver (static)
G.part('receiver', 'frame', 'dark', [
    ('add', slab([(-150, 48), (120, 48), (120, -14), (30, -14), (24, -8), (-150, -8)], ZR, 4.5)),
    ('cut', box(20, 84, 20, 34, 16.6, 19)),                                              # ejection port recess (right side)
    ('cut', box(36, 112, -15, 4, -10, 10)),                                              # loading gate pocket (blind)
    ('add', plate([(-28, -8), (24, -8), (24, -36), (18, -40), (-36, -40)], 6)),          # trigger guard
    ('cut', plate([(-24, -11), (21, -11), (21, -34), (17, -37), (-32, -37)], 7)),
    ('cut', box(-4, 14, -12, 6, -2.7, 2.7)),                                             # trigger slot
    ('cut', row(6, lambda i: box2(-116 + i * 9, -112 + i * 9, 0, 28, 17, 19))),           # rear grooves
    ('cut', box2(-40, 12, 6, 14, 17.2, 19)),
])
G.part('port_door', 'frame', 'steel', [('add', box(22, 82, 21.5, 32.5, 16.2, 16.7))])
G.part('bolt_handle', 'frame', 'steel', [('add', cyl((72, 27, 16.4), (72, 27, 27), 3.2)), ('add', cyl((72, 27, 24), (72, 27, 28.5), 4.4))])
G.part('receiver_collar', 'frame', 'steel', [('add', obox(116, 134, -13, 45, 15.5, 4))])
G.part('top_rail', 'frame', 'steel', [('add', rail(-100, 60, 48, 7))])
G.part('sight_rear', 'frame', 'steel', [('add', plate([(-126, 47), (-102, 47), (-102, 55), (-108, 60), (-126, 60)], 7)), ('cut', box(-127, -101, 53, 61, -2.5, 2.5))])
G.part('safety', 'frame', 'accent', [('add', cyl((-30, 0, 17.6), (-30, 0, 19.2), 3.6))], mirror=True)
G.part('grip', 'frame', 'polymer', [
    ('add', plate([(-22, -7.9), GR.pt(8, 14), GR.pt(86, 14), GR.pt(90, 10), GR.pt(90, -15), GR.pt(40, -17), (-62, -7.9)], 12.5)),
    ('add', plate2([GR.pt(14, 11), GR.pt(82, 11), GR.pt(82, -12), GR.pt(20, -13)], 12.5, 14)),
    ('cut', row(8, lambda i: box2(-80, -20, -24 - i * 8, -22.2 - i * 8, 13.3, 15))),
])
G.part('stock_pin', 'frame', 'chrome', [('add', cyl((PX, PY, -24), (PX, PY, 24), 3.2))])

# ------------------------------------------------------------------ barrel, tube magazine, heat shield (static)
G.part('barrel', 'frame', 'dark', [('add', cyl((118, AX, 0), (654, AX, 0), 11.5)), ('cut', cyl((650, AX, 0), (655, AX, 0), 9.2))])   # solid, shallow recess
G.part('tube', 'frame', 'steel', [('add', cyl((118, TY, 0), (550, TY, 0), 12.0)), ('add', cyl((548, TY, 0), (562, TY, 0), 13.0)),
                                  ('add', cyl((561, TY, 0), (566, TY, 0), 7.0))])
G.part('heat_shield', 'frame', 'steel', [
    ('add', cyl((150, AX, 0), (500, AX, 0), 17.0)),
    ('cut', cyl((149, AX, 0), (501, AX, 0), 15.0)),
    ('int', box(140, 510, AX + 2.5, AX + 24, -24, 24)),
    ('cut', holes(0, 172, 12, 28)), ('cut', holes(50, 186, 11, 28)), ('cut', holes(-50, 186, 11, 28)),
])
G.part('shield_bands', 'frame', 'dark', [('add', cyl((148, AX, 0), (156, AX, 0), 15.6)), ('add', cyl((494, AX, 0), (502, AX, 0), 15.6))])
G.part('barrel_clamp', 'frame', 'dark', [('add', cyl((512, AX, 0), (528, AX, 0), 14.5)), ('add', cyl((512, TY, 0), (528, TY, 0), 15.0)),
                                         ('add', box(512, 528, TY, AX, -7, 7))])
G.part('sight_front', 'frame', 'steel', [('add', cyl((624, AX, 0), (648, AX, 0), 13.2)),
                                         ('add', plate([(626, AX + 10), (646, AX + 10), (643, AX + 24), (634, AX + 24)], 2.2))])

# ------------------------------------------------------------------ folding stock (twin arms outside the receiver, hook butt)
G.part('stock_arm', 'stock', 'steel', [
    ('add', prism('xy', [(-134, 35), (-134, 47), (-296, 47), (-368, 33), (-380, 22), (-380, -46), (-368, -54), (-368, 6), (-304, 35)], ZA, 23)),
    ('add', cyl((PX, PY, ZA), (PX, PY, 23), 8.0)),
    ('cut', row(6, lambda i: box(-290 + i * 24, -276 + i * 24, 38.5, 43.5, 21.6, 24))),
], mirror=True)
G.part('stock_butt', 'stock', 'steel', [
    ('add', plate([(-380, 28), (-368, 28), (-368, -40), (-356, -40), (-342, -36), (-334, -46), (-344, -58), (-368, -62), (-380, -54)], 19.2)),   # plate + hook
    ('cut', row(3, lambda i: box(-381, -367, 6 - i * 15, 15 - i * 15, -11, 11))),
])
G.part('butt_pad', 'stock', 'polymer', [('add', plate([(-379.6, 28), (-386, 24), (-386, -50), (-379.6, -54)], 19.2))])

# ------------------------------------------------------------------ moving parts
G.part('forend', 'pump', 'polymer', [
    ('add', obox(240, 410, -18, 27, 23, 7)),
    ('cut', cyl((239, TY, 0), (411, TY, 0), 12.6)),                                      # tunnel for the tube
    ('cut', cyl((239, AX, 0), (411, AX, 0), 12.2)),                                      # open channel under the barrel
    ('cut', row(9, lambda i: box2(252 + i * 17, 261 + i * 17, -11, 20, 21.2, 24))),       # ribs
    ('cut', plate([(239, -19), (256, -19), (239, -9)], 24)), ('cut', plate([(411, -19), (394, -19), (411, -9)], 24)),
])
G.part('forend_bars', 'pump', 'steel', [('add', box(196, 242, TY - 3.5, TY + 3.5, 12.9, 15.4))], mirror=True)
G.part('gate_flap', 'gate', 'steel', [('add', box(38.5, 109.5, -13.6, -11.6, -9.5, 9.5)), ('cut', row(3, lambda i: box(50 + i * 14, 57 + i * 14, -14, -13, -6, 6)))])
G.part('trigger', 'trigger', 'steel', [('add', plate([(1, 1), (7, 1), (7.6, -10), (6.6, -18), (7.6, -28), (5, -30), (2.6, -20), (1.4, -10)], 2.2))])

# ------------------------------------------------------------------ motion
G.group('pump', [G.move('pump', (-1, 0, 0), 55.0)])
G.group('stock', [G.rot('stock', (PX, PY, 0), (0, 0, 1), -180.0)])
G.group('gate', [G.rot('gate', (109, -12.6, 0), (0, 0, 1), -12.0)])
G.group('trigger', [G.rot('trigger', (4, -3, 0), (0, 0, 1), -15.0)])
G.mode('OPEN', pump=1.0, gate=1.0)
G.mode('FOLDED', stock=1.0)

G.clip('Idle', 2)
G.clip('Fire', 10, trigger=[(0, 0), (0.15, 1), (0.6, 1), (1, 0)])
G.clip('Pump', 18, pump=[(0.05, 0), (0.45, 1), (0.55, 1), (0.95, 0)])
G.clip('Reload', 72, gate=[(0.03, 0), (0.12, 1), (0.66, 1), (0.74, 0)], pump=[(0.78, 0), (0.87, 1), (0.9, 1), (0.98, 0)])
G.clip('Stock_Fold', 28, stock=[(0, 0), (1, 1)])
G.clip('Stock_Unfold', 28, stock=[(0, 1), (1, 0)])
G.check()
