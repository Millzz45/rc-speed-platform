"""Chassis, D34 package v3: three-piece floor plate (D27 laps), full-length three-piece upper deck, BMI-1
chassis-side mounts, bumper and pads. All shapes are built in vehicle coordinates (see params.py).

D34 changes (owner: "you can make this car 1000x better of a package"): the cooling shroud and its gasket are gone
(the bought fan heat sink cools the motor, the body's hood intake blows straight onto the ESC fan); the 14 mm side
walls are now 7 mm lips; the floor is a rounded plate with a 2 mm isogrid pocketed into its top (flat underside kept
for the aero); the upper deck runs bulkhead to bulkhead like a pro touring car and carries the stiffness; every plate
is drawn as a rounded 2D outline (cad/shape2d.py) instead of raw boxes. The D33 copy is in rnd/archive/d33/cad/."""
from functools import lru_cache
from build123d import Pos, Axis, fillet
import params as P
from lib import (box, cbox, cyl_z, cyl_y, cyl_x, insert_hole, clear_hole, csk_hole, magnet_pocket_z)
import shape2d as S2
import anchors as AN

POCKET_D = P.FLOOR_POCKET_D   # D53: 2.8 (1.2 mm skin); D34 was 2.0 (4 mm floor -> 2 mm skin + ribs)


def tub_outline():
    left = [(x, w) for x, w in P.TUB_LEFT]
    right = [(x, -w) for x, w in reversed(P.TUB_RIGHT)]
    return left + right


def tub_poly():
    """Floor plan: the D27 outline with its corners rounded (r 10 outside, r 14 in the waist)."""
    return S2.rounded(S2.poly(tub_outline()), r_convex=10.0, r_concave=14.0)


def _rail(x0, x1, y0, t, h):
    """Edge lip / corridor wall: XZ profile with 45 deg ramped ends and a rounded top, t thick from y0."""
    zf = P.FLOOR_TOP
    prof = S2.poly([(x0, zf - 0.01), (x1, zf - 0.01), (x1 - h, zf + h), (x0 + h, zf + h)])
    return S2.solid_xz(S2.rounded(prof, r_convex=1.2), y0, t)


def screw_points():
    """Every countersunk screw through the floor (running gear, mounts, diffuser, laps)."""
    pts = (P.bulkhead_floor_holes(0.0) + P.bulkhead_floor_holes(P.WB) + P.motor_plate_floor_holes()
           + P.lay_holder_floor_holes() + front_mount_holes() + rear_mount_holes() + diffuser_holes())
    return pts + list(P.JOINT_SCREWS)


def floor_pockets():
    """D34 isogrid region: inside a 6 mm edge band, clear of the laps, bulkheads, mounts, posts, walls, slots and
    every screw (5.5 mm round). Pockets are blind from the top (POCKET_D), so the underside stays flat."""
    R = S2.rect
    keep = [R(a - 1.5, -200, b + 1.5, 200) for a, b in P.TUB_JOINTS]
    for ax in (0.0, P.WB):
        keep += [R(ax - 17, 21, ax + 17, 46), R(ax - 17, -46, ax + 17, -21)]
    keep += [R(-60, -80, -18, 80), R(P.WB + 20, -80, P.WB + 60, 80)]                   # front + rear mounts
    keep += [R(hx - 6.5, -50, hx + 6.5, -30) for hx in P.SERVO_TAB_HOLES_X]             # servo posts
    bx, by, bz, bl, bw, bh = P.BATTERY_BOX
    keep += [R(bx - 6, by, bx + 2, by + bw + 2), R(bx + bl - 2, by, bx + bl + 6, by + bw + 2)]   # battery stops
    keep += [R(bx - 2, 9, 160, 14), R(182, 9, bx + bl + 2, 14), R(188, -14, 234, -9)]   # belt-corridor walls (D47)
    keep += [R(119.5, -17, P.LAYSHAFT_X + 12, -3)]                                     # motor plate foot (D47: fixed, was ESC end)
    keep += [R(P.LAYSHAFT_X - 12, 6.5, P.LAYSHAFT_X + 12, 18.5)]                       # layshaft holder
    for sx in P.BATTERY_STRAP_X:
        keep += [R(sx - 14, by - 6, sx + 14, by), R(sx - 14, by + bw, sx + 14, by + bw + 5)]   # strap slots
    ex, ey, _, el, ew, _ = P.ESC_BOX
    keep += [R(ex + 2, ey + 2, ex + el - 2, ey + ew - 2)]                              # cooling slots under the ESC (D47)
    keep += [R(36, 56, 248, 69), R(42, -74, 176, -63)]                                 # edge lips
    keep += [S2.disc(x, y, 5.5) for x, y in screw_points()]
    region = tub_poly().buffer(-6.0).difference(S2.unary_union(keep))
    return S2.isogrid(region, pitch=24.0, rib=2.6, r=1.8, min_area=40.0, origin=(0.0, 0.0))


