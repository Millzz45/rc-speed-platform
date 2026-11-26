"""D55 threaded anchors: captive M3 HEX NUTS (DIN 934, 5.5 AF x 2.4 mm) on an M3 flat washer (DIN 125, 7 x 0.5 mm).

D55 (owner rule 2026-11-19, restated in the D55 brief: "M3 hex nuts (DIN 934) in printed pockets; no heat inserts, no
square nuts"). The pocket is two stacked slots run out sideways from the screw: a 7.3 mm WASHER slot on the entry side and a
5.8 mm NUT slot behind it. The washer spreads the screw's pull over 29.4 mm2 of plastic (the bare hex face is 17.1 mm2,
the D53 square nut 21.2 mm2), which is what R38's bearing limit was short of; the 5.8 mm nut slot holds the hex on its
flats so it cannot turn (6.35 mm across corners). Washers and nuts are pre-approved hardware (owner 2026-11-20).

Was (D53):"""
"""D53 threaded anchors: captive M3 SQUARE NUTS (DIN 562, 5.5 x 1.8 mm) instead of heat-set inserts.

Owner standing preference (2026-11-16): "no heat inserts but you can make cutouts to use square nuts". Owner 2026-11-19:
"can we use square nuts instead of heated inserts". No soldering-iron work and no brass, and the nut is captive in plastic,
so a stripped thread costs a nut, not a melted-out insert.

Every threaded point on a printed part calls `anchor(part, entry, axis, tag)`:
  entry  point on the face where the screw ENTERS the part (vehicle coordinates)
  axis   unit direction the screw travels into the part
The nut sits `t` mm in from the entry face; the plastic between the nut and the entry face takes the screw's pull. A slot
5.8 x 2.1 mm runs from the nut pocket sideways (perpendicular to the screw) to the nearest outside face, so the nut slides
in before the part is fitted; once the screw is through it, the nut cannot leave. With far_ok the pocket may instead open
on the face opposite the entry (that face must be reachable at assembly; the screw pulls the nut against the pocket floor).

The search tries t = 3.0, 2.5, 3.5, 4.0, 5.0, 6.0, 7.0 mm and every slot direction on a local crop of the part, and keeps the
shortest slot that leaves >= WALL mm of plastic round the pocket and along the slot (checked to 1.5 mm short of the exit face).
If none passes, D55 grows a local pad round the best pocket (PAD_*); only past PAD_MAX does the site keep an insert
pilot (the build then reports it and R38 fails).

`REGISTRY` (one dict per site) is written to out/anchors.json by build_all.py and read by rnd/tests/test_fasteners.py.
"""
from build123d import Pos, Box, Cylinder, Vector, Plane, Polygon, extrude
import math
import params as P

NUT_S, NUT_M = 5.5, 2.4                         # D55: DIN 934 M3 hex: width across flats, thickness (was DIN 562 square 5.5 x 1.8)
NUT_C = NUT_S / 0.8660254                       # across corners 6.35 mm
WASH_D, WASH_T = 7.0, 0.5                       # D55: DIN 125 M3 washer under the nut, entry side
POCKET_S, POCKET_N = NUT_S + 0.3, NUT_M + 0.3   # nut slot 5.8 wide (holds the hex on its flats), 2.7 thick
POCKET_W, POCKET_WT = WASH_D + 0.3, WASH_T + 0.3   # washer slot 7.3 wide, 0.8 thick
POCKET_M = POCKET_WT + POCKET_N                 # whole pocket thickness along the screw: 3.5 mm
THIN_M = 1.8                                    # D55: DIN 439 M3 THIN hex nut (5.5 AF x 1.8): where a 2.4 mm nut will not fit
# kind -> (nut pocket thickness, washer under it); tried strongest first (washer face 29.4 mm2 > bare hex face 17.1 mm2)
KINDS = {"washer": (POCKET_N, True), "thin_washer": (THIN_M + 0.3, True), "hex": (POCKET_N, False), "thin": (THIN_M + 0.3, False)}
WALL = 1.0                                      # plastic kept round the pocket and the slot
T_TRY = (3.0, 2.5, 3.5, 4.0, 5.0, 6.0, 7.0, 8.0)
TIP = 1.0                                       # screw-tip room past the nut that must still be inside the part
TIP_HOLE = 3.0                                  # clearance hole cut past the nut, so a standard-length screw never bottoms out
MAX_SLOT = 26.0                                 # longest slot accepted (nut centre to exit face, mm)
MIN_EXIT = POCKET_W / 2 - 0.5                   # a nut may open through a face, but most of it must stay inside the plastic
PAD_KINDS = ("washer", "hex")                    # D55: kinds a grown pad may carry (one nut type for the customer: DIN 934)
PAD_MAX = 300.0                                 # mm3 (about 0.4 g of PETG-CF): never grow more; past it the site stays an insert (build fails R38)
REGISTRY = []


