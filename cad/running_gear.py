"""Option B running gear (Stage 3, decision D15): everything printed between the tub and the
wheels, plus envelopes of the bought power-path parts for the fit check.

Printed designs (one design is used at several corners wherever possible, so a spares box
needs few different parts):
  bulkhead_rL/rR (D57d; bulkhead_half x2 before) + bulkhead_fL/fR (D46: front diff seat offset for a whole-tooth belt)  cheek with the diff bearing seat + lower-arm hinge lugs + upper-link tab
  lower_arm      x4  same at every corner: X-pin hole (rear upright) + vertical ball-stud hole (front knuckle)
  upper_link     x4  same at every corner, same two-hole trick
  upright_rear   x2  fixed rear hub carrier, two 10x15 bearings
  knuckle_L / _R x1  front steering knuckles (mirror pair) on M3 ball studs
  (shocks)        D33: BOUGHT 1/10 touring 55 mm oil shocks; only the droop rings on their shafts are printed
  tower_front    x1  on the deck top;  tower_rear x1 the same part (D34: the deck now runs over the rear bulkheads)
  bellcrank_L/_R x1  steering bellcranks on the deck top
  drag_link, tie_rod x2, servo_link    printed links with M3 ball-stud ends
  motor_plate    x1  holds the motor (4 standoff bosses) and the layshaft right bearing
  lay_holder     x1  layshaft left bearing block
  lay_drum       x1  spur hub + rear and front 19T S3M pulleys in ONE printed piece
  wheel_hex      x4  12 mm hex with a drive-pin slot (wear part)

Frame: vehicle coordinates (params.py). Parts are built at the LEFT side of the FRONT axle (or
where they sit) and placed elsewhere by `place()`; designs are symmetric about their own XZ
plane where marked, so a 180 deg turn places them on the right."""
import math
from build123d import Pos, Rot, Polygon, Circle, extrude, make_face, Polyline, Plane, Cylinder, Box
import params as P
from lib import box, cbox, cyl_x, cyl_y, cyl_z, insert_hole, clear_hole, crush_seat_y, rod
import shape2d as S2
import anchors as AN

PIN = 3.2            # M3 bolt used as a hinge pin: printed hole size (tolerance ladder tunes it)
BALL_HOLE = 2.6      # tap-size hole for an M3 ball stud
ZF = P.FLOOR_TOP


def pitch_r(teeth):
    return teeth * P.PULLEY_PITCH / (2 * math.pi)


# =====================================================================================
# D46: belt lengths. Stock S3M loops come in whole teeth and the layshaft is fixed, so the FRONT diff seat moves the
# few tenths needed for a whole-tooth front belt (no tensioner); the rear belt already lands on a whole tooth (23T).
def belt_len(x1, z1, t1, x2, z2, t2):
    """S3M pitch length (mm) of an open belt over pulleys of t1, t2 teeth at (x1, z1), (x2, z2)."""
    r1, r2 = pitch_r(t1), pitch_r(t2)
    c = math.hypot(x2 - x1, z2 - z1); d = abs(r1 - r2); a = math.asin(d / c)
    return 2 * math.sqrt(c * c - d * d) + math.pi * (r1 + r2) + 2 * a * d


def front_diff_dx():
    """x shift of the front diff (mm, + = rearward) that puts the front belt on the nearest whole tooth."""
    L0 = belt_len(0.0, P.DIFF_Z, P.DIFF_PULLEY_T, P.LAYSHAFT_X, P.LAYSHAFT_Z, P.LAY_PULLEY_T)
    target = round(L0 / 3.0) * 3.0
    dx = 0.0
    for _ in range(30):                       # Newton on dL/dx ~ -2
        L = belt_len(dx, P.DIFF_Z, P.DIFF_PULLEY_T, P.LAYSHAFT_X, P.LAYSHAFT_Z, P.LAY_PULLEY_T)
        dx += (L - target) / 2.0
    return round(dx, 2)


def belt_fit():
    """Both belts: (teeth, nearest stock teeth, error mm) at the design geometry."""
    dx = front_diff_dx()
    out = {}
    for tag, args in (("front", (dx, P.DIFF_Z, P.DIFF_PULLEY_T, P.LAYSHAFT_X, P.LAYSHAFT_Z, P.LAY_PULLEY_T)),
                      ("rear", (P.LAYSHAFT_X, P.LAYSHAFT_Z, P.LAY_PULLEY_T, P.WB, P.DIFF_Z, P.DIFF_PULLEY_T))):
        L = belt_len(*args); n = round(L / 3.0)
        out[tag] = dict(L=round(L, 2), teeth=round(L / 3.0, 3), stock=n, err_mm=round(L - 3.0 * n, 2))
    out["front_diff_dx"] = dx
    return out


# bulkhead half (left side shown; right side = same part turned 180 deg about Z)
def _bulkhead_body(dx=0.0, hw=15.0, z_wide=None):
    """Cheek + lugs + gussets + link tab + bearing seat, no threaded points (shared by the D34 one-piece bulkhead and
    the D57 saddle/cap pair). D57b z_wide: the cheek is 15 mm half width below z_wide and hw above it."""
    y0, y1 = P.CHEEK_Y
    R = S2.rect
    if z_wide is None:
        prof = S2.rounded(R(-hw, ZF, hw, P.DECK_Z), r_convex=4.0)
    else:
        prof = S2.rounded(S2.rounded(R(-P.BH_LOW_HW, ZF, P.BH_LOW_HW, P.DECK_Z), r_convex=4.0)
                          .union(S2.rounded(R(-hw, z_wide, hw, P.DECK_Z), r_convex=1.0)), r_concave=1.0)
    prof = prof.difference(S2.rounded(R(-7, P.DIFF_Z + 11, 7, P.DIFF_Z + 17), r_convex=2.5))     # over the bearing
    prof = prof.difference(S2.rounded(R(-5, ZF + 3, 5, P.DIFF_Z - P.DIFF_BRG[1] / 2 - 2.8), r_convex=2.0))   # under it
    prof = S2.rounded(prof.union(R(-15, ZF, 15, ZF + 2)), r_concave=0.0)                     # flat foot on the floor
    c = S2.solid_xz(prof, y0, y1 - y0)
    c -= crush_seat_y(P.DIFF_BRG[1], P.DIFF_BRG[2], dx, y0, P.DIFF_Z, +1)    # diff bearing (inner face); D46 dx: front belt
    c -= cyl_y(P.DIFF_BRG[0] + 1.5, 40, dx, y1, P.DIFF_Z)                   # outdrive passes through
    # lower-arm hinge lugs (pin along X), with floor screws, braced up to the cheek
    for xa, xb in ((-16.5, -8), (8, 16.5)):      # D53: 8.5 wide (was 7, outer edge 15) so the floor-screw nut keeps 1.3 mm walls
        c += S2.solid(S2.rounded(R(xa, y1 - 1, xb, 44), r_convex=1.5), ZF, 12.5)   # D53: 12.5 tall (was 10): the floor-screw nut sits above the hinge pin
        xg = xa + 2 if xa < 0 else xb - 5
        c += S2.solid_yz(S2.poly([(y1 - 0.5, ZF + 9.9), (y1 - 0.5, ZF + 21), (41.5, ZF + 9.9)]), xg, 3.0)
    c -= cyl_x(PIN, 40, 0, P.ARM_PIN_Y, P.ARM_PIN_Z)
    # upper-link tab: fork prongs either side of the link tongue (X +-3)
    for xa, xb in ((-8, -3.5), (3.5, 8)):
        c += S2.solid(S2.rounded(R(xa, y1 - 1, xb, y1 + 6), r_convex=1.0), P.LINK_IN[1] - 4, 8)   # D30: tab Z 40..48
    c -= cyl_x(PIN, 20, 0, P.LINK_IN[0], P.LINK_IN[1])
    return c