@lru_cache(maxsize=1)
def tub_full():
    z0, ft = P.RIDE_Z, P.FLOOR_T
    pl = tub_poly()
    # floor with a 1.2 mm stepped chamfer round the underside edge (reads as a chamfer, keeps the flat floor)
    t = S2.solid(pl.buffer(-1.2, quad_segs=S2.RES), z0, 1.2) + S2.solid(pl, z0 + 1.2, ft - 1.2)
    rh = P.RAIL_TOP - P.FLOOR_TOP
    # D34 edge lips (7 mm, ramped ends): left over the battery side, right along the servo / ESC / motor bay
    # D47: the left lip has gaps where the battery straps wrap down to their floor slots
    xs = [P.RAIL_X[0]] + [v for sx in P.BATTERY_STRAP_X for v in (sx - 13, sx + 13)] + [P.RAIL_X[1]]
    for a, b in zip(xs[0::2], xs[1::2]):
        if b - a > 2 * rh + 2:
            t += _rail(a, b, P.TUB_LEFT_W - P.RAIL_T - 0.5, P.RAIL_T, rh)
    t += _rail(46.0, 172.0, -70 + 0.5, P.RAIL_T, rh)
    # belt-corridor walls: left = battery barrier, right = ESC side
    bx, by, bz, bl, bw, bh = P.BATTERY_BOX
    t += _rail(bx, 158, 10.5, 2.0, 15)                   # D47: battery side, up to the lay holder (it is the wall to x 181)
    t += _rail(183, bx + bl, 10.5, 2.0, 15)              #      and behind it
    t += _rail(190, P.ESC_BOX[0] + P.ESC_BOX[3] - 2, -12.5, 2.0, 15)   # ESC side (D47: behind the spur, x > 189)
    # battery end stops (rounded blocks, 8 tall)
    bx, by, bz, bl, bw, bh = P.BATTERY_BOX
    st = P.BATTERY_STOP_T                                # D50: 6 mm (was 4), grown AWAY from the pack inside the kept floor band
    for x0, y0 in ((bx - st, by + 2), (bx + bl, max(by + 2, P.BATTERY_REAR_STOP_Y0))):   # D46: rear one clears the lay holder
        t += S2.solid(S2.rounded(S2.rect(x0, y0, x0 + st, by + bw - 2), r_convex=1.5), P.FLOOR_TOP - 0.01, 8)
    # servo tab posts (servo lies on its side, screws along Y into inserts)
    # D53: posts grown 1.5 mm on the side AWAY from the servo case (8.5 wide, was 7) so a square nut pocket keeps 1 mm of wall
    for hx in P.SERVO_TAB_HOLES_X:
        away = -1 if hx < P.SERVO_BOX[0] else 1
        x0, x1 = (hx - 5.0, hx + 3.5) if away < 0 else (hx - 3.5, hx + 5.0)
        t += S2.solid(S2.rounded(S2.rect(x0, P.SERVO_TAB_Y - 12, x1, P.SERVO_TAB_Y), r_convex=2.0),
                      P.FLOOR_TOP - 0.01, 22)
    servo_sites = [(hx, P.FLOOR_TOP + 10 + dz) for hx in P.SERVO_TAB_HOLES_X for dz in (-P.SERVO_TAB_HOLES_DZ / 2, P.SERVO_TAB_HOLES_DZ / 2)]
    # battery strap slots (strap: up through the corridor slot, over the pack, down by the lip)
    bx_, by_, _, bl_, bw_, _ = P.BATTERY_BOX
    slots = [S2.rounded(S2.rect(sx - 11, y - 1.5, sx + 11, y + 1.5), r_convex=1.4) for sx in P.BATTERY_STRAP_X for y in (by_ - 3.0, by_ + bw_ + 1.6)]   # D47: inner slot between the wall and the pack
    # cooling / lightening slots under the ESC + motor (air exits downward too), stadium shaped
    ex, ey, _, el, ew, _ = P.ESC_BOX                     # D47: under the moved ESC, clear of the rear tub lap (x < 201)
    slots += [S2.rounded(S2.rect(ex + 19 + k * 12, ey + 6, ex + 25 + k * 12, ey + ew - 6), r_convex=2.9) for k in range(3)]
    t -= S2.cutter(S2.unary_union(slots), z0 - 1, ft + 2)
    # isogrid pockets in the floor top
    t -= S2.cutter(floor_pockets(), P.FLOOR_TOP - POCKET_D, POCKET_D + 1)
    # countersunk screws from below (flat underside)
    for (x, y) in screw_points():
        if (x, y) not in P.JOINT_SCREWS:
            t -= csk_hole(x, y, z0, ft)
    # crash ridge right behind the front mount (D18): the beam bears on it in a frontal hit
    rx0, rx1, rw, rh_ = P.FLOOR_RIDGE
    t += S2.solid(S2.rounded(S2.rect(rx0, -rw / 2, rx1, rw / 2), r_convex=1.5), P.FLOOR_TOP - 0.01, rh_)
    # D36: pegs the TPU pads press over (no glue)
    for (x, y) in pad_pegs():
        t += cyl_z(PEG_D, PEG_H + 2.0, x, y, P.FLOOR_TOP - 2.0)
    # D53: servo tab screws (along -Y into the posts) into captive square nuts, cut last so the walls are checked on the finished tub
    for i, (hx, z) in enumerate(servo_sites):
        t = AN.anchor(t, (hx, P.SERVO_TAB_Y, z), (0, -1, 0), f"tub servo post {i + 1}", keep=electronics()["servo"])   # D55: pad clipped at the servo
    return t


