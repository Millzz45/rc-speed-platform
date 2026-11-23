#!/usr/bin/env python3
"""D56 body "GT-2": an ORIGINAL printable GT coupe shell for the customer car (owner pick 2026-11-21: option (b)).
Drawn from scratch as numbers in this file: no scanned, traced or licensed model, no brand styling, no logo.

Shape: a low GT coupe on the car's own chassis. Every value is a table below (x rear from the front axle, y left,
z up, mm, ground at z 0):
  main body  superellipse sections, half-width HALF_W(x), top TOP_Z(x), exponent N_MAIN(x)
  fenders    raised pods over each wheel (centre y POD_Y), so the hood and deck sit lower than the wheel tops
  cabin      a fastback greenhouse, half-width CAB_W(x), top CAB_Z(x)
  tail       a cut-off (Kamm) tail with exit slots; integrated 12 mm splitter blade at the nose
Skin = union of the outer lofts minus the union of the same lofts offset inward by GT2_T along their own 3D surface
normals (exact wall on the smooth surface), opened below BODY_SKIRT_Z, wheel arches and the tyre sweep cut out.

Assembly (rules: no glue; every threaded point is a DIN 934 M3 hex nut in a printed pocket; screws hidden):
  6 panels (front/mid/rear x left/right) that fit the 176 mm bed standing upright.
  Seams: a 1.2 mm joggle-lap flange on one panel runs 7 mm under its neighbour (flush skin, no light gap); paired
  blocks inside the skin meet at the seam and take one M3 x 12 across it into a captive hex nut.
  Mount: the car's BMI-1 interface unchanged (front tongue under the chassis hook lips, rear quarter-turn keys,
  10 x 3 magnets for alignment), on two carrier plates fixed to the shell by M3 x 12 from below into captive nuts.
  Wing: an original NACA 6412 wing (inverted) with flat end plates on two legs; each leg's peg drops into a socket
  boss under the deck and one M3 x 10 from below locks it into a captive nut in the peg.

  cd cad && ../.venv/bin/python body_gt2.py            # build, check, export to out/body_gt2/
  cd cad && ../.venv/bin/python body_gt2.py --skin     # skin + chassis clearance only (fast iteration)
"""
import argparse, json, math, os, sys, time
import numpy as np
import trimesh
import manifold3d as mf
from scipy.interpolate import PchipInterpolator

HERE = os.path.dirname(os.path.abspath(__file__))
PROJ = os.path.dirname(HERE)
sys.path.insert(0, HERE)
import params as P  # noqa: E402

OUT = os.path.join(PROJ, "out", "body_gt2")
CACHE = os.path.join(OUT, "cache")
PFX = "gt2"
T = getattr(P, "GT2_T", 1.2)          # wall: 2 lines on a 0.6 mm nozzle, 3 on a 0.4
CLR = 1.0                              # air kept between the shell (and anything on it) and every chassis part
SKIRT = P.BODY_SKIRT_Z
BED_LIM = min(P.BED[0], P.BED[1]) - 2 * P.BED_MARGIN

# ---------------------------------------------------------------- style tables (x, value)
X0, X1 = -92.0, 338.0
HALF_W = [(-92, 44), (-91.2, 54), (-89.5, 62), (-86.5, 69), (-82, 75), (-76, 80.5), (-66, 86), (-54, 90), (-40, 92.5),
          (-20, 93.5), (0, 93.5), (12, 93), (30, 91), (55, 88.5), (90, 87.5), (130, 87.5), (170, 88.5), (205, 91),
          (232, 93), (263, 93.5), (288, 93), (308, 90.5), (322, 86.5), (332, 81), (338, 76)]
TOP_Z = [(-92, 15), (-91.2, 19), (-89.5, 22.5), (-86.5, 25.5), (-81, 29), (-71, 35), (-60, 42), (-50, 49), (-40, 56.5),
         (-30, 63.5), (-22, 66.3), (-12, 68.5), (0, 71), (15, 74.5), (30, 77), (50, 76), (90, 72), (150, 71), (200, 71.5),
         (235, 72.5), (263, 73), (290, 72), (310, 68.5), (325, 64), (333, 60.5), (338, 58)]
N_MAIN = [(-92, 2.6), (-70, 3.0), (-30, 3.6), (40, 4.0), (200, 4.0), (290, 3.6), (338, 3.2)]
Z_BOT = -12.0                          # every loft closes below the ground; the skirt cut opens the shell
# fender pods: centre |y|, half-width, top (front pair round x 0, rear pair round x WB)
POD_Y = 70.0
POD_F = dict(x=[-74, -60, -42, -22, 0, 18, 34, 48, 60], b=[4, 13, 20, 25, 26, 25, 21, 14, 4],
             z=[18, 40, 60, 73, 79, 77, 69, 56, 34], n=3.0, zb=18.0)
POD_R = dict(x=[198, 212, 228, 246, 263, 282, 300, 316, 330], b=[4, 14, 21, 25, 25.5, 25, 22, 14, 4],
             z=[40, 58, 70, 77, 79, 77.5, 73, 62, 44], n=3.0, zb=18.0)
# cabin (greenhouse): fastback roof into the deck
CAB_X = [18, 28, 42, 62, 90, 120, 150, 180, 205, 226, 246, 262]
CAB_W = [44, 56, 63, 67.5, 69.5, 70, 69.5, 67, 62, 54, 44, 30]
CAB_Z = [72, 82.5, 92, 100.5, 106.5, 108.5, 108, 104.5, 98, 89.5, 80.5, 69]
N_CAB = 2.5
CAB_ZB = 40.0
NPTS = 144                             # points round every section


def pchip(tab):
    xs, vs = zip(*tab) if isinstance(tab[0], tuple) else tab
    return PchipInterpolator(np.asarray(xs, float), np.asarray(vs, float), extrapolate=True)


# ---------------------------------------------------------------- loft machinery
def _ring(yc, zc, a, h, n, npts=NPTS):
    """Superellipse ring in the y-z plane, counter-clockwise seen from +x (outward normals when lofted along +x)."""
    t = np.linspace(0, 2 * np.pi, npts, endpoint=False)
    c, s = np.cos(t), np.sin(t)
    y = yc + a * np.sign(c) * np.abs(c) ** (2 / n)
    z = zc + h * np.sign(s) * np.abs(s) ** (2 / n)
    return y, z


def loft_grid(xs, sec):
    """xs: ring stations; sec(x) -> (yc, zc, a, h, n). Returns P[i, j, 3]."""
    out = np.zeros((len(xs), NPTS, 3))
    for i, x in enumerate(xs):
        yc, zc, a, h, n = sec(x)
        y, z = _ring(yc, zc, max(a, 0.05), max(h, 0.05), n)
        out[i, :, 0], out[i, :, 1], out[i, :, 2] = x, y, z
    return out


def grid_normals(G):
    """Outward unit normals of a lofted ring grid (central differences; one-sided at the end rings)."""
    tr = np.roll(G, -1, axis=1) - np.roll(G, 1, axis=1)                      # along the ring
    tx = np.zeros_like(G)
    tx[1:-1] = G[2:] - G[:-2]
    tx[0], tx[-1] = G[1] - G[0], G[-1] - G[-2]
    n = np.cross(tx, tr)
    c = G.mean(axis=1, keepdims=True)
    flip = np.sum(n * (G - c), axis=2) < 0
    n[flip] *= -1
    return n / (np.linalg.norm(n, axis=2, keepdims=True) + 1e-12)