def _floor_anchors(c):
    # D53: captive nuts (cad/anchors.py) for the floor screws (cheek + lugs)
    for (x, y) in P.bulkhead_floor_holes(0.0):
        if y > 0:
            c = AN.anchor(c, (x, y, ZF), (0, 0, 1), f"bulkhead floor ({x:+.1f}, {y:.0f})")
    return c


def bulkhead_half(dx=0.0, front=False, side=1):
    """D34: the cheek is a rounded XZ profile (r 4 corners) with radiused windows above and below the diff bearing;
    the hinge lugs are rounded and braced to the cheek by 3 mm gussets (was a stack of raw boxes). Interfaces unchanged.
    D57 (P.TOP_LOAD): this is the lower SADDLE; bulkhead_cap() is the part above it."""
    if getattr(P, "TOP_LOAD", False):
        return bulkhead_saddle(dx, front, side)
    c = _floor_anchors(_bulkhead_body(dx))
    for dx_ in (-10, 10):
        c = AN.anchor(c, (dx_, 27.0, P.DECK_Z), (0, 0, -1), f"bulkhead deck ({dx_:+d}, 27)")
    return c


def _local_slot(front, side):
    """D57d: the U-slot edges in this part's own x (the right-hand part is the left one's frame turned 180 deg about Z)."""
    lo, hi = P.bh_slot(0.0 if front else P.WB)
    return (lo, hi) if side > 0 else (-hi, -lo)


def _local_screws(side, front=True):
    """D57d: the two cap-screw x positions in this part's own frame (vehicle: forward -13.90, aft +12.90 from the axle).
    D58.2: the rear axle has its own pair (params.BH_SCREW_X_R; the same numbers on the 263 mm car)."""
    return tuple(side * x for x in (P.BH_SCREW_X if front else P.BH_SCREW_X_R))


def _cap_zone(dx, grow=0.0, front=False, side=1):
    """D57: the bearing cap's volume: everything above the post tops + the plug that fills the U-slot down to the diff axis.
    grow widens the plug in X only (the saddle's slot clearance); the horizontal faces stay shared. D57d: the slot is
    asymmetric (drift room only toward the layshaft) and already includes the front bearing's offset, so dx is not used."""
    y0 = P.CHEEK_Y[0] - 5
    lo, hi = _local_slot(front, side)
    above = box(80, 40, P.DECK_Z + 5 - P.BH_POST_Z, -40, y0, P.BH_POST_Z)
    plug = box(hi - lo + 2 * grow, 40, P.BH_POST_Z - P.DIFF_Z + 0.01, lo - grow, y0, P.DIFF_Z)
    return above + plug


def bulkhead_saddle(dx=0.0, front=False, side=1):
    """D57 lower saddle: floor, arm lugs, gussets, the lower half of the diff bearing seat, and two posts either side of an
    open U-slot (BH_SLOT_HW, wide enough for the bearing's belt arc). Captive hex nuts in the post tops take the deck screws
    that hold the cap; the floor screws are unchanged."""
    c = _bulkhead_body(dx, P.BH_HW, P.BH_STEP_Z)
    y1 = P.CHEEK_Y[1]
    edges = _local_slot(front, side)
    for sx, e in ((-1, edges[0]), (1, edges[1])):   # posts 1.2 mm thicker outboard, so the washer + nut pocket fits as drawn (its slot
        xa, xb = sorted((e + sx * P.BH_CLR, sx * P.BH_HW))                  # opens inboard; nothing may grow into the diff side)
        c += S2.solid(S2.rounded(S2.rect(xa, y1 - 1.0, xb, y1 + P.BH_POST_PAD), r_convex=1.0), P.BH_STEP_Z, P.BH_POST_Z - P.BH_STEP_Z)
    c = c - _cap_zone(dx, P.BH_CLR, front, side)
    c = _floor_anchors(c)
    for xs in _local_screws(side, front):
        c = AN.anchor(c, (xs, P.BH_SCREW_Y, P.BH_POST_Z), (0, 0, -1), f"bulkhead deck ({xs:+.2f}, {P.BH_SCREW_Y:g})",
                      t_try=(2.5, 3.0, 3.5),   # shallow: a 7 mm-deep nut would need an M3 x 35 (BH_POST_Z is set for M3 x 30)
                      keep=box(80, 40, 60, -40, P.CHEEK_Y[0] - 40, 0)    # no pad growth past the cheek's inner face (the diff is there)
                      + box(40, 80, P.BH_STEP_Z + 20, P.BH_LOW_HW, -40, -20)      # D57b: nor outboard below BH_STEP_Z (shell floor)
                      + box(40, 80, P.BH_STEP_Z + 20, -40 - P.BH_LOW_HW, -40, -20))
    return c


