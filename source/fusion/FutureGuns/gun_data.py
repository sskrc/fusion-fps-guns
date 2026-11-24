# Pure-data definitions of the three guns. No Fusion imports here, so the same
# file drives the Fusion script and the offline preview.
# Units: cm.  +X = muzzle direction, +Y = up, Z = left/right.  Origin near the trigger.


def rect(x0, y0, x1, y1):
    return [(x0, y0), (x1, y0), (x1, y1), (x0, y1)]


def slot(x, y, w, h, slant):
    """Parallelogram vent. (x, y) = lower-left corner, slant = x shift of the top edge."""
    return [(x, y), (x + w, y), (x + w + slant, y + h), (x + slant, y + h)]


def slots(x, y, w, h, slant, pitch, n):
    return [slot(x + i * pitch, y, w, h, slant) for i in range(n)]


def teeth(x0, x1, y0, y1, pitch, gap, depth):
    """Picatinny-like rail profile: flat bottom, toothed top."""
    pts = [(x0, y0), (x1, y0)]
    x = x1
    top = True
    pts.append((x, y1))
    while x - pitch > x0:
        xa = x - (pitch - gap)
        pts += [(xa, y1), (xa, y1 - depth), (xa - gap, y1 - depth), (xa - gap, y1)]
        x -= pitch
    pts.append((x0, y1))
    return pts


class Gun:
    def __init__(self, name, colors):
        self.name = name
        self.colors = colors      # material key -> dict(rgb, metal, rough, emit)
        self.parts = []

    def plate(self, n, pts, t, m, z=0.0, mirror=False, holes=None, ch=0.0):
        self.parts.append(dict(k='plate', n=n, pts=pts, t=t, m=m, z=z, mirror=mirror,
                               holes=holes or [], ch=ch))

    def cyl(self, n, p1, p2, r, m, r2=None, bore=0.0, mirror=False):
        self.parts.append(dict(k='cyl', n=n, p1=p1, p2=p2, r=r, r2=r if r2 is None else r2,
                               bore=bore, m=m, mirror=mirror))

    def box(self, n, c, s, m, mirror=False):
        self.parts.append(dict(k='box', n=n, c=c, s=s, m=m, mirror=mirror))


def M(rgb, metal, rough, emit=0.0):
    return dict(rgb=rgb, metal=metal, rough=rough, emit=emit)


BASE = dict(
    body=M((38, 42, 50), 0.9, 0.42),
    barrel=M((20, 21, 24), 1.0, 0.3),
    grip=M((16, 16, 18), 0.0, 0.85),
    lens=M((60, 140, 220), 0.2, 0.05, 0.6),
)