def _piece(full, joints, i, z_lo, thick, x_lo, x_hi):
    """Piece i of a plate split at lap joints: the front piece keeps the lower half-thickness tongue in each lap,
    the rear piece the upper one."""
    x0 = x_lo - 1 if i == 0 else joints[i - 1][0]
    x1 = x_hi + 1 if i == len(joints) else joints[i][1]
    t = full & box(x1 - x0, 300, 120, x0, -150, 0)
    if i < len(joints):
        a, b = joints[i]
        t -= box(b - a + 1, 300, 80, a, -150, z_lo + thick / 2)
    if i > 0:
        a, b = joints[i - 1]
        t -= box(b - a, 300, thick / 2, a - 0.01, -150, z_lo - 0.01)
    return t


def _tub_piece(i):
    return joint_holes(_piece(tub_full(), P.TUB_JOINTS, i, P.RIDE_Z, P.FLOOR_T, P.TUB_X0, P.TUB_X1))


def tub_front():
    return _tub_piece(0)


def tub_mid():
    return _tub_piece(1)


def tub_rear():
    return _tub_piece(len(P.TUB_JOINTS))


LAP_NUT_RECESS = 0.8     # D53: the nut on top of the lap's upper tongue sits in a 0.8 mm recess (stops it turning); D55: hex recess, DIN 934 hex nut


def joint_holes(t):
    """Lap screws: M3 x 6 flat-head up from the flat underside through both 2 mm tongues into a DIN 934 hex nut on top (D55; was a DIN 562 square nut).
    D53: until now the holes were clearance through both tongues with nothing to thread into (a 2 mm tongue cannot hold a
    heat-set insert or a captive nut); the recess keys the nut so the screw tightens from below without holding it."""
    for (x, y) in P.JOINT_SCREWS:
        t -= csk_hole(x, y, P.RIDE_Z, P.FLOOR_T)
        # D55: hex nuts (owner 11-19 "not square nuts.. hexagon nuts"): a 5.8 mm AF hex recess keys the DIN 934 nut
        t -= AN._hex(AN.Vector(x, y, P.FLOOR_TOP - LAP_NUT_RECESS), AN.Vector(0, 0, 1), AN.Vector(1, 0, 0), AN.POCKET_S, LAP_NUT_RECESS + 0.01)
    return t


# ---------------------------------------------------------------------------------
def deck_poly():
    return S2.rounded(S2.mirror_half(P.DECK_HALF_W), r_convex=6.0, r_concave=18.0)


def deck_windows():
    """Through-windows in a 26 mm isogrid (3 mm ribs) over the battery / receiver bay and the rear belt, clear of
    every screw, the tower feet, the laps and the steering step."""
    R = S2.rect
    keep = [R(a - 3, -60, b + 3, 60) for a, b in P.DECK_LAPS]
    keep += [R(-40, -60, 22, 60), R(P.WB - 20, -60, P.WB + 30, 60)]          # bulkhead / tower zones
    keep += [S2.disc(x, y, 6.0) for x, y in P.deck_holes()]
    keep += [R(-16, -23, 20, -9)]                                            # servo-link slot surround
    if P.MOTOR_DUCT:
        import ducts as DU
        keep += [S2.disc(x, y, 6.0) for x, y in DU.DUCT_SCREWS]               # D40: solid round the duct screws
    rx, ry, _, rl, rw, _ = P.RX_BOX
    keep += [R(rx - 6, ry - 6, rx + rl + 6, ry + rw + 6)]                    # D36: solid under the receiver cradle
    if getattr(P, "TECH_PACK", False):
        keep += [S2.disc(x, y, 6.0) for x, y in P.TECH_SCREWS]                # D51: solid under the tech-tray bosses
    region = deck_poly().buffer(-5.0).difference(S2.unary_union(keep))
    return S2.isogrid(region, pitch=26.0, rib=3.0, r=2.5, min_area=60.0, angle0=90.0, origin=(70.0, 0.0))


