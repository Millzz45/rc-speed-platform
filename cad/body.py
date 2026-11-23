"""
Reference body "GT-1": a generic sports coupe built to BMI-1. No brand styling, no logos.
Every future body copies this file and only changes the PROFILE tables.

Construction:
  lower body = loft of superellipse sections (half-width a(x), top z_belt(x))
  greenhouse = loft of superellipse sections (half-width g(x), top z_top(x)) in the cabin span
  shell      = outer - inner (inner = same lofts inset by BODY_T), open below BODY_SKIRT_Z
  arches, functional vents, hood intake collar (mates to chassis intake gasket)
  split      = 3 sections along X x left/right halves -> 6 panels that fit the bed
  carriers   = plates conforming to the inner surface, carrying the BMI-1 features
"""
import math
import numpy as np
from build123d import Spline, Face, Wire, loft, Pos, Rot, Box, Cylinder
import params as P
from lib import box, cbox, cyl_y, cyl_z, insert_hole, clear_hole, magnet_pocket_z
import wheels as Wh

# ---- style tables (x, value) ---------------------------------------------------
# drawn for the original 216 mm wheelbase; D27 stretches the cabin to P.WB (overhangs unchanged)
WB0 = 216.0


def sx(x):
    return x if x <= 0 else x * P.WB / WB0 if x <= WB0 else x + P.WB - WB0


def _sx(tab):
    return [(sx(x), v) for x, v in tab]


X0, X1 = -52.0, sx(293.0)          # 392 mm overall at WB 263 (345 at 216)
HALF_W = [(-52, 44), (-50, 58), (-46, 68), (-38, 84), (-15, 95), (0, 97), (40, 95), (110, 93), (180, 94),
          (216, 97), (255, 95), (282, 88), (293, 80)]
BELT_Z = [(-52, 26), (-50, 34), (-46, 44), (-38, 56), (-15, 72), (0, 80), (25, 79), (60, 74), (150, 75),
          (200, 80), (216, 82), (245, 80), (275, 73), (293, 64)]
GH_X0, GH_X1 = 48.0, 252.0
GH_HALF_W = [(48, 46), (75, 66), (110, 72), (170, 72), (220, 66), (252, 44)]
GH_TOP_Z = [(48, 76), (75, 90), (112, 102), (160, 101), (205, 92), (235, 82), (252, 78)]
N_LOWER, N_GH = 5.0, 3.0           # superellipse exponents (boxy body, rounder cabin)
NPTS = 40
SECT_X0 = [-52, -50, -46, -38, -28, -15, 0, 15, 35, 60, 90, 120, 150, 180, 200, 216, 232, 255, 275, 287, 293]
GH_SECT_X0 = [48, 60, 75, 92, 112, 135, 160, 185, 205, 225, 240, 252]
ARCH_R = P.TIRE_D / 2 + 5.0
HALF_W, BELT_Z, GH_HALF_W, GH_TOP_Z = _sx(HALF_W), _sx(BELT_Z), _sx(GH_HALF_W), _sx(GH_TOP_Z)
GH_X0, GH_X1 = sx(GH_X0), sx(GH_X1)
SECT_X = [sx(x) for x in SECT_X0]
GH_SECT_X = [sx(x) for x in GH_SECT_X0]
SPLIT_X = (90.0, 215.0)            # panel cuts: front 142 / mid 125 / rear 125 mm; seams clear the hood intake


def interp(tab, x):
    xs, vs = zip(*tab)
    return float(np.interp(x, xs, vs))


def superellipse(x, a, zc, h, n):
    pts = []
    for i in range(NPTS):
        t = 2 * math.pi * i / NPTS
        c, s = math.cos(t), math.sin(t)
        y = a * math.copysign(abs(c) ** (2 / n), c)
        z = zc + h * math.copysign(abs(s) ** (2 / n), s)
        pts.append((x, y, z))
    return Face(Wire([Spline(*pts, periodic=True)]))


def lower_sections(inset=0.0):
    out = []
    for i, x in enumerate(SECT_X):
        xx = x + (inset if i == 0 else -inset if i == len(SECT_X) - 1 else 0)
        a = interp(HALF_W, xx) - inset
        top = interp(BELT_Z, xx) - inset
        bot = -20.0 - (6.0 if inset else 0.0)   # inner pokes out below: no coincident faces
        out.append(superellipse(xx, a, (top + bot) / 2, (top - bot) / 2, N_LOWER))
    return out


