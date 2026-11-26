"""Stage 3 test coupons: small, cheap prints that replace the measuring tools we are not buying
(decision D11). Each one answers ONE question by feel, and the answer is typed back into
params.py. Procedures: rnd/stage3/coupons.md.

  C1 tolerance_ladder   which printed hole size gives slip / snug / press on THIS printer
  C2 insert_block       heat-set insert pull test (hang a water jug)
  C3 tread_ring         tread key-in-slot fit (short rim segment + tread segment); D44 belted: + belt_ring, one
                        full-circle cord ring to practise the print pause + Kevlar winding and check the slide-on fit
  C4 hinge_pin          M3 bolt as hinge pin: free swing without slop
  G1 bearing_ladder     bearing OD seats 14.6..15.4 (10x15) and 9.6..10.4 (5x10), with crush ribs
  G2 diff_span_gauge    slots 44..48 mm: which one the bought diff drops into = DIFF_SPAN
  G3 motor_face_gauge   motor face bolt spacing 23..27 mm (+ 30 mm pattern)
  G4 axle_pin_gauge     CVD axle holes 4.6..5.4 and drive-pin slots 1.8..2.4

Sizes are marked with notches (1 notch = smallest) so no text engraving is needed."""
from build123d import Pos, Rot, Box, Cylinder
import params as P
from lib import box, cbox, cyl_z, cyl_x, crush_seat_y
import running_gear as RG
import wheels as Wh


def _notches(n, x0, y, z_top, pitch=2.5):
    s = None
    for k in range(n):
        c = cbox(1.0, 3.0, 0.8, x0 + k * pitch, y, z_top - 0.79)
        s = c if s is None else s + c
    return s


def tolerance_ladder():
    """C1: 3 mm pin row (hinge pins) and, D53, a nut pocket row (D55: nominal 5.8 across flats x 2.7 for a DIN 934 M3 hex nut; was 2.1 deep for a square nut), +-0.3 in
    0.1 steps (7 each). Drop a nut in each pocket from the top: the smallest pocket it falls into flat is the fit; set
    anchors.POCKET_S to it."""
    steps = [-0.3, -0.2, -0.1, 0.0, 0.1, 0.2, 0.3]
    b = box(8 + 10 * len(steps), 26, 5, 0, 0, 0)
    for i, d in enumerate(steps):
        x = 9 + 10 * i
        b -= cyl_z(3.0 + 0.2 + d, 10, x, 7, -1)          # M3 bolt as pin: nominal 3.2
        b -= cbox(5.8 + d, 5.8 + d, 2.7 + 0.01, x, 19, 5 - 2.7) + cyl_z(3.4, 10, x, 19, -1)   # D55 hex-nut pocket: nominal 5.8 across flats, 2.7 deep
        b -= _notches(i + 1, x - 3, 13, 5) if i < 6 else _notches(1, x - 3, 13, 5) + cbox(6, 3, 0.8, x, 13, 4.21)
    return b


def insert_block():
    """C2 (D55: hex nut + washer; D53 square nuts; was heat-set inserts): two 12 mm bosses on a base with a strap slot, each with the car's
    captive-nut layout (cad/anchors.py, nut 3 mm under the top face). Screw an M3 in from the top, hang a known load from
    it: the nut must hold the 400 N the retention check assumed for an insert (rnd/tests/test_fasteners.py)."""
    import anchors as AN
    b = box(40, 20, 4, 0, 0, 0)
    for x in (12, 28):
        b += cyl_z(14, 8, x, 10, 4)                     # D55: 14 mm (was 12) so the washer pocket keeps 1 mm walls
    # D59: boss 2 copies the car's weakest nut joint, the servo post: a flat 3.5 mm from the screw (the post's servo-side
    # face), the washer slot opening through it, nut 4 mm deep. Boss 1 = the ordinary washer joint. (D55: boss 2 was a bare hex.)
    b -= box(10, 20, 8.01, 28 + 3.5, 0, 4)
    for i, x in enumerate((12, 28)):
        b = AN.anchor(b, (x, 10, 12), (0, 0, -1), f"coupon C2 boss {i + 1}", kinds=("washer",), pad_ok=False,
                      **(dict(open_mouth=True, t_try=(4.0, 3.5, 3.0)) if i == 1 else {}))
    b -= box(24, 4, 10, 8, 8, -1)                          # strap slot through the base
    return b


def tread_ring():
    """C3: a 30 deg segment of the rim and of the tread (T1: rib-in-dovetail fit; T2 belted: key-in-slot fit)."""
    seg = box(80, 80, 40, 0, -40, -5)
    seg = Rot(0, 0, 0) * seg
    rim = Wh.rim() & (Pos(0, 0, 0) * Rot(0, 0, -15) * box(40, 40, 40, 0, 0, -5) & Rot(0, 0, 15) * box(40, 40, 40, 0, -40, -5))
    tread = Wh.tread() & (Rot(0, 0, -15) * box(40, 40, 40, 0, 0, -5) & Rot(0, 0, 15) * box(40, 40, 40, 0, -40, -5))
    return rim, tread


def belt_ring():
    """C3 (D44): the tread's first 4.4 mm as a full ring: one cord channel, one print pause (Wh.belt_pauses()[0]).
    Wind it like the real tread, then slide it onto a real rim against the clamp ring: practice + the bore fit."""
    z0, _ = Wh.tread_z()
    zt = Wh.belt_z()[0] + 2.0
    return Wh.tread() & Pos(0, 0, (z0 + zt) / 2) * Box(80, 80, zt - z0)