RX_CLR, RX_ARM_T, RX_HOOK = 0.2, 1.6, 0.8   # D36 receiver cradle


def rx_cradle():
    """D36 (no tape): 4 corner guides + 2 snap arms on the deck top. The receiver + gyro stack drops in and the
    arms' 0.8 mm hooks click over its top edge; pull the arms out with a thumbnail to lift it."""
    rx, ry, rz, rl, rw, rh = P.RX_BOX
    zt = P.DECK_Z + P.DECK_T
    x0, y0, x1, y1 = rx - RX_CLR, ry - RX_CLR, rx + rl + RX_CLR, ry + rw + RX_CLR
    g, leg, gh = 1.6, 5.0, 5.0
    out = None
    for (cx, sx) in ((x0, -1), (x1, 1)):
        for (cy, sy) in ((y0, -1), (y1, 1)):
            xa = cx if sx > 0 else cx - g
            ya = cy if sy > 0 else cy - g
            # an L round each corner, outside the box footprint
            Lx = box(g, leg, gh, xa, (cy - leg) if sy > 0 else cy, zt - 0.01) + box(g, g, gh, xa, ya, zt - 0.01)
            Ly = box(leg, g, gh, (cx - leg) if sx > 0 else cx, ya, zt - 0.01)
            piece = Lx + Ly
            out = piece if out is None else out + piece
    top = zt + rh
    for yi, sg in ((y0, 1), (y1, -1)):               # sg = inward direction
        o = -sg
        prof = S2.poly([(yi + o * RX_ARM_T, zt - 0.01), (yi, zt - 0.01), (yi, top + 0.15), (yi + sg * RX_HOOK, top + 0.15),
                        (yi, top + 1.8), (yi + o * RX_ARM_T, top + 1.8)])
        out += S2.solid_yz(prof, rx + rl / 2 - 4.0, 8.0)
    return out


# ---------------------------------------------------------------------------------
# D51 tech tray + lid (params.TECH_*). The tray prints flat, pockets up; the lid prints upside down (top on the bed). No supports.
TECH_HW = 27.8                      # tray half-width (the deck is 26)
TECH_LEDGE, TECH_CLR = 1.2, 0.25


def _tech_pockets():
    """[(name, x0, y0, x1, y1, depth, open)] pocket outlines = board + clearance."""
    return [(n, b[0] - TECH_CLR, b[1] - TECH_CLR, b[0] + b[2] + TECH_CLR, b[1] + b[3] + TECH_CLR, b[5], b[6]) for n, b in P.TECH_BOARDS.items()]


def tech_bosses():
    """Three bosses on the deck top that carry the tray; D53: each holds a captive square nut (cad/anchors.py)."""
    zd = P.DECK_Z + P.DECK_T
    out = None
    for (x, y) in P.TECH_SCREWS:
        b = cyl_z(P.TECH_BOSS_D, P.TECH_BOSS_H + 0.01, x, y, zd - 0.01)
        out = b if out is None else out + b
    return out


def tech_tray():
    x0, x1 = P.TECH_TRAY_X
    zb, t = P.TECH_TRAY_Z, P.TECH_TRAY_T
    zt = zb + t
    R = S2.rect
    plate = S2.rounded(R(x0, -TECH_HW, x1, TECH_HW), r_convex=3.0)
    pockets = _tech_pockets()
    # lightening windows: everything more than 2.5 mm from a pocket, a screw and the rim
    keep = [R(a - 2.5, b - 2.5, c + 2.5, d + 2.5) for _, a, b, c, d, _, _ in pockets]
    keep += [S2.disc(x, y, 6.0) for x, y in P.TECH_SCREWS]
    free = plate.buffer(-2.5).difference(S2.unary_union(keep)).buffer(-1.0).buffer(1.0)
    holes = [g for g in (free.geoms if hasattr(free, "geoms") else [free]) if g.area > 30.0]
    out = S2.solid(plate, zb, t)
    if holes:
        out -= S2.cutter(S2.unary_union(holes), zb - 1, t + 2)
    for _, a, b, c, d, dep, opn in pockets:
        out -= box(c - a, d - b, dep + 0.01, a, b, zt - dep)                                      # the pocket the part drops into
        if opn:                                                                                    # open under a bare board: solder joints, wires
            out -= box(c - a - 2 * TECH_LEDGE, d - b - 2 * TECH_LEDGE, t + 2, a + TECH_LEDGE, b + TECH_LEDGE, zb - 1)
    for (x, y) in P.TECH_SCREWS:
        out -= clear_hole(x, y, zb, t)
    # corner posts round the speed meter: its 38 g at the crash plateau (R9) is ~39 N, more than a 1.2 mm pocket step should
    # be asked to stop on a 16 mm tall box. The lid only has to hold it down.
    g = next(pk for pk in pockets if pk[0] == "gsm020")
    _, a, b, c, d, _, _ = g
    w, L, h = 1.6, 8.0, 6.0
    for cx, sx in ((a, 1), (c, -1)):
        for cy, sy in ((b, 1), (d, -1)):
            out += box(L + w, w, h + 0.01, (cx - w) if sx > 0 else (cx - L), (cy - w) if sy > 0 else cy, zt - 0.01)
            out += box(w, L + w, h + 0.01, (cx - w) if sx > 0 else cx, (cy - w) if sy > 0 else (cy - L), zt - 0.01)
    return out