def grid_to_mf(G):
    """Close a ring grid into a solid: quads between rings, fans at both end rings."""
    nr, npts = G.shape[:2]
    V = G.reshape(-1, 3)
    c0, c1 = G[0].mean(0), G[-1].mean(0)
    V = np.vstack([V, c0, c1])
    i0, i1 = nr * npts, nr * npts + 1
    F = []
    for i in range(nr - 1):
        a = i * npts + np.arange(npts)
        b = i * npts + (np.arange(npts) + 1) % npts
        c = (i + 1) * npts + (np.arange(npts) + 1) % npts
        d = (i + 1) * npts + np.arange(npts)
        F.append(np.column_stack([a, d, c]))
        F.append(np.column_stack([a, c, b]))
    j = np.arange(npts)
    F.append(np.column_stack([np.full(npts, i0), j, (j + 1) % npts]))
    F.append(np.column_stack([np.full(npts, i1), (nr - 1) * npts + (j + 1) % npts, (nr - 1) * npts + j]))
    F = np.vstack(F)
    m = trimesh.Trimesh(V, F, process=False)
    if m.volume < 0:
        F = F[:, ::-1]
    M = mf.Manifold(mf.Mesh(vert_properties=np.asarray(V, np.float32), tri_verts=np.asarray(F, np.uint32)))
    if M.status() != mf.Error.NoError:
        raise RuntimeError(f"loft not manifold: {M.status()}")
    return M


def offset_loft(G, d, x_lo=None, x_hi=None):
    """The loft grid moved inward by d along its surface normals; rings whose moved points pass x_lo / x_hi are
    dropped (the solid nose lip / tail edge stays full)."""
    if d == 0:
        return grid_to_mf(G)
    Q = G - d * grid_normals(G)
    keep = np.ones(len(Q), bool)
    if x_lo is not None:
        keep &= Q[:, :, 0].min(1) >= x_lo
    if x_hi is not None:
        keep &= Q[:, :, 0].max(1) <= x_hi
    idx = np.nonzero(keep)[0]
    return grid_to_mf(Q[idx[0]:idx[-1] + 1])


def stations(x0, x1, fine=1.0, coarse=2.0, fine_len=14.0):
    """Ring x positions: fine near both ends (where the nose / tail round off), coarse between."""
    a = np.arange(x0, x0 + fine_len, fine)
    b = np.arange(x0 + fine_len, x1 - fine_len, coarse)
    c = np.arange(x1 - fine_len, x1 + 1e-6, fine)
    return np.unique(np.round(np.concatenate([a, b, c, [x1]]), 4))


_hw, _tz, _nm = pchip(HALF_W), pchip(TOP_Z), pchip(N_MAIN)


def sec_main(x):
    a, top, n = float(_hw(x)), float(_tz(x)), float(_nm(x))
    return 0.0, (top + Z_BOT) / 2, a, (top - Z_BOT) / 2, n


def _pod_sec(pod, sgn):
    fb, fz = PchipInterpolator(pod["x"], pod["b"]), PchipInterpolator(pod["x"], pod["z"])

    def sec(x):
        top = float(fz(x))
        return sgn * POD_Y, (top + pod["zb"]) / 2, float(fb(x)), (top - pod["zb"]) / 2, pod["n"]
    return sec


_cw, _cz = PchipInterpolator(CAB_X, CAB_W), PchipInterpolator(CAB_X, CAB_Z)


def sec_cab(x):
    top = float(_cz(x))
    return 0.0, (top + CAB_ZB) / 2, float(_cw(x)), (top - CAB_ZB) / 2, N_CAB


def grids():
    g = {"main": loft_grid(stations(X0, X1), sec_main)}
    for nm, pod in (("podF", POD_F), ("podR", POD_R)):
        for sgn, sd in ((1, "L"), (-1, "R")):
            g[f"{nm}_{sd}"] = loft_grid(stations(pod["x"][0], pod["x"][-1], 1.0, 2.0, 6.0), _pod_sec(pod, sgn))
    g["cab"] = loft_grid(stations(CAB_X[0], CAB_X[-1], 1.0, 2.0, 6.0), sec_cab)
    return g


_GRIDS = None


def solid(d=0.0):
    """Union of every loft moved inward by d (d = 0: the outer body)."""
    global _GRIDS
    if _GRIDS is None:
        _GRIDS = grids()
    parts = []
    for k, G in _GRIDS.items():
        if k == "main":
            parts.append(offset_loft(G, d, X0 + d + 0.5 if d else None, X1 - d - 0.5 if d else None))
        else:
            parts.append(offset_loft(G, d))
    return mf.Manifold.batch_boolean(parts, mf.OpType.Add)


# ---------------------------------------------------------------- helpers
def box(sx, sy, sz, x0, y0, z0):
    return mf.Manifold.cube((sx, sy, sz)).translate((x0, y0, z0))


def cbox(sx, sy, sz, cx, cy, z0):
    return box(sx, sy, sz, cx - sx / 2, cy - sy / 2, z0)


def cyl(p0, axis, r, L, seg=40):
    """Cylinder of radius r from p0 along unit axis, length L."""
    axis = np.asarray(axis, float) / np.linalg.norm(axis)
    c = mf.Manifold.cylinder(L, r, r, seg)
    return c.transform(_frame(axis, p0))


def hexprism(p0, axis, af, L, spin=0.0):
    """Hex prism (across flats af) from p0 along axis, length L; spin turns it about the axis (deg)."""
    axis = np.asarray(axis, float) / np.linalg.norm(axis)
    rc = af / math.sqrt(3)
    c = mf.Manifold.cylinder(L, rc, rc, 6).rotate((0, 0, 30 + spin))
    return c.transform(_frame(axis, p0))


def _frame(axis, p0):
    z = np.asarray(axis, float)
    t = np.array([1.0, 0, 0]) if abs(z[0]) < 0.9 else np.array([0, 1.0, 0])
    x = np.cross(t, z); x /= np.linalg.norm(x)
    y = np.cross(z, x)
    return [[x[0], y[0], z[0], p0[0]], [x[1], y[1], z[1], p0[1]], [x[2], y[2], z[2], p0[2]]]


def to_tm(M):
    m = M.to_mesh()
    return trimesh.Trimesh(np.asarray(m.vert_properties)[:, :3], np.asarray(m.tri_verts), process=False)


def from_tm(m):
    return mf.Manifold(mf.Mesh(vert_properties=np.asarray(m.vertices, np.float32), tri_verts=np.asarray(m.faces, np.uint32)))


def stl_clean(M):
    """D56: the mesh as an STL reader sees it: vertices merged by position (float32), rebuilt as a manifold and its
    sub-micron slivers collapsed. Without this 5 of 6 panels were not watertight once written (touching features keep
    separate vertices in the manifold; merged by position in the STL they pinch). Falls back to M if the rebuild fails."""
    t = to_tm(M)
    t = trimesh.Trimesh(np.asarray(t.vertices, np.float32), t.faces, process=True)
    R = from_tm(t)
    return R.simplify(1e-3) if R.status() == mf.Error.NoError else M


def largest(M):
    comps = M.decompose()
    return max(comps, key=lambda c: c.volume()) if len(comps) > 1 else M


def from_b3d(shape, tol=0.25):
    v, f = shape.tessellate(tol, 0.3)
    m = trimesh.Trimesh(np.array([[p.X, p.Y, p.Z] for p in v]), np.array(f), process=True)
    m.merge_vertices(digits_vertex=4)
    trimesh.repair.fix_normals(m)
    out = from_tm(m)
    if out.status() != mf.Error.NoError:
        raise RuntimeError(f"tessellated shape is not manifold: {out.status()}")
    return out