def hinge_pin():
    """C4: a lug pair and an arm stub, 3.2 mm pin holes (C1 picks the final size)."""
    lug = box(30, 10, 4, 0, 0, 0) + box(5, 10, 12, 0, 0, 0) + box(5, 10, 12, 25, 0, 0)
    lug -= cyl_x(RG.PIN, 40, 15, 5, 8)
    arm = box(14.5, 10, 8, 0, 0, 0) + box(14.5, 25, 4, 0, 0, 0)
    arm = arm - (Pos(0, 0, 0) * cyl_x(RG.PIN, 20, 7, 5, 4))
    return lug, arm


def _seat_z(d, depth, x, y, z0):
    """Vertical crush-rib seat (same rib rule as lib.crush_seat_y), opening upward from z0."""
    return (Rot(90, 0, 0) * crush_seat_y(d, depth, 0, 0, 0, +1)).moved(Pos(x, y, z0))


def bearing_ladder():
    """G1: crush-rib seats for the 15 mm OD (diff + upright) and 10 mm OD (layshaft) bearings,
    nominal -0.4 .. +0.4 in 0.2 steps. The snug one = the size the CAD uses for this printer."""
    steps = [-0.4, -0.2, 0.0, 0.2, 0.4]
    b = box(10 + 20 * len(steps), 40, 5, 0, 0, 0)
    for i, d in enumerate(steps):
        x = 12 + 20 * i
        b -= _seat_z(15 + d, 4.2, x, 10, 1.0)          # 15 mm OD seat, 4 mm deep, 1 mm floor
        b -= cyl_z(11.5, 10, x, 10, -1)               # through hole to push the bearing out
        b -= _seat_z(10 + d, 4.2, x, 30, 1.0)
        b -= cyl_z(6.5, 10, x, 30, -1)
        b -= _notches(i + 1, x - 5, 20, 5)
    return b


def diff_span_gauge():
    """G2: five slots 44..48 mm long (bearing-to-bearing outer span of the bought diff).
    The diff drops into the shortest slot it fits without forcing: DIFF_SPAN = that slot."""
    spans = [44.0, 45.0, 46.0, 47.0, 48.0]
    b = box(60, 12 + 14 * len(spans), 6, 0, 0, 0)
    for i, s in enumerate(spans):
        y = 10 + 14 * i
        b -= box(s, 10, 6, (60 - s) / 2, y - 5, 2)
        b -= _notches(i + 1, 2, y, 6, 0)
    return b


def motor_face_gauge():
    """G3: plate with M3 hole pairs at 23, 24, 25, 26, 27 mm and a 30 mm pair, plus a 16 mm boss
    hole. Hold it on the motor face: the pair whose screws both start by hand = the spacing."""
    b = cyl_z(48, 3, 0, 0, 0) - cyl_z(16.5, 10, 0, 0, -1)
    import math
    for i, s in enumerate([23.0, 24.0, 25.0, 26.0, 27.0, 30.0]):
        a = math.radians(i * 30)
        for sg in (1, -1):
            b -= cyl_z(P.M3_CLEAR, 10, sg * s / 2 * math.cos(a), sg * s / 2 * math.sin(a), -1)
    return b


def axle_pin_gauge():
    """G4: CVD axle holes 4.6..5.4 (0.2 steps) and drive-pin slots 1.8..2.4 (0.15 steps)."""
    b = box(70, 26, 6, 0, 0, 0)
    for i, d in enumerate([4.6, 4.8, 5.0, 5.2, 5.4]):
        b -= cyl_z(d, 10, 8 + 13 * i, 8, -1)
    for i, w in enumerate([1.8, 1.95, 2.1, 2.25, 2.4]):
        b -= box(10, w, 4, 3 + 13 * i, 18 - w / 2, 2.01)
    return b


def belt_gap_gauge():
    """G5 (D60): a comb with six fingers 3.5 .. 6.0 mm wide in 0.5 mm steps, for the gap between the flanges of the bought
    diff's belt pulley. That gap is published nowhere (rnd/market/belt_upgrade_d60.md) and decides whether a 4 mm or 5 mm
    belt fits; the 3 mm belt is at 0.8x its catalogue rating in a full-grip launch (R3). The widest finger that drops
    between the flanges down to the teeth = the gap. Prints flat: the finger widths are in the bed plane."""
    widths = [3.5, 4.0, 4.5, 5.0, 5.5, 6.0]
    b = box(10 + 13 * len(widths), 14, 3, 0, 0, 0)
    for i, w in enumerate(widths):
        x = 11.5 + 13 * i
        b += box(w, 8, 3, x - w / 2, 13.99, 0)             # the finger: 8 mm long, 3 mm thick, w wide
        b -= _notches(i + 1, x - 5.0, 5, 3, 1.6)            # 1 notch = 3.5 mm, then +0.5 mm per notch
    return b


COUPONS = {
    "C1_tolerance_ladder": tolerance_ladder,
    "C2_insert_block": insert_block,
    "C4_hinge_lug": lambda: hinge_pin()[0],
    "C4_hinge_arm": lambda: hinge_pin()[1],
    "G1_bearing_ladder": bearing_ladder,
    "G2_diff_span_gauge": diff_span_gauge,
    "G3_motor_face_gauge": motor_face_gauge,
    "G4_axle_pin_gauge": axle_pin_gauge,
    "G5_belt_gap_gauge": belt_gap_gauge,
    "C3_tread_rim_segment": lambda: tread_ring()[0],
    "C3_tread_segment": lambda: tread_ring()[1],
}
if Wh.BELTED:
    COUPONS["C3_tread_segment_belt"] = belt_ring