def bulkhead_cap(dx=0.0, front=False, side=1):
    """D57 bearing cap: the plug (upper half of the diff bearing seat and of the outdrive hole) + a bridge on the post tops
    with the upper-link tab. No screws of its own: the two deck screws pass through it into the saddle's post nuts, so once
    the deck is off the cap lifts away (pull the upper-link pin first) and the diff lifts out on its belt arc."""
    c = _bulkhead_body(dx, P.BH_HW, P.BH_STEP_Z) & _cap_zone(dx, 0.0, front, side)
    y0, y1 = P.CHEEK_Y
    c &= S2.solid_xz(S2.rounded(S2.rect(-P.BH_BRIDGE_HW, P.DIFF_Z - 1, P.BH_BRIDGE_HW, P.DECK_Z), r_convex=3.0), y0 - 5, 50)
    for xs in _local_screws(side, front):
        c -= clear_hole(xs, P.BH_SCREW_Y, P.BH_POST_Z, P.DECK_Z - P.BH_POST_Z)
    for sx in (1, -1):                       # spring clearance: shocks sit behind the axle; the right-hand cap is this one turned
        lo, hi = shock_ends(0.0, 1)          # 180 deg, so its spring is at local -x: clear both sides
        lo, hi = (sx * lo[0], lo[1], lo[2]), (sx * hi[0], hi[1], hi[2])
        c -= rod(lo, hi, P.SPRING_OD + 2.0)
    return c


# =====================================================================================
def lower_arm():
    """Inner hinge at ARM_PIN_Y between the lugs; outer tongue carries BOTH an X-pin hole (rear
    upright fork) and a vertical ball-stud hole (front knuckle). Shock ears both sides.
    D34: the body is a tapered, rounded plan (15 wide at the hinge -> 8 at the tongue) instead of two boxes."""
    zc = P.ARM_PIN_Z
    plan = S2.rounded(S2.poly([(-7.5, 34), (7.5, 34), (7.5, 45), (4, 52), (4, 66), (-4, 66), (-4, 52), (-7.5, 45)]),
                      r_convex=1.5, r_concave=5.0)
    a = S2.solid(plan, zc - 4, 8)
    a += cyl_x(9, 15, 0, P.ARM_PIN_Y, zc)                                     # hinge boss
    for s in (1, -1):        # shock ears (D30): outboard, Y 46..59.5, beside the rear fork prongs (X 4.5..9.5)
        xe = 10.0 if s > 0 else -16.5
        a += S2.solid(S2.rounded(S2.rect(xe, 46, xe + 6.5, 59.5), r_convex=2.0), zc - 2, 8)
        a += box(2.6, 6, 8, 7.45 if s > 0 else -10.05, 46, zc - 2)          # bridge to the arm body, 2 mm short of the prongs
    a -= cyl_x(PIN, 20, 0, P.ARM_PIN_Y, zc)
    a -= cyl_x(PIN, 12, 0, P.ARM_OUT_Y, zc)                                   # rear: pin to upright fork
    a -= cyl_z(BALL_HOLE, 20, 0, P.KINGPIN_Y, zc - 10)                       # front: ball stud
    a -= cyl_x(P.M3_CLEAR, 40, 0, P.SHOCK_LOW[0], P.SHOCK_LOW[1])            # shock eye screw
    return a


def upper_link():
    """D30: inner pin LINK_IN sits 4 mm below the outer pins, so the link is inclined (camber gain, RC up).
    Bar from the inner boss to the outer block; the outer block carries the rear pin and the front ball stud."""
    z = P.LINK_Z
    yi, zi = P.LINK_IN
    ye, ze = 52.0, z - 0.5
    d = math.hypot(ye - yi, ze - zi)
    ny, nz = -(ze - zi) / d * 3.0, (ye - yi) / d * 3.0                    # half-thickness normal: flat-sided bar (prints on its side)
    bar = Plane.YZ * Polygon((yi + ny, zi + nz), (ye + ny, ze + nz), (ye - ny, ze - nz), (yi - ny, zi - nz))
    l = Pos(3, 0, 0) * extrude(bar, 6) + box(6, 65 - 50, 6.5, -3, 50, z - 3)       # Plane.YZ extrudes along -X here
    l += cyl_x(7, 6, 0, yi, zi)
    l -= cyl_x(PIN, 10, 0, yi, zi)                                            # inner pin (cheek tab)
    l -= cyl_x(PIN, 10, 0, 56.0, z)                                           # rear: pin to upright fork
    l -= cyl_z(BALL_HOLE, 20, 0, P.KINGPIN_Y, z - 10)                        # front: ball stud
    l -= cyl_z(10.0, 1.2, 0, P.KINGPIN_Y, z - 3 - 0.01)                      # D30: relief over the knuckle's top ball boss
    l -= box(7, 4.1, 0.8 + 0.01, -3.5, 49.9, z - 3 - 0.01)                   # D30: 0.8 mm relief over the rear upright's hub at full bump
    return l


# =====================================================================================
def _hub_body():
    """Bearing housing shared by the rear upright and the front knuckle: X +-9.5, Y 54..66."""
    zc = P.TIRE_D / 2
    h = S2.solid_xz(S2.rounded(S2.rect(-9.5, zc - 10.5, 9.5, zc + 10.5), r_convex=3.0), 54, 12)   # D34: rounded housing
    b, bi = P.AXLE_BRG, P.AXLE_BRG_IN     # D50: 5 x 10 x 4 outboard (Y 66), 5 x 10 x 3 inboard (Y 54), as the driveshaft's maker draws it
    h -= crush_seat_y(bi[1], bi[2], 0, 54, zc, +1)
    h -= crush_seat_y(b[1], b[2], 0, 66, zc, -1)
    h -= cyl_y(P.AXLE_BORE, 20, 0, 60, zc)
    return h


def upright_rear():
    zc = P.TIRE_D / 2
    u = _hub_body()
    for s in (1, -1):
        xa = 4.5 if s > 0 else -9.5
        u += box(5, 8, zc - 10.5 - (ZF + 1), xa, 54, ZF + 1)                 # lower fork prongs
        xb = 3.5 if s > 0 else -8
        u += box(4.5, 6, P.LINK_Z + 4 - (zc + 10.5), xb, 53, zc + 10.5)      # upper fork prongs
    u -= cyl_x(PIN, 24, 0, P.ARM_OUT_Y, P.ARM_PIN_Z)
    u -= cyl_x(PIN, 24, 0, 56.0, P.LINK_Z)
    return u


