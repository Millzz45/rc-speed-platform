"""Splitter and rear diffuser. Chassis-mounted, so every body gets the same aero floor."""
import params as P
from lib import box, cbox, cyl_z, cyl_x, clear_hole, csk_hole, outline_solid
from build123d import Axis, fillet

SPLIT_Z0, SPLIT_T = 6.0, 2.5     # splitter underside 6 mm off the ground


def splitter():
    pts = [(-58, 70), (-52, 85), (-36, 85), (-36, -85), (-52, -85), (-58, -70)]
    s = outline_solid(pts, SPLIT_Z0, SPLIT_T)
    zt = SPLIT_Z0 + SPLIT_T
    for side in (1, -1):
        y = side * 42
        s += box(2.0, 6, 22 - zt, -37, y - 3, zt)                    # tab up to the beam face
        s += box(4.0, 6, 2.5, -40, y - 3, zt)                        # gusset foot
        s -= cyl_x(P.M3_CLEAR, 10, -36, y, P.FLOOR_TOP + 8)          # screw into beam insert
    return s


def diffuser():
    """Flange on the tub tail (X WB+26..WB+35, Z 9..12) + ramp from the floor edge (Z 5 @ X WB+35)
    up to Z 22 @ X WB+74, with strakes and side plates."""
    x0, x1 = P.TUB_X1, P.WB + 74.0
    t = 2.5
    hw = 60.0
    d = box(9, 60, 3, P.WB + 26, -30, P.FLOOR_TOP)                          # flange on the floor top
    d += box(2.5, 60, P.FLOOR_TOP + 3 - P.RIDE_Z, x0, -30, P.RIDE_Z)  # web down the tub tail
    # ramp: an inclined plate, built as a polygon extruded in Y
    from build123d import Polyline, make_face, extrude, Plane, Pos
    prof = [(x0, P.RIDE_Z), (x1, 22.0), (x1, 22.0 + t), (x0, P.RIDE_Z + t)]
    face = make_face(Polyline(*prof, close=True))
    ramp = Pos(0, hw, 0) * extrude(Plane.XZ * face, 2 * hw)
    d += ramp
    # strakes + side plates hang down to the floor plane (Z 5)
    for y in (-60, -30, 0, 30, 60):
        th = 1.6 if abs(y) < 60 else 2.0
        sprof = [(x0, P.RIDE_Z), (x1, P.RIDE_Z), (x1, 22.0), (x0, P.RIDE_Z)]
        sface = make_face(Polyline(*[(x0 + 2, P.RIDE_Z + 0.5), (x1, P.RIDE_Z + 0.5), (x1, 22.2)], close=True))
        d += Pos(0, y + th / 2 - (th if y == 60 else 0) + (th if y == -60 else 0), 0) * extrude(Plane.XZ * sface, th)
    for (x, y) in [(P.WB + 28, 24), (P.WB + 28, -24), (P.WB + 30, 14), (P.WB + 30, -14)]:
        d -= clear_hole(x, y, P.FLOOR_TOP - 1, 6)
    return d


# ---------------------------------------------------------------------------------------------- D53 rear underbody
def _ramp_z(x, deg):
    """Flow-side (underside) height of the diffuser plate at x: flush with the floor's underside at the tub tail."""
    import math
    return P.RIDE_Z + max(0.0, x - P.TUB_X1) * math.tan(math.radians(deg))


def _xz_prism(pts, y0, y1):
    from build123d import Polyline, make_face, extrude, Plane, Pos
    face = make_face(Polyline(*pts, close=True))
    return Pos(0, y1, 0) * extrude(Plane.XZ * face, y1 - y0)


def _csk_teardrop(x, y, z_bottom, h):
    """D53 QA: csk_hole with a 45 deg teardrop roof pointing +X. The diffuser prints stood on its leading edge (print-up is
    +X within 8-13 deg), so its Z-axis pad holes lie sideways; a round hole and countersink then need support under their
    roof (0.18-0.25 g sliced, rnd/aero/out/d53_diff_print.json). The roof is a loft of two similar triangles (tangent points
    at +-45 deg, apex at r*sqrt(2)) over the countersink and a prism over the plain hole."""
    import math
    from build123d import Polyline, make_face, extrude, loft, Plane, Pos, Sketch
    rc, rh = P.M3_CSK_D / 2, P.M3_CLEAR / 2
    hc = rc - rh                                                       # 90 deg countersink depth

    def tri(r, z):
        c = r * math.cos(math.radians(45))
        return make_face(Polyline((x + c * 0.98, y + c), (x + r * math.sqrt(2), y), (x + c * 0.98, y - c), close=True)).moved(Pos(0, 0, z))

    s = csk_hole(x, y, z_bottom, h)
    s += loft([tri(rc, z_bottom - 0.01), tri(rh, z_bottom + hc - 0.01)])
    s += extrude(tri(rh, z_bottom - 0.01), h + 0.02)
    return s