def gh_sections(inset=0.0):
    out = []
    for i, x in enumerate(GH_SECT_X):
        xx = x + (inset if i == 0 else -inset if i == len(GH_SECT_X) - 1 else 0)
        g = interp(GH_HALF_W, xx) - inset
        top = interp(GH_TOP_Z, xx) - inset
        base = interp(BELT_Z, xx) - 12.0
        out.append(superellipse(xx, g, (top + base) / 2, (top - base) / 2, N_GH))
    return out


def outer_solid():
    return loft(lower_sections()) + loft(gh_sections())


def inner_solid(extra=0.0):
    t = P.BODY_T + extra
    return loft(lower_sections(t)) + loft(gh_sections(t))


def vents():
    """Functional openings. Air in: hood intake -> chassis duct. Air/pressure out:
    fender louvres (wheel-well lift relief), side exits behind front wheels, rear valance."""
    v = []
    ix, iy, iw, il = P.BMI_INTAKE_X, P.BMI_INTAKE_Y, P.BMI_INTAKE_W, P.BMI_INTAKE_L
    v.append(cbox(il, iw, 60, ix, iy, 40))                             # hood intake opening
    for side in (1, -1):
        for k in range(3):                                             # fender louvres
            v.append(cbox(5, 22, 40, -14 + k * 10, side * 76, 50))
        for k in range(3):                                             # side exits
            v.append(cbox(5, 40, 14, 44 + k * 8, side * 95, 30 + k * 4))
        for k in range(3):                                             # rear valance exits
            v.append(cbox(40, 12, 8, sx(290), side * (20 + k * 18), 22))
    out = v[0]
    for s in v[1:]:
        out = out + s
    return out


def intake_collar():
    """Rectangular collar from the hood skin down to the chassis gasket (Z = intake + 2)."""
    ix, iy, iw, il = P.BMI_INTAKE_X, P.BMI_INTAKE_Y, P.BMI_INTAKE_W, P.BMI_INTAKE_L
    z0 = P.BMI_INTAKE_Z + 2.0
    t = 1.6
    outer = cbox(il + 2 * t, iw + 2 * t, 40, ix, iy, z0)
    inner = cbox(il, iw, 60, ix, iy, z0 - 5)
    return (outer & inner_solid()) - inner     # only the part inside the body


def shell():
    s = outer_solid() - inner_solid()
    s = s + intake_collar()
    s = s - box(600, 400, P.BODY_SKIRT_Z + 30, -150, -200, -30)       # open bottom at skirt
    for ax in (0.0, P.WB):
        s = s - cyl_y(2 * ARCH_R, 260, ax, 0, P.TIRE_D / 2)
    s = s - vents()
    return s


def panels(sh=None):
    """6 panels: front/mid/rear x left/right, each inside the bed."""
    sh = sh or shell()
    cuts = [X0 - 5, SPLIT_X[0], SPLIT_X[1], X1 + 5]
    names = ["front", "mid", "rear"]
    out = {}
    for i, n in enumerate(names):
        for side, (y0, y1) in (("L", (0, 120)), ("R", (-120, 0))):
            out[f"body_{n}_{side}"] = sh & box(cuts[i + 1] - cuts[i], y1 - y0, 200, cuts[i], y0, -10)
    return out


def joiners():
    """Glue-on doubler strips (inside the skin) across every seam."""
    band = inner_solid() - inner_solid(1.2)
    band = band - box(600, 400, P.BODY_SKIRT_Z + 30, -150, -200, -30)
    for ax in (0.0, P.WB):
        band = band - cyl_y(2 * ARCH_R + 2, 260, ax, 0, P.TIRE_D / 2)
    band = band - vents()
    out = {}
    for i, cx in enumerate(SPLIT_X):           # transverse seams, split L/R
        for side, (y0, y1) in (("L", (1, 120)), ("R", (-120, -1))):
            out[f"joiner_x{i+1}_{side}"] = band & box(16, y1 - y0, 200, cx - 8, y0, -10)
    cuts = [-42.0, SPLIT_X[0] - 9, SPLIT_X[1] - 9, X1 + 5]   # nose tip is below the strip's Z 30 floor
    for i in range(3):                         # centerline seam, one per section
        out[f"joiner_c{i+1}"] = band & box(cuts[i + 1] - cuts[i] - 1, 16, 200, cuts[i] + 0.5, -8, 30)
    return out