def knuckle(side=1):
    """Front knuckle on two M3 ball studs (bottom: lower arm, top: upper link) at KINGPIN_Y.
    Steering arm reaches forward to STEER_ARM_X. side=+1 left, -1 right (mirror)."""
    zc = P.TIRE_D / 2
    k = _hub_body()
    k += cyl_z(9, 3, 0, P.KINGPIN_Y, zc - 13.5)                              # bottom ball cup boss
    k += cyl_z(9, 2.5, 0, P.KINGPIN_Y, zc + 10.5)                            # top ball cup boss
    k -= cyl_z(6.2, 5, 0, P.KINGPIN_Y, zc - 13.6)                            # ball cup sockets (6 mm ball)
    k -= cyl_z(6.2, 5, 0, P.KINGPIN_Y, zc + 8.1)
    # steering arm forward, top of the knuckle
    k += box(abs(P.STEER_ARM_X) - 9.5 + 3, 6, 4, P.STEER_ARM_X - 3, 51, zc + 6.5)
    # D39: a post (D39b: 10 x 11) on the arm end carries the tie-rod ball up to TIE_OUT_Z (bump steer fix); the ball stud
    # screws down into its top (pad top = ball centre - 2.5 + 4, as the old arm)
    pz = P.TIE_OUT_Z - 2.5
    pxs, pys, py0 = P.KNUCKLE_POST
    k += box(pxs, pys, pz + 4 - (zc + 6.5), P.STEER_ARM_X - pxs / 2, py0, zc + 6.5)
    k -= cyl_z(BALL_HOLE, 10, P.STEER_ARM_X, 54, pz - 1.5 + 4 - 8.5)
    if side < 0:
        k = k.mirror(Plane.XZ)
    return k


# =====================================================================================
def shock_ends(axle_x, side):
    """D33 bought shock: lower eye on the arm ear (SHOCK_X), upper eye on a stand-off screw SHOCK_TOP_X behind
    the tower plate, so the spring clears the plate face."""
    yl, zl = P.SHOCK_LOW
    yt, zt = P.SHOCK_TOP
    return (axle_x + P.SHOCK_X, side * yl, zl), (axle_x + P.SHOCK_TOP_X, side * yt, zt)


def shock_installed(axle_x, side):
    """Envelope of the bought 55 mm touring shock at static length (fit check / renders): rod ends SHOCK_END_D,
    spring OD over the body from 5 mm above the lower eye to 6 mm below the upper eye."""
    lo, hi = shock_ends(axle_x, side)
    L = math.dist(lo, hi)
    d = [(b - a) / L for a, b in zip(lo, hi)]
    at = lambda p, t: tuple(c + t * dc for c, dc in zip(p, d))  # noqa: E731
    s = rod(lo, at(lo, 5.0), P.SHOCK_END_D) + rod(at(hi, -6.0), hi, P.SHOCK_END_D)
    s += rod(at(lo, 5.0), at(hi, -6.0), P.SPRING_OD)
    return s


def droop_spacer(t=0.5):
    """D30/D33: ring on the bought shock's shaft inside the body; a stack of them limits extension (droop).
    Front: DROOP_FRONT = 0.3 mm of wheel droop past static (nose can't rise under aero lift). Bore 3.7 fits a 3 or 3.5 mm shaft."""
    return cyl_z(6.0, t, 0, 0, 0) - cyl_z(3.7, t + 2, 0, 0, -1)


def droop_stack(axle):
    """D33: droop-ring stack (mm) that makes the bought shock top out at DROOP_FRONT / DROOP_REAR of wheel droop:
    SHOCK_EXT - (static eye-to-eye + droop x motion ratio). MR from rnd/suspension/current_geometry.json."""
    import json, os
    lo, hi = shock_ends(0.0, 1)
    static = math.dist(lo, hi)
    gp = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "rnd", "suspension", "current_geometry.json")
    mr = json.load(open(gp))[axle]["motion_ratio"] if os.path.exists(gp) else {"front": 0.63, "rear": 0.73}[axle]
    droop = P.DROOP_FRONT if axle == "front" else P.DROOP_REAR
    return P.SHOCK_EXT - (static + droop * mr)


def tower(z_base):
    """D34 shock tower, the SAME part front and rear (both now sit on the full-length deck top): a 6 mm plate drawn
    as a rounded YZ profile, hull of the two shock-eye ears and the deck foot, with an arch for the servo link and
    a radiused weight window; L-feet with gussets bolt through the deck into the bulkhead inserts. The bought shock's
    upper eye sits on an M3 screw behind the plate; a printed 3.5 mm boss shortens the bare screw (D33 stand-off)."""
    px = P.SHOCK_TOP_X - P.SPRING_OD / 2 - 0.5 - 6.0                        # D33: plate 6 thick, 0.5 mm off the spring
    yt, zt = P.SHOCK_TOP
    R = S2.rect
    ears = S2.unary_union([S2.disc(s * yt, zt, 5.0) for s in (1, -1)] + [R(-33, z_base, 33, z_base + 4)])
    prof = ears.convex_hull
    prof = prof.difference(S2.affinity_ellipse(0.0, z_base - 0.5, 17.0, 5.0))                 # servo-link arch
    prof = prof.difference(S2.rounded(R(-22, z_base + 6.5, 22, zt - 1.0), r_convex=2.5))       # weight window
    prof = S2.rounded(prof, r_convex=1.5, r_concave=2.0)
    t = S2.solid_yz(prof, px, 6.0)
    for s in (1, -1):
        y = s * P.SHOCK_TOP[0]
        bx = P.BH_SCREW_X[1] if getattr(P, "TOP_LOAD", False) else 10              # D57d: feet on the aft cap screws
        t += S2.solid(S2.rounded(R(px, s * 20 - (11 if s < 0 else 0), max(14, bx + 2.8), s * 20 + (11 if s > 0 else 0)), r_convex=2.0),
                      z_base, 3)                                                                 # foot on the deck
        t += S2.solid_xz(S2.poly([(px + 5.9, z_base + 2.9), (13.5, z_base + 2.9), (px + 5.9, z_base + 9)]),
                         s * 21 - (2.5 if s > 0 else 0.5), 3.0)                                  # gusset
        t += cyl_x(8.0, 3.5, px + 6.0 + 1.75, y, zt)                                            # stand-off boss
        t -= cyl_x(P.M3_CLEAR, 40, P.SHOCK_X - 6, y, zt)
        t -= clear_hole(bx, s * (P.BH_SCREW_Y if getattr(P, "TOP_LOAD", False) else 27.0), z_base, 20)
        lo, hi = shock_ends(0.0, s)                                          # D33: feet notched round the spring
        L = math.dist(lo, hi)
        d = [(b - a) / L for a, b in zip(lo, hi)]
        t -= rod(tuple(c + 3 * dc for c, dc in zip(lo, d)), tuple(c - 6 * dc for c, dc in zip(hi, d)), P.SPRING_OD + 1.0)
    return t


def tower_front():
    return tower(P.DECK_Z + P.DECK_T)


def tower_rear():
    return tower(P.DECK_Z + P.DECK_T)            # D34: rear tower sits on the deck too -> same part as the front