def tech_lid():
    """Cover over the tray: holds the boards and the speed meter down in their pockets, keeps wires and fingers off them, and
    has a window over the meter's display. Snaps over the tray's long edges. 1 mm PETG over the GPS antenna."""
    x0, x1 = P.TECH_TRAY_X
    zt, zb = P.TECH_TRAY_Z + P.TECH_TRAY_T, P.TECH_TRAY_Z
    h, w, skin = P.TECH_LID_H, 1.2, 1.0
    hw = TECH_HW + 0.15 + w
    R = S2.rect
    outer = S2.rounded(R(x0 - 0.15 - w, -hw, x1 + 0.15 + w, hw), r_convex=3.5)
    g = P.TECH_BOARDS["gsm020"]
    window = S2.rounded(R(g[0] + 3.0, g[1] + 3.0, g[0] + g[2] - 3.0, g[1] + g[3] - 3.0), r_convex=2.0)
    out = S2.solid(outer.difference(window), zt + h, skin)
    wall = outer.difference(S2.rounded(R(x0 - 0.15, -hw + w, x1 + 0.15, hw - w), r_convex=2.3))
    out += S2.solid(wall, zt + 2.0, h - 2.0 + 0.01)                      # wall stops 2 mm above the tray top: wires leave all round
    for sd in (1, -1):                                                   # snap tabs hook under the plate's bottom edge
        yi = sd * (TECH_HW + 0.15)
        for xa in (x0 + 14.0, (x0 + x1) / 2 - 5.0, x1 - 30.0):
            prof = S2.poly([(yi, zt + 2.0), (yi + sd * w, zt + 2.0), (yi + sd * w, zb - 1.6), (yi - sd * 0.1, zb - 1.6), (yi - sd * 0.6, zb - 0.9), (yi - sd * 0.6, zb - 0.15), (yi, zb - 0.15)])
            out += S2.solid_yz(prof, xa, 10.0)
    # hold-down posts: from the lid skin to 0.3 mm over each bare board's top face, at two opposite corners
    for n, b in P.TECH_BOARDS.items():
        if n == "gsm020":
            continue                                                     # the window's 3 mm rim holds the meter
        top = zt - b[5] + 1.6 + 0.3                                      # PCB 1.6 thick on the pocket floor
        for (px, py) in ((b[0] + 0.3, b[1] + 0.3), (b[0] + b[2] - 2.3, b[1] + b[3] - 2.3)):
            out += box(2.0, 2.0, zt + h - top + 0.01, px, py, top)
    return out


def tech_envelopes():
    """Bare boards as a 1.6 mm PCB plus a component block 2.6 mm in from the edges (the lid's posts land on the bare corners);
    the speed meter as its listed box."""
    zt = P.TECH_TRAY_Z + P.TECH_TRAY_T
    out = {}
    for n, b in P.TECH_BOARDS.items():
        z0 = zt - b[5]
        if n == "gsm020":
            out[n] = box(b[2], b[3], b[4], b[0], b[1], z0)
        else:
            out[n] = box(b[2], b[3], 1.6, b[0], b[1], z0) + box(b[2] - 5.2, b[3] - 5.2, b[4] - 1.6 + 0.01, b[0] + 2.6, b[1] + 2.6, z0 + 1.59)
    return out