# ----------------------------------------------------------------------------
# 1) SMG  "VX-9 WASP"  (compact, ~56 cm)
# ----------------------------------------------------------------------------
def smg():
    g = Gun('SMG_VX9_Wasp', dict(BASE,
            armor=M((214, 218, 224), 0.3, 0.35),
            accent=M((255, 118, 20), 0.4, 0.4),
            glow=M((40, 230, 255), 0.0, 0.3, 6.0)))
    A = 5.0  # barrel axis height

    # core receiver
    g.plate('receiver', [(-15, 1.5), (-15, 7.2), (-12.5, 8.6), (13, 8.6), (19, 7.4), (21.5, 6.2),
                         (21.5, 2.6), (18, 1.2), (15.5, 1.2), (15.5, 0.2), (8.5, 0.2), (8.5, 1.2),
                         (5.5, -0.5), (-4, -0.5), (-6.5, 1.5)], 3.4, 'body', ch=0.25)
    # white upper shroud with vents
    g.plate('upper_shroud', [(-11, 5.9), (-9, 9.4), (9.5, 9.4), (17.5, 8.0), (27.5, 6.9), (28.5, 5.9),
                             (27.5, 4.9), (14, 4.9), (12, 5.9)], 4.4, 'armor', ch=0.3,
            holes=slots(15.2, 5.6, 1.1, 1.5, -0.8, 2.3, 5))
    # lower hand guard
    g.plate('handguard', [(16.5, 1.2), (20.5, 2.2), (27.5, 3.3), (27.5, 4.4), (16, 4.4)], 3.9, 'body', ch=0.2)
    g.plate('foregrip', [(17.5, 1.6), (24.5, 2.9), (22.6, -3.6), (21.6, -4.4), (18.6, -4.4), (17.8, -3.6)],
            2.6, 'grip', ch=0.3)
    # barrel + muzzle
    g.cyl('barrel', (20, A, 0), (31, A, 0), 1.15, 'barrel', bore=0.5)
    g.cyl('muzzle', (30, A, 0), (35, A, 0), 1.75, 'barrel', bore=0.6)
    g.cyl('muzzle_ring', (31.2, A, 0), (32.0, A, 0), 2.0, 'accent', bore=0.6)
    g.cyl('muzzle_tip', (34.4, A, 0), (35.2, A, 0), 1.95, 'glow', bore=0.9)
    # grip, trigger
    g.plate('grip', [(-4.2, -0.5), (1.6, -0.5), (0.4, -3.2), (-1.0, -10.2), (-2.0, -11.2), (-6.4, -11.2),
                     (-7.0, -10.2), (-5.2, -3.0)], 3.0, 'grip', ch=0.4)
    g.plate('trigger_guard', [(1.2, -0.5), (8.5, -0.5), (8.5, -1.6), (7.2, -4.6), (0.6, -4.6), (0.4, -3.2)],
            1.2, 'body', holes=[[(1.9, -1.2), (7.6, -1.2), (6.6, -3.9), (1.3, -3.9)]])
    g.plate('trigger', [(3.6, -0.6), (4.7, -0.6), (4.5, -2.4), (3.5, -3.3), (3.1, -3.0), (3.7, -2.2)], 0.6, 'accent')
    # magazine
    g.plate('magazine', [(9.0, 1.0), (15.0, 1.0), (13.2, -13.0), (7.2, -13.0)], 2.5, 'body', ch=0.2,
            holes=[[(11.3, -1.5), (12.3, -1.5), (11.0, -11.0), (10.0, -11.0)]])
    g.plate('mag_window', [(11.1, -1.3), (12.5, -1.3), (11.2, -11.2), (9.8, -11.2)], 1.9, 'glow')
    g.plate('mag_base', [(6.8, -13.0), (13.6, -13.0), (13.8, -14.4), (6.6, -14.4)], 3.0, 'accent', ch=0.2)
    # skeleton stock
    g.plate('stock', [(-15, 7.2), (-27, 7.8), (-30.5, 6.6), (-30.5, -3.2), (-28.5, -4.4), (-25.5, -3.2),
                      (-22, 1.8), (-15, 2.2)], 2.2, 'body', ch=0.25,
            holes=[[(-17, 3.8), (-22.8, 3.6), (-26.4, -1.4), (-28.6, -1.6), (-28.6, 5.4), (-26.6, 6.2), (-17, 5.8)]])
    g.plate('butt_pad', [(-30.5, 7.0), (-31.8, 6.4), (-31.8, -3.6), (-30.5, -4.0)], 3.0, 'grip', ch=0.3)
    g.plate('cheek', [(-16.5, 7.3), (-26, 7.8), (-26, 8.6), (-17.5, 8.6)], 2.8, 'armor', ch=0.2)
    # rail and holo sight
    g.plate('top_rail', teeth(-8, 9, 9.4, 10.2, 1.0, 0.45, 0.35), 1.8, 'body')
    g.box('sight_base', (1.5, 10.6, 0), (7.0, 0.9, 2.4), 'body')
    g.box('sight_wall', (2.5, 12.6, 1.25), (4.4, 3.2, 0.35), 'body', mirror=True)
    g.box('sight_roof', (2.5, 14.35, 0), (4.4, 0.35, 2.85), 'body')
    g.box('sight_lens', (3.4, 12.6, 0), (0.15, 3.0, 2.2), 'lens')
    g.box('sight_emitter', (-1.0, 11.4, 0), (1.6, 0.8, 1.6), 'accent')
    g.plate('front_sight', [(24.5, 6.9), (27.0, 6.9), (26.4, 8.8), (25.4, 8.8)], 0.8, 'accent')
    # side dressing
    g.plate('side_stripe', [(-8, 2.6), (6, 2.6), (8, 4.3), (-6.5, 4.3)], 0.5, 'accent', z=1.8, mirror=True)
    g.plate('glow_line', [(-8.5, 6.6), (11, 6.6), (11.6, 7.1), (-8.2, 7.1)], 0.3, 'glow', z=2.25, mirror=True)
    g.plate('glow_stock', [(-16.5, 6.0), (-26.4, 6.6), (-26.4, 6.95), (-16.5, 6.4)], 0.3, 'glow', z=1.15, mirror=True)
    g.cyl('pin_a', (-10, 3.4, -1.9), (-10, 3.4, 1.9), 0.45, 'accent')
    g.cyl('pin_b', (12.5, 3.0, -1.9), (12.5, 3.0, 1.9), 0.45, 'accent')
    g.cyl('charging_handle', (6, 7.8, 2.0), (6, 7.8, 3.6), 0.5, 'accent')
    g.cyl('selector', (-2.5, 2.2, 1.6), (-2.5, 2.2, 2.0), 0.7, 'armor', mirror=True)
    return g


