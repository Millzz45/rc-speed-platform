#!/usr/bin/env python3
"""
Speed / power / thermal model for the compact printed RC speed platform.

Physics (steady state, flat ground, no wind):
  motor:   V_bemf = rpm / KV ;  I = (V_pack - V_bemf) / R_total ;  T = Kt * (I - I0)
           Kt = 60 / (2*pi*KV)  [N*m/A]   (KV in rpm/V)
           R_total = R_motor + R_esc + n_cells * R_cell
  wheel:   F_drive = T * G * eta_drive / r_tire(v)
  resist:  F_res = 0.5*rho*CdA*v^2 + Crr*N*g ,  N = m*g + downforce
  tire:    free spinning ring hoop strain  eps = rho_tire * v^2 / E_tire  (upper bound;
           a tread bonded to a rigid hub grows less, a belted tire ~0). r = r0*(1+k*eps)
  top speed = v where F_drive(v) == F_res(v)   (bisection)
  current-limited speed: same, but I capped at min(ESC cont., pack C*Ah)

Nothing here is measured on the real car yet. Every preset parameter is an input
assumption; see docs/architecture.md for sources and which ones are [unverified].

Usage:
  python3 calc/speed_model.py                       # recommended preset + gearing sweep
  python3 calc/speed_model.py --preset stretch_4s
  python3 calc/speed_model.py --preset rec_3s --pinion 22 --spur 54
  python3 calc/speed_model.py --list
"""
import argparse
import math
from dataclasses import dataclass, replace, asdict

G0 = 9.81
RHO_AIR = 1.20  # kg/m^3, ~20 C sea level
MPH = 2.23694   # m/s -> mph


@dataclass
class Car:
    name: str
    # --- motor ---
    kv: float            # rpm/V
    r_motor: float       # ohm, phase-to-phase / 2 equivalent
    i0: float            # A, no-load current at test voltage
    motor_mass: float    # kg
    motor_max_rpm: float  # mechanical/bearing ceiling
    # --- electrics ---
    cells: int
    v_cell: float        # V under load at start of run (fresh pack ~3.9-4.0, nominal 3.7)
    r_cell: float        # ohm per cell internal resistance
    pack_mah: float
    pack_c: float        # continuous C (manufacturer label, usually optimistic)
    r_esc: float         # ohm (FET + wiring)
    esc_cont_a: float
    # --- drivetrain ---
    pinion: int
    spur: int
    internal_ratio: float  # transmission/diff ratio after the spur (1.0 = direct to diff)
    eta_drive: float      # gear + diff + CVD + bearing efficiency
    # --- tire ---
    tire_d_mm: float
    tire_rho: float       # kg/m^3
    tire_e_mpa: float     # tensile modulus
    growth_k: float       # 1.0 = free ring (unbelted, worst), ~0.3 bonded to hub, 0 = belted
    # --- body / chassis ---
    mass: float           # kg, ready to run
    cda: float            # m^2
    cla: float            # m^2, positive = LIFT, negative = downforce
    crr: float
    # --- launch ---
    mu: float = 0.6          # tire/road friction; printed TPU ~45-55% of rubber (research notes)
    esc_burst_a: float = 0   # current cap while accelerating (punch/ESC limit); 0 -> 2x continuous

    @property
    def gear(self):
        return self.spur / self.pinion * self.internal_ratio

    @property
    def v_pack(self):
        return self.cells * self.v_cell

    @property
    def r_total(self):
        return self.r_motor + self.r_esc + self.cells * self.r_cell

    @property
    def kt(self):
        return 60.0 / (2 * math.pi * self.kv)

    @property
    def i_limit(self):
        return min(self.esc_cont_a, self.pack_c * self.pack_mah / 1000.0)


def tire_radius(c: Car, v: float) -> float:
    r0 = c.tire_d_mm / 2000.0
    eps = c.tire_rho * v * v / (c.tire_e_mpa * 1e6)
    return r0 * (1.0 + c.growth_k * eps)