# =====================================================================================
# steering (bellcranks on the deck top, drag link ahead of them, tie rods down to the knuckles)
def bellcrank(side=1):
    px, py = P.STEER_PIVOT
    z0, z1 = P.CRANK_Z
    y = side * py
    pts = [(P.TIE_IN[0], side * P.TIE_IN[1]), (px - DRAG_ARM, y)]          # D39: tie-rod arm points forward
    if side < 0:
        pts.append(P.SERVO_ARM)                                                # servo arm (right crank)
    top_load = getattr(P, "TOP_LOAD", False)
    c = cyl_z(9, (P.PIVOT_SPACER[1] - 0.4) if top_load else (z1 - z0), px, y, z0)   # D57: hub 0.4 mm shorter than its spacer
    for (x, yy) in pts:
        c += rod((px, y, z0 + 1.5), (x, yy, z0 + 1.5), 6) & box(60, 60, z1 - z0, px - 30, y - 30, z0)
        c += cyl_z(7, z1 - z0, x, yy, z0)
        c -= cyl_z(BALL_HOLE, 10, x, yy, z0 - 1)
    c -= cyl_z(P.PIVOT_SPACER[0] + 0.2 if top_load else P.M3_CLEAR, 10, px, y, z0 - 1)   # D57: turns on the spacer
    return c


def link_flat(length, d=5.0):
    """Print version of a link: flat bar with two ball-cup ends, lying on the bed."""
    l = box(length, d, d - 1, 0, -d / 2, 0)
    for x in (0, length):
        l += cyl_z(9, d - 1, x, 0, 0)
        l -= cyl_z(6.2, d, x, 0, -0.5)
    return l


LINKS = {"drag_link": 2 * P.STEER_PIVOT[1],
         "tie_rod": math.dist(P.TIE_IN, (P.STEER_ARM_X, 54.0, P.TIE_OUT_Z)),
         "servo_link": math.dist((*P.SERVO_ARM, P.CRANK_Z[1] + 2.5), (46.0, -19.0, 31.0))}


def _link(p1, p2, d=4.0):                 # d = printed link thickness (link_flat d - 1)
    l = rod(p1, p2, d)
    for p in (p1, p2):
        l += Pos(*p) * Cylinder(4.5, d)                                       # ball-cup ends
    return l


def drag_link():
    px, py = P.STEER_PIVOT
    return _link((px - DRAG_ARM, py, TOP), (px - DRAG_ARM, -py, TOP))


TOP = P.CRANK_Z[1] + 2.5          # links ride on top of the cranks (ball studs point up): 0.5 mm gap under a 4 mm link
DRAG_ARM = 5.0                    # crank arm to the drag link (was 6; D21: 1 mm clear of the body nose)


def tie_rod(side=1):
    """D39: inner ball hangs under the crank's forward arm, outer ball on the knuckle post: the rod lies along the
    suspension's instant-centre line, so bump barely steers the wheel."""
    x, y, z = P.TIE_IN
    return _link((x, side * y, z), (P.STEER_ARM_X, side * 54.0, P.TIE_OUT_Z))


def servo_link():
    """Right bellcrank servo arm -> servo horn (servo lies on its side, shaft +Y).
    The horn tip position is [unverified] until the servo is in hand (gauge-free: set by the
    printed link length, two lengths printed)."""
    return _link((*P.SERVO_ARM, TOP), (46.0, -19.0, 31.0), 4.5)


# =====================================================================================
# layshaft
def lay_drum(teeth=None):
    """Spur hub flange + rear pulley + front pulley, one printed piece. D50: it turns on two MR105 pressed into its ends,
    on the fixed 5 mm shoulder screw (params.LAY_AXLE); it used to be clamped on a turning M5 bolt.
    S3M teeth approximated by round grooves (tooth depth 1.14 mm, Pfeifer chart).
    D46: teeth = params.LAY_PULLEY_T (23T fitted, 101.6 mph); lay_drum_22t is the printed fallback (98.6 mph)."""
    x, z = P.LAYSHAFT_X, P.LAYSHAFT_Z
    nt = teeth or P.LAY_PULLEY_T
    pr = pitch_r(nt)
    od = pr - 0.38
    y0 = P.SPUR_Y[1]
    d = cyl_y(26, 1.5, x, y0 + 0.75, z)                                       # spur flange
    for k in range(3):
        a = 2 * math.pi * k / 3
        d -= cyl_y(P.M3_CLEAR - 0.6, 6, x + 8 * math.cos(a), y0 + 1, z + 8 * math.sin(a))   # self-tap M3
    for yc in (P.RB_Y, P.FB_Y):
        w = P.BELT_W + 0.5
        p = cyl_y(2 * od, w, x, yc, z)
        for k in range(nt):
            a = 2 * math.pi * (k + 0.5) / nt
            p -= cyl_y(1.9, w + 1, x + (od + 0.2) * math.cos(a), yc, z + (od + 0.2) * math.sin(a))
        d += p
        for s in (-1, 1):                                                     # belt flanges
            d += cyl_y(2 * od + 4, 0.8, x, yc + s * (w / 2 + 0.4), z)
    y1 = P.LAY_AXLE_END + 0.2                                                 # drum end, 0.6 mm short of the holder face
    d += cyl_y(14, y1 - y0, x, (y0 + y1) / 2, z)                              # core (D50: 14 mm, was 10, to house the bearings)
    d -= cyl_y(8.0, 60, x, 0, z)                                              # bore: clear of the fixed axle and the inner rings
    d -= crush_seat_y(P.LAY_BRG[1], P.LAY_BRG[2], x, y0, z, +1)               # bearing A, in from the spur-flange face
    yb_in = P.LAY_AXLE_END - 0.1 - P.LAY_BRG[2]                               # bearing B: its inner ring ends 0.1 mm short of the washer
    d -= crush_seat_y(P.LAY_BRG[1], y1 - yb_in, x, y1, z, -1)
    return d


def lay_spacer_head():
    """D50: ring between the shoulder screw's head and the motor plate's outer face."""
    y_head = P.LAY_AXLE_END - P.LAY_AXLE["shoulder"]
    L = P.MOTOR_PLATE_Y[0] - y_head - 0.1
    return cyl_y(9.0, L, P.LAYSHAFT_X, P.MOTOR_PLATE_Y[0] - L / 2, P.LAYSHAFT_Z) - cyl_y(P.LAY_AXLE["d"] + 0.3, 40, P.LAYSHAFT_X, 0, P.LAYSHAFT_Z)