def _sect(z, x0, x1, band=None):
    """Planar section of the inner skin at height z (a 2D face), optionally reduced to a band
    of width `band` along the skin, then clipped to x0..x1."""
    from build123d import section, Plane, Rectangle, offset, Pos as P2
    f = section(inner_solid(), Plane.XY.offset(z))
    if band is not None:
        f = f - offset(f, -band)                 # band follows the skin only (not the clip line)
    f = f & (P2((x0 + x1) / 2, 0, z) * Rectangle(x1 - x0, 400))
    return _polygonize(f)


def _polygonize(sk, step=0.5):
    """Replace spline outlines by 0.5 mm polylines -> all-planar solids that tessellate
    watertight at any tolerance."""
    from build123d import Polyline, make_face
    def pts(w):
        n = max(8, int(w.length / step))
        return [w.position_at(i / n) for i in range(n)]
    out = None
    for fc in sk.faces():
        g = make_face(Polyline(*pts(fc.outer_wire()), close=True))
        for iw in fc.inner_wires():
            g = g - make_face(Polyline(*pts(iw), close=True))
        out = g if out is None else out + g
    return out


def skin_plate(x0, x1, z0, h, band=None, nz=4, overlap=0.4):
    """Plate (band=None) or glue band of width `band` hugging the inner skin, x0..x1, z0..z0+h.
    Built from 2D sections taken at each slab's TOP (the skin narrows upward) so it stays inside
    the shell; slabs overlap in Z so they fuse into one manifold solid. Avoids 3D booleans
    between near-coincident spline surfaces, which fail silently in OCC."""
    from build123d import extrude, Pos as P2
    dz = h / nz
    out = None
    for k in range(nz):
        zt = z0 + (k + 1) * dz
        ext = dz + (overlap if k else 0.0)
        slab = P2(0, 0, -ext) * extrude(_sect(zt, x0, x1, band), ext)
        out = slab if out is None else out + slab
    return out


def _largest(shape):
    sols = shape.solids()
    return max(sols, key=lambda s: s.volume) if len(sols) > 1 else shape


def carriers():
    """BMI-1 carrier plates, shaped to the inner skin so every body uses identical mounts."""
    out = {}
    keep = Wh.keepouts(2.0)
    # front carrier: plate in the nose, ahead of the front wheels, under the chassis hook lips.
    # Body is set down BMI_F_SLIDE forward of home and pushed rearward to engage.
    zf = P.BMI_F_Z - 1.0 - P.CARRIER_T
    xf0, xf1 = X0 + 1.0, -35.5                   # tongue rear edge stops 0.5 mm short of the beam
    plate = skin_plate(xf0, xf1, zf, P.CARRIER_T, nz=1)
    lip = skin_plate(xf0, xf1, zf, 10.0, band=3.0)
    front = _largest((plate + lip) - keep)
    for s in (1, -1):
        front = front - magnet_pocket_z(P.BMI_F_X, s * P.BMI_F_Y, zf + P.CARRIER_T - P.MAGNET_T + 0.01)   # D36 press fit
    out["carrier_front"] = front
    # rear carrier: plate Z 40..43 on the post shoulders, X-slots for the quarter-turn keys
    zr = P.BMI_R_Z
    xr0, xr1 = P.BMI_R_X - 17.5, P.WB + 60.0  # 44 mm deep: fits the bed on a diagonal
    plate = skin_plate(xr0, xr1, zr, P.CARRIER_T, nz=1)
    lip = skin_plate(xr0, xr1, zr, 10.0, band=3.0)
    rear = _largest((plate + lip) - keep)
    for s in (1, -1):
        rear = rear - cbox(26, 8, 20, P.BMI_R_X, s * P.BMI_R_Y, zr - 5)       # key slot
        rear = rear - magnet_pocket_z(P.BMI_R_X + 14, s * P.BMI_R_Y, zr - 0.01)                       # D36 press fit
    rear = rear - cbox(20, 64, 30, xr0 + 8, 0, zr - 5)                    # rear bulkhead
    for s in (1, -1):                                                    # rear shocks (D21; D33 bought shock + spring)
        rear = rear - cbox(P.SPRING_OD + 2.0, 24, 30, P.WB + P.SHOCK_X, s * 44.5, zr - 5)   # D33: bought shock + spring, 1 mm clear
    out["carrier_rear"] = rear
    return out


if __name__ == "__main__":
    import time
    t = time.time()
    s = shell()
    print("shell ok", round(time.time() - t, 1), "s, vol", round(s.volume / 1000, 1), "cm3",
          s.bounding_box().size)