@lru_cache(maxsize=1)
def deck_full():
    d = S2.solid(deck_poly(), P.DECK_Z, P.DECK_T)
    for (x, y) in P.deck_holes():
        d -= clear_hole(x, y, P.DECK_Z, P.DECK_T)
    # 1 mm step under the bellcranks (D21): deck is 2 mm thick ahead of STEER_STEP_X
    d -= box(P.STEER_STEP_X - P.DECK_X[0] + 2, 120, 2, P.DECK_X[0] - 2, -60, P.DECK_Z + P.DECK_T - 1)
    # servo-link slot (the link drops from the right bellcrank to the servo horn)
    d -= S2.cutter(S2.rounded(S2.rect(P.SERVO_ARM[0] - 4, P.SERVO_ARM[1] - 5, 18, P.SERVO_ARM[1] + 5), r_convex=4.0), P.DECK_Z - 1, 10)   # D39b: follows SERVO_ARM
    d -= S2.cutter(deck_windows(), P.DECK_Z - 1, P.DECK_T + 2)
    if P.MOTOR_DUCT:                                   # D40: M3 x 8 up through the deck into the duct tabs' inserts
        import ducts as DU
        for (x, y) in DU.DUCT_SCREWS:
            d -= clear_hole(x, y, P.DECK_Z, P.DECK_T)
    # D39: the tie-rod inner cup hangs under each crank's forward arm (Z 49-53); notch the deck along its sweep
    # (crank +-32 deg, cup 4.5 + 0.8 mm), so the deck corners clear it at full lock
    import math as _m
    px, py = P.STEER_PIVOT
    for sd in (1, -1):
        r = _m.dist((px, py), P.TIE_IN[:2])
        a0 = _m.atan2(P.TIE_IN[1] - py, P.TIE_IN[0] - px)
        arc = S2.unary_union([S2.disc(px + r * _m.cos(a0 + _m.radians(t)), sd * (py + r * _m.sin(a0 + _m.radians(t))), 5.3)
                              for t in range(-32, 33, 4)])
        d -= S2.cutter(arc, P.DECK_Z - 1, P.DECK_T + 2)
    d += rx_cradle()
    if getattr(P, "TECH_PACK", False):                 # D51: three bosses with insert pilots for the tech tray
        d += tech_bosses()
        for i, (x, y) in enumerate(P.TECH_SCREWS):        # D53: square nuts in the 4.5 mm bosses
            d = AN.anchor(d, (x, y, P.DECK_Z + P.DECK_T + P.TECH_BOSS_H), (0, 0, -1), f"deck tech boss {i + 1}")
    # shock cut-outs: each bought shock + spring passes through the deck plane outboard of the tower feet (1 mm clear)
    import running_gear as RG
    from lib import rod
    for ax in (0.0, P.WB):
        for sd in (1, -1):
            lo, hi = RG.shock_ends(ax, sd)
            d -= rod(lo, hi, P.SPRING_OD + 2.0)
    return d


def _deck_piece(i):
    return _piece(deck_full(), P.DECK_LAPS, i, P.DECK_Z, P.DECK_T, P.DECK_X[0], P.DECK_X[1])


def deck_front():
    return _deck_piece(0)


def deck_mid():
    return _deck_piece(1)


def deck_rear():
    return _deck_piece(2)


# ---------------------------------------------------------------------------------
# BMI-1 chassis side
def front_mount_holes():
    return [(-30, 10), (-30, -10), (-30, 18.5), (-30, -18.5)]   # D53: (was (-31, +-14), (-28, +-20)) spaced so four nut pockets
                                                                  # and the bumper-screw nut slots keep 1 mm walls between them


def front_mount():
    """Hook beam on the floor nose. D34: the beam is a rounded YZ profile with an arch between the bumper screws
    (was a solid block). Lips X -43..-35 at Z = BMI_F_Z..+LIP_T project forward from the beam face and open forward.
    The body is set down BMI_F_SLIDE ahead of home and pushed rearward: the carrier tongue (in the body nose,
    ahead of the front wheels) slides under the lips and stops on the beam face. Magnet pockets open downward."""
    zf = P.FLOOR_TOP
    top = P.BMI_F_Z + P.BMI_F_LIP_T
    hw = P.BMI_F_Y + 8
    arch = S2.affinity_ellipse(0.0, top, 21.0, 11.5)
    prof = S2.rounded(S2.rect(-hw, zf, hw, top).difference(arch), r_convex=2.5, r_concave=3.0)
    prof = prof.union(S2.rect(-hw + 2, zf, hw - 2, zf + 3))                  # square foot on the floor
    blk = S2.solid_yz(prof, -35.0, 10.0)
    blk += box(10, 52, 8, -35, -26, zf)                                      # base pad round the floor screws
    for s in (1, -1):
        y = s * P.BMI_F_Y
        blk += S2.solid(S2.rounded(S2.rect(-43, y - 8, -34.9, y + 8), r_convex=2.0), P.BMI_F_Z, P.BMI_F_LIP_T)
        blk -= magnet_pocket_z(P.BMI_F_X, y, P.BMI_F_Z - 0.01)                # D36 press fit
    # D53: square nuts. Bumper screws (beam front face, |y| 26) first: they are in the crash path; then the splitter tabs
    # (|y| 42), then the four floor screws
    for s in (1, -1):
        blk = AN.anchor(blk, (-35, s * 26, zf + 8), (1, 0, 0), f"front mount bumper {'L' if s > 0 else 'R'}", tip_hole=5.0)   # M3 x 25 through 15 mm of TPU: the hole runs on through the 10 mm beam
    for s in (1, -1):
        blk = AN.anchor(blk, (-35, s * 42, zf + 8), (1, 0, 0), f"front mount splitter tab {'L' if s > 0 else 'R'}")
    for (x, y) in front_mount_holes():
        blk = AN.anchor(blk, (x, y, zf), (0, 0, 1), f"front mount floor ({x}, {y})")
    return blk


