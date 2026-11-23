#!/usr/bin/env python3
"""Build every printed part, export STL + 3MF in print orientation, write the print table,
and render previews.

  ../.venv/bin/python build_all.py            # chassis + wheels (the car's body is the scale shell: cad/body_m3.py --model source)
  ../.venv/bin/python build_all.py --gt1      # also the RETIRED GT-1 reference body (D37; glued joiners, not on the car)
"""
import argparse
import json
import os
import time
import numpy as np
import trimesh
import check_bed as CB
from build123d import Pos, Rot, export_stl, Mesher
import params as P
import chassis as C
import wheels as Wh
import aero as A
import body as B
import render as R
import running_gear as RG
import coupons as CP
import anchors as AN

ROOT = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(ROOT, "..", "out")
STL, MF, PREV = (os.path.join(OUT, d) for d in ("stl", "3mf", "preview"))

ROTATED = {}        # id(shape) -> baked-in Z rotation (deg)
BAD = []           # parts whose mesh is not watertight -> build fails
FLAT = Rot(0, 0, 0)
FLIP = Rot(180, 0, 0)

# name: (builder, material, qty, print rotation, supports, layer, walls/infill, note)
CHASSIS = {
    "tub_front":   (C.tub_front, P.PETG_CF, 1, FLAT, "none", 0.20, "4 walls / 25% gyroid", "floor down; countersinks face the bed; D34 isogrid pockets up"),
    "tub_mid":     (C.tub_mid, P.PETG_CF, 1, FLAT, "none", 0.20, "4 walls / 25% gyroid", "floor down"),
    "tub_rear":    (C.tub_rear, P.PETG_CF, 1, FLAT, "none", 0.20, "4 walls / 25% gyroid", "floor down"),
    **({"motor_duct":  (lambda: __import__("ducts").motor_duct(), P.PETG, 1, FLIP, "none", 0.20, "3 walls / 100% (1.2 mm walls)",
                    "D40: top face on the bed; 3 M3 heat-set inserts in the tabs from below (not on the car since D45); M3 x 8 up through the deck"),} if getattr(P, "MOTOR_DUCT", True) else {}),   # D45: no hood intake -> no ram duct
    "deck_front":  (C.deck_front, P.PETG_CF, 1, FLAT, "none", 0.20, "100% (3 mm plate)", "D34: lap tongue under"),
    "deck_mid":    (C.deck_mid, P.PETG_CF, 1, FLAT, "none", 0.20, "100% (3 mm plate)", "D34: isogrid windows; prints on the diagonal"),
    "deck_rear":   (C.deck_rear, P.PETG_CF, 1, FLAT, "none", 0.20, "100% (3 mm plate)", "D34: runs over the rear bulkheads; rear tower bolts through it"),
    "front_mount": (C.front_mount, P.PETG_CF, 1, Rot(0, 90, 0), "none", 0.16, "5 walls / 60%", "beam rear face down; lips point up"),
    "rear_mount":  (C.rear_mount, P.PETG_CF, 1, FLAT, "none", 0.16, "5 walls / 60%", "bar down, posts up"),
    "twist_key":   (C.twist_key, P.PETG_CF, 2, FLAT, "none", 0.12, "100%", ""),
    "bumper":      (C.bumper, P.TPU, 1, FLAT, "none", 0.20, "2 walls / 25% gyroid", "crush block: the gyroid infill sets the crush force"),
    # D53: the 3 mm spacer the rear mount sits on (its floor screws were short since D37) + the CFD-kept rear diffuser
    "rear_spacer": (lambda: __import__("aero").rear_spacer(), P.PETG_CF, 1, Rot(90, 0, 0) if P.DIFFUSER else FLAT, "none", 0.20, "4 walls / 100%",
                    "D53: flat as fitted (a 3 mm plate, its 4 floor-screw holes vertical): nothing overhangs; the 4 floor screws pass through it into the rear mount"
                    if not P.DIFFUSER else "D53: on its side (x-z profile on the bed) with the diffuser block [check print_audit: its screw holes then lie sideways]"),
    **({"diffuser": (lambda: __import__("aero").diffuser_d53(), P.PETG_CF, 1, Rot(0, P.DIFFUSER_CANDS[P.DIFFUSER]["deg"] - 90, 0), "none", 0.20, "3 walls / 100%",
                     "D53: stood on its leading edge: plate upright, fences and strakes are buttress walls; brim 5 mm. 2 M3 x 8 flat-heads up into the spacer's nuts")} if P.DIFFUSER else {}),
    # D37: the GT-1 splitter + diffuser retired with the GT-1 body (the scale shell shell has its own diffuser; its fitted
    # splitter is rnd/aero/out/print/shell_splitter20.stl, D31)
    "rim":         (Wh.rim, P.PETG_CF, 4, FLAT, "organic (D53 sliced: 5.0 g under the 52 mm face-web bridges)", 0.12, "5 walls / 25%",
                    ("D45: inboard face down; bought Tamiya 54994 belted tyre CA-glued to both bead seats; balance <= 0.5 g" if Wh.BOUGHT else
                     "D44: barrel end down (z 2.5 = bed); 3 M3 hex nuts slide into the boss slots from the hub side; balance <= 0.5 g")),
    **({} if Wh.BOUGHT else {   # D45: bought tyres (CA-glued to the bead seats); no clamp ring, no printed tread
        "rim_ring":    (Wh.clamp_ring, P.PETG_CF, 4, FLAT, "none", 0.12, "100%",
                        "D44: inboard clamp lip, outer face down; 3 M3 x 8 flat-heads into the rim's hex nuts"),
        "tread":       (Wh.tread, P.TPU, 4, FLAT, "none", 0.12, "100%",
                        "D44 belted: PAUSE at " + "/".join(f"{z:.2f}" for z in Wh.belt_pauses()) + " mm, lay " + str(Wh.BELT_TURNS) +
                        " turns of size-69 Kevlar in the open channel (" + str(Wh.WIND_G) + " g hanging weight), resume; slides onto the rim (no glue)"),
    }),
    "battery_pad": (lambda: C.pad(100), P.TPU, 2, FLAT, "none", 0.20, "100%", ""),
    **({"tech_tray": (C.tech_tray, P.PETG, 1, FLAT, "none", 0.20, "3 walls / 100% (3 mm plate)", "D51: flat, pockets up; 3 M3 screws into the deck bosses' captive hex nuts on washers (D55)"),
        "tech_lid":  (C.tech_lid, P.PETG, 1, FLIP, "none", 0.20, "2 walls / 100% (1 mm skin)", "D51: top on the bed, walls up; snaps over the tray edges"),} if getattr(P, "TECH_PACK", False) else {}),
    "esc_pad":     (lambda: C.pad(32), P.TPU, 2, FLAT, "none", 0.20, "100%", ""),
}