def _basis(axis):
    a = Vector(*axis).normalized()
    ref = Vector(0, 0, 1) if abs(a.Z) < 0.9 else Vector(1, 0, 0)
    u = a.cross(ref).normalized()
    v = a.cross(u).normalized()
    return a, u, v


def _box_along(start, d, L, w, a, h):
    """Box from `start` running L along d, w wide (along a x d), h thick along a; centred on the d-line."""
    pl = Plane(origin=tuple(start + d * (L / 2)), x_dir=tuple(d), z_dir=tuple(a))
    return pl.location * Box(L, w, h)


def _box_axial(start, a, u, L, w):
    """Square-section box from `start` running L along a, w x w section."""
    pl = Plane(origin=tuple(start + a * (L / 2)), x_dir=tuple(u), z_dir=tuple(a))
    return pl.location * Box(w, w, L)


def _cyl(p0, a, d, L):
    pl = Plane(origin=tuple(p0 + a * (L / 2)), x_dir=tuple(_basis(tuple(a))[1]), z_dir=tuple(a))
    return pl.location * Cylinder(d / 2, L)


def _hex(p0, a, d, af, L):
    """Hex prism from p0 along a, `af` across flats, one pair of corners along d (so its flats run parallel to d)."""
    rc = af / 2 / math.cos(math.pi / 6)
    pl = Plane(origin=tuple(p0), x_dir=tuple(d), z_dir=tuple(a))
    return pl.location * extrude(Polygon(*[(rc * math.cos(k * math.pi / 3), rc * math.sin(k * math.pi / 3)) for k in range(6)]), L)


def _exit_dist(part, c, d, step=0.25):
    s = 0.0
    while s <= MAX_SLOT:
        s += step
        if not part.is_inside(tuple(c + d * s)):
            return s
    return None


def _vol(shape):
    try:
        return sum(s.volume for s in shape.solids())
    except Exception:
        return 0.0


def _insert(part, entry, a, tag, why):
    REGISTRY.append(dict(tag=tag, mode="insert", entry=[round(float(x), 2) for x in entry], axis=[round(float(x), 3) for x in a], why=why))
    return part - _cyl(Vector(*entry) - a * 0.01, a, P.M3_INSERT_D, P.M3_INSERT_L + 0.01)