def state(c: Car, v: float, i_cap: float = None):
    """Forces and electrics at road speed v (m/s)."""
    r = tire_radius(c, v)
    wheel_rpm = v / (2 * math.pi * r) * 60.0
    motor_rpm = wheel_rpm * c.gear
    bemf = motor_rpm / c.kv
    i = max(0.0, (c.v_pack - bemf) / c.r_total)
    if i_cap is not None:
        i = min(i, i_cap)
    torque = max(0.0, c.kt * (i - c.i0))
    f_drive = torque * c.gear * c.eta_drive / r
    q = 0.5 * RHO_AIR * v * v
    lift = q * c.cla
    normal = c.mass * G0 - lift
    f_res = q * c.cda + c.crr * max(normal, 0.0) * 1.0
    return dict(r=r, wheel_rpm=wheel_rpm, motor_rpm=motor_rpm, i=i, torque=torque,
                f_drive=f_drive, f_res=f_res, lift=lift, normal=normal, q=q)


def solve_top_speed(c: Car, i_cap: float = None):
    lo, hi = 0.1, 150.0
    if state(c, lo, i_cap)["f_drive"] < state(c, lo, i_cap)["f_res"]:
        return 0.0
    for _ in range(200):
        mid = 0.5 * (lo + hi)
        s = state(c, mid, i_cap)
        if s["f_drive"] > s["f_res"]:
            lo = mid
        else:
            hi = mid
    return lo


def launch(c: Car, v_top: float, dt: float = 0.002):
    """Full-throttle run from rest. Current capped at the burst limit, force capped by
    traction (4WD: all wheels driven). Returns time/distance to 90% and 95% of v_top,
    peak current and adiabatic motor temperature rise over the run."""
    burst = c.esc_burst_a or 2 * c.esc_cont_a
    i_cap = min(burst, c.pack_c * c.pack_mah / 1000.0 * 2)  # packs tolerate ~2x label briefly
    v = x = t = heat = 0.0
    i_peak = 0.0
    marks = {}
    while t < 60:
        s = state(c, max(v, 0.05), i_cap)
        traction = c.mu * max(s["normal"], 0.0)
        i = s["i"]
        f = s["f_drive"]
        if f > traction:
            # driver/punch setting holds the tires at the grip limit instead of spinning them
            f = traction
            i = traction * s["r"] / (c.gear * c.eta_drive * c.kt) + c.i0
        a = (f - s["f_res"]) / c.mass
        if a <= 1e-4:
            break
        i_peak = max(i_peak, i)
        heat += (i ** 2 * c.r_motor + c.i0 * c.v_pack) * dt
        v += a * dt
        x += v * dt
        t += dt
        for frac in (0.9, 0.95):
            if frac not in marks and v >= frac * v_top:
                marks[frac] = (t, x)
        if 0.95 in marks:
            break
    dT = heat / (c.motor_mass * 460.0)
    return marks, i_peak, dT


def sensitivity(c: Car):
    rows = [f"Sensitivity for {c.name} (top speed, mph):"]
    rows.append("  CdA cm^2 :  " + "  ".join(f"{x*1e4:5.0f}" for x in (0.003, 0.0045, 0.006, 0.008, 0.010)))
    rows.append("  top mph  :  " + "  ".join(f"{solve_top_speed(replace(c, cda=x))*MPH:5.1f}"
                                         for x in (0.003, 0.0045, 0.006, 0.008, 0.010)))
    rows.append("  lift (ClA, + = lift) at that top speed, % of weight:")
    for cla in (-0.004, 0.0, 0.004, 0.008, 0.015):
        cc = replace(c, cla=cla)
        v = solve_top_speed(cc)
        s = state(cc, v)
        pct = s["lift"] / (cc.mass * G0) * 100
        tag = "   << body lifts / flips" if pct >= 50 else ("   < unstable, light front" if pct >= 25 else "")
        rows.append(f"    ClA {cla*1e4:+5.0f} cm^2 -> {v*MPH:5.1f} mph, aero load {pct:+5.0f}%{tag}")
    return "\n".join(rows)


