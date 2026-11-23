"""T1 wheel: PETG-CF rim + TPU 95A tread ring keyed into 3 circumferential dovetail grooves.
D44 (owner 2026-11-16: "can we design our own TPU tires with belts in them? or design rims that can prevent that?"):
BELTED = True gives the T2 wheel. The tread carries an aramid belt (6 cord rings x 3 turns of size-69 Kevlar
thread wound into channels at print pauses, then printed over: no glue), so the belt, not the TPU, holds the tread
against 12,900 rpm. A belted ring cannot stretch over a lip, so the rim splits: its inboard lip is a separate PETG-CF
clamp ring held by 3 hidden M3 x 8 flat-heads into square nuts in 3 bosses inside the barrel (the inboard face is
behind the wheel), located on a spigot. The tread slides on axially; the 6 axial keys still carry the drive torque
and the two lips clamp its edges. The dovetails are gone (they only existed to stop growth).
D45 (owner 2026-11-17: buy the tyres, print the scale rims, CA-glue tyre to rim): TYRE_BOUGHT gives the T3 wheel: the
printed rim is a standard 1/10 touring wheel barrel (52 mm bead seat, 24 mm wide [unverified: maker gives no
drawing], 0.6 mm edge lips locate the beads) behind the scale spoke face; tread() is then only the bought tyre's
envelope (for renders, keep-outs and CFD), not a printed part.
Built in local coords: wheel axis = Z, inboard face at Z = 0 (print orientation)."""
import math
from build123d import Polygon, revolve, Axis, Plane, Pos, Rot, Cylinder, Box, Cone, Align, make_face, Polyline, extrude
import params as P
from lib import cyl_z, cbox

W = P.TIRE_W
R_SEAT = P.RIM_D / 2              # 29.0
LIP_H, LIP_W = 1.0, 1.5           # axial locating lips at both rim edges
GROOVES = 3
G_TOP, G_BOT, G_DEPTH = 3.0, 4.5, 1.5   # dovetail: opening, base, depth
RIM_WALL = 2.0                    # D53 weight: barrel wall 2.5 -> 2.0 mm (4 lines of 0.5); rnd/structure/light_strong_d50.md #7, hoop check in test_tire.py
HUB_D = 22.0
WEB_T = 3.0
WEB_Z = 7.0                       # web position from the inboard face (behind the hex pocket)
SPOKE_HOLES = 6
FIT = 0.3                         # tread rib interference per side (stretch fit; D36: no CA)
KEYS, KEY_W, KEY_D = 6, 2.4, 1.0  # D36 axial anti-rotation keys: tread ribs into rim slots (drive torque)
# ---- D44 belted tread + split rim ----
BOUGHT = getattr(P, "TYRE_BOUGHT", False)   # D45: bought belted tyre, glued (see the docstring)
BELTED = not BOUGHT               # D44 T2 printed Kevlar-belted tread (superseded by D45)
if BOUGHT:
    LIP_H, LIP_W = 2.0, 1.2       # D50: flanges to 52 mm OD over the 48 mm bead seat (standard touring wheel; were 0.6 mm lips on a 52 mm seat)
RING_T = 2.5                      # inboard clamp ring thickness (z 0..RING_T); its lip stands RING_LIP_H over the seat
RING_LIP_H = 1.5
RING_R_IN = 20.5
RING_SCREWS, SCREW_R, SCREW_A0 = 3, 24.0, 30.0    # M3 x 8 flat-head (90 deg), between the web's lightening holes
BOSS_W, BOSS_L = 7.5, 8.0         # boss tangential width, axial length from the barrel end
NUT_S, NUT_T, NUT_Z = 5.7, 2.0, 2.0   # M3 square-nut slot (5.5 x 1.8 nut + clearance), from the barrel end, radial entry
                                  # (slot z 4.5..6.5: under the web at WEB_Z, so the nut slides in from the hub side)
SPIGOT_H, SPIGOT_R = (0.8, (25.3, 26.4))   # 3 spigot arcs on the clamp ring, up into the barrel bore between the
                                  # bosses: concentric to the seat, and they key the ring against turning