def lay_spacer_in():
    """D50: thin ring on the axle between the motor plate's inner face and bearing A's inner ring (it passes through the spur's
    centre hole, which must be at least 7.2 mm [unverified])."""
    L = P.SPUR_Y[1] - P.MOTOR_PLATE_Y[1] - 0.1
    return cyl_y(6.9, L, P.LAYSHAFT_X, P.MOTOR_PLATE_Y[1] + 0.05 + L / 2, P.LAYSHAFT_Z) - cyl_y(P.LAY_AXLE["d"] + 0.3, 40, P.LAYSHAFT_X, 0, P.LAYSHAFT_Z)


def _motor_plate_raw():
    """D34: the plate is a rounded XZ profile with radiused windows round a solid ring at the motor (bolt bosses)
    and another at the layshaft bearing, instead of a slab with one square hole. Interfaces unchanged."""
    x, z = P.LAYSHAFT_X, P.LAYSHAFT_Z
    ya, yb = P.MOTOR_PLATE_Y
    xa = 121.5                                                                # plate front (D47: fixed; was ESC end + 2 before the ESC moved aft)
    R = S2.rect
    keep = S2.unary_union([S2.disc(P.MOTOR_X, z, 17.5), S2.disc(x, z, 9.5),
                           S2.disc(P.MOTOR_X + 12.5 * math.cos(math.pi / 4), z + 12.5 * math.sin(math.pi / 4), 6.0),
                           S2.disc(P.MOTOR_X - 12.5 * math.cos(math.pi / 4), z - 12.5 * math.sin(math.pi / 4), 6.0)])
    wins = [R(xa + 3, ZF + 4, P.MOTOR_X - 14.5, P.DECK_Z - 9), R(P.MOTOR_X + 6, P.DECK_Z - 16, x - 5, P.DECK_Z - 7),
            R(P.MOTOR_X + 6, ZF + 3.5, x - 5, z - 5.5)]
    wins = [S2.rounded(w.difference(keep), r_convex=2.0) for w in wins]
    prof = S2.rounded(R(xa, ZF, x + 10, P.DECK_Z), r_convex=4.0)
    prof = prof.difference(S2.unary_union([w for w in wins if not w.is_empty])).union(R(xa + 4, ZF, x + 6, ZF + 2))
    p = S2.solid_xz(prof, ya, yb - ya)                                        # plate
    p += S2.solid(S2.rounded(R(xa, yb - 0.5, P.MOTOR_X + 9.5, yb + 6), r_convex=1.5), ZF, 6)   # floor foot (inserts)
    p += S2.solid(S2.rounded(R(xa + 1, ya, x + 9, ya + 8), r_convex=2.0), P.DECK_Z - 5, 5)     # top lip (stiffener); 5 deep: the spur's top is 2 mm under it
    # D53: the rear deck-lap screw moved 4.1 mm outboard (params.deck_holes) onto this block, so its square nut is not over
    # the spur (a 7 mm lip there hit the spur's top: 9 mm3, check_fit). The block is clear of the motor, heat sink and fans.
    lx, ly = next((hx, hy) for hx, hy in P.deck_holes() if hy < 0 and abs(hx - (P.LAYSHAFT_X - 3)) < 0.1)
    p += S2.solid(S2.rounded(R(lx - 5.5, ly - 4.0, lx + 5.5, yb - 0.2), r_convex=1.5), P.DECK_Z - 7, 7)
    p += S2.solid(S2.rounded(R(P.MOTOR_X - 8, ya, P.MOTOR_X + 2, ya + 8), r_convex=2.0), P.DECK_Z - 7.5, 7.5)  # deck boss
    # D55 gearing slots: the motor slides along X (the mesh line: motor and layshaft share Z) so any 48P pinion from
    # P.PINION_RANGE fits the 66T spur (30T-38T: 50 mph and 80 mph builds, tuning). Each hole becomes a slot from the
    # largest pinion's motor position to the smallest's; the design pinion (P.PINION_T) sits inside the range.
    dxa, dxb = P.motor_slot_dx()
    def slot_y(d, cx, cz):
        s = cyl_y(d, 20, cx + dxa, ya, cz) + cyl_y(d, 20, cx + dxb, ya, cz)
        return s + Pos(cx + (dxa + dxb) / 2, ya, cz) * Box(dxb - dxa, 20, d)
    p -= slot_y(16, P.MOTOR_X, z)                                             # motor boss [unverified], slotted (D55)
    for k in range(4):                                                        # motor screw stations (D18)
        a = math.pi / 4 + k * math.pi / 2
        bx, bz = P.MOTOR_X + 12.5 * math.cos(a), z + 12.5 * math.sin(a)
        if k in (0, 2):
            # D48 thermal break: the 1 mm printed standoff bosses are gone. A bought 1 mm fibre washer (P.MOTOR_ISO_WASHER)
            # sits between the motor face and the flat plate at each screw (the motor face stays at MOTOR_Y0), a second
            # one under each screw head, and the screw hole is 4.2 mm so the hot screw does not touch the plastic.
            p -= slot_y(P.MOTOR_SCREW_HOLE, bx, bz)                           # D55: slotted for the pinion range
    p -= cyl_y(P.LAY_AXLE["d"] + 0.2, 20, x, (ya + yb) / 2, z)               # D50: the fixed axle passes here (was a bearing seat)
    return p


LAY_CAP_X0 = P.LAYSHAFT_X - 9.5          # D57: front edge of the plate's layshaft cap (the solid ring round the axle starts here)
LIP_CAP_X0 = P.LAYSHAFT_X - 19.0         # D57: the plate's top lip is cut from here aft (1 mm ahead of the spur's 18 mm tip radius)


def _plate_cap_zone(grow=0.0):
    """D57: the part of the motor plate that lifts off with the deck: the plate above the axle centre from LAY_CAP_X0 aft
    (legs 3 mm lower at both ends locate it in X on the plate's tongue), the deck-lap screw block, and the strip of the top
    lip that overhangs the spur (y > -11), so the spur can rise past it. grow opens the plate's cut at the vertical faces
    only (front face, leg faces, lip strip); the axle split face stays shared."""
    x, z = P.LAYSHAFT_X, P.LAYSHAFT_Z
    ya, yb = P.MOTOR_PLATE_Y
    leg, g, y0, xe = P.LAY_SPLIT_LEG, grow, ya - 10, x + 30
    zone = box(xe - (LAY_CAP_X0 - g), 30, P.DECK_Z + 5 - z, LAY_CAP_X0 - g, y0, z)
    zone += box((x - 7.0 + g) - (LAY_CAP_X0 - g), 30, leg, LAY_CAP_X0 - g, y0, z - leg)
    zone += box(xe - (x + 7.0 - g), 30, leg, x + 7.0 - g, y0, z - leg)
    zone += box(LAY_CAP_X0 + 0.1 - (LIP_CAP_X0 - g), P.SPUR_Y[1] + 2 - (yb - g), 10, LIP_CAP_X0 - g, yb - g, P.DECK_Z - 5.0)
    return zone