def report(c: Car):
    r0 = c.tire_d_mm / 2000.0
    noload_motor_rpm = c.kv * c.v_pack
    v_noload = noload_motor_rpm / c.gear / 60.0 * 2 * math.pi * r0
    v_top = solve_top_speed(c)
    s = state(c, v_top)
    v_lim = solve_top_speed(c, c.i_limit)
    sl = state(c, v_lim, c.i_limit)

    v_pack_loaded = c.v_pack - s["i"] * c.cells * c.r_cell
    p_elec = c.v_pack * s["i"]
    p_mech_motor = s["torque"] * s["motor_rpm"] * 2 * math.pi / 60.0
    p_wheel = s["f_drive"] * v_top
    loss_motor = s["i"] ** 2 * c.r_motor + c.i0 * c.v_pack
    loss_esc = s["i"] ** 2 * c.r_esc
    loss_batt = s["i"] ** 2 * c.cells * c.r_cell
    loss_drive = p_mech_motor - p_wheel
    # adiabatic motor heating (no airflow): steel+copper average cp ~ 460 J/kgK
    dTdt = loss_motor / (c.motor_mass * 460.0)
    runtime_full = (c.pack_mah / 1000.0) * 0.8 / max(s["i"], 1e-6) * 3600.0
    eps = c.tire_rho * v_top ** 2 / (c.tire_e_mpa * 1e6)
    hoop_mpa = c.tire_rho * v_top ** 2 / 1e6

    out = []
    p = out.append
    p(f"== {c.name} ==")
    p(f"  {c.cells}S @ {c.v_cell:.2f} V/cell = {c.v_pack:.1f} V | {c.kv:.0f} KV | "
      f"{c.pinion}/{c.spur} x {c.internal_ratio:.2f} = {c.gear:.2f}:1 | tire {c.tire_d_mm:.0f} mm | "
      f"{c.mass*1000:.0f} g | CdA {c.cda*1e4:.0f} cm^2")
    p(f"  no-load (theoretical) speed : {v_noload*MPH:6.1f} mph  ({noload_motor_rpm:,.0f} motor rpm)")
    p(f"  equilibrium top speed       : {v_top*MPH:6.1f} mph  at {s['motor_rpm']:,.0f} rpm, "
      f"{s['i']:.0f} A, pack {v_pack_loaded:.1f} V loaded")
    p(f"  current-limited top speed   : {v_lim*MPH:6.1f} mph  (cap {c.i_limit:.0f} A = "
      f"min(ESC {c.esc_cont_a:.0f} A, pack {c.pack_c:.0f}C x {c.pack_mah:.0f} mAh))")
    if s["motor_rpm"] > c.motor_max_rpm:
        p(f"  !! motor rpm {s['motor_rpm']:,.0f} exceeds ceiling {c.motor_max_rpm:,.0f}")
    if s["i"] > c.i_limit:
        p(f"  !! equilibrium current {s['i']:.0f} A exceeds limit {c.i_limit:.0f} A -> "
          f"real speed ~ current-limited figure")
    p(f"  power: electrical {p_elec:5.0f} W | at wheels {p_wheel:5.0f} W | "
      f"aero {s['q']*c.cda*v_top:4.0f} W | rolling {(s['f_res']-s['q']*c.cda)*v_top:3.0f} W")
    p(f"  losses: motor {loss_motor:4.0f} W | ESC {loss_esc:3.0f} W | pack {loss_batt:3.0f} W | "
      f"drivetrain {loss_drive:3.0f} W")
    p(f"  motor heating, no airflow   : +{dTdt:.1f} C/s  (-> +40 C in {40/max(dTdt,1e-6):.0f} s at top speed)")
    p(f"  run time at sustained top   : {runtime_full:4.0f} s (80% of pack)")
    p(f"  tire: hoop stress (free ring) {hoop_mpa:.2f} MPa, free-ring strain {eps*100:.1f}%, "
      f"modelled growth {c.growth_k*eps*100:.1f}% -> D {s['r']*2000:.1f} mm")
    lw = s["lift"] / (c.mass * G0)
    p(f"  aero load at top speed      : {'lift' if s['lift']>0 else 'downforce'} "
      f"{abs(s['lift']):.1f} N = {abs(lw)*100:.0f}% of car weight"
      + ("   !! >= 50% weight: flip/liftoff risk" if lw >= 0.5 else ""))
    # traction-limited top speed: drag + rolling == mu * normal load
    lo, hi = 0.1, 150.0
    for _ in range(100):
        mid = 0.5 * (lo + hi)
        st = state(c, mid)
        if c.mu * max(st["normal"], 0) > st["f_res"]:
            lo = mid
        else:
            hi = mid
    v_trac = lo
    p(f"  traction-limited top speed  : {v_trac*MPH:6.1f} mph  (mu {c.mu} x normal load = drag)"
      + ("   !! BELOW motor top speed -> grip/downforce is the limit" if v_trac < v_top else ""))
    v_tgt = min(v_top, v_trac * 0.999)
    marks, ipk, dT = launch(c, v_tgt)
    m90 = marks.get(0.9)
    m95 = marks.get(0.95)
    p(f"  launch (mu {c.mu}, burst cap {c.esc_burst_a or 2*c.esc_cont_a:.0f} A): "
      + (f"90% ({0.9*v_tgt*MPH:.0f} mph) in {m90[0]:.1f} s / {m90[1]:.0f} m" if m90 else "never reaches 90%")
      + (f", 95% in {m95[0]:.1f} s / {m95[1]:.0f} m" if m95 else "")
      + f"; peak {ipk:.0f} A; motor +{dT:.0f} C over the run (no airflow)")
    return "\n".join(out)