# The belted rim's print face is the barrel end at z = RING_T (barrel, bosses and hub all start there: no supports).
# The hub face moves out RING_T with it; the 6 mm wheel hex keeps its place on the axle (inboard face at z 0) and
# simply stands RING_T proud of the hub, still engaged HEX_DEPTH - RING_T = 3.5 mm in the pocket.
BELT_LEVELS, BELT_TURNS = 6, 3    # cord rings across the tread x turns of thread per ring (3.2 mm pitch: the
                                  # TPU span between rings is what bulges, rnd/tests/test_tire.py)
BELT_R, BELT_CH = 30.3, 0.8       # channel centre radius (1.3 over the seat, 1.7 under the tread face), square side
BELT_EDGE = 2.0                   # outer channel centre from each tread edge
BORE_CLR = 0.15                   # radial bore allowance (varioShore 92A): winding the cord (WIND_G hanging weight) squeezes the soft
WIND_G = 10                       # ring up to ~0.1 mm smaller and the belt then stops it stretching back (rnd/tests/test_tire.py)


def groove_z():
    span = W - 2 * LIP_W
    return [LIP_W + span * (i + 0.5) / GROOVES for i in range(GROOVES)]


def _ring(r_in, r_out, z0, z1):
    """annulus r_in..r_out between z0 and z1 (D44: the old form sat h/2 high; it had no callers before)"""
    return cyl_z(2 * r_out, z1 - z0, 0, 0, z0) - cyl_z(2 * r_in, z1 - z0 + 2, 0, 0, z0 - 1)


def _revolve_xz(pts):
    """Revolve a closed (r, z) polyline about the Z axis."""
    face = make_face(Polyline(*pts, close=True))
    face = Plane.XZ.from_local_coords(face) if False else face
    return revolve(Plane.XZ * face, Axis.Z, 360)


def dovetail_profile(zc, r_surface, depth, top, bot, grow=0.0):
    """(r, z) trapezoid cut into a surface at radius r_surface, narrow at the surface."""
    return [(r_surface + 0.01, zc - top / 2 - grow), (r_surface - depth, zc - bot / 2 - grow),
            (r_surface - depth, zc + bot / 2 + grow), (r_surface + 0.01, zc + top / 2 + grow)]


def tread_z():
    """(z0, width) of the tread between the lips."""
    if BELTED:     # 0.1 mm axial squeeze at each lip: the clamp ring's screws pinch the tread edges
        return RING_T - 0.1, W - RING_T - LIP_W + 0.2
    return LIP_W + 0.1, W - 2 * LIP_W - 0.2


def belt_z():
    z0, w = tread_z()
    return [z0 + BELT_EDGE + (w - 2 * BELT_EDGE) * i / (BELT_LEVELS - 1) for i in range(BELT_LEVELS)]


def belt_pauses(layer=0.12):
    """Print-pause heights (mm above the tread's bed face, PrusaSlicer "pause before the layer at Z", Z = a layer's
    top): the first layer whose slice mid-plane is above the channel roof, i.e. the first layer that bridges it.
    Assumes a uniform layer height including the first layer."""
    z0, _ = tread_z()
    return [round((math.floor(round((zc + BELT_CH / 2 - z0) / layer + 0.5, 6)) + 1) * layer, 2) for zc in belt_z()]


def screw_pts():
    return [(SCREW_R * math.cos(math.radians(SCREW_A0 + 360.0 / RING_SCREWS * k)),
             SCREW_R * math.sin(math.radians(SCREW_A0 + 360.0 / RING_SCREWS * k))) for k in range(RING_SCREWS)]