UP_Y = Rot(90, 0, 0)        # Y axis -> Z: bearing seats print as round vertical holes
ON_SIDE = Rot(0, 90, 0)     # X axis -> Z: X-direction pin holes print round
# Stage 3 running gear (option B) + links + coupons
RUNNING = {
    "bulkhead_half": (RG.bulkhead_half, P.PETG_CF, 2, UP_Y, "none", 0.16, "5 walls / 40%", "cheek inner face down (bearing seat round); rear pair (same part both sides)"),
    "bulkhead_fL":   (lambda: RG.bulkhead_half(RG.front_diff_dx()), P.PETG_CF, 1, UP_Y, "none", 0.16, "5 walls / 40%", "D46 front LEFT: diff seat offset for a whole-tooth front belt (mark L)"),
    "bulkhead_fR":   (lambda: RG.bulkhead_half(-RG.front_diff_dx()), P.PETG_CF, 1, UP_Y, "none", 0.16, "5 walls / 40%", "D46 front RIGHT: mirror offset (mark R)"),
    "lower_arm":     (RG.lower_arm, P.PETG_CF, 4, ON_SIDE, "none", 0.16, "5 walls / 50%", "on its side: pin holes vertical; same part at all 4 corners"),
    "upper_link":    (RG.upper_link, P.PETG_CF, 4, ON_SIDE, "none", 0.16, "100%", "on its side; same part at all 4 corners"),
    "upright_rear":  (RG.upright_rear, P.PETG_CF, 2, UP_Y, "none", 0.16, "5 walls / 50%", "bearing axis vertical"),
    "knuckle_L":     (lambda: RG.knuckle(1), P.PETG_CF, 1, UP_Y, "tree, under the steering arm", 0.16, "5 walls / 50%", "front left"),
    "knuckle_R":     (lambda: RG.knuckle(-1), P.PETG_CF, 1, UP_Y, "tree, under the steering arm", 0.16, "5 walls / 50%", "front right (mirror)"),
    "droop_front":   (lambda: RG.droop_spacer(round(RG.droop_stack("front"), 2)), P.PETG, 2, FLAT, "none", 0.12, "100%", "D33: front droop stack, one ring on each bought front shock's shaft (0.3 mm wheel droop)"),
    "droop_rear":    (lambda: RG.droop_spacer(round(RG.droop_stack("rear"), 2)), P.PETG, 2, FLAT, "none", 0.12, "100%", "D33: rear droop stack, one ring on each bought rear shock's shaft (3 mm wheel droop)"),
    "droop_spacer_05": (lambda: RG.droop_spacer(0.5), P.PETG, 8, FLAT, "none", 0.12, "100%", "D30: 0.5 mm droop shim, add/remove to tune"),
    "tower_front":   (RG.tower_front, P.PETG_CF, 1, FLAT, "none", 0.20, "4 walls / 40%", ""),
    "tower_rear":    (RG.tower_rear, P.PETG_CF, 1, FLAT, "none", 0.20, "4 walls / 40%", ""),
    "bellcrank_L":   (lambda: RG.bellcrank(1), P.PETG_CF, 1, FLAT, "none", 0.16, "100%", ""),
    "bellcrank_R":   (lambda: RG.bellcrank(-1), P.PETG_CF, 1, FLAT, "none", 0.16, "100%", "has the servo arm"),
    "drag_link":     (lambda: RG.link_flat(RG.LINKS["drag_link"]), P.PETG_CF, 1, FLAT, "none", 0.16, "100%", "M3 ball-stud cups"),
    "tie_rod":       (lambda: RG.link_flat(RG.LINKS["tie_rod"]), P.PETG_CF, 2, FLAT, "none", 0.16, "100%", "M3 ball-stud cups"),
    "servo_link":    (lambda: RG.link_flat(RG.LINKS["servo_link"]), P.PETG_CF, 1, FLAT, "none", 0.16, "100%", "length [unverified] until the servo horn is fitted; the 2 spare_servo_link parts are 2 mm shorter / longer"),
    "spare_servo_link_m2": (lambda: RG.link_flat(RG.LINKS["servo_link"] - 2.0), P.PETG_CF, 1, FLAT, "none", 0.16, "100%", "D53 QA: servo_link 2 mm shorter (the horn tip is [unverified]); keep the one that gives equal lock, not on the car's mass"),
    "spare_servo_link_p2": (lambda: RG.link_flat(RG.LINKS["servo_link"] + 2.0), P.PETG_CF, 1, FLAT, "none", 0.16, "100%", "D53 QA: servo_link 2 mm longer (the horn tip is [unverified]); keep the one that gives equal lock, not on the car's mass"),
    "motor_plate":   (RG.motor_plate, P.PETG_CF, 1, UP_Y, "tree, under the plate (bosses on the bed side)", 0.16, "5 walls / 50%", "touches the motor only on 2 standoff bosses"),
    "lay_holder":    (RG.lay_holder, P.PETG_CF, 1, UP_Y, "none", 0.16, "5 walls / 50%", "nut trap up; clamps the fixed layshaft axle (D50)"),
    "lay_spacer_head": (RG.lay_spacer_head, P.PETG_CF, 1, UP_Y, "none", 0.16, "100%", "ring between the axle screw head and the motor plate (D50)"),
    "lay_spacer_in": (RG.lay_spacer_in, P.PETG_CF, 1, UP_Y, "none", 0.12, "100%", "thin ring on the axle inside the spur (D50)"),
    "lay_drum":      (RG.lay_drum, P.PETG_CF, 1, UP_Y, "none", 0.12, "100%", "spur flange down; wear part"),
    # D46: no spare drum. A slower ratio now means new belts too (the front diff offset is solved per LAY_PULLEY_T):
    # the stock-belt fallback is LAY_PULLEY_T = 21 (95.5 mph, 144T + 91T belts): rebuild reprints lay_drum + bulkhead_fL/fR
    "wheel_hex":     (RG.wheel_hex, P.PETG_CF, 4, FLAT, "none", 0.12, "100%", "wear part"),
}
COUPON_PARTS = {k: (f, P.PLA_CF if k.startswith("G") else (P.TPU if "tread_segment" in k else P.PETG_CF), 1, FLAT,
                    "none", 0.16, "100%", "coupon: see rnd/stage3/coupons.md") for k, f in CP.COUPONS.items()}


