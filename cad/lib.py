"""Shared helpers: holes, inserts, extrusions from 2D outlines."""
from build123d import (Box, Cylinder, Cone, Polyline, Polygon, make_face, extrude, Pos, Rot,
                       Location, Axis, Plane, Vector, Compound)
import params as P


def at(shape, x=0, y=0, z=0):
    return Pos(x, y, z) * shape


def cyl_z(d, h, x=0, y=0, z=0):
    """Vertical cylinder, base at z."""
    return Pos(x, y, z + h / 2) * Cylinder(d / 2, h)


def cyl_y(d, h, x=0, y=0, z=0):
    """Cylinder along Y centered at (x, y, z)."""
    return Pos(x, y, z) * Rot(90, 0, 0) * Cylinder(d / 2, h)


def cyl_x(d, h, x=0, y=0, z=0):
    return Pos(x, y, z) * Rot(0, 90, 0) * Cylinder(d / 2, h)


def box(sx, sy, sz, x=0, y=0, z=0):
    """Box with min corner at (x, y, z)."""
    return Pos(x + sx / 2, y + sy / 2, z + sz / 2) * Box(sx, sy, sz)


def cbox(sx, sy, sz, x=0, y=0, z=0):
    """Box centered in X/Y at (x, y), base at z."""
    return Pos(x, y, z + sz / 2) * Box(sx, sy, sz)


def insert_hole(x, y, z_top, depth=P.M3_INSERT_L):
    """Heat-set insert pilot opening at z_top going down."""
    return cyl_z(P.M3_INSERT_D, depth + 0.01, x, y, z_top - depth)


def clear_hole(x, y, z0, h):
    return cyl_z(P.M3_CLEAR, h + 0.02, x, y, z0 - 0.01)


def csk_hole(x, y, z_bottom, h):
    """Through hole with a 90 deg countersink opening on the underside (flat-head screw)."""
    hole = clear_hole(x, y, z_bottom, h)
    r = P.M3_CSK_D / 2
    csk = Pos(x, y, z_bottom + (r - P.M3_CLEAR / 2) / 2 - 0.01) * Cone(r, P.M3_CLEAR / 2, r - P.M3_CLEAR / 2)
    return hole + csk


def outline_solid(pts_xy, z0, h):
    """Extrude a closed XY outline from z0 by h."""
    face = make_face(Polyline(*[(x, y) for x, y in pts_xy], close=True))
    return Pos(0, 0, z0) * extrude(face, h)


def mirror_outline(half):
    """[(x, half_width)] -> closed polygon symmetric about Y=0."""
    left = [(x, w) for x, w in half]
    right = [(x, -w) for x, w in reversed(half)]
    return left + right


def clip(shape, x0=-1e4, x1=1e4, y0=-1e4, y1=1e4, z0=-1e4, z1=1e4):
    return shape & box(x1 - x0, y1 - y0, z1 - z0, x0, y0, z0)


def crush_seat_y(d, depth, x, y0, z, toward=+1, ribs=3, rib_w=1.2, crush=0.3):
    """Bearing seat along Y with crush ribs (D18): a hole d + 0.3 with `ribs` small ribs that
    stand `crush` mm proud of the bearing OD, so the bearing presses in by deforming them.
    Starts at y0 and goes `depth` in the `toward` direction."""
    import math
    from build123d import Box
    rh = (d + 0.3) / 2
    hole = Cylinder(rh, depth)
    t = rh - (d / 2 - crush)                       # rib height
    for k in range(ribs):
        a = 360.0 / ribs * k + 90
        hole -= Rot(0, 0, a) * Pos(rh - t / 2 + 0.05, 0, 0) * Box(t + 0.1, rib_w, depth + 0.2)
    return Pos(x, y0 + toward * depth / 2, z) * Rot(90, 0, 0) * hole


def rod(p1, p2, d):
    """Cylinder of diameter d from point p1 to point p2."""
    import math
    from build123d import Location, Vector
    a, b = Vector(*p1), Vector(*p2)
    v = b - a
    L = v.length
    c = Cylinder(d / 2, L)                          # along Z, centred
    z = Vector(0, 0, 1)
    axis = z.cross(v)
    ang = math.degrees(math.acos(max(-1, min(1, z.dot(v) / L))))
    loc = Location((a + b) * 0.5)
    if axis.length > 1e-9:
        c = c.rotate(Axis((0, 0, 0), axis.normalized()), ang)
    return loc * c


def magnet_pocket_z(x, y, z0, h=None, d=10.0, ribs=4, rib_w=1.2, crush=0.08):
    """D36 press-fit magnet pocket along +Z from z0: hole d + 0.3 with `ribs` crush ribs standing `crush` mm
    inside the magnet OD, so a 10 x 3 disc presses in and stays without glue (same idea as the bearing seats)."""
    from build123d import Box
    h = P.MAGNET_T if h is None else h
    rh = (d + 0.3) / 2
    hole = Cylinder(rh, h)
    t = rh - (d / 2 - crush)
    for k in range(ribs):
        hole -= Rot(0, 0, 360.0 / ribs * k + 45) * Pos(rh - t / 2 + 0.05, 0, 0) * Box(t + 0.1, rib_w, h + 0.2)
    return Pos(x, y, z0 + h / 2) * hole