def clamp_ring():
    """D44: the rim's inboard lip as its own part (z 0..RING_T in wheel coords; prints flat, outer face down)."""
    rr = _ring(RING_R_IN, R_SEAT + RING_LIP_H, 0, RING_T)
    sp = _ring(SPIGOT_R[0], SPIGOT_R[1], RING_T - 0.01, RING_T + SPIGOT_H)
    for x, y in screw_pts():                       # gaps for the bosses (0.3 mm a side)
        sp -= Rot(0, 0, math.degrees(math.atan2(y, x))) * Pos(SPIGOT_R[1], 0, RING_T + SPIGOT_H / 2) * Box(6, BOSS_W + 0.6, SPIGOT_H + 2)
    rr += sp
    for x, y in screw_pts():
        rr -= cyl_z(P.M3_CLEAR, RING_T + 2, x, y, -1)
        rr -= Pos(x, y, -0.01) * Cone(P.M3_CSK_D / 2, P.M3_CLEAR / 2, (P.M3_CSK_D - P.M3_CLEAR) / 2, align=(Align.CENTER, Align.CENTER, Align.MIN))
    return rr


def rim(web=True):
    """web=False leaves the hub and barrel unjoined (a body kit adds its own spoke face)."""
    if BELTED:
        # D44: no inboard lip (the clamp ring is it), no dovetails; barrel from the ring face to the outboard lip
        z_b = RING_T
        prof = [(R_SEAT - RIM_WALL, z_b), (R_SEAT, z_b), (R_SEAT, W - LIP_W), (R_SEAT + LIP_H, W - LIP_W),
                (R_SEAT + LIP_H, W), (R_SEAT - RIM_WALL, W)]
        r = _revolve_xz(prof)
        for x, y in screw_pts():                                  # bosses inside the barrel (holes cut last)
            a = math.degrees(math.atan2(y, x))
            r += Rot(0, 0, a) * Pos((SCREW_R - 3.5 + R_SEAT - RIM_WALL + 0.5) / 2, 0, z_b + BOSS_L / 2) * \
                Box(R_SEAT - RIM_WALL + 0.5 - (SCREW_R - 3.5), BOSS_W, BOSS_L)
    else:
        # tread-seat ring with edge lips (D45 bought tyre: plain glued bead seat, no dovetails, no keys)
        prof = [(R_SEAT - RIM_WALL, 0), (R_SEAT + LIP_H, 0), (R_SEAT + LIP_H, LIP_W), (R_SEAT, LIP_W),
                (R_SEAT, W - LIP_W), (R_SEAT + LIP_H, W - LIP_W), (R_SEAT + LIP_H, W), (R_SEAT - RIM_WALL, W)]
        r = _revolve_xz(prof)
        for zc in (() if BOUGHT else groove_z()):
            r -= _revolve_xz(dovetail_profile(zc, R_SEAT, G_DEPTH, G_TOP, G_BOT))
        # D48 balance stations (R6): tape and putty are out (D36), so each rim carries n blocks inside the barrel, hidden on
        # the inboard side, each with a counterbored 2.5 mm pilot for an M3 socket-cap screw from the hardware kit. Screws
        # of different lengths in opposite stations trim the wheel (2 mm of screw = 0.11 g = 2.2 g.mm at r 20).
        bn, br, bw, bl = P.RIM_BALANCE
        for k in range(bn):
            a_ = 360.0 / bn * k + 45.0
            r_in = br - 3.5
            r += Rot(0, 0, a_) * Pos((r_in + R_SEAT - RIM_WALL + 0.5) / 2, 0, bl / 2) * Box(R_SEAT - RIM_WALL + 0.5 - r_in, bw, bl)
    z0, w = tread_z()
    for k in range(0 if BOUGHT else KEYS):    # D36: axial key slots across the seat (tread ribs drop in)
        r -= Rot(0, 0, 360.0 / KEYS * k) * Pos(R_SEAT - KEY_D / 2 + 0.05, 0, z0 + w / 2) * Box(KEY_D + 0.1, KEY_W + 0.2, w + 0.2 + (RING_T if BELTED else 0))
    # web + hub
    if web:
        r += cyl_z(2 * (R_SEAT - RIM_WALL) + 0.5, WEB_T, 0, 0, WEB_Z)
    hz = RING_T if BELTED else 0.0
    r += cyl_z(HUB_D, W - 4 - hz, 0, 0, hz)
    # 12 mm hex pocket from the inboard face, axle hole, outboard nut recess
    hexr = P.HEX_AF / 2 / math.cos(math.pi / 6) + 0.1
    hexagon = Polygon(*[(hexr * math.cos(math.pi / 6 + k * math.pi / 3),
                         hexr * math.sin(math.pi / 6 + k * math.pi / 3)) for k in range(6)])
    r -= Pos(0, 0, -0.01) * extrude(hexagon, P.HEX_DEPTH + 0.01)
    # D48 (R17): 3 crush ribs on alternate flats of the hex pocket, 0.15 mm proud, 1 mm wide. The plain pocket's working
    # window was 0..0.25 mm of clearance, which a printer scattering 50 % more than assumed missed 16 % of the time; the
    # ribs take up to ~0.2 mm of interference, as the bearing seats' ribs do.
    flat_r = hexr * math.cos(math.pi / 6)
    for k in range(3):
        r += Rot(0, 0, 120.0 * k) * Pos(flat_r - 0.025, 0, P.HEX_DEPTH / 2) * Box(0.25, 1.0, P.HEX_DEPTH)
    r -= cyl_z(P.AXLE_HOLE, W + 2, 0, 0, -1)
    r -= cyl_z(10.5, W, 0, 0, P.HEX_DEPTH + 2.5)         # M4 flanged nut + socket
    if BOUGHT and not BELTED:                                # D48 balance-screw pilots + head counterbores (inboard face)
        bn, br, bw, bl = P.RIM_BALANCE
        for k in range(bn):
            a_ = math.radians(360.0 / bn * k + 45.0)
            bx, by = br * math.cos(a_), br * math.sin(a_)
            r -= cyl_z(2.5, bl - 1.0 + 0.01, bx, by, -0.01)
            r -= cyl_z(6.2, 3.2 + 0.01, bx, by, -0.01)
    # balanced lightening holes in the web
    rr = (HUB_D / 2 + R_SEAT - RIM_WALL) / 2
    for k in range(SPOKE_HOLES if web else 0):
        a = 2 * math.pi * k / SPOKE_HOLES
        r -= cyl_z(9.0, WEB_T + 2, rr * math.cos(a), rr * math.sin(a), WEB_Z - 1)
    if BELTED:     # clamp screws: clearance through boss + web (the M3 x 8 tip ends at z 8), square-nut slot open inward
        for x, y in screw_pts():
            a = math.degrees(math.atan2(y, x))
            r -= cyl_z(P.M3_CLEAR, BOSS_L + 1, x, y, RING_T - 0.5)
            r -= Rot(0, 0, a) * Pos((SCREW_R - 6.0 + SCREW_R + NUT_S / 2) / 2, 0, RING_T + NUT_Z + NUT_T / 2) * \
                Box(SCREW_R + NUT_S / 2 - (SCREW_R - 6.0), NUT_S, NUT_T)
    return r