BUMPER_X0 = -50.0       # D18: grows to the body nose (Phase 2: -41)
BUMPER_NOSE = True      # D43: crush block runs on to 3 mm short of the scale shell body's inner nose
BUMPER_NOSE_Z0 = 10.5   # nose part sits above the printed splitter plate (top Z 10)
# face X at each |y| (inner nose skin + 3 mm, made monotonic toward the corners; geometry probe 2026-11-16)
BUMPER_NOSE_FACE = [(0.0, -63.6), (10.0, -63.3), (14.0, -62.8), (18.0, -62.3), (22.0, -61.8), (26.0, -61.4),
                    (28.0, -58.9), (36.0, -58.6)]


def bumper():
    """TPU 95A crush block bolted to the beam front face (X -50..-35), inside the body nose.
    Print with gyroid infill (see print table): the crush plateau is set by the infill, ~1.9 kN
    over ~11 mm of stroke (rnd/tests/test_crash.py).
    D34: the face is an arc (R 164, ends 4 mm back) that follows the body nose, with a 3 mm top-front chamfer and
    rounded corners; the crush section behind the face (72 x 15) is unchanged, so the crash numbers stand."""
    zf = P.FLOOR_TOP
    d = -35 - BUMPER_X0
    Rr = 164.0
    plan = S2.rect(BUMPER_X0, -36, -35, 36).intersection(S2.Point(BUMPER_X0 + Rr, 0).buffer(Rr, quad_segs=96))   # fine arc (no facets)
    plan = S2.rounded(plan, r_convex=4.0)
    b = S2.solid(plan, zf, 15)                                     # top Z 24: body carrier tongue passes 1 mm above
    side = S2.poly([(BUMPER_X0 - 1, zf - 1), (-34, zf - 1), (-34, zf + 16), (BUMPER_X0 + 3, zf + 16), (BUMPER_X0 - 1, zf + 12)])
    b &= S2.solid_xz(side, -40, 80)
    if BUMPER_NOSE:
        # D43 (R9 9.5 -> 10 mph): the scale shell body's inner nose is 13-17 mm ahead of the X -50 face at bumper height
        # (rays from the face through the shell, panels and front carrier; X -66.6 on the centre line, -62 at
        # |y| 36), so the block grows forward to 3 mm short of the skin. The nose part sits on Z 10.5 (the printed
        # splitter plate's top is Z 10 there); the section behind X -50 is unchanged. Same gyroid, same plateau:
        # only the stroke grows.
        pts = [(x, y) for y, x in BUMPER_NOSE_FACE] + [(-49.0, BUMPER_NOSE_FACE[-1][0]), (-49.0, -BUMPER_NOSE_FACE[-1][0])] \
            + [(x, -y) for y, x in reversed(BUMPER_NOSE_FACE) if y > 0]
        nose = S2.rounded(S2.poly(pts), r_convex=4.0)
        b += S2.solid(nose, BUMPER_NOSE_Z0, zf + 15 - BUMPER_NOSE_Z0)
        d = -35 - BUMPER_NOSE_FACE[0][1]
    for s in (1, -1):
        b -= cyl_x(P.M3_CLEAR, 40, -38, s * 26, zf + 8)
        x0 = -35 - d
        b -= cyl_x(P.M3_HEAD_D + 1, 2 * (d - 4), x0, s * 26, zf + 8)   # long screw: driver access from the face
    return b


def rear_mount_holes():
    return [(P.WB + 30, 14), (P.WB + 30, -14)]


def rear_mount():
    """Cross bar on the floor tail with two posts. Post top = BMI_R_Z shoulder; a 7 mm boss passes through the body
    carrier slot; the twist key clamps on the boss top. D34: rounded bar with a centre window, posts flared at the foot."""
    zb = P.FLOOR_TOP + 3.0           # sits on the 3 mm rear spacer (cad/aero.py, D53; the GT-1 diffuser flange until D37)
    hw = P.BMI_R_Y + 6
    plan = S2.rounded(S2.rect(P.BMI_R_X - 7, -hw, P.BMI_R_X + 7, hw), r_convex=5.0)
    plan = plan.difference(S2.rounded(S2.rect(P.BMI_R_X - 3.5, -7, P.BMI_R_X + 3.5, 7), r_convex=3.0))
    bar = S2.solid(plan, zb, 6)
    for s in (1, -1):
        y = s * P.BMI_R_Y
        bar += cyl_z(12.5, P.BMI_R_Z - zb, P.BMI_R_X, y, zb)                     # D53: 12.5 (was 11): room for the twist-key square nut
        bar += cyl_z(15, 3, P.BMI_R_X, y, zb + 5.99)                         # flared foot
        bar += cyl_z(7, P.CARRIER_T, P.BMI_R_X, y, P.BMI_R_Z)
        bar = AN.anchor(bar, (P.BMI_R_X, y, P.BMI_R_Z + P.CARRIER_T), (0, 0, -1), f"rear mount twist-key post {'L' if s > 0 else 'R'}")   # D53
        # magnet pocket in a side ear at the shoulder (opens upward)
        bar += S2.solid(S2.rounded(S2.rect(P.BMI_R_X + 6, y - 6, P.BMI_R_X + 18, y + 6), r_convex=3.0), P.BMI_R_Z - 4, 4)
        bar += cbox(6, 8, P.BMI_R_Z - 4 - zb, P.BMI_R_X + 9, y, zb)
        bar -= magnet_pocket_z(P.BMI_R_X + 14, y, P.BMI_R_Z - P.MAGNET_T + 0.01)   # D36 press fit
    for (x, y) in rear_mount_holes() + diffuser_holes():    # D53: all 4 come up through the floor and the rear spacer
        bar = AN.anchor(bar, (x, y, zb), (0, 0, 1), f"rear mount floor ({x}, {y})")
    return bar