# ----------------------------------------------------------------------------
# 2) SHOTGUN  "HR-12 BREAKER"  (chunky pump, ~100 cm)
# ----------------------------------------------------------------------------
def shotgun():
    g = Gun('Shotgun_HR12_Breaker', dict(BASE,
            armor=M((122, 128, 136), 0.8, 0.4),
            accent=M((222, 38, 38), 0.4, 0.4),
            glow=M((255, 160, 30), 0.0, 0.3, 6.0),
            brass=M((205, 160, 60), 1.0, 0.3)))
    A = 5.4   # main barrel axis
    T = 1.9   # magazine tube axis

    g.plate('receiver', [(-14, -0.2), (-14, 7.4), (-10.5, 9.4), (13, 9.4), (17, 8.0), (17, 0.2),
                         (11, -1.6), (-6, -1.6)], 4.8, 'body', ch=0.35)
    g.plate('receiver_panel', [(-10, 4.6), (10, 4.6), (13.5, 7.2), (12, 8.4), (-9, 8.4), (-11.5, 6.8)],
            5.4, 'armor', ch=0.25, holes=slots(-3.5, 5.5, 1.3, 2.0, 1.0, 2.9, 4))
    g.plate('ejection_port', [(-7.5, 5.2), (-0.5, 5.2), (0.5, 7.4), (-7.5, 7.4)], 0.5, 'barrel', z=2.6)
    # barrels
    g.cyl('barrel', (15, A, 0), (56, A, 0), 1.85, 'barrel', bore=1.25)
    g.cyl('mag_tube', (15, T, 0), (49, T, 0), 1.6, 'barrel')
    g.cyl('mag_cap', (49, T, 0), (51, T, 0), 1.75, 'accent')
    # heat shield
    g.plate('heat_shield', [(17, 5.6), (50, 5.6), (52.5, 6.6), (50.5, 8.4), (19, 8.4), (17, 7.4)],
            5.0, 'armor', ch=0.3, holes=slots(21.5, 6.3, 1.2, 1.5, 0.9, 3.0, 9))
    g.plate('barrel_clamp', [(44.5, -0.2), (49, -0.2), (50, 0.8), (50, 5.6), (44.5, 5.6)], 4.6, 'body', ch=0.3)
    # muzzle brake
    g.cyl('muzzle_brake', (54, A, 0), (61, A, 0), 2.5, 'body', bore=1.3)
    g.cyl('brake_ring_a', (55.3, A, 0), (56.3, A, 0), 2.75, 'accent', bore=1.3)
    g.cyl('brake_ring_b', (58.6, A, 0), (59.6, A, 0), 2.75, 'armor', bore=1.3)
    g.cyl('brake_glow', (60.6, A, 0), (61.3, A, 0), 2.2, 'glow', bore=1.5)
    # pump fore-end
    g.plate('pump', [(22, -1.6), (41, -1.6), (42.5, -0.2), (42.5, 3.4), (21, 3.4), (20, 2.2), (20, 0)],
            5.6, 'armor', ch=0.4)
    for i in range(6):
        x = 23.5 + i * 3.0
        g.plate('pump_rib_%d' % i, slot(x, -1.9, 1.3, 4.6, 1.0), 6.0, 'grip')
    g.plate('pump_glow', [(21.5, 2.3), (41.5, 2.3), (41.5, 2.75), (21.5, 2.75)], 0.3, 'glow', z=2.85, mirror=True)
    # grip and trigger
    g.plate('grip', [(-9.5, -1.6), (-2.5, -1.6), (-4.0, -4.4), (-6.2, -11.6), (-7.2, -12.6), (-12.2, -12.6),
                     (-12.8, -11.6), (-10.8, -4.5)], 3.4, 'grip', ch=0.45)
    g.plate('trigger_guard', [(-3, -1.6), (6.5, -1.6), (6.5, -2.8), (4.8, -6.0), (-3.6, -6.0), (-4.0, -4.4)],
            1.4, 'body', holes=[[(-2.2, -2.4), (5.5, -2.4), (4.2, -5.2), (-3.0, -5.2)]])
    g.plate('trigger', [(0.6, -1.7), (1.8, -1.7), (1.6, -3.6), (0.5, -4.6), (0.1, -4.3), (0.7, -3.4)], 0.7, 'accent')
    # stock
    g.plate('stock', [(-14, 7.4), (-20, 7.6), (-40, 6.0), (-42.5, 5.0), (-42.5, -5.6), (-40.5, -6.6),
                      (-27, -2.6), (-19, -0.6), (-14, -0.2)], 3.8, 'body', ch=0.4,
            holes=[[(-22, 1.6), (-29, 0.2), (-38.5, -3.2), (-38.5, 3.4), (-23, 5.0)]])
    g.plate('cheek_rest', [(-19, 7.6), (-36.5, 6.3), (-36.5, 7.9), (-22, 9.0)], 4.4, 'armor', ch=0.3)
    g.plate('butt_pad', [(-42.5, 5.6), (-44.3, 4.9), (-44.3, -6.0), (-42.5, -6.8)], 4.4, 'grip', ch=0.4)
    g.plate('stock_glow', [(-22.5, 5.3), (-38, 3.9), (-38, 4.3), (-22.5, 5.7)], 0.3, 'glow', z=1.95, mirror=True)
    # shell carrier (right side)
    g.box('shell_rack', (2, 2.2, 2.75), (15.5, 2.4, 0.7), 'body')
    for i in range(5):
        x = -4 + i * 3.0
        g.cyl('shell_%d' % i, (x, 0.4, 3.9), (x, 3.3, 3.9), 0.95, 'accent')
        g.cyl('shell_cap_%d' % i, (x, 3.3, 3.9), (x, 4.1, 3.9), 1.0, 'brass')
    # sights
    g.plate('top_rail', teeth(-9, 12, 9.4, 10.3, 1.0, 0.45, 0.4), 2.0, 'body')
    g.box('rear_sight_wall', (-5, 11.4, 0.85), (2.4, 2.2, 0.4), 'body', mirror=True)
    g.box('rear_sight_base', (-5, 10.55, 0), (3.0, 0.5, 2.1), 'accent')
    g.plate('front_sight', [(46.5, 8.4), (50, 8.4), (49.2, 11.4), (47.6, 11.4)], 0.9, 'accent')
    g.cyl('front_sight_dot', (48.4, 10.6, -0.55), (48.4, 10.6, 0.55), 0.35, 'glow')
    g.cyl('pin_a', (-11, 2.2, -2.7), (-11, 2.2, 2.7), 0.55, 'accent')
    g.cyl('pin_b', (14, 2.4, -2.7), (14, 2.4, 2.7), 0.55, 'accent')
    return g