def diffuser_pad_screws():
    return [(P.DIFF_SCREW_X, P.DIFF_PAD_Y), (P.DIFF_SCREW_X, -P.DIFF_PAD_Y)]


def rear_spacer():
    """D53: 3 mm flange on the floor top under the rear-mount bar (the gap the D37-retired GT-1 diffuser flange used to
    fill: without it the mount floats 3 mm up and its floor screws stop short of their nuts). The four floor screws go
    up through the floor and this flange into square nuts in the rear-mount bar. With a diffuser fitted, a block behind
    the tub tail (under the bar's overhang) holds the diffuser's front pad: 2 flat-heads up from the flow side into
    square nuts in the block. Prints upside down (its top face, z FLOOR_TOP + 3, on the bed): nothing overhangs."""
    import anchors as AN
    x0, x1 = P.SPACER_X
    zt = P.FLOOR_TOP + 3.0
    s = box(x1 - x0, 2 * P.SPACER_HW, 3.0, x0, -P.SPACER_HW, P.FLOOR_TOP)
    if P.DIFFUSER:
        c = P.DIFFUSER_CANDS[P.DIFFUSER]
        bx0, bx1 = P.DIFF_PAD
        xb = P.BMI_R_X + 7.2                                             # rear end of the rear-mount bar (+0.2)
        hy = P.DIFF_PAD_Y + 6.0
        under = _xz_prism([(bx0 - 1, 0.0), (bx1 + 1, 0.0), (bx1 + 1, _ramp_z(bx1 + 1, c["deg"]) + P.DIFF_PAD_T),
                           (bx0 - 1, _ramp_z(bx0 - 1, c["deg"]) + P.DIFF_PAD_T)], -hy - 1, hy + 1)   # the pad and the air under it
        zs = _ramp_z(P.DIFF_SCREW_X, c["deg"]) + P.DIFF_PAD_T
        top = zs + 3.0 + 2.1 + 1.0 + 0.5                                  # nut 3 mm in, 2.1 pocket, 1 mm wall, 0.5 spare
        blk = box(xb - bx0, 2 * hy, zt - P.RIDE_Z, bx0, -hy, P.RIDE_Z) + box(bx1 - xb, 2 * hy, top - P.RIDE_Z, xb, -hy, P.RIDE_Z)
        s += blk - under
        for (x, y) in diffuser_pad_screws():
            s = AN.anchor(s, (x, y, _ramp_z(x, c["deg"]) + P.DIFF_PAD_T), (0, 0, 1), f"rear spacer diffuser pad {'L' if y > 0 else 'R'}")
    from chassis import rear_mount_holes, diffuser_holes
    for (x, y) in rear_mount_holes() + diffuser_holes():
        s -= clear_hole(x, y, P.FLOOR_TOP - 0.5, 4.0)
    return s


def diffuser_d53():
    """D53 rear diffuser (P.DIFFUSER picks the candidate the CFD kept): one flat plate from the floor's underside at the tub
    tail, fences at its edges and strakes under it, all on the flow side. Its front 14 mm is a 3 mm pad clamped under the
    rear spacer's block. PRINT (measured, rnd/aero/diffuser_print_check.py 2026-11-19): stood on its leading edge, as
    build_all exports it. Round countersunk pad holes lie sideways there and needed 0.18-0.25 g of support; with the
    teardrop countersinks (_csk_teardrop) a and c slice with 0.0 g, b with 0.06 g (its strakes)."""
    import math
    c = P.DIFFUSER_CANDS[P.DIFFUSER]
    t = math.tan(math.radians(c["deg"]))
    x0, L, T = P.TUB_X1, P.DIFFUSER_L, P.DIFFUSER_T
    x1 = x0 + L
    z0, zt = P.RIDE_Z, P.RIDE_Z + L * t
    hw = c["hw"]
    d = _xz_prism([(x0, z0), (x1, zt), (x1, zt + T), (x0, z0 + T)], -hw, hw)
    px1 = P.DIFF_PAD[1]
    d += _xz_prism([(x0, z0), (px1, _ramp_z(px1, c["deg"])), (px1, _ramp_z(px1, c["deg"]) + P.DIFF_PAD_T),
                    (x0, z0 + P.DIFF_PAD_T)], -(P.DIFF_PAD_Y + 6.0), P.DIFF_PAD_Y + 6.0)
    F = P.DIFFUSER_FIN
    for y in [hw - F, -hw] + [s - F / 2 for s in c["strakes"]] + [-s - F / 2 for s in c["strakes"]]:
        d += _xz_prism([(x0 + 2.0, z0 + 2.0 * t + 0.2), (x1, z0), (x1, zt + 0.2)], y, y + F)
    for (x, y) in diffuser_pad_screws():
        d -= _csk_teardrop(x, y, _ramp_z(x, c["deg"]) - 0.01, P.DIFF_PAD_T + 0.5)
    return d