def twist_key():
    """Quarter-turn key: 22 x 6 bar + grip, M3 screw into the post boss insert."""
    zt = P.BMI_R_Z + P.CARRIER_T
    k = cbox(22, 6, 3, 0, 0, zt) + cyl_z(10, 6, 0, 0, zt + 3) + cbox(14, 3, 4, 0, 0, zt + 9)
    k -= clear_hole(0, 0, zt - 1, 20)
    k -= cyl_z(P.M3_HEAD_D, 20, 0, 0, zt + 5)
    return k


def diffuser_holes():
    # The rear mount's outer floor screws (the name is from the GT-1 diffuser flange they held until D37). D53: x moved
    # 291 -> 293 (the inner pair's x): at 291 the nut sat 1.5 mm from the bar's front face and no square nut fitted (the
    # anchor fell back to an insert); 293 keeps them inside the floor (ends at TUB_X1 298) and the rear spacer.
    return [(P.WB + 30, 24), (P.WB + 30, -24)]


PEG_D, PEG_H, PEG_HOLE = 2.8, 2.5, 2.5      # D36 pad pegs: TPU pad hole 0.3 under the peg -> stays on by itself


def pad_pegs():
    """Floor pegs: battery pads (100 long, along X, 2 rows under the pack) and ESC pads (32 long, 2 rows)."""
    bx, by, _, bl, bw, _ = P.BATTERY_BOX
    ex, ey, _, el, ew, _ = P.ESC_BOX
    bc, ec = bx + bl / 2, ex + el / 2
    out = [(bc + d, y) for y in (by + 6, by + bw - 6) for d in (-45, 45)]
    out += [(ec + d, y) for y in (ey + 6, ey + ew - 6) for d in (-10, 10)]
    return out


def pad(length, width=6.0, t=3.0):
    """TPU pad with two holes that press over the floor pegs (battery pads +-45, ESC pads +-10 from centre)."""
    off = 45.0 if length > 60 else 10.0
    p = box(length, width, t, 0, 0, 0)
    for d in (-off, off):
        p -= cyl_z(PEG_HOLE, t + 1, length / 2 + d, width / 2, -0.5)
    return p


# ---------------------------------------------------------------------------------
# reference envelopes for the fit check (not exported); render_platform.py draws detailed versions
def heatsink():
    """D34 bought 36 mm fan heat sink: finned sleeve over the top three quarters of the can + twin fans on top."""
    x, z = P.MOTOR_X, P.LAYSHAFT_Z
    yc = P.MOTOR_Y0 - P.MOTOR_L + P.HEATSINK_L / 2                           # flush with the can's outer end
    sleeve = cyl_y(P.HEATSINK_D, P.HEATSINK_L, x, yc, z)
    sleeve &= box(80, 80, 80, x - 40, yc - 40, z - 12)                     # open underneath (plate / floor side)
    fx, fy, fz = P.FAN_BOX
    fans = cbox(fx, fy, fz, x, yc, z + P.HEATSINK_D / 2 - 1)
    return sleeve + fans


def electronics():
    bx = lambda b: box(b[3], b[4], b[5], b[0], b[1], b[2])  # noqa: E731
    motor = cyl_y(P.MOTOR_D, P.MOTOR_L, P.MOTOR_X, P.MOTOR_Y0 - P.MOTOR_L / 2, P.LAYSHAFT_Z)
    return {"battery": bx(P.BATTERY_BOX), "esc": bx(P.ESC_BOX), "servo": bx(P.SERVO_BOX),
            "motor": motor, "heatsink": heatsink(), "receiver": bx(P.RX_BOX),
            **(dict(tech_envelopes(), current_sensor=bx(P.TECH_SENSOR_BOX)) if getattr(P, "TECH_PACK", False) else {})}