def to_print(shape, rot):
    s = rot * shape
    # bake in a Z rotation if the part only fits the bed on a diagonal
    try:
        v, _ = s.tessellate(0.1, 0.3)
    except AttributeError:          # OCC occasionally fails a face at coarse settings
        v = [p.center() for p in s.vertices()]
    ang = CB.best_angle(np.array([(p.X, p.Y) for p in v]))
    if ang:
        s = Rot(0, 0, ang) * s
        ROTATED[id(shape)] = ang
    bb = s.bounding_box()
    return Pos(-bb.min.X, -bb.min.Y, -bb.min.Z) * s


def export(name, shape, rot):
    """STL + 3MF. Retries tessellation tolerances until the mesh is watertight (OCC can leave
    T-junction cracks on spline-edged faces at some tolerances)."""
    s = to_print(shape, rot)
    stl = os.path.join(STL, f"{name}.stl")
    for tol in (0.05, 0.02, 0.01, 0.1):
        export_stl(s, stl, tolerance=tol, angular_tolerance=0.2)
        m = trimesh.load(stl)
        m.merge_vertices(digits_vertex=4)
        if m.is_watertight:
            break
    else:
        BAD.append(name)
    try:
        mm = Mesher()
        mm.add_shape(s, linear_deflection=tol, angular_deflection=0.2)
        mm.write(os.path.join(MF, f"{name}.3mf"))
    except RuntimeError:
        BAD.append(name + " (3mf)")
    bb = s.bounding_box()
    return (round(bb.size.X, 1), round(bb.size.Y, 1), round(bb.size.Z, 1))