# ----------------------------------------------------------------------------
# 3) SNIPER  "LR-X LONGSHOT"  (rail-gun style, ~150 cm)
# ----------------------------------------------------------------------------
def sniper():
    g = Gun('Sniper_LRX_Longshot', dict(BASE,
            armor=M((228, 230, 235), 0.3, 0.35),
            accent=M((35, 70, 150), 0.6, 0.35),
            glow=M((150, 90, 255), 0.0, 0.3, 7.0)))
    A = 4.6

    g.plate('receiver', [(-18, 0), (-18, 8.0), (-14, 9.6), (18, 9.6), (22, 8.4), (22, 0.8), (16, -1), (-10, -1)],
            4.2, 'body', ch=0.35)
    g.plate('receiver_armor', [(-14, 5.4), (14, 5.4), (19.5, 7.0), (17.5, 8.8), (-13, 8.8), (-16, 7.0)],
            4.8, 'armor', ch=0.25)
    # twin rails
    g.plate('rail_upper', [(20, A + 0.7), (86, A + 0.7), (88, A + 1.2), (88, A + 1.9), (85, A + 2.5), (20, A + 3.3)],
            2.4, 'body', ch=0.2)
    g.plate('rail_lower', [(20, A - 0.7), (86, A - 0.7), (88, A - 1.2), (88, A - 1.9), (85, A - 2.5), (20, A - 3.3)],
            2.4, 'body', ch=0.2)
    g.cyl('core', (20, A, 0), (87, A, 0), 0.5, 'glow')
    for i, x in enumerate([29, 39, 49, 59, 69, 79]):
        g.cyl('coil_%d' % i, (x, A, 0), (x + 2.0, A, 0), 3.5, 'accent' if i % 2 == 0 else 'armor', bore=2.6)
        g.plate('coil_brace_%d' % i, rect(x + 0.3, A - 3.0, x + 1.7, A + 3.0), 3.0, 'body')
    g.plate('muzzle_block', [(84, A - 3.2), (92, A - 2.4), (93, A - 1.4), (93, A + 1.4), (92, A + 2.4), (84, A + 3.2)],
            3.4, 'armor', ch=0.3, holes=[[(86, A - 0.55), (93.5, A - 0.55), (93.5, A + 0.55), (86, A + 0.55)]])
    g.plate('muzzle_glow', [(86, A - 0.5), (92, A - 0.5), (92, A + 0.5), (86, A + 0.5)], 1.4, 'glow')
    # chassis / fore-end
    g.plate('forend', [(16, -1), (46, 0.2), (49, 1.4), (49, 2.4), (22, 2.4)], 4.6, 'armor', ch=0.3,
            holes=slots(26, 0.75, 1.2, 1.1, 0.7, 3.2, 6))
    # capacitor cells
    g.cyl('cell', (-8, 3.2, 2.5), (12, 3.2, 2.5), 1.25, 'accent', mirror=True)
    g.cyl('cell_glow_a', (-4, 3.2, 2.5), (-3, 3.2, 2.5), 1.4, 'glow', mirror=True)
    g.cyl('cell_glow_b', (7, 3.2, 2.5), (8, 3.2, 2.5), 1.4, 'glow', mirror=True)
    # stock with thumbhole
    g.plate('stock', [(-18, 8.0), (-30, 8.6), (-52, 7.6), (-54.5, 6.4), (-54.5, -6.4), (-52.5, -7.6),
                      (-41, -5.2), (-31, -1.4), (-27.5, -9.6), (-26.5, -10.6), (-21.5, -10.6), (-20.8, -9.6),
                      (-16.5, -1), (-18, 0)], 3.6, 'body', ch=0.4,
            holes=[[(-21.5, 1.6), (-28.5, 2.0), (-37, 0.2), (-47, -2.6), (-49.5, -2.2), (-49.5, 4.4),
                    (-47, 5.2), (-22.5, 5.6)]])
    g.plate('grip_pad', [(-20.2, -2.2), (-23.6, -9.6), (-26.0, -9.6), (-29.0, -2.4)], 4.0, 'grip', ch=0.3)
    g.plate('cheek_rest', [(-26, 8.6), (-47, 7.9), (-47, 9.8), (-28.5, 10.9)], 4.2, 'armor', ch=0.3)
    g.plate('butt_pad', [(-54.5, 7.0), (-56.5, 6.4), (-56.5, -6.8), (-54.5, -7.8)], 4.2, 'grip', ch=0.4)
    g.plate('stock_glow', [(-23, 6.3), (-50, 5.5), (-50, 5.9), (-23, 6.7)], 0.3, 'glow', z=1.85, mirror=True)
    # trigger and magazine
    g.plate('trigger_guard', [(-16.5, -1), (-5, -1), (-5, -2.2), (-6.8, -5.4), (-17.6, -5.4), (-18.2, -4.2)],
            1.4, 'body', holes=[[(-16.2, -1.8), (-6.0, -1.8), (-7.4, -4.6), (-17.4, -4.6)]])
    g.plate('trigger', [(-12.4, -1.1), (-11.2, -1.1), (-11.4, -3.0), (-12.5, -4.0), (-12.9, -3.7), (-12.3, -2.8)],
            0.7, 'accent')
    g.plate('magazine', [(1, -1), (12, -1), (10.8, -9.5), (2.2, -9.5)], 3.2, 'body', ch=0.25,
            holes=[rect(4, -7.8, 9, -6.9), rect(4, -5.8, 9, -4.9), rect(4, -3.8, 9, -2.9)])
    g.plate('mag_core', [(3.6, -8.2), (9.4, -8.2), (9.4, -2.5), (3.6, -2.5)], 2.4, 'glow')
    g.plate('mag_base', [(1.8, -9.5), (11.2, -9.5), (11.4, -10.7), (1.6, -10.7)], 3.6, 'accent', ch=0.2)
    # scope
    S = 14.4
    g.plate('scope_rail', teeth(-12, 16, 9.6, 10.5, 1.0, 0.45, 0.4), 2.0, 'body')
    g.plate('mount_rear', [(-7.5, 10.5), (-3.5, 10.5), (-4.2, S), (-6.8, S)], 2.4, 'body')
    g.plate('mount_front', [(7.5, 10.5), (11.5, 10.5), (10.8, S), (8.2, S)], 2.4, 'body')
    g.cyl('scope_tube', (-11, S, 0), (15, S, 0), 1.7, 'body')
    g.cyl('scope_ring_r', (-7.2, S, 0), (-3.8, S, 0), 2.0, 'accent')
    g.cyl('scope_ring_f', (7.8, S, 0), (11.2, S, 0), 2.0, 'accent')
    g.cyl('scope_bell_cone', (15, S, 0), (21, S, 0), 1.7, 'body', r2=2.9)
    g.cyl('scope_bell', (21, S, 0), (31, S, 0), 2.9, 'armor', bore=2.5)
    g.cyl('scope_lens_front', (29.4, S, 0), (29.8, S, 0), 2.55, 'lens')
    g.cyl('scope_eye_cone', (-15, S, 0), (-11, S, 0), 2.3, 'body', r2=1.7)
    g.cyl('scope_eyepiece', (-20, S, 0), (-15, S, 0), 2.3, 'armor', bore=1.9)
    g.cyl('scope_lens_rear', (-19.0, S, 0), (-18.6, S, 0), 1.95, 'lens')
    g.cyl('turret_top', (2, S + 1.2, 0), (2, S + 3.6, 0), 1.15, 'accent')
    g.cyl('turret_side', (2, S, 1.2), (2, S, 3.6), 1.15, 'accent')
    g.cyl('turret_cap', (2, S + 3.6, 0), (2, S + 4.0, 0), 1.3, 'glow')
    # bipod
    g.box('bipod_mount', (43, 0.2, 0), (4.0, 1.6, 4.0), 'body')
    g.cyl('bipod_leg', (43, 0.0, 1.6), (47, -17.0, 8.0), 0.6, 'body', mirror=True)
    g.cyl('bipod_foot', (47, -17.0, 8.0), (47.5, -19.0, 8.8), 0.9, 'grip', mirror=True)
    # dressing
    g.plate('glow_line', [(-13, 6.6), (15, 6.6), (16.2, 7.1), (-13.4, 7.1)], 0.3, 'glow', z=2.45, mirror=True)
    g.cyl('bolt_handle', (-4, 7.6, 2.0), (-4, 6.2, 5.0), 0.5, 'body')
    g.cyl('bolt_knob', (-4, 6.2, 5.0), (-4, 5.5, 6.4), 0.95, 'accent')
    g.cyl('pin_a', (-14, 2.6, -2.3), (-14, 2.6, 2.3), 0.5, 'accent')
    g.cyl('pin_b', (18, 4.4, -2.3), (18, 4.4, 2.3), 0.5, 'accent')
    return g


def all_guns():
    return [smg(), shotgun(), sniper()]
