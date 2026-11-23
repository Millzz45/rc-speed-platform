"""Shaded PNG previews (matplotlib) of build123d shapes or STL files."""
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d.art3d import Poly3DCollection

VIEWS = {"iso": (22, -135), "side": (0, -90), "top": (90, -90), "front": (0, 180), "rear_iso": (25, -40)}


def tris_of(shape, tol=0.4):
    verts, faces = shape.tessellate(tol, 0.3)
    v = np.array([[p.X, p.Y, p.Z] for p in verts])
    return v[np.array(faces)]


def render(items, path, views=("iso", "side", "top", "front"), title=None, size=5.5):
    """items: list of (triangles Nx3x3, rgb)."""
    allv = np.concatenate([t.reshape(-1, 3) for t, _ in items])
    lo, hi = allv.min(0), allv.max(0)
    ctr, span = (lo + hi) / 2, (hi - lo).max() / 2
    light = np.array([0.4, -0.5, 0.8]); light /= np.linalg.norm(light)
    ncol = 2 if len(views) == 4 else len(views)
    nrow = (len(views) + ncol - 1) // ncol
    fig = plt.figure(figsize=(size * ncol, size * nrow * 0.75))
    for i, vname in enumerate(views):
        ax = fig.add_subplot(nrow, ncol, i + 1, projection="3d")
        for tris, rgb in items:
            n = np.cross(tris[:, 1] - tris[:, 0], tris[:, 2] - tris[:, 0])
            n /= (np.linalg.norm(n, axis=1, keepdims=True) + 1e-12)
            shade = 0.35 + 0.65 * np.abs(n @ light)
            cols = np.clip(np.outer(shade, rgb), 0, 1)
            pc = Poly3DCollection(tris, facecolors=cols, edgecolors="none", linewidths=0)
            ax.add_collection3d(pc)
        for k, c in enumerate("xyz"):
            getattr(ax, f"set_{c}lim")(ctr[k] - span, ctr[k] + span)
        ax.set_box_aspect((1, 1, 1), zoom=1.45)
        ax.view_init(*VIEWS[vname])
        ax.set_axis_off()
        ax.set_title(vname, fontsize=9)
    if title:
        fig.suptitle(title, fontsize=11)
    fig.subplots_adjust(left=0, right=1, bottom=0, top=0.93, wspace=0, hspace=0)
    fig.savefig(path, dpi=130)
    plt.close(fig)