# ---------------------------------------------------------------- chassis (cached: the parts take ~4 min to build)
def _src_stamp():
    fs = ["params.py", "chassis.py", "running_gear.py", "wheels.py", "anchors.py", "lib.py", "check_fit.py", "coupons.py"]
    return max(os.path.getmtime(os.path.join(HERE, f)) for f in fs if os.path.exists(os.path.join(HERE, f)))


def chassis(rebuild=False):
    """{name: Manifold} of every fitted chassis part in the car frame, plus 'keep1'/'keep2' = the tyre sweep
    keep-outs grown 1 / 2 mm (steering lock + suspension travel)."""
    os.makedirs(CACHE, exist_ok=True)
    f = os.path.join(CACHE, "chassis.npz")
    if os.path.exists(f) and not rebuild and os.path.getmtime(f) > _src_stamp():
        z = np.load(f)
        names = [k[:-2] for k in z.files if k.endswith("_v")]
        return {n: mf.Manifold(mf.Mesh(vert_properties=z[n + "_v"].astype(np.float32), tri_verts=z[n + "_f"].astype(np.uint32))) for n in names}
    import check_fit as CF
    import wheels as Wh
    t0 = time.time()
    out = {}
    for n, shp in CF.parts(body=False).items():
        if n in ("tire_sweep", "gasket", "splitter", "diffuser"):
            continue
        out[n] = from_b3d(shp, 0.3)
    out["keep1"] = from_b3d(Wh.keepouts(1.0), 0.4)
    out["keep2"] = from_b3d(Wh.keepouts(2.0), 0.4)
    arr = {}
    for n, M in out.items():
        m = M.to_mesh()
        arr[n + "_v"], arr[n + "_f"] = np.asarray(m.vert_properties)[:, :3], np.asarray(m.tri_verts)
    np.savez_compressed(f, **arr)
    print(f"chassis: {len(out) - 2} parts cached ({time.time() - t0:.0f} s)")
    return out


def chassis_union(ch):
    return mf.Manifold.batch_boolean([M for n, M in ch.items() if not n.startswith("keep")], mf.OpType.Add)


H_SAMP = 0.35                          # surface sample spacing for the distance checks (error <= ~H_SAMP / 2 [sampling])


def dense(tm, h=H_SAMP, cap=4_000_000):
    n = int(min(cap, max(2000, 2.5 * tm.area / (h * h))))
    p, _ = trimesh.sample.sample_surface(tm, n, seed=7)
    return np.vstack([np.asarray(tm.vertices), p])


class Near:
    """Distance to a surface from dense surface samples and a KD-tree (trimesh's closest-point query took this build
    to 9.7 GB). Penetration is checked separately and exactly with manifold intersections."""
    def __init__(self, tm, h=H_SAMP):
        from scipy.spatial import cKDTree
        self.tree = cKDTree(dense(tm, h))

    def dist(self, pts, ub=6.0):
        """Distance to the surface, capped at ub (the search stops there: only small gaps matter)."""
        d = self.tree.query(np.asarray(pts, float), k=1, distance_upper_bound=ub)[0]
        return np.minimum(d, ub)


def clearance(shell, ch, worst=12):
    """Gap from every chassis part to the shell: exact overlap volume (manifold) + the smallest sampled distance.
    Returns {part: (overlap_mm3, gap_mm)}, list of the worst points under CLR."""
    near = Near(to_tm(shell))
    b = shell.bounding_box()
    res, bad = {}, []
    for n, M in ch.items():
        if n.startswith("keep"):
            continue
        ov = (shell ^ M).volume()
        pts = dense(to_tm(M), 0.5, 400_000)
        sel = np.all((pts > np.array(b[:3]) - 3) & (pts < np.array(b[3:]) + 3), axis=1)
        pts = pts[sel]
        if not len(pts):
            continue
        g = near.dist(pts)
        res[n] = (round(ov, 2), round(float(g.min()), 2))
        for k in np.argsort(g)[:2]:
            if g[k] < CLR or ov > 0:
                bad.append((round(float(g[k]), 2), round(ov, 1), n, tuple(np.round(pts[k], 1))))
    bad.sort()
    return res, bad[:worst]


# ---------------------------------------------------------------- skin
ARCH_Y0 = 62.0                         # the clean arch cut runs from here outward; inboard, the sweep itself is cut


def arch_cuts(ch=None):
    """Wheel openings as clean shapes: per wheel, the convex outline (side view) of the tyre's full sweep (steering
    lock + travel, the 2 mm keep-out) outboard of ARCH_Y0, together with a circle 4 mm round the tyre, grown 1.5 mm
    and extruded across the fender. The sweep itself never touches the visible skin, so the arch edge is one smooth
    convex curve."""
    from shapely.geometry import MultiPoint, Point
    out = []
    kv = np.asarray(to_tm(ch["keep2"]).vertices) if ch is not None else np.zeros((0, 3))
    for ax in (0.0, P.WB):
        for sgn in (1, -1):
            sel = (np.abs(kv[:, 0] - ax) < 90) & (kv[:, 1] * sgn >= ARCH_Y0 - 6)
            pts = [tuple(p) for p in kv[sel][:, [0, 2]]]
            circ = Point(ax, P.TIRE_D / 2).buffer(P.TIRE_D / 2 + 4.0, 64)
            hull = MultiPoint(pts).convex_hull.union(circ).convex_hull.buffer(1.5, 32) if pts else circ
            poly = np.asarray(hull.exterior.coords)[:-1]
            if not MultiPoint([tuple(q) for q in poly]).convex_hull.exterior.is_ccw:
                poly = poly[::-1]
            sec = mf.CrossSection([poly], mf.FillRule.Positive)
            e = mf.Manifold.extrude(sec, 80.0)                      # x-z outline extruded along local z
            e = e.transform([[1, 0, 0, 0], [0, 0, -1, 0], [0, 1, 0, 0]])   # local (x, y, z) -> (x, -z, y): along -y
            e = e.translate((0, sgn * ARCH_Y0 + (80.0 if sgn > 0 else 0.0), 0))
            out.append(e)
    return mf.Manifold.batch_boolean(out, mf.OpType.Add)


def skin(ch=None):
    t0 = time.time()
    outer = solid(0.0)
    inner = solid(T)
    raw = outer - inner
    raw = raw - box(1000, 1000, 100, -500, -500, SKIRT - 100)            # open below the skirt
    raw = raw - arch_cuts(ch)
    if ch is not None:
        raw = raw - ch["keep2"]                          # inboard of the arch cut only (hidden wheel-well walls)
    print(f"skin: {raw.num_tri()} tris, {raw.volume() / 1000:.1f} cm3 ({time.time() - t0:.1f} s)")
    return outer, inner, raw


def wall_report(outer, inner, n=6000):
    """Wall thickness measured, not assumed: from points on the outer surface, the distance to the inner surface
    along the inward normal (rays), where the skin is kept (above the skirt)."""
    o, i = to_tm(outer), to_tm(inner)
    pts, fi = trimesh.sample.sample_surface(o, n, seed=2)
    nrm = o.face_normals[fi]
    sel = pts[:, 2] > SKIRT + 3
    pts, nrm = pts[sel], nrm[sel]
    loc, ir, _ = i.ray.intersects_location(pts + 0.01 * (-nrm), -nrm, multiple_hits=False)
    d = np.full(len(pts), np.nan)
    d[ir] = np.linalg.norm(loc - pts[ir], axis=1)
    d = d[np.isfinite(d) & (d < 20)]
    return dict(n=int(len(d)), p1=round(float(np.percentile(d, 1)), 3), p50=round(float(np.median(d)), 3),
                p99=round(float(np.percentile(d, 99)), 3), min=round(float(d.min()), 3))