def est_hours(vol_cm3, material, infill_note):
    # crude: effective deposition ~9 cm3/h PETG/PLA-CF, ~6 cm3/h TPU, scaled for sparse infill
    rate = 6.0 if material == P.TPU else 9.0
    fill = 0.65 if "%" in infill_note and "100%" not in infill_note else 1.0
    return vol_cm3 * fill / rate + 0.15


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--no-body", action="store_true", help="no-op since D37 (kept for old command lines)")
    ap.add_argument("--gt1", action="store_true", help="also build the retired GT-1 reference body (D37)")
    a = ap.parse_args()
    for d in (STL, MF, PREV):
        os.makedirs(d, exist_ok=True)
    rows, placed = [], []
    t0 = time.time()

    anchors = []
    built = {}
    for name, (fn, mat, qty, rot, sup, layer, walls, note) in {**CHASSIS, **RUNNING, **COUPON_PARTS}.items():
        n0 = len(AN.REGISTRY)
        shp = fn()
        built[name] = (shp, qty)
        anchors += [dict(r, part=name, qty=qty) for r in AN.REGISTRY[n0:]]
        size = export(name, shp, rot)
        vol = shp.volume / 1000
        rows.append(dict(part=name, material=mat, qty=qty, size=size, zrot=ROTATED.get(id(shp), 0), vol=round(vol, 1), supports=sup,
                         layer=layer, walls=walls, note=note, hours=round(est_hours(vol, mat, walls), 1)))
        print(f"  {name:14s} {size}  {vol:6.1f} cm3")
        if name in CHASSIS and name not in ("rim", "tread", "battery_pad", "esc_pad", "twist_key"):
            placed.append((name, shp))
    placed += list(RG.printed_installed().items())

    if a.gt1:
        t = time.time()
        sh = B.shell()
        parts = {**B.panels(sh), **B.joiners(), **B.carriers()}
        for name, shp in parts.items():
            mat = P.PETG
            if name.startswith("body_"):
                sup, walls, note = "tree, inside only", "2 walls / 0% (0.9 mm skin)", "upright; supports touch the inside only"
            elif name.startswith("joiner"):
                sup, walls, note = "tree", "100%", "glue across the seam (inside)"
            else:
                sup, walls, note = "none", "4 walls / 40%", "plate down; glue lip to the skin"
                mat = P.PETG_CF
            size = export(name, shp, FLAT)
            vol = shp.volume / 1000
            rows.append(dict(part=name, material=mat, qty=1, size=size, zrot=ROTATED.get(id(shp), 0), vol=round(vol, 1), supports=sup,
                             layer=0.16 if name.startswith("body_") else 0.2, walls=walls, note=note,
                             hours=round(est_hours(vol, mat, walls) * (1.6 if name.startswith("body_") else 1), 1)))
            print(f"  {name:14s} {size}  {vol:6.1f} cm3")
        placed.append(("body", sh))
        print(f"  body built in {time.time() - t:.0f} s")

    json.dump(rows, open(os.path.join(OUT, "parts.json"), "w"), indent=1)
    # D53f (QA): the tub and the deck are each built whole (cached) and then cut into pieces, so every nut site cut into
    # the whole plate was registered under the FIRST piece built: servo posts 3-4 (in tub_mid) and the three tech-tray
    # bosses (in deck_mid) read as tub_front / deck_front. Credit each split-plate site to the piece whose solid holds
    # the material round its nut (8 points 3.8 mm out from the nut centre, in the nut's plane).
    from build123d import Vector
    import numpy as _np
    for fam in ("tub_", "deck_"):
        pcs = {n: built[n] for n in built if n.startswith(fam)}
        for r in anchors:
            if r["part"] not in pcs or r["mode"] != "nut":      # D55: an insert fallback has no nut centre
                continue
            c, ax = _np.array(r["nut"]), _np.array(r["axis"])
            u = _np.cross(ax, [0, 0, 1] if abs(ax[2]) < 0.9 else [1, 0, 0]); u /= _np.linalg.norm(u); v = _np.cross(ax, u)
            ring = [c + 3.8 * (_np.cos(t) * u + _np.sin(t) * v) for t in _np.linspace(0, 2 * _np.pi, 8, endpoint=False)]
            hits = {n: sum(sh.is_inside(Vector(*p)) for p in ring) for n, (sh, _q) in pcs.items()}
            best = max(hits, key=hits.get)
            if hits[best] and best != r["part"]:
                print(f"  anchor '{r['tag']}' is in {best}, not {r['part']} (split plate)")
                r["part"], r["qty"] = best, pcs[best][1]
    json.dump(anchors, open(os.path.join(OUT, "anchors.json"), "w"), indent=1)       # D53: every threaded point (rnd/tests/test_fasteners.py)
    print(f"  D55 anchors: {sum(a['mode'] == 'nut' for a in anchors)} hex-nut + washer sites, {sum(a['mode'] == 'insert' for a in anchors)} heat-set insert sites (per part design; x qty in the test)")
    if BAD:
        raise SystemExit(f"NON-MANIFOLD MESH: {BAD}")

    # ---- previews --------------------------------------------------------------------
    col = {"tub_front": (0.25, 0.25, 0.28), "tub_mid": (0.29, 0.29, 0.32), "tub_rear": (0.32, 0.32, 0.36), "deck_front": (0.2, 0.2, 0.2),
           "deck_mid": (0.2, 0.2, 0.2), "deck_rear": (0.2, 0.2, 0.2), "body": (0.85, 0.22, 0.18),
           "splitter": (0.15, 0.15, 0.15), "diffuser": (0.15, 0.15, 0.15)}
    items = [(R.tris_of(s, 0.8), col.get(n, (0.45, 0.45, 0.5) if n in CHASSIS else (0.95, 0.55, 0.15)))
             for n, s in placed if n != "body"]
    for n, e in RG.bought_envelopes().items():
        items.append((R.tris_of(e, 1.0), (0.55, 0.75, 0.95) if n.startswith(("belt", "diff", "cvd")) else (0.85, 0.85, 0.3)))
    for nm, e in C.electronics().items():
        items.append((R.tris_of(e, 1.0), {"battery": (0.2, 0.4, 0.9), "esc": (0.2, 0.7, 0.3),
                                         "servo": (0.6, 0.3, 0.8), "motor": (0.85, 0.6, 0.1),
                                         "spur": (0.9, 0.9, 0.2)}.get(nm, (0.2, 0.45, 0.85))))
    rim, tread = Wh.rim(), Wh.tread()
    ring = Wh.clamp_ring() if Wh.BELTED else None
    for ax in (0.0, P.WB):
        for s in (1, -1):
            items.append((R.tris_of(Wh.place(rim, ax, s), 0.8), (0.75, 0.75, 0.78)))
            if ring is not None:
                items.append((R.tris_of(Wh.place(ring, ax, s), 0.8), (0.6, 0.6, 0.64)))
            items.append((R.tris_of(Wh.place(tread, ax, s), 0.8), (0.08, 0.08, 0.08)))
    R.render(items, os.path.join(PREV, "chassis_assembly.png"), views=("iso", "top", "side", "rear_iso"),
             title="Platform v1, option B: printed running gear (orange), bought power path (blue/yellow)")
    if a.gt1:
        body_items = items + [(R.tris_of(dict(placed)["body"], 0.8), col["body"])] + \
            [(R.tris_of(v, 0.8), (0.3, 0.3, 0.3)) for k, v in parts.items() if k.startswith("carrier")]
        R.render(body_items, os.path.join(PREV, "car_with_body.png"), views=("iso", "side", "front", "rear_iso"),
                 title="Platform v1 + GT-1 body")
    R.render([(R.tris_of(rim, 0.3), (0.75, 0.75, 0.78))] + ([(R.tris_of(ring, 0.3), (0.6, 0.6, 0.64))] if ring is not None else []) +
             [(R.tris_of(tread, 0.3), (0.1, 0.1, 0.1))],
             os.path.join(PREV, "wheel.png"), views=("iso", "front", "top"),
             title="T3 wheel (D45): printed rim + bought belted tyre, glued" if Wh.BOUGHT else
             "T2 wheel (D44): split rim + clamp ring + Kevlar-belted tread" if Wh.BELTED else "T1 wheel: rim + keyed tread")
    print(f"done in {time.time() - t0:.0f} s -> {OUT}")


if __name__ == "__main__":
    main()