def tread():
    z0, w = tread_z()
    if BOUGHT:
        # D45: the bought tyre's envelope only (bead seat to OD between the rim lips, 1.5 mm shoulder rounds)
        rb, ro = R_SEAT, P.TIRE_D / 2
        a, b = LIP_W, W - LIP_W
        return _revolve_xz([(rb, a), (ro - 1.5, a), (ro, a + 1.5), (ro, b - 1.5), (ro - 1.5, b), (rb, b)])
    if BELTED:
        # D44: slides on (bore = seat, no stretch), 6 axial keys, BELT_LEVELS closed square channels for the cord
        r_in = R_SEAT + BORE_CLR
        ring = _revolve_xz([(r_in, z0), (P.TIRE_D / 2, z0), (P.TIRE_D / 2, z0 + w), (r_in, z0 + w)])
        for k in range(KEYS):
            ring += Rot(0, 0, 360.0 / KEYS * k) * Pos(r_in - (KEY_D - 0.1) / 2 + 0.05, 0, z0 + w / 2) * Box(KEY_D - 0.1, KEY_W, w)
        for zc in belt_z():
            ring -= _revolve_xz([(BELT_R - BELT_CH / 2, zc - BELT_CH / 2), (BELT_R + BELT_CH / 2, zc - BELT_CH / 2),
                                 (BELT_R + BELT_CH / 2, zc + BELT_CH / 2), (BELT_R - BELT_CH / 2, zc + BELT_CH / 2)])
        return ring
    r_in = R_SEAT - FIT
    ring = _revolve_xz([(r_in, z0), (P.TIRE_D / 2, z0), (P.TIRE_D / 2, z0 + w), (r_in, z0 + w)])
    # ribs: dovetail keys (slightly oversize -> interference), joined to the ring
    for zc in groove_z():
        prof = dovetail_profile(zc, r_in + 0.01, G_DEPTH - 0.1 - FIT, G_TOP, G_BOT, grow=0.05)
        ring += _revolve_xz(prof)
    for k in range(KEYS):                     # D36: axial anti-rotation keys (0.1 mm interference each side)
        ring += Rot(0, 0, 360.0 / KEYS * k) * Pos(r_in - (KEY_D - FIT) / 2 + 0.01, 0, z0 + w / 2) * Box(KEY_D - FIT + 0.02 - 0.1, KEY_W + 0.2 + 0.2, w)
    return ring