# ---------------------------------------------------------------- vents and splitter
SPLIT_BLADE = 12.0                     # splitter blade ahead of the nose skin (the owner's milder 12 mm, D49)
SPLIT_T = 2.0


def vents():
    """Functional openings: front-fender louvres over the wheel's rear quarter (wheel-well pressure out = less
    front lift), side exits behind the front wheels, Kamm-tail exit slots (cavity air out)."""
    v = []
    for sgn in (1, -1):
        for x in (14.0, 22.0, 30.0):
            v.append(cbox(4.0, 18.0, 40.0, x, sgn * POD_Y, 60.0))
        for x in (46.0, 54.0, 62.0):
            v.append(cbox(4.0, 24.0, 18.0, x, sgn * 92.0, 30.0))
        for k in range(3):                                         # Kamm-tail exit louvres: 3 horizontal slots a side
            v.append(cbox(10.0, 40.0, 4.0, X1, sgn * 40.0, 14.0 + 7.0 * k))
    return mf.Manifold.batch_boolean(v, mf.OpType.Add)


def splitter(outer):
    """Flat blade at the skirt: the body's footprint just above the skirt, grown SPLIT_BLADE ahead of the nose and
    tapering out along the sides before the front arch, plus a 6 mm ledge inside the skin that fuses it on."""
    from shapely.geometry import Polygon, MultiPolygon, box as sbox
    from shapely.ops import unary_union
    cs = outer.slice(SKIRT + 0.6)
    polys = [Polygon(p) for p in cs.to_polygons()]
    foot = unary_union([p for p in polys if p.area > 100]).buffer(0)
    grown = foot.buffer(SPLIT_BLADE, join_style=1)
    zone = sbox(X0 - SPLIT_BLADE - 5, -200, -42.0, 200)               # ahead of the front arch only
    taper = Polygon([(-42.0, -200), (-30.0, -200), (-30.0, 200), (-42.0, 200)])
    blade = (grown.intersection(zone) - foot.buffer(-6.0)).buffer(0)
    blade = blade.intersection(foot.buffer(SPLIT_BLADE).union(foot)) if blade.area else blade
    blade = blade - taper
    geoms = list(blade.geoms) if isinstance(blade, MultiPolygon) else [blade]
    pl = [np.asarray(g.exterior.coords)[:-1] for g in geoms if g.area > 50]
    sec = mf.CrossSection([p[::-1] if Polygon(p).exterior.is_ccw is False else p for p in pl], mf.FillRule.Positive)
    return mf.Manifold.extrude(sec, SPLIT_T).translate((0, 0, SKIRT))


# ---------------------------------------------------------------- panels and seams
SEAM_X = (64.0, 196.0)                 # transverse cuts: windscreen base / behind the cabin, clear of both arches
FL, FL_T = 7.0, 1.2                    # flange: reaches 7 mm under the neighbour, 1.2 mm thick
SEAM_GAP = 0.15
BLK_W, BLK_D = 10.0, 9.0               # seam block: across the seam line x into the car
BLK_A, BLK_B = 6.0, 8.0                # block length on the head side / the nut side of the seam
NUT_AT = 3.5                           # nut centre past the seam (M3 x 12 from the head face: tip 1.15 mm past the nut)
HOLE_R = 1.7                           # M3 clearance
STN_STEP = 44.0                        # station spacing along a seam (mm of arc)


def _frame_tnu(p, n, u):
    """Local frame: X = t = n x u, Y = n (into the car), Z = u (screw axis, head side -> nut side)."""
    n = np.asarray(n, float); n /= np.linalg.norm(n)
    u = np.asarray(u, float); u = u - n * np.dot(u, n); u /= np.linalg.norm(u)
    t = np.cross(n, u)
    return [[t[0], n[0], u[0], p[0]], [t[1], n[1], u[1], p[1]], [t[2], n[2], u[2], p[2]]]


def _lbox(M, x0, x1, y0, y1, z0, z1):
    return box(x1 - x0, y1 - y0, z1 - z0, x0, y0, z0).transform(M)


def station(p, n, u, outer):
    """Seam screw station at p (on the inner skin surface, on the seam), n into the car, u across the seam from the
    head side to the nut side. Returns (head_block, nut_block, holes, flange_notch)."""
    M = _frame_tnu(p, n, u)
    hb = _lbox(M, -BLK_W / 2, BLK_W / 2, -0.6, BLK_D, -BLK_A, -SEAM_GAP) ^ outer
    nb = _lbox(M, -BLK_W / 2, BLK_W / 2, -0.6, BLK_D, SEAM_GAP, BLK_B) ^ outer
    yc = BLK_D / 2 + 0.3
    hole = mf.Manifold.cylinder(BLK_A + BLK_B + 2, HOLE_R, HOLE_R, 32).translate((0, yc, -BLK_A - 1)).transform(M)
    import anchors as AN
    nut = mf.Manifold.cylinder(AN.POCKET_N, AN.POCKET_S / math.sqrt(3), AN.POCKET_S / math.sqrt(3), 6).rotate((0, 0, 30)) \
        .translate((0, yc, NUT_AT - AN.POCKET_N / 2)).transform(M)
    slot = _lbox(M, -AN.POCKET_S / 2, AN.POCKET_S / 2, yc, BLK_D + 2, NUT_AT - AN.POCKET_N / 2, NUT_AT + AN.POCKET_N / 2)
    notch = _lbox(M, -BLK_W / 2 - 0.3, BLK_W / 2 + 0.3, -2.0, BLK_D + 1, -BLK_A - 0.3, 0.0)
    return hb, nb, hole + nut + slot, notch


def _arc_points(poly, step, first=10.0, last=6.0):
    """Points every `step` mm of arc along an open polyline, starting `first` mm in, ending `last` mm short."""
    seg = np.linalg.norm(np.diff(poly, axis=0), axis=1)
    s = np.concatenate([[0], np.cumsum(seg)])
    L = s[-1]
    if L < first + last:
        return [], []
    want = np.arange(first, L - last + 1e-6, step)
    if len(want) and L - last - want[-1] > step * 0.6:
        want = np.append(want, L - last)
    pts = np.column_stack([np.interp(want, s, poly[:, k]) for k in range(poly.shape[1])])
    tan = np.column_stack([np.interp(want + 0.5, s, poly[:, k]) - np.interp(want - 0.5, s, poly[:, k]) for k in range(poly.shape[1])])
    return pts, tan


def transverse_seam_curve(inner_tm, cx, sgn):
    """The inner skin's section at x = cx on one side (y*sgn >= 0), ordered from the skirt up to the centre line:
    returns (N, 2) y, z."""
    sec = inner_tm.section(plane_origin=(cx, 0, 0), plane_normal=(1, 0, 0))
    best = None
    for ent in sec.discrete:
        yz = ent[:, 1:]
        if best is None or len(yz) > len(best):
            best = yz
    yz = best
    keep = (yz[:, 0] * sgn >= -0.01) & (yz[:, 1] >= SKIRT + 2)
    pts = yz[keep]
    # order by angle about a point low on the centre line, from the skirt (side) up over to the centre
    ang = np.arctan2(pts[:, 1] - 20.0, pts[:, 0] * sgn)
    return pts[np.argsort(ang)]