def motor_plate():
    p = _motor_plate_raw()
    top_load = getattr(P, "TOP_LOAD", False)
    if top_load:
        p -= _plate_cap_zone(P.BH_CLR)
    for (hx, hy) in P.motor_plate_floor_holes():                               # D53: captive square nuts
        p = AN.anchor(p, (hx, hy, ZF), (0, 0, 1), f"motor plate floor ({hx:.1f}, {hy:.0f})")
    for (hx, hy) in P.deck_holes():
        if hy < 0 and 100 < hx < P.LAYSHAFT_X + 10 and not (top_load and hx > LAY_CAP_X0):   # D34: + the rear deck-lap screw
            p = AN.anchor(p, (hx, hy, P.DECK_Z), (0, 0, -1), f"motor plate deck ({hx:.1f}, {hy:.0f})")
    return p


def lay_cap_plate():
    """D57: motor-plate layshaft cap (see _plate_cap_zone). Held by the rear deck-lap screw, whose captive nut is in it:
    deck off, and it lifts away; the axle cartridge then lifts out of the plate's half-bore."""
    c = _motor_plate_raw() & _plate_cap_zone()
    for (hx, hy) in P.deck_holes():
        if hy < 0 and LAY_CAP_X0 < hx < P.LAYSHAFT_X + 10:
            c = AN.anchor(c, (hx, hy, P.DECK_Z), (0, 0, -1), f"motor plate deck ({hx:.1f}, {hy:.0f})")
    return c


def _lay_holder_raw():
    """D34: tapered, rounded XZ profile (22 mm at the floor, 12 mm at the deck) with radiused windows above and
    below the MR105 seat (was a 20 mm block)."""
    x, z = P.LAYSHAFT_X, P.LAYSHAFT_Z
    ya, yb = P.LAY_HOLDER_Y
    R = S2.rect
    prof = S2.rounded(S2.poly([(x - 10.5, ZF), (x + 10.5, ZF), (x + 6, P.DECK_Z), (x - 6, P.DECK_Z)]), r_convex=2.0)
    prof = prof.difference(S2.rounded(R(x - 4, z + 8, x + 4, P.DECK_Z - 7), r_convex=2.5))
    prof = prof.difference(S2.rounded(R(x - 3.5, ZF + 3, x + 3.5, z - P.LAY_BRG[1] / 2 - 2.5), r_convex=2.0))
    prof = prof.simplify(0.05)
    h = S2.solid_xz(prof, ya, yb - ya)
    # D50: the axle's M4 thread passes the holder; an M4 nyloc sits in a hex trap in the outer face (5 mm deep), an M4 washer
    # bears on the inner face. 3 mm of holder is clamped between them. (Was a bearing seat + a 6 mm hole.)
    h -= cyl_y(4.4, 30, x, (ya + yb) / 2, z)
    rn = (P.LAY_AXLE["nut_af"] + 0.2) / 2 / math.cos(math.pi / 6)
    nut = extrude(Polygon(*[(rn * math.cos(k * math.pi / 3), rn * math.sin(k * math.pi / 3)) for k in range(6)]), P.LAY_AXLE["nut_h"])
    h -= Pos(x, yb + 0.01, z) * Rot(90, 0, 0) * nut
    return h


def _holder_cap_zone(grow=0.0):
    """D57: the lay holder above the axle centre, with legs 3 mm lower outboard of |dx| 5.5 that locate it in X."""
    x, z = P.LAYSHAFT_X, P.LAYSHAFT_Z
    ya, yb = P.LAY_HOLDER_Y
    leg, g = P.LAY_SPLIT_LEG, grow
    zone = box(30, yb - ya + 2, P.DECK_Z + 5 - z, x - 15, ya - 1, z)
    zone += box(15 - 5.5 + g, yb - ya + 2, leg, x - 15, ya - 1, z - leg)
    zone += box(15 - 5.5 + g, yb - ya + 2, leg, x + 5.5 - g, ya - 1, z - leg)
    return zone


def lay_holder():
    h = _lay_holder_raw()
    top_load = getattr(P, "TOP_LOAD", False)
    if top_load:
        h -= _holder_cap_zone(P.BH_CLR)
    for (hx, hy) in P.lay_holder_floor_holes():                                # D53: captive square nuts
        h = AN.anchor(h, (hx, hy, ZF), (0, 0, 1), f"lay holder floor ({hx:.1f}, {hy:.1f})")
    if not top_load:
        h = AN.anchor(h, (P.LAYSHAFT_X, sum(P.LAY_HOLDER_Y) / 2, P.DECK_Z), (0, 0, -1), "lay holder deck")
    return h


def lay_cap_holder():
    """D57: lay-holder cap: the upper half of the axle hole and of the M4 nyloc's hex trap, held by the holder's deck screw
    (its captive nut is in this cap). Deck off, it lifts away and the nyloc rises with the axle cartridge."""
    c = _lay_holder_raw() & _holder_cap_zone()
    return AN.anchor(c, (P.LAYSHAFT_X, sum(P.LAY_HOLDER_Y) / 2, P.DECK_Z), (0, 0, -1), "lay holder deck")


def wheel_hex():
    """12 mm printed wheel hex, 6 mm thick, axle bore + 2 mm drive-pin slot (wear part)."""
    r = P.HEX_AF / 2 / math.cos(math.pi / 6)
    hx = extrude(Polygon(*[(r * math.cos(math.pi / 6 + k * math.pi / 3), r * math.sin(math.pi / 6 + k * math.pi / 3))
                           for k in range(6)]), P.HEX_DEPTH)
    hx -= cyl_z(P.CVD_AXLE_D + 0.2, 20, 0, 0, -1)
    hx -= cbox(P.CVD_AXLE_D + 6, P.HEX_PIN_D + 0.2, P.HEX_PIN_D + 0.2, 0, 0, -0.01)   # pin slot, inboard face
    return hx


# =====================================================================================
# placement
def place(shape, axle_x, side):
    """Built at the left side of the front axle -> any corner (180 deg turn for the right)."""
    if side > 0:
        return Pos(axle_x, 0, 0) * shape
    return Pos(axle_x, 0, 0) * Rot(0, 0, 180) * shape


