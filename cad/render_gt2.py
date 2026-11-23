#!/usr/bin/env python3
"""D56: preview of the GT-2 body on the car (matplotlib, flat shaded): side, top, front, rear three-quarter.
Reads out/body_gt2/assembly/*.stl (car frame); tyres drawn as cylinders at the car's track and tyre size.
  cd cad && ../.venv/bin/python render_gt2.py [--out ../out/body_gt2/preview.png] [--chassis]"""
import argparse, glob, os, sys
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d.art3d import Poly3DCollection
import trimesh
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import params as P  # noqa: E402

OUT = os.path.join(os.path.dirname(HERE), "out", "body_gt2")
COL = {"body": (0.86, 0.33, 0.12), "wing": (0.16, 0.16, 0.18), "carrier": (0.3, 0.3, 0.32), "tyre": (0.08, 0.08, 0.08),
       "chassis": (0.55, 0.55, 0.58)}


def tyres():
    out = []
    for ax, tr in ((0.0, P.TRACK_F), (P.WB, P.TRACK_R)):
        for s in (1, -1):
            c = trimesh.creation.cylinder(P.TIRE_D / 2, P.TIRE_W, sections=48)
            c.apply_transform(trimesh.transformations.rotation_matrix(np.pi / 2, (1, 0, 0)))
            c.apply_translation((ax, s * tr / 2, P.TIRE_D / 2))
            out.append(c)
    return trimesh.util.concatenate(out)


def shade(m, base, light):
    t = m.vertices[m.faces]
    n = np.cross(t[:, 1] - t[:, 0], t[:, 2] - t[:, 0]); n /= np.linalg.norm(n, axis=1, keepdims=True) + 1e-12
    s = 0.35 + 0.65 * np.clip(np.abs(n @ light), 0, 1)
    return t, np.clip(np.asarray(base)[None, :] * (0.45 + 0.75 * s[:, None]), 0, 1)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default=os.path.join(OUT, "preview.png"))
    ap.add_argument("--chassis", action="store_true")
    ap.add_argument("--max-faces", type=int, default=60000)
    a = ap.parse_args()
    groups = []
    for f in sorted(glob.glob(os.path.join(OUT, "assembly", "gt2_*.stl"))):
        k = "wing" if "wing" in f else "carrier" if "carrier" in f else "body"
        groups.append((k, trimesh.load(f, process=False)))
    groups.append(("tyre", tyres()))
    if a.chassis and os.path.exists(os.path.join(OUT, "assembly", "chassis.stl")):
        groups.append(("chassis", trimesh.load(os.path.join(OUT, "assembly", "chassis.stl"), process=False)))
    views = [("side (left)", 0, 90), ("top", 90, -90), ("front", 0, 180), ("rear three-quarter", 22, 35), ("front three-quarter", 18, 145)]
    fig = plt.figure(figsize=(20, 11))
    allv = np.vstack([m.vertices for _, m in groups])
    lo, hi = allv.min(0), allv.max(0)
    c = (lo + hi) / 2; s = (hi - lo).max() / 2
    for i, (title, el, az) in enumerate(views):
        ax = fig.add_subplot(2, 3, i + 1, projection="3d")
        ea, aa = np.radians(el), np.radians(az)
        light = np.array([np.cos(ea) * np.cos(aa) + 0.3, np.cos(ea) * np.sin(aa) - 0.3, np.sin(ea) + 0.6]); light /= np.linalg.norm(light)
        for k, m in groups:
            if len(m.faces) > a.max_faces:
                idx = np.random.default_rng(0).choice(len(m.faces), a.max_faces, replace=False)
                m = trimesh.Trimesh(m.vertices, m.faces[idx], process=False)
            t, fc = shade(m, COL[k], light)
            ax.add_collection3d(Poly3DCollection(t, facecolors=fc, edgecolor="none"))
        ax.set_xlim(c[0] - s, c[0] + s); ax.set_ylim(c[1] - s, c[1] + s); ax.set_zlim(c[2] - s, c[2] + s)
        ax.set_box_aspect((1, 1, 1))
        ax.view_init(el, az); ax.set_axis_off(); ax.set_title(title)
        try:
            ax.set_proj_type("ortho")
        except Exception:
            pass
    fig.suptitle("GT-2 original body (D56) on the car", fontsize=14)
    plt.tight_layout()
    fig.savefig(a.out, dpi=80)
    print("wrote", a.out)


if __name__ == "__main__":
    main()