CARRIER_ZONES = (box(-35.5 + 90, 300, P.CARRIER_T + 2, -90, -150, P.BMI_F_Z - 2.0 - P.CARRIER_T)
                 + box(P.WB + 60 - (P.BMI_R_X - 17.5) + 2, 300, P.CARRIER_T + 2, P.BMI_R_X - 18.5, -150, P.BMI_R_Z - 1))


def seams(outer, inner_tm, ch_u, near_ch):
    """Station list: (panel_head, panel_nut, p, n, u) for both transverse seams and the centre seam."""
    out = []

    def clear(p, n, u):
        # the block pair must not touch the chassis (exact) and keep CLR + 0.5 of air to it (sampled)
        M = _frame_tnu(p, n, u)
        blk = _lbox(M, -BLK_W / 2, BLK_W / 2, -0.6, BLK_D, -BLK_A, BLK_B)
        if not (blk ^ (ch_u + CARRIER_ZONES)).is_empty():
            return False
        return bool(near_ch.dist(dense(to_tm(blk), 1.0, 5000)).min() >= CLR + 0.5)
    names = ("front", "mid", "rear")
    for i, cx in enumerate(SEAM_X):
        for sgn, sd in ((1, "L"), (-1, "R")):
            yz = transverse_seam_curve(inner_tm, cx, sgn)
            pts, tan = _arc_points(yz, STN_STEP, first=12.0, last=14.0)
            for q, tg in zip(pts, tan):
                p = np.array([cx, q[0], q[1]])
                nrm = np.array([0.0, -tg[1], tg[0]])
                c = np.array([cx, 0.0, 30.0])
                if np.dot(nrm, c - p) < 0:
                    nrm = -nrm
                if abs(p[1]) < 12:                      # the centre seam's own stations sit there
                    continue
                if clear(p, nrm, (1, 0, 0)):
                    out.append((f"{names[i]}_{sd}", f"{names[i + 1]}_{sd}", p, nrm, np.array([1.0, 0, 0])))
    # centre seam: along the top centre line, every STN_STEP, per section; + one on the Kamm tail face
    xs_sec = [X0, SEAM_X[0], SEAM_X[1], X1]
    for i, nm in enumerate(names):
        xa, xb = xs_sec[i] + (FL + 8 if i else 10.0), xs_sec[i + 1] - (FL + 8 if i < 2 else 12.0)
        cands = np.arange(xa, xb + 1e-6, 4.0)
        hits = []
        for x in cands:
            loc, _, fi = inner_tm.ray.intersects_location([[x, 0.0, 300.0]], [[0, 0, -1.0]], multiple_hits=False)
            if len(loc):
                f_n = inner_tm.face_normals[fi[0]]
                n = -f_n if f_n[2] > 0 else f_n                 # into the car = down-ish
                hits.append((x, loc[0], n))
        picked, last = [], -1e9
        for x, p, n in hits:
            if x - last >= STN_STEP and clear(p, n, (0, -1, 0)):
                picked.append((p, n)); last = x
        if len(picked) < 2 and hits:                       # every panel pair gets at least two
            for x, p, n in hits[::-1]:
                if all(abs(x - q[0][0]) > 20 for q in picked) and clear(p, n, (0, -1, 0)):
                    picked.append((p, n))
                    if len(picked) >= 2:
                        break
        for p, n in picked:
            out.append((f"{nm}_L", f"{nm}_R", p, n, np.array([0.0, -1.0, 0])))
    p = np.array([X1 - T, 0.0, 34.0])
    out.append(("rear_L", "rear_R", p, np.array([-1.0, 0, 0]), np.array([0.0, -1.0, 0])))
    return out


def panel_boxes():
    xs = [X0 - SPLIT_BLADE - 6, SEAM_X[0], SEAM_X[1], X1 + 6]
    out = {}
    for i, nm in enumerate(("front", "mid", "rear")):
        for sd, (y0, y1) in (("L", (0.0, 150.0)), ("R", (-150.0, 0.0))):
            out[f"{nm}_{sd}"] = box(xs[i + 1] - xs[i], y1 - y0, 400, xs[i], y0, -50)
    return out, xs


def flanges(shell_cut):
    """Joggle-lap flange per panel: a FL_T band under the skin, fused into its own panel (0.2 mm into the skin) and
    reaching FL under the neighbour with SEAM_GAP of air to that neighbour's skin.
    Transverse seams: the panel BEHIND owns it. Centre seam: the RIGHT-hand panel owns it."""
    own = solid(T - 0.2) - solid(T + FL_T)
    nbr = solid(T + SEAM_GAP) - solid(T + SEAM_GAP + FL_T)
    own, nbr = own - shell_cut, nbr - shell_cut
    floor = box(1000, 1000, 400, -500, -500, SKIRT + SPLIT_T + 0.3)          # flanges stop above the splitter blade
    own, nbr = own ^ floor, nbr ^ floor
    big = lambda x0, x1, y0, y1: box(x1 - x0, y1 - y0, 400, x0, y0, -50)   # noqa: E731
    _, xs = panel_boxes()
    names = ("front", "mid", "rear")
    fl = {f"{n}_{s}": [] for n in names for s in "LR"}
    for i, cx in enumerate(SEAM_X):
        for sd, (y0, y1) in (("L", (0.0, 150.0)), ("R", (-150.0, 0.0))):
            fl[f"{names[i + 1]}_{sd}"] += [own ^ big(cx, cx + FL, y0, y1), nbr ^ big(cx - FL, cx + 0.5, y0, y1)]   # 0.5 mm overlap fuses the two bands
    for j, n in enumerate(names):
        x0 = xs[j] + (FL + 1 if j else 0.0)
        x1 = xs[j + 1] - (FL + 1 if j < 2 else 0.0)
        fl[f"{n}_R"] += [own ^ big(x0, x1, -FL, 0.0), nbr ^ big(x0, x1, -0.5, FL)]
    return {k: mf.Manifold.batch_boolean(v, mf.OpType.Add) for k, v in fl.items() if v}


# ---------------------------------------------------------------- carriers (BMI-1) and their screw columns
COL_R = 5.0
COL_SCREW = 12.0                        # M3 x 12 from under the carrier plate


def _ray_up(tm, x, y, z):
    loc, _, _ = tm.ray.intersects_location([[x, y, z]], [[0, 0, 1.0]], multiple_hits=False)
    return float(loc[0][2]) if len(loc) else None


def column(x, y, z_plate_top, z_skin, outer):
    """Screw column hanging from the skin to 0.3 mm above a carrier plate, with a captive hex nut 4 mm up and its
    slot opening toward the car's centre line. Returns (column, cut)."""
    import anchors as AN
    z0 = z_plate_top + 0.3
    c = cyl((x, y, z0), (0, 0, 1), COL_R, z_skin - z0 + 1.0) ^ outer
    zn = z0 + 4.0
    hole = cyl((x, y, z0 - 1), (0, 0, 1), HOLE_R, COL_SCREW - (z0 - (z_plate_top - P.CARRIER_T)) + 1 + 1 + AN.TIP_HOLE)
    nut = hexprism((x, y, zn - AN.POCKET_N / 2), (0, 0, 1), AN.POCKET_S, AN.POCKET_N, spin=0.0)
    d = -np.sign(y) if abs(y) > 1 else 1.0                     # slot toward the centre line (y = 0)
    slot = box(AN.POCKET_S, 12.0, AN.POCKET_N, x - AN.POCKET_S / 2, y if d > 0 else y - 12.0, zn - AN.POCKET_N / 2)
    return c, hole + nut + slot