def printed_installed():
    """Every printed running-gear part at its installed position (for the fit check/renders)."""
    out = {}
    la, ul, ur = lower_arm(), upper_link(), upright_rear()
    fdx = front_diff_dx()
    assert abs(fdx - P.FRONT_DIFF_DX) < 0.01, f"params.FRONT_DIFF_DX {P.FRONT_DIFF_DX} != front_diff_dx() {fdx}"
    bhf = {1: bulkhead_half(fdx, True, 1), -1: bulkhead_half(-fdx, True, -1)}      # D46: local x flips on the 180-deg right-hand part
    bhr = {1: bulkhead_half(0.0, False, 1), -1: bulkhead_half(0.0, False, -1)}     # D57d: rear L and R differ (asymmetric slot)
    for ax, tag in ((0.0, "f"), (P.WB, "r")):
        for sd, s in ((1, "L"), (-1, "R")):
            out[f"bulkhead_{tag}{s}"] = place(bhf[sd] if tag == "f" else bhr[sd], ax, sd)
            out[f"arm_{tag}{s}"] = place(la, ax, sd)
            out[f"link_{tag}{s}"] = place(ul, ax, sd)
            out[f"shock_{tag}{s}"] = shock_installed(ax, sd)
        out[f"upright_rL"] = place(ur, P.WB, 1)
        out[f"upright_rR"] = place(ur, P.WB, -1)
    out["knuckle_fL"] = knuckle(1)
    out["knuckle_fR"] = knuckle(-1)
    out["tower_f"] = tower_front()
    out["tower_r"] = Pos(P.WB, 0, 0) * tower_rear()
    out["crank_L"], out["crank_R"] = bellcrank(1), bellcrank(-1)
    out["drag_link"], out["servo_link"] = drag_link(), servo_link()
    out["tierod_L"], out["tierod_R"] = tie_rod(1), tie_rod(-1)
    out["motor_plate"], out["lay_holder"], out["lay_drum"] = motor_plate(), lay_holder(), lay_drum()
    if getattr(P, "TOP_LOAD", False):                                          # D57 caps
        capr = {1: bulkhead_cap(0.0, False, 1), -1: bulkhead_cap(0.0, False, -1)}
        capf = {1: bulkhead_cap(fdx, True, 1), -1: bulkhead_cap(-fdx, True, -1)}
        for ax, tag in ((0.0, "f"), (P.WB, "r")):
            for sd, sx in ((1, "L"), (-1, "R")):
                out[f"bulkhead_cap_{tag}{sx}"] = place(capf[sd] if tag == "f" else capr[sd], ax, sd)
        out["lay_cap_plate"], out["lay_cap_holder"] = lay_cap_plate(), lay_cap_holder()
    return out


def _belt(x1, z1, r1, x2, z2, r2, yc):
    """Envelope of a closed belt: convex hull of the two pulleys (XZ), BELT_W wide in Y."""
    pts = []
    for (x, z, r) in ((x1, z1, r1), (x2, z2, r2)):
        for k in range(48):
            a = 2 * math.pi * k / 48
            pts.append((x + r * math.cos(a), z + r * math.sin(a)))
    import numpy as np
    from scipy.spatial import ConvexHull
    h = ConvexHull(np.array(pts))
    poly = [tuple(pts[i]) for i in h.vertices]
    face = make_face(Polyline(*[(x, z) for x, z in poly], close=True))      # XY sketch -> rotate to XZ
    slab = extrude(face, P.BELT_W)
    return Pos(0, yc + P.BELT_W / 2, 0) * Rot(90, 0, 0) * slab


def bought_envelopes():
    """Bought power-path parts as simple envelopes (prefix e_ in the fit check)."""
    out = {}
    rd = pitch_r(P.DIFF_PULLEY_T) + 1.2                                       # belt outer surface
    rl = pitch_r(P.LAY_PULLEY_T) + 1.2
    fdx = front_diff_dx()
    for ax, tag, yb in ((fdx, "f", P.FB_Y), (P.WB, "r", P.RB_Y)):
        half = P.DIFF_SPAN / 2
        d = cyl_y(P.DIFF_CASE_D, 2 * half - 0.2, ax, 0, P.DIFF_Z)
        d += cyl_y(2 * pitch_r(P.DIFF_PULLEY_T) - 0.8, P.BELT_W + 0.5, ax, yb, P.DIFF_Z)
        d += cyl_y(P.DIFF_BRG[0], 2 * P.CHEEK_Y[1], ax, 0, P.DIFF_Z)          # outdrives
        out[f"diff_{tag}"] = d
        for sd in (1, -1):                                                    # CVDs: cheek -> upright
            out[f"cvd_{tag}{'L' if sd > 0 else 'R'}"] = rod((ax, sd * (P.CHEEK_Y[1] + 0.6), P.DIFF_Z),
                                                         (round(ax), sd * 53.4, P.TIRE_D / 2), 12)   # upright at the axle
    out["belt_f"] = _belt(fdx, P.DIFF_Z, rd, P.LAYSHAFT_X, P.LAYSHAFT_Z, rl, P.FB_Y)
    out["belt_r"] = _belt(P.LAYSHAFT_X, P.LAYSHAFT_Z, rl, P.WB, P.DIFF_Z, rd, P.RB_Y)
    m48 = 25.4 / 48
    sy = (P.SPUR_Y[0] + P.SPUR_Y[1]) / 2
    sw = P.SPUR_Y[1] - P.SPUR_Y[0]
    out["spur"] = cyl_y(m48 * 68, sw, P.LAYSHAFT_X, sy, P.LAYSHAFT_Z)
    out["pinion"] = cyl_y(m48 * (P.PINION_T + 2), sw, P.MOTOR_X, sy, P.LAYSHAFT_Z)
    _a = P.LAY_AXLE                                                           # D50: the fixed shoulder screw, head to thread end
    _y0, _y1 = P.LAY_AXLE_END - _a["shoulder"], P.LAY_AXLE_END + _a["thread"]
    out["layshaft"] = (cyl_y(_a["d"], _a["shoulder"], P.LAYSHAFT_X, (_y0 + P.LAY_AXLE_END) / 2, P.LAYSHAFT_Z)
                       + cyl_y(4.0, _a["thread"], P.LAYSHAFT_X, P.LAY_AXLE_END + _a["thread"] / 2, P.LAYSHAFT_Z)
                       + cyl_y(_a["head_d"], _a["head_h"], P.LAYSHAFT_X, _y0 - _a["head_h"] / 2, P.LAYSHAFT_Z))
    return out