def sweep(c: Car, pinions):
    rows = []
    hdr = (f"  {'pinion':>6} {'ratio':>6} {'no-load':>8} {'top':>6} {'cur-lim':>8} "
           f"{'amps':>5} {'W elec':>6} {'motor W loss':>12} {'rpm':>7}  flags")
    rows.append(f"Gearing sweep for {c.name} (spur {c.spur}, internal {c.internal_ratio:.2f}):")
    rows.append(hdr)
    for pn in pinions:
        cc = replace(c, pinion=pn)
        r0 = cc.tire_d_mm / 2000.0
        vnl = cc.kv * cc.v_pack / cc.gear / 60 * 2 * math.pi * r0
        v = solve_top_speed(cc)
        s = state(cc, v)
        vl = solve_top_speed(cc, cc.i_limit)
        loss = s["i"] ** 2 * cc.r_motor + cc.i0 * cc.v_pack
        flags = []
        if s["i"] > cc.i_limit:
            flags.append("over-current")
        if s["motor_rpm"] > cc.motor_max_rpm:
            flags.append("over-rpm")
        if loss > 120:
            flags.append("hot")
        rows.append(f"  {pn:>6} {cc.gear:6.2f} {vnl*MPH:7.1f}  {v*MPH:6.1f} {vl*MPH:7.1f}  "
                    f"{s['i']:5.0f} {cc.v_pack*s['i']:6.0f} {loss:12.0f} {s['motor_rpm']:7.0f}  "
                    f"{','.join(flags)}")
    return "\n".join(rows)


# ---------------------------------------------------------------------------
# Presets. Values are filled from docs/research.md; see architecture.md table
# for the source / [unverified] status of each.
# ---------------------------------------------------------------------------
PRESETS = {}


def preset(**kw):
    c = Car(**kw)
    PRESETS[c.name] = c
    return c