def carriers(outer, inner_tm, ch, ch_u, near_ch):
    """BMI-1 carrier plates (front tongue under the hook lips, rear plate on the post shoulders with quarter-turn key
    slots) + the shell's screw columns over them. Returns (parts, columns_by_panel, cuts_by_panel, info)."""
    from lib import magnet_pocket_z
    inner_c = solid(T + FL_T + SEAM_GAP + 0.3)              # plates stay 0.3 mm clear of the seam flanges too
    keep = ch["keep2"]
    info, cols, cuts = {}, {}, {}
    zf = P.BMI_F_Z - 1.0 - P.CARRIER_T
    xmin = outer.bounding_box()[0]
    front = (box(-35.5 - (xmin + 1), 300, P.CARRIER_T, xmin + 1, -150, zf) ^ inner_c) - keep
    front = largest(front)
    for sgn in (1, -1):
        front = front - from_b3d(magnet_pocket_z(P.BMI_F_X, sgn * P.BMI_F_Y, zf + P.CARRIER_T - P.MAGNET_T + 0.01), 0.03)
    zr = P.BMI_R_Z
    xr0, xr1 = P.BMI_R_X - 17.5, P.WB + 60.0
    rear = (box(xr1 - xr0, 300, P.CARRIER_T, xr0, -150, zr) ^ inner_c) - keep
    rear = largest(rear)
    for sgn in (1, -1):
        rear = rear - box(26, 8, 20, P.BMI_R_X - 13, sgn * P.BMI_R_Y - 4, zr - 5)
        rear = rear - from_b3d(magnet_pocket_z(P.BMI_R_X + 14, sgn * P.BMI_R_Y, zr - 0.01), 0.03)
        w = P.SPRING_OD + 3.0                               # 1.5 mm clear of the bought shock + spring
        rear = rear - box(w, 25, 30, P.WB + P.SHOCK_X - w / 2, sgn * 44.5 - 12.5, zr - 5)
    rear = rear - box(20, 64, 30, xr0 - 2, -32, zr - 5)
    # plates must also clear every chassis part except by design (they sit 1 mm under the lips / on the posts)
    for nm, (pl, ztop, cand) in dict(
            front=(front, zf + P.CARRIER_T, [(x, y) for x in np.arange(xmin + 8, -38.0, 2.0) for y in np.arange(12, 76, 2.0)]),
            rear=(rear, zr + P.CARRIER_T, [(x, y) for x in np.arange(xr0 + 4, xr1 - 4, 2.0) for y in np.arange(14, 86, 2.0)])).items():
        pl_tm = to_tm(pl)
        good = []
        for x, y in cand:
            if abs(x - (P.BMI_F_X if nm == "front" else P.BMI_R_X)) < 12 and abs(y - (P.BMI_F_Y if nm == "front" else P.BMI_R_Y)) < 12:
                continue                                   # keys / lips
            if nm == "rear" and abs(x - (P.BMI_R_X + 14)) < 10 and abs(y - P.BMI_R_Y) < 10:
                continue                                   # magnet
            if nm == "rear" and abs(x - WING_X) < 12 and abs(y - WING_Y) < 10:
                continue                                   # wing-lock driver hole
            # the column's foot must sit fully on the plate: 8 samples round it + centre inside the plate outline
            ring = [(x + COL_R * 1.2 * math.cos(a), y + COL_R * 1.2 * math.sin(a)) for a in np.linspace(0, 2 * np.pi, 8, endpoint=False)] + [(x, y)]
            inside = pl_tm.contains([[px, py, ztop - P.CARRIER_T / 2] for px, py in ring])
            if not inside.all():
                continue
            zs = _ray_up(inner_tm, x, y, ztop + 0.5)
            if zs is None or not (COL_SCREW - P.CARRIER_T + 1.0 + 0.3 <= zs - ztop <= 30.0):
                continue
            samp = [[x + COL_R * math.cos(a), y + COL_R * math.sin(a), z] for a in np.linspace(0, 2 * np.pi, 12, endpoint=False)
                    for z in np.linspace(ztop + 0.5, zs, 8)]
            if near_ch.dist(samp).min() < CLR + 0.3:
                continue
            if not (cyl((x, y, ztop + 0.3), (0, 0, 1), COL_R, zs - ztop) ^ ch_u).is_empty():
                continue
            good.append((zs - ztop, x, y, zs))
        n_want = 2                                          # pairs (mirrored left/right): 4 screws per carrier (D36 target)
        sep = 22.0 if nm == "front" else 30.0               # the nose tongue is short: pairs 22 mm apart there
        good.sort()
        picked = []
        for g in good:
            if all(math.hypot(g[1] - q[1], g[2] - q[2]) > sep for q in picked):
                picked.append(g)
            if len(picked) >= n_want:
                break
        info[nm] = [dict(x=round(g[1], 1), y=round(g[2], 1), height=round(g[0], 1)) for g in picked]
        for h, x, y, zs in picked:
            for sgn, sd in ((1, "L"), (-1, "R")):
                c, cut = column(x, sgn * y, ztop, zs, outer)
                panel = ("front" if x < SEAM_X[0] else "mid" if x < SEAM_X[1] else "rear") + "_" + sd
                cols.setdefault(panel, []).append(c)
                cuts.setdefault(panel, []).append(cut)
                hole = cyl((x, sgn * y, ztop - P.CARRIER_T - 1), (0, 0, 1), HOLE_R, P.CARRIER_T + 2)
                pl = pl - hole
        if nm == "front":
            front = pl
        else:
            rear = pl
    for sgn in (1, -1):                                     # driver access to the wing-lock screws
        rear = rear - cyl((WING_X, sgn * WING_Y, zr - 1), (0, 0, 1), 4.0, P.CARRIER_T + 2)
    return {"carrier_front": front, "carrier_rear": rear}, cols, cuts, info


# ---------------------------------------------------------------- wing (original NACA 6412, inverted)
WING_LE = (338.4, 136.9)               # same placement, chord, angle and span as the car's fitted wing (owner rule:
WING_C, WING_A = 30.4, 18.9            # the wing's position and angle never change); the section is an original NACA
WING_SPAN = 162.0                      # 6412 and the end plates and legs are original
WING_X, WING_Y = 326.0, 40.0           # leg peg centre (each side)
PEG = (14.0, 8.0, 12.0)                # peg x, y, depth below the deck skin


def naca4(m, p, t, c, n=60, te=1.0):
    b = 0.5 * (1 - np.cos(np.linspace(0, np.pi, n)))
    x = b * c
    yt = 5 * t * c * (0.2969 * np.sqrt(b) - 0.1260 * b - 0.3516 * b ** 2 + 0.2843 * b ** 3 - 0.1036 * b ** 4) + 0.5 * te * b
    yc = np.where(b < p, m / p ** 2 * (2 * p * b - b ** 2), m / (1 - p) ** 2 * ((1 - 2 * p) + 2 * p * b - b ** 2)) * c
    dy = np.where(b < p, 2 * m / p ** 2 * (p - b), 2 * m / (1 - p) ** 2 * (p - b))
    th = np.arctan(dy)
    xu, yu = x - yt * np.sin(th), yc + yt * np.cos(th)
    xl, yl = x + yt * np.sin(th), yc - yt * np.cos(th)
    pts = np.vstack([np.column_stack([xu[::-1], yu[::-1]]), np.column_stack([xl[1:], yl[1:]])])
    return pts