def anchor(part, entry, axis, tag, far_ok=False, t_try=None, tip_hole=TIP_HOLE, kinds=("washer", "hex"), pad_ok=True, keep=None, open_mouth=False):
    """D59 open_mouth: the slot may open through a face that is CLOSER to the screw than the seat's 1 mm wall envelope
    (the servo posts: the servo case stands 4.25 mm from the screw and closes the mouth once fitted). The envelope is then
    only checked up to that face, and the site records `mouth_mm` (screw axis to the open face); rnd/tests/test_fasteners.py
    leaves out the part of the washer face and of its outline that lies within 1 mm of the open face.
    D55: try a DIN 934 hex nut on a DIN 125 washer first ("washer"); where its 9.3 mm wall envelope will not fit, a hex
    nut alone ("hex", 7.8 mm envelope, the D53 square-nut size). Only if neither fits does the site fall back to an insert
    pilot (the build reports it; R38 fails on any insert)."""
    a, u, v = _basis(axis)
    e = Vector(*entry)
    if getattr(P, "FASTEN", "nut") != "nut":
        return _insert(part, entry, a, tag, "params.FASTEN is not 'nut'")
    crop = Pos(*tuple(e + a * 8.0)) * Box(60, 60, 60)
    local = part & crop
    tried = []
    pads = []
    fits = {}
    for kind in kinds:
        PN, WSH = KINDS[kind]
        PM = PN + (POCKET_WT if WSH else 0.0)                    # pocket thickness along the screw
        EW = POCKET_W if WSH else POCKET_S                       # widest layer (wall envelope = EW + 2 WALL)
        for t in (t_try or T_TRY):
            c = e + a * (t + PM / 2)                             # pocket centre
            if not local.is_inside(tuple(c)):
                tried.append((kind, t, "pocket centre outside the part"))
                continue
            best = None
            cands = [(u, "u+"), (-u, "u-"), (v, "v+"), (-v, "v-")] + ([(a, "far")] if far_ok else [])
            for d, name in cands:
                ex = _exit_dist(local, c, d)
                if ex is None:
                    tried.append((kind, t, name, "no exit"))
                    continue
                if name == "far":
                    if WSH:                                      # a 7 mm washer cannot pass a 5.8 mm hex bore: no washer here
                        continue
                    core = _box_axial(c - a * (PM / 2), a, u, ex + PM / 2 + 1.0, POCKET_S)
                    gL = max(ex - 1.5, 0.0) + PM / 2 + WALL
                    grown = _box_axial(c - a * (PM / 2 + WALL), a, u, gL, POCKET_S + 2 * WALL)
                    tip_ok = True
                else:
                    # true pocket shape: (washer kind) a round washer seat + its slot on the entry side; a hex seat with two
                    # flats along the slot (the nut slides in on its flats and cannot turn) + its slot; round wall envelope
                    cn = c + a * (PM / 2 - PN / 2)                       # nut layer centre
                    core = _hex(cn - a * (PN / 2), a, d, POCKET_S, PN) + _box_along(cn, d, ex + 1.0, POCKET_S, a, PN)
                    if WSH:
                        cw = c - a * (PM / 2 - POCKET_WT / 2)            # washer layer centre (entry side)
                        core = core + _cyl(cw - a * (POCKET_WT / 2), a, POCKET_W, POCKET_WT) + _box_along(cw, d, ex + 1.0, POCKET_W, a, POCKET_WT)
                    # walls: 1 mm all round the seat (washer envelope 9.3 mm), and along the slot at the NUT width (7.8 mm,
                    # as D53) to 1.5 mm short of the exit; the 7.3 mm washer slot itself must stay inside the part to 1 mm
                    # short of the exit (its sides near the open mouth carry no load: the pull goes through the plastic
                    # between washer and entry face, the nut's torque into the walls round the hex)
                    gL = max(ex - 1.5, 0.0)
                    grown = _cyl(c - a * (PM / 2 + WALL), a, EW + 2 * WALL, PM + 2 * WALL)
                    if gL > 0.05:
                        grown = grown + _box_along(c, d, gL, POCKET_S + 2 * WALL, a, PM + 2 * WALL)
                    tip_ok = local.is_inside(tuple(c + a * (PM / 2 + TIP)))
                    wslot = _box_along(cw, d, max(ex - 1.0, 0.1), POCKET_W, a, POCKET_WT) if WSH else None
                screw = _cyl(e - a * 1.0, a, P.M3_CLEAR, t + PM + tip_hole + 1.0)
                ring = (grown - core) - screw
                mouth = None
                if open_mouth and name != "far":
                    mouth = _exit_dist(local, c, d, step=0.05) - 0.05          # screw axis to the face the slot opens through
                    ring = ring - _box_along(c + d * mouth, d, 30.0, 60.0, a, 60.0)   # nothing to check beyond that face
                breach = _vol(ring - local)
                if name != "far" and WSH:
                    breach += _vol(wslot - local)
                tried.append((kind, t, name, round(breach, 2), tip_ok))
                if kind in PAD_KINDS and ex >= EW / 2 - 0.5 and name != "far":
                    pads.append((breach, kind, t, name, ex, d, core, screw, c, PM, EW))
                if breach < 0.5 and tip_ok and ex >= EW / 2 - 0.5 and (best is None or ex < best[0]):
                    best = (ex, d, name, core, screw, breach, mouth)
            if best is not None and kind not in fits:
                fits[kind] = (best, t, PM, c)
                break                                    # shallowest t that fits this kind
        if kind == kinds[0] and kind in fits:
            break                                        # the strongest kind fits as drawn: nothing to compare
    # D55.1b: the order is strength first. A nut on a washer (29.4 mm2 face, R38 515 N) beats a bare hex (17.1 mm2, 300 N,
    # under R38's 400 N bar), and mass is not a target since D55, so a washer that fits only on a GROWN PAD beats a bare
    # hex that fits the plastic as drawn: washer fit -> washer pad -> hex fit -> hex pad -> insert (fails R38).
    # A pad is the 1 mm wall envelope (seat + slot to 1.5 mm short of the exit) plus TIP + 0.5 mm of screw-tip room,
    # clipped by `keep` (a bought part's envelope); the candidate with the least wall still missing after the clip wins,
    # then the least new plastic. check_fit proves each pad clears its neighbours.

    def take_fit(kind):
        (ex, d, name, core, screw, breach, mouth), t, PM, c = fits[kind]
        REGISTRY.append(dict(tag=tag, mode="nut", nut_kind=kind, entry=[round(float(x), 2) for x in entry],
                             axis=[round(float(x), 3) for x in a], t=t, slot=name, slot_dir=[round(float(x), 3) for x in d],
                             slot_len=round(ex, 2), breach_mm3=round(breach, 3), nut=[round(float(x), 2) for x in c],
                             pocket_mm=round(PM, 2), hole_mm=round(t + PM + tip_hole, 2),
                             **({"mouth_mm": round(mouth, 2)} if mouth is not None and mouth < (POCKET_W if KINDS[kind][1] else POCKET_S) / 2 + WALL else {})))
        return (part - core) - screw

    def best_pad(kind):
        out = None
        for breach, k, t, name, ex, d, core, screw, c, PM, EW in sorted((p for p in pads if p[1] == kind), key=lambda p: p[0]):
            if breach > PAD_MAX:
                break
            full = _cyl(c - a * (PM / 2 + WALL), a, EW + 2 * WALL, PM + 2 * WALL + TIP + 0.5)
            gL = max(ex - 1.5, 0.0)
            if gL > 0.05:
                full = full + _box_along(c, d, gL, POCKET_S + 2 * WALL, a, PM + 2 * WALL)
            pad = full - keep if keep is not None else full
            added = _vol(pad - local)
            left = _vol(((full - core) - screw) - (local + pad)) if keep is not None else 0.0
            if added > PAD_MAX:
                continue
            key = (round(left, 2), added)
            if out is None or key < out[0]:
                out = (key, dict(kind=k, t=t, name=name, ex=ex, d=d, core=core, screw=screw, c=c, PM=PM, pad=pad, added=added, left=left))
            if left < 0.05:
                break                                     # sorted by drawn breach: the first clean one is the smallest pad
        return out

    def take_pad(o):
        REGISTRY.append(dict(tag=tag, mode="nut", nut_kind=o["kind"], entry=[round(float(x), 2) for x in entry],
                             axis=[round(float(x), 3) for x in a], t=o["t"], slot=o["name"], slot_dir=[round(float(x), 3) for x in o["d"]],
                             slot_len=round(o["ex"], 2), breach_mm3=round(o["left"], 3), pad_mm3=round(o["added"], 2),
                             nut=[round(float(x), 2) for x in o["c"]], pocket_mm=round(o["PM"], 2), hole_mm=round(o["t"] + o["PM"] + tip_hole, 2)))
        return ((part + o["pad"]) - o["core"]) - o["screw"]

    spare = None
    for kind in kinds:
        if kind in fits:
            return take_fit(kind)
        if pad_ok and kind in PAD_KINDS:
            o = best_pad(kind)
            if o is not None and o[0][0] < 0.05:
                return take_pad(o[1])
            if o is not None and (spare is None or o[0] < spare[0]):
                spare = o
    if spare is not None:                                 # every pad leaves some wall missing (clipped): least-bad pad
        return take_pad(spare[1])
    return _insert(part, entry, a, tag, "no layout with %.1f mm walls: %s" % (WALL, tried))


def reset():
    REGISTRY.clear()
