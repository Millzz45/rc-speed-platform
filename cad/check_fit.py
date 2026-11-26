#!/usr/bin/env python3
"""Interference gate for the assembled car.
  - every printed part + electronics envelope, pairwise
  - every part vs the swept tire envelopes (steering lock + bump/droop, wheels.keepout, 0.5 mm)
  - the car's body (scale shell, D37): its shell + carriers are checked against all of this inside body_m3.py at build
    time; here we read that result (out/bodies/shell/parts.json "clashes"). The GT-1 body is retired.
Exit 1 if any unintended overlap exceeds TOL_MM3.

  ../.venv/bin/python check_fit.py
"""
import itertools, sys
import chassis as C, aero as A, wheels as Wh, running_gear as RG
import params as P
TOL_MM3 = 5.0
# intended contact: lap joints, glued carriers (D34: no shroud/gasket; three deck pieces)
ALLOWED = {("tub_front", "tub_mid"), ("tub_mid", "tub_rear"), ("deck_front", "deck_mid"), ("deck_mid", "deck_rear"),
           ("shell", "carrier_front"), ("shell", "carrier_rear")}


# intended contact in the running gear: pinned joints, ball cups, bearings in seats, bolted stacks
JOINTS = [("ubec_bridge", "e_ubec"),                # D60: the sleeve's crush ribs pinch the regulator by design (0.1 mm)
          ("bulkhead", "arm"), ("bulkhead", "link"), ("bulkhead", "e_diff"), ("bulkhead", "e_cvd"),
          ("arm", "upright"), ("arm", "knuckle"), ("arm", "shock"), ("link", "upright"), ("link", "knuckle"),
          ("shock", "tower"), ("knuckle", "tierod"), ("knuckle", "e_cvd"), ("upright", "e_cvd"),
          ("crank", "drag_link"), ("crank", "tierod"), ("crank", "servo_link"), ("servo_link", "e_servo"),
          ("lay_drum", "e_spur"), ("lay_drum", "e_belt"), ("lay_drum", "e_layshaft"),
          ("motor_plate", "e_motor"), ("e_motor", "e_heatsink"), ("motor_plate", "e_layshaft"), ("lay_holder", "e_layshaft"), ("lay_cap", "e_layshaft"),
          ("tower", "deck"), ("crank", "deck"),
          ("knuckle", "tire_sweep")]          # the knuckle steers WITH the tire


def joint(a, b):
    return any((a.startswith(x) and b.startswith(y)) or (b.startswith(x) and a.startswith(y)) for x, y in JOINTS)


def parts(body=True):
    p = {"tub_front": C.tub_front(), "tub_mid": C.tub_mid(), "tub_rear": C.tub_rear(), "deck_front": C.deck_front(),
         "deck_mid": C.deck_mid(), "deck_rear": C.deck_rear(), "front_mount": C.front_mount(), "rear_mount": C.rear_mount(),
         "bumper": C.bumper(), "ubec_bridge": C.ubec_bridge(),              # D60: fan supply sleeve on the servo
         }
    import aero as AE                                                        # D53: rear spacer (always) + the CFD-kept diffuser
    p["rear_spacer"] = AE.rear_spacer()
    if getattr(P, "DIFFUSER", None):
        p["diffuser_d53"] = AE.diffuser_d53()
    p.update({f"e_{k}": v for k, v in C.electronics().items()})
    if getattr(P, "TECH_PACK", False):                                       # D51: electronics tray + lid on the mid deck
        p["tech_tray"], p["tech_lid"] = C.tech_tray(), C.tech_lid()
    if P.MOTOR_DUCT:
        import ducts as DU
        p["motor_duct"] = DU.motor_duct()                                    # D40
    p.update(RG.printed_installed())
    p.update({f"e_{k}": v for k, v in RG.bought_envelopes().items()})
    p["tire_sweep"] = Wh.keepouts(0.5)
    if body == "gt1":                       # D37: retired GT-1 reference body, only on request
        import body as B
        p["shell"] = B.shell()
        p.update(B.carriers())
    return p


def overlaps(p):
    out = []
    for (a, sa), (b, sb) in itertools.combinations(p.items(), 2):
        if (a, b) in ALLOWED or (b, a) in ALLOWED or (a.startswith("e_") and b.startswith("e_")) or joint(a, b):
            continue
        if "tire_sweep" in (a, b) and "shell" in (a, b):
            continue        # the shell's arches are open cut-outs; the tire passes through them
        b1, b2 = sa.bounding_box(), sb.bounding_box()
        if any(getattr(b1.max, k) < getattr(b2.min, k) or getattr(b2.max, k) < getattr(b1.min, k) for k in "XYZ"):
            continue
        i = sa & sb
        if i.volume > TOL_MM3:
            bb = i.bounding_box()
            out.append((a, b, i.volume, bb))
    return out


def main():
    p = parts(body="gt1" if "--gt1" in sys.argv else False)
    bad = overlaps(p)
    for a, b, v, bb in bad:
        print(f"  CLASH {a} x {b}: {v:.0f} mm3 at X{bb.min.X:.0f}..{bb.max.X:.0f} "
              f"Y{bb.min.Y:.0f}..{bb.max.Y:.0f} Z{bb.min.Z:.0f}..{bb.max.Z:.0f}")
    import json, os
    pj = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "out", "bodies", "shell", "parts.json")
    g2 = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", P.OUT_NAME, "body_gt2", "parts.json")
    if "--nobody" in sys.argv:                  # D58.2: the bare chassis (a bought body goes on the post adapter)
        body_bad, bname = [], "no"
    elif os.path.exists(pj) and "--gt2" not in sys.argv and not P.VARIANT:   # the scale shell body exists at 263 mm only
        body_bad, bname = json.load(open(pj)).get("clashes", []), "scale shell"
    elif os.path.exists(g2):                    # D56: the original GT-2 body (cad/body_gt2.py checks every chassis part exactly)
        ck = json.load(open(g2))["checks"]
        body_bad, bname = [f"{k}: {v}" for k in ("clash", "tight", "overlap") for v in ck[k]], "GT-2"
    else:
        body_bad, bname = ["no body build"], "body"
    for c in body_bad:
        print(f"  {bname} BODY CLASH", c)
    print("fit check:", "FAIL" if (bad or body_bad) else "PASS",
          f"({len(p)} bodies incl. tire sweep; {bname} body + carriers {'clash' if body_bad else 'clear'} per its build)")
    sys.exit(1 if (bad or body_bad) else 0)


if __name__ == "__main__":
    main()
