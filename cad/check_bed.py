#!/usr/bin/env python3
"""Bed-fit gate. Every exported STL must fit BED minus BED_MARGIN on each side, as exported
(build_all bakes in a Z rotation when a part only fits on the diagonal). Exit 1 on any failure.

  ../.venv/bin/python check_bed.py            # checks out/stl/*.stl
"""
import glob, math, os, sys
import numpy as np
import trimesh
import params as P

LIM_XY = min(P.BED[0], P.BED[1]) - 2 * P.BED_MARGIN
LIM_Z = P.BED[2] - P.BED_MARGIN


def footprint(xy, deg):
    a = math.radians(deg)
    r = xy @ np.array([[math.cos(a), -math.sin(a)], [math.sin(a), math.cos(a)]]).T
    ext = r.max(0) - r.min(0)
    return ext[0], ext[1]


def best_angle(xy):
    """Z rotation (deg) that minimises the larger footprint side; 0 if it already fits."""
    if max(footprint(xy, 0)) <= LIM_XY:
        return 0.0
    angs = np.arange(0, 90, 0.5)
    return float(min(angs, key=lambda d: max(footprint(xy, d))))


def main():
    files = sorted(glob.glob(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", P.OUT_NAME, "stl", "*.stl")))
    if not files:
        sys.exit("no STLs - run build_all.py first")
    bad = 0
    print(f"bed limit {LIM_XY:.0f} x {LIM_XY:.0f} x {LIM_Z:.0f} mm  ({P.BED} minus {P.BED_MARGIN} mm margin)")
    for f in files:
        m = trimesh.load(f)
        ext = m.bounds[1] - m.bounds[0]
        ok = ext[0] <= LIM_XY and ext[1] <= LIM_XY and ext[2] <= LIM_Z
        wt = m.is_watertight
        bad += (not ok) + (not wt)
        print(f"  {'OK ' if ok and wt else 'FAIL'} {os.path.basename(f):22s} {ext[0]:6.1f} x {ext[1]:6.1f} x {ext[2]:6.1f}"
              + ("" if wt else "  NOT WATERTIGHT"))
    print(f"{len(files)} parts, {bad} failures")
    sys.exit(1 if bad else 0)


if __name__ == "__main__":
    main()