def build_presets():
    # placeholder base; overwritten by tuned presets below once research is in
    base = dict(
        kv=3900, r_motor=0.018, i0=2.5, motor_mass=0.170, motor_max_rpm=50000,
        cells=3, v_cell=3.85, r_cell=0.004, pack_mah=2200, pack_c=50, r_esc=0.003, esc_cont_a=60,
        pinion=20, spur=54, internal_ratio=1.0, eta_drive=0.88,
        tire_d_mm=66, tire_rho=1210, tire_e_mpa=26, growth_k=0.3,
        mass=1.05, cda=0.0062, cla=0.0, crr=0.020,
    )
    # (base dict is only a template; not registered as a preset)

    # Shared platform: Sakura XI belt 4WD parts, 230 mm wheelbase, 190 mm width,
    # printed PETG-CF chassis, 64 mm printed rim + bonded/keyed TPU 95A tread.
    plat = dict(base,
                internal_ratio=2.0,          # Sakura XI Sport internal 2:1 (HobbyKing listing)
                eta_drive=0.87,              # belt 4WD + 2 gear diffs + CVDs [estimate]
                tire_d_mm=64, tire_rho=1150, tire_e_mpa=3.0,   # D45: bought soft rubber touring tyre [estimate]
                growth_k=0.0156,             # D45: cloth belt holds it to ~1.2% at 100 mph (rnd/tests/test_tire.py T3) [estimate]
                cda=0.0045,                  # research range 0.002-0.005, conservative
                cla=0.0,                     # neutral with undertray; see --cla scenarios
                crr=0.022)

    # TIER B (recommended, budget-sourced): Surpass/GoolRC 3650 3900 KV + 60 A combo
    # (EUR 39, racer.lt/Banggood): 3.175 mm shaft, 50k rpm, 69 A / 900 W, <13 V (3S only).
    # ESC 60 A cont / 320 A burst, LVC. Rm/I0 not published -> estimates.
    preset(name="rec_3650_3s", **{**plat,
           "kv": 3900, "r_motor": 0.016, "i0": 3.5, "motor_mass": 0.185, "motor_max_rpm": 50000,
           "cells": 3, "v_cell": 3.85, "r_cell": 0.005, "pack_mah": 2200, "pack_c": 70,
           "r_esc": 0.005, "esc_cont_a": 60, "esc_burst_a": 120,
           "pinion": 38, "spur": 66, "mass": 1.25})

    # TIER C (stretch): Castle 1406 3800 KV 4-pole (100k rpm rated) + EZRun MAX10 G2 140 A, 4S 1500 100C
    preset(name="stretch_1406_4s", **{**plat,
           "kv": 3800, "r_motor": 0.012, "i0": 4.0, "motor_mass": 0.197, "motor_max_rpm": 100000,
           "cells": 4, "v_cell": 3.85, "r_cell": 0.004, "pack_mah": 1500, "pack_c": 100,
           "r_esc": 0.003, "esc_cont_a": 140,
           "pinion": 34, "spur": 66, "mass": 1.30,
           "mu": 0.9,        # needs the cast-urethane/rubber tread upgrade, not plain TPU
           "cla": -0.003})   # needs undertray + splitter + low-drag wing
    # CALIBRATION: Tamiya TT-02, 3300 KV, 3S, 28T/64T x 2.6 internal, rubber 64 mm tires.
    # GPS 50 mph (53 best, "partly sideways") -- wheelspinmodels.co.uk TT-02 3S article.
    preset(name="cal_tt02", **{**base,
           "kv": 3300, "r_motor": 0.020, "i0": 3.0, "motor_mass": 0.200,
           "cells": 3, "v_cell": 3.95, "pack_mah": 3600, "pack_c": 50, "esc_cont_a": 80,
           "pinion": 28, "spur": 64, "internal_ratio": 2.6, "eta_drive": 0.85,
           "tire_d_mm": 64, "tire_rho": 1150, "tire_e_mpa": 3.0, "growth_k": 0.3,
           "mass": 1.55, "cda": 0.0110, "cla": 0.0, "crr": 0.025})


build_presets()


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--preset", default=None)
    ap.add_argument("--list", action="store_true")
    ap.add_argument("--all", action="store_true", help="report every preset")
    ap.add_argument("--no-sweep", action="store_true")
    for f in ("kv", "cells", "pinion", "spur", "tire_d_mm", "mass", "cda", "cla", "growth_k",
              "v_cell", "esc_cont_a", "pack_mah", "eta_drive", "mu"):
        ap.add_argument("--" + f, type=float, default=None)
    a = ap.parse_args()

    if a.list:
        for k, v in PRESETS.items():
            print(k, asdict(v))
        return
    names = list(PRESETS) if a.all else [a.preset or DEFAULT_PRESET]
    for n in names:
        c = PRESETS[n]
        over = {f: getattr(a, f) for f in ("kv", "cells", "pinion", "spur", "tire_d_mm", "mass", "cda",
                                           "cla", "growth_k", "v_cell", "esc_cont_a", "pack_mah", "eta_drive", "mu")
                if getattr(a, f) is not None}
        for k in ("cells", "pinion", "spur"):
            if k in over:
                over[k] = int(over[k])
        c = replace(c, **over)
        print(report(c))
        if not a.no_sweep:
            print(sensitivity(c))
            lo = max(8, c.pinion - 6)
            print(sweep(c, range(lo, c.pinion + 7, 2)))
        print()


DEFAULT_PRESET = "rec_3650_3s"

if __name__ == "__main__":
    main()