def place(shape, axle_x, side):
    """Local wheel (inboard face Z=0) -> vehicle frame. side=+1 left, -1 right."""
    y_center = side * (P.TRACK_F if axle_x == 0 else P.TRACK_R) / 2
    y_in = y_center - side * W / 2
    if side > 0:   # left: local +Z points +Y (outboard)
        return Pos(axle_x, y_in, P.TIRE_D / 2) * Rot(-90, 0, 0) * shape
    return Pos(axle_x, y_in, P.TIRE_D / 2) * Rot(90, 0, 0) * shape


# ---- wheel keep-out envelopes (steer + suspension travel) --------------------------------
STEER_DEG = 16.0       # max steering lock either way (Stage 3: 28 -> 16, runway car; turn radius ~0.75 m)
KINGPIN_IN = P.TRACK_F / 2 - P.KINGPIN_Y   # steering axis inboard of the tire centre plane (Stage 3: 19.5)
BUMP, DROOP = 6.0, 4.0  # wheel travel from static (bump limited by the 5 mm ride height)


def keepout(axle_x, side, clr=2.0, steer=None):
    """Volume swept by one tire (+clr) over steering lock and suspension travel.
    Front axle (x == 0) steers; rear does not."""
    from build123d import Cylinder, Box, Pos, Rot
    steer = (STEER_DEG if axle_x == 0 else 0.0) if steer is None else steer
    r, w = P.TIRE_D / 2 + clr, W + 2 * clr
    yc = side * (P.TRACK_F if axle_x == 0 else P.TRACK_R) / 2
    zc = P.TIRE_D / 2
    # stadium in XZ (droop..bump), extruded along Y, centred on the tire
    st = (Pos(0, 0, -DROOP) * Rot(90, 0, 0) * Cylinder(r, w)) + (Pos(0, 0, BUMP) * Rot(90, 0, 0) * Cylinder(r, w)) \
        + Pos(0, 0, (BUMP - DROOP) / 2) * Box(2 * r, w, BUMP + DROOP)
    piv = -side * KINGPIN_IN                     # pivot offset from tire centre, toward the chassis
    n = 1 if steer == 0 else 9
    env = None
    for k in range(n):
        a = 0.0 if n == 1 else -steer + 2 * steer * k / (n - 1)
        s = Pos(axle_x, yc + piv, zc) * Rot(0, 0, a) * Pos(0, -piv, 0) * st
        env = s if env is None else env + s
    return env


def keepouts(clr=2.0):
    out = None
    for ax in (0.0, P.WB):
        for sd in (1, -1):
            k = keepout(ax, sd, clr)
            out = k if out is None else out + k
    return out