def wing(outer, outer_tm):
    th = math.radians(WING_A)
    ch_ = np.array([math.cos(th), 0, math.sin(th)])
    nn = np.array([-math.sin(th), 0, math.cos(th)])
    prof = naca4(0.06, 0.4, 0.12, WING_C)
    prof[:, 1] *= -1                                       # inverted: camber down = downforce
    prof = prof[::-1]                                      # keep it counter-clockwise after the flip
    half = WING_SPAN / 2 - 2.0
    sec = mf.CrossSection([prof], mf.FillRule.Positive)
    w = mf.Manifold.extrude(sec, 2 * half + 0.4)
    o = np.array([WING_LE[0], half + 0.2, WING_LE[1]])
    Mx = [[ch_[0], nn[0], 0, o[0]], [ch_[1], nn[1], -1, o[1]], [ch_[2], nn[2], 0, o[2]]]
    plane = w.transform(Mx)
    ep = mf.CrossSection([np.array([(334.0, 128.0), (371.0, 136.0), (371.0, 155.0), (334.0, 146.0)])], mf.FillRule.Positive)
    parts = [plane]
    for sgn in (1, -1):
        e = mf.Manifold.extrude(ep, 2.0).transform([[1, 0, 0, 0], [0, 0, -1, 0], [0, 1, 0, 0]])      # x-z plate, y 0..-2
        parts.append(e.translate((0, sgn * (half + 2.0) if sgn > 0 else -half, 0)))
    # legs: 4 mm plates leaning back from the deck to the wing's chord line, + the peg under the deck
    zs = {}
    for sgn in (1, -1):
        loc, _, _ = outer_tm.ray.intersects_location([[WING_X, sgn * WING_Y, 300.0]], [[0, 0, -1.0]], multiple_hits=False)
        z_deck = float(loc[0][2])
        zs[sgn] = z_deck
        zc = lambda x: WING_LE[1] + (x - WING_LE[0]) * math.tan(th)   # noqa: E731
        lp = np.array([(WING_X - 7.0, z_deck - 3.0), (WING_X + 7.0, z_deck - 3.0), (357.0, zc(357.0)), (345.0, zc(345.0))])
        leg = mf.Manifold.extrude(mf.CrossSection([lp], mf.FillRule.Positive), 4.0).transform([[1, 0, 0, 0], [0, 0, -1, 0], [0, 1, 0, 0]])
        leg = leg.translate((0, sgn * WING_Y + 2.0, 0))
        leg = leg - outer
        peg = box(PEG[0], PEG[1], PEG[2] + 1.0, WING_X - PEG[0] / 2, sgn * WING_Y - PEG[1] / 2, z_deck - PEG[2])
        parts += [leg, peg]
    W = mf.Manifold.batch_boolean(parts, mf.OpType.Add)
    import anchors as AN
    cuts, socks = [], {}
    for sgn in (1, -1):
        z_deck = zs[sgn]
        zb = z_deck - PEG[2]
        zn = zb + 3.5
        cuts.append(cyl((WING_X, sgn * WING_Y, zb - 1), (0, 0, 1), HOLE_R, 8.0 + AN.TIP_HOLE))
        cuts.append(hexprism((WING_X, sgn * WING_Y, zn - AN.POCKET_N / 2), (0, 0, 1), AN.POCKET_S, AN.POCKET_N, spin=90.0))
        cuts.append(box(PEG[0] / 2 + 1.0, AN.POCKET_S, AN.POCKET_N, WING_X - PEG[0] / 2 - 1.0, sgn * WING_Y - AN.POCKET_S / 2, zn - AN.POCKET_N / 2))
        socks[sgn] = z_deck
    W = W - mf.Manifold.batch_boolean(cuts, mf.OpType.Add)
    return W, socks


def wing_sockets(outer, socks):
    """Socket boss under the deck for each leg peg (0.2 mm clearance round the peg), 2.8 mm floor with the lock
    screw's clearance hole."""
    adds, cuts = [], []
    for sgn, z_deck in socks.items():
        zb = z_deck - PEG[2]
        adds.append(box(PEG[0] + 6, PEG[1] + 6, PEG[2] + 4.0, WING_X - PEG[0] / 2 - 3, sgn * WING_Y - PEG[1] / 2 - 3, zb - 2.8) ^ outer)
        cuts.append(box(PEG[0] + 0.4, PEG[1] + 0.4, PEG[2] + 20, WING_X - PEG[0] / 2 - 0.2, sgn * WING_Y - PEG[1] / 2 - 0.2, zb - 0.2))
        cuts.append(cyl((WING_X, sgn * WING_Y, zb - 5), (0, 0, 1), HOLE_R, 6))
    return adds, cuts


# ---------------------------------------------------------------- build
MATERIAL = {"panel": "PETG", "carrier": "PETG-CF", "wing": "PETG-CF"}
SOLID_PARTS = {"gt2_carrier_front"}    # D56.6: printed solid (+9.8 g at the nose) to hold the owner's 48/52 (R32): the GT-2 kit's
                                       # own CG (wing + rear carrier, x 149 mm) put the car at 47.5 % front, on the band's edge
DENS = {"PETG-CF": 1.25, "PETG": 1.27}


def build(ch):
    t0 = time.time()
    outer, inner, raw = skin(ch)
    outer_tm, inner_tm = to_tm(outer), to_tm(inner)
    ch_u = chassis_union(ch)
    ch_tm = to_tm(ch_u)
    cut_all = box(1000, 1000, 100, -500, -500, SKIRT - 100) + ch["keep2"] + arch_cuts(ch)
    vt = vents()
    raw = raw - vt
    sp = splitter(outer) - ch["keep2"]
    raw = raw + sp
    cut_all = cut_all + vt
    W, socks = wing(outer, outer_tm)
    s_add, s_cut = wing_sockets(outer, socks)
    print(f"  skin + vents + splitter + wing ({time.time() - t0:.0f} s)")
    near_ch = Near(ch_tm)
    st = seams(outer, inner_tm, ch_u, near_ch)
    fl = flanges(cut_all)
    car, cols, ccuts, cinfo = carriers(outer, inner_tm, ch, ch_u, near_ch)
    print(f"  {len(st)} seam stations, flanges, carriers ({time.time() - t0:.0f} s)")
    boxes, xs = panel_boxes()
    adds = {k: [] for k in boxes}
    holes = {k: [] for k in boxes}
    notches = {k: [] for k in boxes}
    for hp, npn, p, n, u in st:
        hb, nb, cut, notch = station(p, n, u, outer)
        adds[hp].append(hb); adds[npn].append(nb)
        holes[hp].append(cut); holes[npn].append(cut)
        notches[npn].append(notch)
    for k, v in cols.items():
        adds[k] += v
    for k, v in ccuts.items():
        holes[k] += v
    for a_ in s_add:
        for k, B in boxes.items():
            if not (a_ ^ B).is_empty():
                adds[k].append(a_ ^ B)
    for c_ in s_cut:
        for k in boxes:
            holes[k].append(c_)
    parts, dropped = {}, {}
    for k, B in boxes.items():
        pnl = raw ^ B
        if k in fl:
            f = fl[k]
            if notches[k]:
                f = f - mf.Manifold.batch_boolean(notches[k], mf.OpType.Add)
            pnl = pnl + f
        if adds[k]:
            pnl = pnl + (mf.Manifold.batch_boolean(adds[k], mf.OpType.Add) ^ B.translate((0, 0, 0)) if False else mf.Manifold.batch_boolean(adds[k], mf.OpType.Add))
        if holes[k]:
            pnl = pnl - mf.Manifold.batch_boolean(holes[k], mf.OpType.Add)
        comps = sorted(pnl.decompose(), key=lambda c: -c.volume())
        dropped[k] = [(round(c.volume(), 1), [round(v, 1) for v in c.bounding_box()]) for c in comps[1:] if c.volume() > 0.5]
        parts[f"{PFX}_body_{k}"] = comps[0]
    parts[f"{PFX}_carrier_front"], parts[f"{PFX}_carrier_rear"] = car["carrier_front"], car["carrier_rear"]
    parts[f"{PFX}_wing"] = W
    info = dict(stations=len(st), stations_by_seam=_count_st(st), columns=cinfo, dropped=dropped,
                wing_deck_z={str(k): round(v, 2) for k, v in socks.items()})
    print(f"  panels ({time.time() - t0:.0f} s)")
    return outer, inner, parts, st, info


