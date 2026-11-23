"""D34 2D shape helpers: rounded outlines, pocket patterns and their extrusion into build123d solids.

The v3 package draws every plate as a 2D outline first (shapely), rounds its corners, cuts windows with radiused
corners, and only then extrudes it. Parts stop being stacks of raw boxes and come out with the flowing outlines
of a machined/printed race chassis, while every interface stays where params.py puts it."""
import math

from build123d import Plane, Polyline, Pos, Rot, extrude, make_face, Compound
from shapely.geometry import LineString, MultiPolygon, Polygon, box as sbox, Point
from shapely.ops import unary_union
from shapely import affinity

RES = 8                                   # arc segments per quarter circle (rounded corners)


def rounded(geom, r_convex=0.0, r_concave=0.0):
    """Round the corners of a shapely polygon: convex corners by r_convex, concave (inside) corners by r_concave."""
    g = geom
    if r_concave > 0:
        g = g.buffer(r_concave, quad_segs=RES).buffer(-r_concave, quad_segs=RES)
    if r_convex > 0:
        g = g.buffer(-r_convex, quad_segs=RES).buffer(r_convex, quad_segs=RES)
    return g


def poly(pts):
    return Polygon(pts)


def mirror_half(half):
    """[(x, half_width)] -> polygon symmetric about Y = 0."""
    return Polygon([(x, w) for x, w in half] + [(x, -w) for x, w in reversed(half)])


def _polys(geom):
    if geom.is_empty:
        return []
    if isinstance(geom, Polygon):
        return [geom]
    if isinstance(geom, MultiPolygon):
        return list(geom.geoms)
    return [g for g in getattr(geom, "geoms", []) if isinstance(g, Polygon)]


def _ring_face(coords, plane=Plane.XY):
    pts = [tuple(c) for c in coords]
    if pts[0] == pts[-1]:
        pts = pts[:-1]
    # drop near-duplicate points (OCC dislikes zero-length edges)
    out = [pts[0]]
    for p in pts[1:]:
        if math.dist(p, out[-1]) > 0.02:
            out.append(p)
    if math.dist(out[0], out[-1]) < 0.02:
        out.pop()
    return make_face(Polyline(*out, close=True))


def solid(geom, z0, h):
    """Extrude a shapely (Multi)Polygon in Z from z0 by h; holes become through-holes."""
    parts = []
    for p in _polys(geom):
        s = Pos(0, 0, z0) * extrude(_ring_face(p.exterior.coords), h)
        for ring in p.interiors:
            s -= Pos(0, 0, z0 - 0.01) * extrude(_ring_face(ring.coords), h + 0.02)
        parts.append(s)
    if not parts:
        return None
    out = parts[0]
    for s in parts[1:]:
        out += s
    return out


def solid_xz(geom, y0, h):
    """Profile drawn in (X, Z), extruded along +Y from y0 by h."""
    parts = []
    for p in _polys(geom):
        f = _ring_face(p.exterior.coords)
        s = Pos(0, y0 + h, 0) * extrude(Plane.XZ * f, h)       # Plane.XZ normal is -Y
        for ring in p.interiors:
            s -= Pos(0, y0 + h + 0.01, 0) * extrude(Plane.XZ * _ring_face(ring.coords), h + 0.02)
        parts.append(s)
    out = parts[0]
    for s in parts[1:]:
        out += s
    return out


def solid_yz(geom, x0, h):
    """Profile drawn in (Y, Z), extruded along +X from x0 by h."""
    parts = []
    for p in _polys(geom):
        f = _ring_face(p.exterior.coords)
        s = Pos(x0, 0, 0) * extrude(Plane.YZ * f, h)
        for ring in p.interiors:
            s -= Pos(x0 - 0.01, 0, 0) * extrude(Plane.YZ * _ring_face(ring.coords), h + 0.02)
        parts.append(s)
    out = parts[0]
    for s in parts[1:]:
        out += s
    return out


def cutter(geom, z0, h):
    """Pockets/windows as one compound to subtract in a single boolean."""
    sols = [Pos(0, 0, z0) * extrude(_ring_face(p.exterior.coords), h) for p in _polys(geom)]
    if not sols:
        return None
    return Compound(children=sols) if len(sols) > 1 else sols[0]


def isogrid(region, pitch=22.0, rib=2.4, r=1.6, min_area=35.0, angle0=0.0, origin=(0.0, 0.0)):
    """Triangular (isogrid) pockets filling `region`: ribs `rib` wide on a 60 deg lattice of `pitch`,
    pocket corners rounded by r; slivers under min_area dropped."""
    minx, miny, maxx, maxy = region.bounds
    L = 2 * math.hypot(maxx - minx, maxy - miny) + 4 * pitch
    cx, cy = origin
    lines = []
    h = pitch * math.sqrt(3) / 2                  # line spacing for a lattice of equilateral triangles
    for k in range(3):
        a = math.radians(angle0 + 60 * k)
        d = (math.cos(a), math.sin(a))
        nrm = (-d[1], d[0])
        n = int(L / h) + 2
        for i in range(-n, n + 1):
            ox, oy = cx + nrm[0] * i * h, cy + nrm[1] * i * h
            lines.append(LineString([(ox - d[0] * L, oy - d[1] * L), (ox + d[0] * L, oy + d[1] * L)]))
    ribs = unary_union(lines).buffer(rib / 2, cap_style=2, quad_segs=2)
    pockets = region.difference(ribs)
    keep = []
    for p in _polys(pockets):
        q = rounded(p, r_convex=r)
        for qq in _polys(q):
            if qq.area >= min_area:
                keep.append(qq)
    return unary_union(keep) if keep else Polygon()


def disc(x, y, r):
    return Point(x, y).buffer(r, quad_segs=RES)


def rect(x0, y0, x1, y1):
    return sbox(min(x0, x1), min(y0, y1), max(x0, x1), max(y0, y1))


def affinity_ellipse(cx, cy, ry, rz):
    """Ellipse with semi-axes (ry, rz) centred at (cx, cy) in the sketch plane."""
    return affinity.scale(Point(cx, cy).buffer(1.0, quad_segs=24), ry, rz)