def _count_st(st):
    out = {}
    for hp, npn, *_ in st:
        k = f"{hp}|{npn}"
        out[k] = out.get(k, 0) + 1
    return out


def checks(parts, ch, outer):
    """Fit: every part vs every chassis part (exact overlap = clash; sampled gap < CLR = tight; the carriers sit on
    the BMI-1 mounts by design), parts vs parts (no overlap), bed fit in print orientation."""
    res = dict(clash=[], tight=[], overlap=[], bed=[], gaps={})
    chs = {n: M for n, M in ch.items() if not n.startswith("keep")}
    dch = {n: dense(to_tm(M), 0.5, 400_000) for n, M in chs.items()}
    for k, M in parts.items():
        near = Near(to_tm(M))
        b = M.bounding_box()
        lo, hi = np.array(b[:3]) - 3, np.array(b[3:]) + 3
        worst = (99.0, None)
        for n, C in chs.items():
            cb = C.bounding_box()
            if (np.array(cb[:3]) > hi).any() or (np.array(cb[3:]) < lo).any():
                continue
            by_design = "carrier" in k and n in ("front_mount", "rear_mount")
            ov = (M ^ C).volume()
            pts = dch[n][np.all((dch[n] > lo) & (dch[n] < hi), axis=1)]
            g = float(near.dist(pts).min()) if len(pts) else 99.0
            if g < worst[0]:
                worst = (g, n)
            if by_design:
                continue
            if ov > 0.01:
                res["clash"].append((k, n, round(ov, 2)))
            elif g < CLR - 0.05:
                res["tight"].append((k, n, round(g, 2)))
        res["gaps"][k] = (round(worst[0], 2), worst[1])
        Mp = print_orient(k, M)
        kb = Mp.bounding_box()
        size = np.array(kb[3:]) - np.array(kb[:3])
        if size[0] > BED_LIM or size[1] > BED_LIM or size[2] > P.BED[2] - P.BED_MARGIN:
            res["bed"].append((k, [round(float(v), 1) for v in size]))
    ks = list(parts)
    for i in range(len(ks)):
        for j in range(i + 1, len(ks)):
            v = (parts[ks[i]] ^ parts[ks[j]]).volume()
            if v > 0.5:
                res["overlap"].append((ks[i], ks[j], round(v, 1)))
    return res


def print_orient(k, M):
    """As printed: panels upright as on the car, carriers flat, wing upside down (pegs up). A part too long for
    the bed square is turned about Z to the angle with the smallest larger side (diagonal placement)."""
    if "wing" in k:
        M = M.rotate((180, 0, 0))
    b = M.bounding_box()
    if max(b[3] - b[0], b[4] - b[1]) > BED_LIM:
        best = None
        for a in np.arange(0, 90.1, 1.0):
            R = M.rotate((0, 0, float(a)))
            rb = R.bounding_box()
            m = max(rb[3] - rb[0], rb[4] - rb[1])
            if best is None or m < best[0]:
                best = (m, float(a), R)
        M = best[2]
        ZROT[k] = best[1]
        b = M.bounding_box()
    return M.translate((-b[0], -b[1], -b[2]))


ZROT = {}


def export(parts, info, chk, outer):
    os.makedirs(os.path.join(OUT, "stl"), exist_ok=True)
    os.makedirs(os.path.join(OUT, "assembly"), exist_ok=True)
    rows = []
    for k, M in parts.items():
        kind = "wing" if "wing" in k else "carrier" if "carrier" in k else "panel"
        mat = MATERIAL[kind]
        Mp = stl_clean(print_orient(k, M))     # D56: watertight as written (see stl_clean)
        M = stl_clean(M)
        parts[k] = M
        tm = to_tm(Mp)
        tm.export(os.path.join(OUT, "stl", k + ".stl"))
        to_tm(M).export(os.path.join(OUT, "assembly", k + ".stl"))
        b = Mp.bounding_box()
        solid_ = kind == "panel" or k in SOLID_PARTS
        fill = 1.0 if solid_ else 0.69
        rows.append(dict(part=k, material=mat, qty=1, zrot=ZROT.get(k, 0), size=[round(b[3] - b[0], 1), round(b[4] - b[1], 1), round(b[5] - b[2], 1)],
                         vol=round(M.volume() / 1000, 2), mass_g=round(M.volume() / 1000 * DENS[mat] * fill, 1), tris=M.num_tri(),
                         walls="solid skin (2 lines at 0.6 mm)" if kind == "panel" else "100% infill" if solid_ else "4 walls / 40%",
                         supports="tree, inside only (paint side clean)" if kind == "panel" else
                         "tree: under the plane and end plates (pegs up)" if kind == "wing" else "none"))
    shell = mf.Manifold.batch_boolean([M for k, M in parts.items() if "_body_" in k], mf.OpType.Add)
    to_tm(shell).export(os.path.join(OUT, "assembly", "shell.stl"))
    to_tm(outer).export(os.path.join(OUT, "assembly", "outer.stl"))
    bb = outer.bounding_box()
    d = dict(body="GT-2 (original, D56)", wall_mm=T, length=round(bb[3] - bb[0], 1), width=round(bb[4] - bb[1], 1),
             height=round(bb[5], 1), parts=rows, mass_g=round(sum(r["mass_g"] for r in rows), 1), info=info, checks=chk)
    json.dump(d, open(os.path.join(OUT, "parts.json"), "w"), indent=1, default=float)
    return d


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--skin", action="store_true")
    ap.add_argument("--rebuild-chassis", action="store_true")
    a = ap.parse_args()
    t0 = time.time()
    ch = chassis(a.rebuild_chassis)
    outer, inner, raw = skin(ch)
    bb = outer.bounding_box()
    print(f"outer: L {bb[3] - bb[0]:.1f}  W {bb[4] - bb[1]:.1f}  H {bb[5]:.1f} mm")
    wall = wall_report(outer, inner)
    print("wall:", wall)
    res, bad = clearance(raw, ch)
    tight = sorted(res.items(), key=lambda kv: (-kv[1][0], kv[1][1]))[:8]
    print("closest chassis parts (overlap mm3, gap mm):", tight)
    print("points under", CLR, "mm:", bad)
    if a.skin:
        return
    outer, inner, parts, st, info = build(ch)
    chk = checks(parts, ch, outer)
    for k in ("clash", "tight", "overlap", "bed"):
        print(f"  {k}: {chk[k]}")
    info["wall"] = wall                                     # D56: measured skin thickness (rays) and chassis clearance, for the tests
    info["closest_chassis"] = [[k, v[0], v[1]] for k, v in tight]
    info["under_clr"] = bad
    d = export(parts, info, chk, outer)
    print(f"  stations {info['stations_by_seam']}  columns {info['columns']}  dropped {info['dropped']}")
    print(f"  kit {d['mass_g']} g: " + ", ".join(f"{r['part'][4:]} {r['mass_g']}" for r in d["parts"]))
    print(f"done ({time.time() - t0:.0f} s)")


if __name__ == "__main__":
    main()
