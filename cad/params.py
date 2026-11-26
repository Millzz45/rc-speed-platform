"""
Single source of truth for every key dimension (mm).

Vehicle frame (BMI-1 datum): origin = front axle centerline, car centerline, ground.
  +X rearward, +Y left, +Z up.

Stage 3 (decision D15, option B): there is no kit. Every value is either
  DESIGN       - our own choice (we print the part on both sides of the interface), or
  a source     - a standard / datasheet / listing, cited inline, or
  [unverified] - a bought-part size nobody publishes. Each of these has a printed gauge in
                 cad/coupons.py; the gauge result is typed back in here (risk K17).
The Phase 2 (kit) version of this file is frozen in rnd/archive/phase2/cad/params.py.
"""

# --- bed ---------------------------------------------------------------------
BED = (180.0, 180.0, 180.0)          # A1 Mini / Prusa Mini build volume
BED_MARGIN = 2.0                     # parts must fit BED - margin

# --- layout --------------------------------------------------------------------
# D58.2 (owner 2026-11-24 "Yes, wheelbase next"): RC_VARIANT picks a second LENGTH of the same chassis for bought 1/10
# 190 mm bodies (listed at 257 mm, sold as fitting 254-260). "" (default) = the 263 mm car: the owner's scale shell and the GT-2 as
# published; nothing about it changes. "u258" = the rear belt one stock size shorter (90T, 270 mm, was 93T): the rear axle
# comes 4.52 mm forward, the layshaft, front belt, motor, pack and every front part stay. Each variant builds into its
# own folder (OUT_NAME) and scores into its own results folder (rnd/tests/common.py); the two never share a file.
import os as _os
VARIANT = _os.environ.get("RC_VARIANT", "")
WB_VARIANTS = {"u257": 256.98, "u258": 258.48, "u260": 259.99}   # rear belt 89T / 90T / 91T on today's layshaft (running_gear.belt_len; rnd/d58/belt_wb.py)
assert VARIANT in ("",) + tuple(WB_VARIANTS), f"unknown RC_VARIANT {VARIANT!r}"
WB_UNIVERSAL = WB_VARIANTS["u258"]
OUT_NAME = "out" + ("_" + VARIANT if VARIANT else "")
WB = WB_VARIANTS.get(VARIANT, 263.0)            # DESIGN (D27): the owner's scale touring shell body at our 64 mm tire (1:10.6); was 216 (D16)
TRACK_F = 163.0       # DESIGN (kept from Phase 2 packaging; fits the 194 mm body)
TRACK_R = 161.0       # DESIGN
LAYSHAFT_X = 167.41   # D50: 3Racing 3 mm belts S3M423-3 (141T) front + S3M279-3 (93T) rear on 20T lay pulleys: centre distances
#   167.78 + 95.61 = 263.39 mm against the 263 mm wheelbase; the 0.39 mm of slack is taken at the FRONT diff seat (running_gear.front_diff_dx), the rear belt lands exact (R3b). Was 170.52:
#        # D48: 171.0 -> 170.52 so the 18T rear belt lands on a stock 90T loop (-0.01 mm; R3b). DESIGN: layshaft (spur + 2 belt pulleys), transverse; fixed when WB grew (D27): only the rear belt lengthens
LAYSHAFT_Z = 27.5        # DESIGN: = motor axis height (transverse motor)
RIDE_Z = 5.0          # floor underside above ground (static ride height)

# --- tires / wheels ------------------------------------------------------------
TIRE_D = 64.0
TIRE_W = 24.0         # D45: bought Tamiya 54994 reinforced (cloth-belted) 1/10 touring tyre, 24 mm wide (was 26, printed tread)
TREAD_T = 8.0         # D50: tyre profile above the BEAD SEAT: 64 mm tyre on a 48 mm seat. Standard 1/10 touring wheels are listed
                      # "1.9 in (47.5 mm)" (Tamiya 53471) with a 52 mm outer flange; the D45 rim had the seat at 52 (was 6.0)
BODY_TIRE_W = 26.0    # D45: the scale shell shell's width scale stays keyed to the 26 mm tyre it was fitted to (the 24 mm bought
                      # tyre sits on the same track centre: 1 mm more arch clearance each side, body unchanged)
TYRE_BOUGHT = True    # D45 (owner 2026-11-17: "we will buy tires then but we will 3d print rims because we want it to match the
                      # scale"; "we can super glue the rim to the tire"): printed show-face rim, bought belted touring tyre CA-glued
                      # to the bead seats (owner-approved exception to D36 no-glue, tyre-to-rim only)
RIM_D = TIRE_D - 2 * TREAD_T          # 58: rim outer (tread seat) diameter
RIM_BALANCE = (4, 18.5, 8.0, 12.0)   # D48 (R6): balance stations in each rim: count, radius of the screw axis (mm), block width, block length.
#   D50: screw axis 20 -> 18.5 mm with the 48 mm bead seat (the counterbore would have cut into the thinner barrel wall).
#   An M3 socket-cap screw (6-12 mm, from the hardware kit) self-taps into each 2.5 mm pilot, head flush in a counterbore.
HEX_AF = 12.0         # 12 mm wheel hex, across flats
HEX_DEPTH = 6.0       # DESIGN: printed hex (we print both the hex and the rim pocket)
AXLE_HOLE = 4.3       # M4 wheel nut axle (1/10 touring standard)
WHEEL_OFFSET = 4.0    # DESIGN (unused since Phase 2; rims are placed by wheels.place)

# --- chassis tub ---------------------------------------------------------------
TUB_X0 = -35.0        # front of tub (bumper is separate)
TUB_X1 = WB + 35.0    # rear of tub
FLOOR_T = 4.0         # floor Z 5..9; lap joint = 2 + 2 mm tongues
FLOOR_TOP = RIDE_Z + FLOOR_T
FLOOR_POCKET_D = 2.8   # D53 weight: isogrid pocket depth in the floor top, 4 mm floor -> 1.2 mm skin (was 2.0 / 2.0, D34); rnd/structure/light_strong_d50.md #3
RAIL_T = 3.0
RAIL_TOP = FLOOR_TOP + 7.0         # D34: low 7 mm edge lips (was 14 mm walls); the full-length upper deck now carries the stiffness
RAIL_X = (70.0, 208.0)       # D47: left lip only along the full-width (68.5) battery side; gaps at the straps (chassis.py)
# floor outline (x, half-width) per side; right side is wider to carry servo/ESC/motor
TUB_LEFT = [(-35, 30), (-12, 38), (26, 57.5), (36, 60.5), (62, 60.5), (70, 68.5), (208, 68.5), (WB - 20, 60.5), (WB + 10, 44), (WB + 35, 34)]   # D47: 68.5 over the moved pack (x 74..206)   # D46: left side 56 -> 60.5 for the 43 mm pack + strap slot
TUB_LEFT_W = 68.5
TUB_RIGHT = [(-35, 30), (-12, 38), (24, 46), (44, 70), (174, 70), (180, 64), (WB - 20, 56), (WB + 10, 44), (WB + 35, 34)]
RAIL_R_X = (44, WB - 42)  # right rail span: clears the steered front tire and the rear tire (wheels.keepout)
# tub lap joints (front tongue under, rear tongue over). D27: 339 mm tub = 3 pieces on a 180 mm bed
TUB_JOINTS = [(78.0, 118.0), (160.0, 200.0)]
SPLIT_X = TUB_JOINTS[0]   # kept for old readers


def joint_screws(a, b):
    """8 countersunk M3 screws across a 40 mm lap: 3 rows on the left, 1 pair on the right."""
    return [(a + 5, 0), (b - 5, 0), (a + 5, 27), (b - 5, 27), (a + 5, 40), (b - 5, 40), (a + 9, -30), (a + 9, -54)]


JOINT_SCREWS = [s for a, b in TUB_JOINTS for s in joint_screws(a, b)]
DECK_Z = 52.0         # DESIGN: underside of top deck = bulkhead / layshaft-holder tops (belt top 48.8)
DECK_T = 3.0
DECK_X = (-26.0, WB + 16.0)                # D34: full-length upper deck, front bulkheads -> rear bulkheads (was -26..181)
# D34 deck plan (x, half-width), rounded in cad/chassis.py: narrow nose under the bonnet, 33 mm over both bulkhead pairs
# (their top inserts at y 27), waisted to 22 mm over the motor so the fan heat sink clears it
DECK_HALF_W = [(-26, 21), (-16, 23), (-7, 33), (17, 33), (32, 26), (118, 26), (126, 22), (162, 22), (172, 27),
               (WB - 26, 27), (WB - 15, 33), (WB + 16, 33)]
DECK_LAPS = [(-2.0, 14.0), (160.0, 176.0)]
# D57 top-loading drivetrain (owner 2026-11-23 "go ahead" on the D55.6 proposal). The bearing-cap screws are deck screws
# at x +-BH_SCREW_DX (were +-10), so the deck grows: wider nose (also puts the D39b bellcrank pivots, y 26, back on the
# deck: they were 2.5 mm past its edge), 2 mm longer tail, front lap 3 mm aft so the rear front-cap screw stays inside it.
TOP_LOAD = True
if TOP_LOAD:
    DECK_X = (-26.0, WB + 18.0)
    DECK_HALF_W = [(-26, 21), (-24, 31), (-7, 33), (17, 33), (32, 26), (118, 26), (126, 22), (162, 22), (172, 27),
                   (WB - 26, 27), (WB - 15, 33), (WB + 18, 33)]
    DECK_LAPS = [(1.0, 17.0), (160.0, 176.0)]  # D34: 3 deck pieces; laps sit on screws that go on into inserts below
DECK_SPLIT = DECK_LAPS[0]  # kept for old readers

# ---- option B running gear (Stage 3) ---------------------------------------------------
# bought parts: sizes nobody publishes are [unverified] and calibrated with cad/coupons.py
DIFF_Z = 29.5                   # DESIGN: diff axis height (belt clears floor 9 and deck 52)
DIFF_BRG = (10.0, 15.0, 4.0)    # [unverified] diff bearing d x D x B (1/10 touring norm; HSP kit lists 10x15x4) -> gauge G1
DIFF_SPAN = 46.0                # [unverified] outer face to outer face of the two diff bearings -> gauge G2
DIFF_CASE_D = 24.0              # [unverified] diff case diameter (envelope only) -> gauge: bulkhead dry-fit, build guide step 2
PULLEY_PITCH = 3.0              # S3M pitch (Pfeifer profile chart, research_notes/stage1_standard_parts.md)
DIFF_PULLEY_T = 38              # 38T (3Racing SAK-XS110/V2 listing)
LAY_PULLEY_T = 20               # D50: 20T (was 18T) so the two 3 mm belts the diff's maker sells fit the 263 mm wheelbase; the 34T
#   pinion (PINION_T) keeps the overall ratio: 66/34 x 38/20 = 3.69 (was 66/38 x 38/18 = 3.67). History: 18T =               # D48 (owner: "lower the ceiling to near 80mph"): 23 -> 18T, 38/18 = 2.11. At the OpenFOAM drag
#   (CdA 141 cm2; the old 62 cm2 was an Ahmed over-correction of FluidX3D) 23T was 91 mph at 82 A, over the 60 A ESC;
#   18T is 79.5 mph at 50 A (rnd/power/gear_sweep_low.py). Belts: front 142T, rear 90T (LAYSHAFT_X 170.52).
#   History: DESIGN (D46: 22 -> 23T, 38/23 = 1.65: 98.6 -> 101.6 mph after the D45b belted tyre cut tyre growth). (D38): 38/22 = 1.73 internal ratio, was 19T (2.0): 90 -> 100 mph at the CFD drag; 21T = fallback drum if the blower test finds no downforce (rnd/tests/test_power.py)
BELT_W = float(_os.environ.get("RC_BELT_W", "3.0"))   # STUDY override only (rnd/d60/belt_fit.sh, belt_track.py); no build sets it. D50: 3 mm S3M belts (3Racing SAK-A577 / SAK-A576, stated 3 mm). Was 6 mm, which the bought diff's
#   touring-car pulley very probably does not take (rnd/market/parts_followup_d50.md); flange gap still unpublished -> gauge
PINION_T, SPUR_T = 35, 66       # D55: 35T (Arrowmax AM-348035, same family and price as the 34T) for >= 80 mph at the HIGH drag; D50 34T: 48P pinion 34T (Arrowmax AM-448034) on the 66T spur; was 38T. The motor plate has no mesh slot,
#   so GEAR_CD fixes the pinion size
PINION_T_GT2 = 33               # D56: the GT-2 customer body is 34 % less draggy (OpenFOAM car_gt2h CdA 81 vs 123 cm2), so on 35T its full-pack best
#   case reaches 90.7 mph, over DESIGN_MPH. 33T (Arrowmax AM-348033, rcjaz USD 5.61) on the same slotted plate (30-38T) keeps >= 80 mph at the
#   high drag with the best case inside DESIGN_MPH (rnd/tests/results_gt2/power.json). The owner's scale shell car keeps PINION_T. Tests: BODY=gt2
FB_Y, RB_Y = 4.25, -2.25        # DESIGN: front / rear belt centre planes (printed spacers set these)
SPUR_Y = (-10.5, -6.0)          # DESIGN: spur face span on the layshaft
GEAR_CD = 25.4 / 48 * (PINION_T + SPUR_T) / 2   # 48P: m (z1 + z2) / 2 (KHK formula): 26.46 mm at 34T/66T (was 27.5 at 38T/66T)
MOTOR_X = LAYSHAFT_X - GEAR_CD  # transverse motor ahead of the layshaft
PINION_RANGE = (30, 38)         # D55: 48P pinions the slotted motor plate takes on the 66T spur (50 / 80 mph builds and tuning)


def motor_slot_dx():
    """D55: motor X offsets (from MOTOR_X) at the largest and smallest pinion of PINION_RANGE: (forward, rearward)."""
    cd = lambda zp: 25.4 / 48 * (zp + SPUR_T) / 2
    return GEAR_CD - cd(PINION_RANGE[1]), GEAR_CD - cd(PINION_RANGE[0])
MOTOR_PLATE_Y = (-15.0, -11.0)  # DESIGN: printed motor plate, 1 mm clear of the motor face (MOTOR_Y0)
MOTOR_ISO_WASHER = (7.0, 3.2, 1.0)   # D48: OD, ID, thickness (mm) of the bought fibre washers that carry the motor on the plate:
#   2 between the motor face and the plate, 2 under the screw heads (were 1 mm printed bosses touching the can, D18).
MOTOR_SCREW_HOLE = 4.2          # D48: plate hole for the 2 motor screws (M3): 0.6 mm air gap round the hot screw
MOTOR_BOLT_SPACING = 25.0       # [unverified] 540/3650 face bolts (M3 on 25 mm) -> gauge G3
LAY_HOLDER_Y = (8.5, 16.5)      # DESIGN: left layshaft bearing block
LAY_BRG = (5.0, 10.0, 4.0)      # MR105 (SKDIN MR105zz, research_notes/stage1_standard_parts.md)
# D50: the layshaft axle is a FIXED 5 mm shoulder screw (McMaster 92981A055: shoulder 5 x 30 mm at -0.010/-0.072, M4 x 0.7 thread
# 9 mm long, head 9 x 4). The two MR105 sit INSIDE the drum; the screw passes the motor plate, and an M4 washer + nyloc clamp it
# to the lay holder. Was an M5 x 35 bolt turning in bearings in the plate and the holder: its plain shank is only 9-13 mm
# long, so the holder-side bearing sat on thread (rnd/market/parts_research_d50.md).
LAY_AXLE = dict(d=5.0, shoulder=30.0, thread=9.0, head_d=9.0, head_h=4.0, washer=0.8, nut_af=7.0, nut_h=5.0)
LAY_AXLE_END = LAY_HOLDER_Y[0] - LAY_AXLE["washer"]     # Y of the shoulder end: the washer sits between its step and the holder face
AXLE_BRG = (5.0, 10.0, 4.0)     # D50: OUTBOARD hub bearing 5 x 10 x 4 (MR105). 3Racing's SAK-X27 driveshaft sheet shows the 5 mm
AXLE_BRG_IN = (5.0, 10.0, 4.0)  # (the 44 mm universal shaft on the BOM runs in two 5 x 10 x 4; only the SSK "40" shaft uses a 3 mm inboard)
#      axle in "M5 x 10 x 4" outboard and "M5 x 10 x 3" INBOARD bearings (rnd/market/downloads_d50/
                                #      3racing_shop_images/SAK-X27-Manual.jpg). Was 6700 (10 x 15 x 4), which cannot run on a 5 mm axle.
AXLE_BORE = 8.0                 #      bore between the two seats: clear of the inner rings (about 6.9), a shoulder for the outer rings
CVD_AXLE_D = 5.0                # [unverified] CVD wheel-axle diameter -> gauge G4
HEX_PIN_D = 2.0                 # [unverified] wheel drive pin (12 mm hex + 2 x 10 pin, GPM listing) -> gauge G4
CHEEK_Y = (23.0, 31.0)          # DESIGN: bulkhead cheek span (inner face = DIFF_SPAN / 2)
ARM_PIN_Y, ARM_PIN_Z = 38.0, 14.0      # DESIGN: lower arm inner hinge (M3 bolt as pin, along X)
ARM_OUT_Y = 58.0                       # DESIGN: lower arm outer pin (to upright / C-hub)
LINK_Z = 48.0                          # DESIGN: upper link OUTER pins (Y 56 rear / ball stud Y 62 front)
LINK_IN = (34.0, 44.0)                 # DESIGN (D30): upper link INNER pin (Y, Z) on the cheek tab, 4 mm below the outer

# D57 top-loading bulkheads: each cheek splits into a lower SADDLE (floor, arm lugs, posts either side of an open U-slot over
# the diff bearing) and a bearing CAP (a plug that fills the slot down to the bearing + a bridge on the post tops carrying the
# upper-link tab). The cap is held by the two deck screws, which go on through it into captive hex nuts in the posts, so
# with the deck off the caps lift free and the diff lifts out. The belt has no slack (whole-tooth, no tensioner), so the diff
# must leave on an arc about the layshaft: BH_SLOT_HW adds that arc's x drift over the lift that clears the posts.
BH_POST_Z = 37.0          # DESIGN: post tops / cap underside (D57b: was 35; raised so the post-nut pocket's 1 mm wall ends at z 30.0, BH_STEP_Z).
                          #   Deck + bridge = 3 + 15 mm: the screw is M3 x 30 with a 3 mm tower foot, M3 x 25 without
BH_HW = 18.6              # DESIGN: saddle half width ABOVE BH_STEP_Z (was 15); the posts hold a washer + nut pocket outboard of the slot
BH_LOW_HW = 15.0          # DESIGN (D57b): saddle half width BELOW BH_STEP_Z = the old bulkhead's, so the cut the scale shell shell's floor sheet
                          #   already has round the chassis (1 mm clearance, top z 29.1) still fits: no body rebuild
BH_STEP_Z = 30.0          # DESIGN (D57b): the saddle widens only above this (shell floor top 29.1 + 0.9)
BH_BRIDGE_HW = 16.3       # DESIGN: cap bridge half width (clears the spring below the deck: rear shocks are 18.5 behind the axle)
BH_CLR = 0.15             # DESIGN: slot-to-plug clearance each side
BH_POST_PAD = 1.5         # DESIGN: posts stand 1.5 mm proud of the cheek's outer face (washer pocket wall)
BH_SCREW_Y = 27.7         # DESIGN: cap screws 0.7 mm outboard of the old y 27, so the 9.3 mm washer-pocket wall stays out of the diff side
def bh_drift(axle_x):
    """x drift (mm, toward the layshaft) of the diff on its belt arc while its bearing rises clear of the posts."""
    import math
    R = math.dist((LAYSHAFT_X, LAYSHAFT_Z), (axle_x, DIFF_Z))
    x0 = math.sqrt(R * R - (DIFF_Z - LAYSHAFT_Z) ** 2)
    zc = DIFF_Z + (BH_POST_Z - (DIFF_Z - DIFF_BRG[1] / 2))
    return x0 - math.sqrt(R * R - (zc - LAYSHAFT_Z) ** 2)
BH_SLOT_HW = round(DIFF_BRG[1] / 2 + 0.1 + max(bh_drift(0.0), bh_drift(263.0)), 2)   # 9.10 mm: widest slot side (rear, toward the layshaft) at the 263 mm design; D58.2: not the variant's, so the FRONT parts are the same on every chassis length
BH_SLOT_HW_F = round(DIFF_BRG[1] / 2 + 0.1 + bh_drift(0.0), 2)   # 8.45 mm (D57c): the front arc drifts only 0.85 mm
BH_SLOT_SEAT = round(DIFF_BRG[1] / 2 + 0.1, 2)                     # 7.60 mm (D57d): the side AWAY from the layshaft needs no drift room
# D58.2b: the REAR slot keeps the 263 mm car's drift room (1.50 mm) on a shorter rear belt while the bearing still clears the
# slot edge on its tighter arc. The slot has 0.10 mm of air beside the seated bearing; a shorter belt uses some of it at the top
# of the lift-out: u258 drifts 1.578 mm, 0.076 more, so 0.024 mm of air is left (263 mm: 0.10). That keeps the rear bulkheads,
# their caps and the cap screws the SAME parts as the 263 mm car, with the nut on its washer (the first u258 build moved the
# forward screw 0.08 mm and the washer pocket no longer fitted: 478 -> 300 N, three new R38 failures). A length whose arc would
# leave under 0.02 mm (u257: -0.003) gets its own wider slot instead.
BH_ARC_AIR_R = round(0.1 - (bh_drift(WB) - bh_drift(263.0)), 3)        # air beside the rear bearing at the top of its lift-out, in the 263 slot
BH_REAR_COMMON = BH_ARC_AIR_R >= 0.02
BH_DRIFT_R = bh_drift(263.0) if BH_REAR_COMMON else bh_drift(WB)
FRONT_DIFF_DX = -0.36     # DESIGN copy of running_gear.front_diff_dx() (params cannot import it; running_gear asserts they agree)


def bh_slot(axle_x):
    """D57d: the U-slot's two edges (x from the axle, vehicle frame) at this axle. The diff only drifts TOWARD the layshaft on
    its belt arc, so only that side gets the drift; the bearing sits FRONT_DIFF_DX off the axle at the front (D46)."""
    b = FRONT_DIFF_DX if axle_x < WB / 2 else 0.0
    d = bh_drift(axle_x) if axle_x < WB / 2 else BH_DRIFT_R
    if LAYSHAFT_X > axle_x:                                   # front: layshaft behind, drift aft (+x)
        return round(b - BH_SLOT_SEAT, 2), round(b + BH_SLOT_SEAT + d, 2)
    return round(b - BH_SLOT_SEAT - d, 2), round(b + BH_SLOT_SEAT, 2)


# D57d: cap screws at x -13.90 (forward) and +12.90 (aft, the spring side) from each axle, both axles, so the shared shock tower's
# foot still lands on the aft screw. Forward: rear slot -9.10 - 0.15 clearance - 1.0 wall - 3.65 washer pocket radius; aft: the
# front slot's aft edge (-0.36 + 7.60 + 0.85 = 8.09) + 0.15 + 1.0 + 3.65 = 12.89, rounded up. At +13.90 (D57b) the aft screw's shank
# came within 0.52 mm of the shock spring at full droop and its deck hole broke into the spring cut-out; at 12.90 the gap is ~1.0 mm.
BH_SCREW_X = (round(-(BH_SLOT_HW + BH_CLR + 1.0 + 3.65), 2), 12.90)
# D58.2: the REAR axle's pair by the same rule on the rear slot. 263 mm: identical (-13.90). D58.2b: u258 and u260 keep the 263 mm
# rear slot (BH_DRIFT_R above), so -13.90 there too; only a length that needs its own wider slot moves the forward screw.
BH_SCREW_X_R = (round(-(round(DIFF_BRG[1] / 2 + 0.1 + max(bh_drift(0.0), BH_DRIFT_R), 2) + BH_CLR + 1.0 + 3.65), 2), 12.90)
BH_SCREW_DX = -BH_SCREW_X[0]                                                     # 13.90 (kept for older callers: the forward screw)
LAY_SPLIT_LEG = 3.0       # DESIGN: layshaft caps (plate + holder) split at the axle centre; the cap's legs reach 3 mm lower to locate it in X
PIVOT_SPACER = (5.5, 4.0)  # D57: bellcrank pivot = M3 x 12 flat-head up through the deck (countersunk underneath), two stacked
                           # 3 x 5.5 x 2.0 mm aluminium shims (RAD-AC-10008, on the BOM for the shock tops) and an M3 nyloc on top;
                           # the crank turns on the shims (was a bare screw
                           # in air: no post, no thread)
                                       #   pins: arms converge inboard -> 0.22-0.27 deg/mm camber gain in bump, roll centre
                                       #   4.4 / 5.3 mm (was parallel: 0 gain, RC on the road) (rnd/suspension/current_geometry.py)
KINGPIN_Y = 62.0                       # DESIGN: front steering axis (M3 ball studs); wheels.KINGPIN_IN follows
SHOCK_X = 18.5                         # DESIGN: shocks behind the axle (steering is ahead of it); D30: +2.5 with the outboard ears
SHOCK_LOW = (55.0, 16.0)               # DESIGN (D30): (Y, Z) lower eye on the arm ear, outboard of the rear fork prongs
                                       #   (was Y 50): motion ratio 0.50/0.60 -> 0.63/0.73 front/rear
SHOCK_TOP_X = SHOCK_X                  # DESIGN (D33): upper eye X; on an M3 stand-off ~7 mm behind the tower plate (moved
                                       #   forward to x 3..9) so the 17.2 mm spring clears it. A rearward lean hit the rear body posts.
SHOCK_TOP = (34.0, 62.5)               # DESIGN (D33): (Y, Z) upper eye on the tower, moved 4.5 mm up the SAME line of
                                       #   action (was (36, 58)): 51 mm static eye-to-eye for the bought 55 mm shock, MR unchanged
# ---- D33 bought shock: 1/10 touring-car 55 mm aluminium oil shock (TT-01/TT-02 type, 4-pack) ----
SHOCK_EXT, SHOCK_COMP = 55.0, 46.0     # LISTED (Hot Racing TR50TRF06M, liquidrc.com): hole-to-hole extended / compressed
SHOCK_STROKE = SHOCK_EXT - SHOCK_COMP  # 9 mm (listed)
SHOCK_BODY_D = 13.0                    # [unverified] body OD under a 14 mm ID spring (listed spring ID 14); gauge: the bought
                                       #   14 mm ID spring itself must slide over the body (go/no-go, risk K23)
SHOCK_COLLAR_D = 16.0                  # LISTED (Absima 2330040 "total diameter" 16 mm): preload collar / largest OD
SHOCK_SHAFT_D = 3.5                    # LISTED (OZRC 55 mm TT shock); some sets use 3 mm: droop rings bored 3.7 fit both
SHOCK_END_D = 7.0                      # DESIGN envelope: rod-end allowance for the fit check (TC rod ends ~6-7 mm); M3 through it
STEER_PIVOT = (-18.0, 26.0)            # DESIGN: bellcrank pivots (X, +-Y), on top of the deck (D39b: was Y 18; out at Y 26 the
                                       # tie-rod arm sits square to the tie rod, so the linkage cannot toggle: no bind to 1.3x lock)
STEER_ARM_X = -14.0                    # DESIGN: tie rods ahead of the axle
TIE_IN = (-26.5, 22.9, 51.0)           # DESIGN (D39b): tie-rod INNER ball (X, Y, Z): a 9 mm crank arm pointing forward (-160 deg)
                                       # with the ball stud hanging under it (was X -14, Z 59.5 above the crank); with TIE_OUT_Z
                                       # bump steer 2.3 -> 0.07 deg/mm, +-16 deg lock at 24.5 deg crank (rnd/tests/test_handling.py)
TIE_OUT_Z = 57.0                       # DESIGN (D39b): tie-rod OUTER ball height on a post on the knuckle arm (was Z 41)
KNUCKLE_POST = (10.0, 11.0, 48.0)      # DESIGN (D39b): tie-rod post on the knuckle arm: X size, Y size (the bending depth), Y start
                                       # (was 10 x 9 from Y 49.5): 1.4x the 50% rule at servo stall through the D39b linkage
SERVO_ARM = (-12.0, -18.0)             # DESIGN (D39b): right crank's servo-link ball (was (-10, -14) on the Y 18 pivot); 9.2 mm
                                       # clear of the bulkhead screw at (-10, -27), 8 mm lever square to the link
CRANK_Z = (54.0, 57.0)                 # DESIGN: bellcranks ride on the deck top (drag link clears the belt), in a 1 mm step
STEER_STEP_X = -5.0                    # DESIGN: front deck is 2 mm thick ahead of this X (crank step, D21: drag link clears the bonnet)
FLOOR_RIDGE = (-25.0, -18.0, 52.0, 4.0)   # DESIGN (D18): X0, X1, width, height - crash stop behind the front mount. D50: 7 mm long
                                          # (was 4): its base shears BETWEEN layers, so it is sized on the across-layer strength
BATTERY_STOP_T = 6.0                      # D50: battery end stops 6 mm thick (were 4): they bend across the layers at the root


def bulkhead_floor_holes(axle_x):
    """Screws up through the floor into each bulkhead half (cheek + lugs)."""
    cheek = [(axle_x + dx, s * 27.0) for s in (1, -1) for dx in (-10, 10)]
    lugs = [(axle_x + dx, s * 40.0) for s in (1, -1) for dx in (-12.25, 12.25)]   # D53: 12.25 (was 11.5), centred in the widened lugs
    return cheek + lugs


def deck_holes():
    """D34: deck screws into the inserts below: both bulkhead pairs (towers share the outer ones), the steering
    pivots, the layshaft holder, and two on the motor plate (one clamps the rear lap)."""
    bxs = BH_SCREW_X if TOP_LOAD else (-10, 10)                                # D57d: the bearing-cap screws (forward, aft)
    by = BH_SCREW_Y if TOP_LOAD else 27.0
    front = [(dx, s * by) for s in (1, -1) for dx in bxs]
    rear = [(WB + dx, s * by) for s in (1, -1) for dx in (BH_SCREW_X_R if TOP_LOAD else bxs)]
    steer = [(STEER_PIVOT[0], s * STEER_PIVOT[1]) for s in (1, -1)]
    lay = [(LAYSHAFT_X, sum(LAY_HOLDER_Y) / 2), (MOTOR_X - 3, MOTOR_PLATE_Y[1]), (LAYSHAFT_X - 3, MOTOR_PLATE_Y[1] - 4.1)]   # D53: lap screw 4.1 mm outboard, its nut clear of the spur
    return front + rear + steer + lay


def motor_plate_floor_holes():
    return [(MOTOR_X - 14, -8.0), (MOTOR_X + 2, -8.0)]   # centred in the 6 mm floor foot


def lay_holder_floor_holes():
    return [(LAYSHAFT_X - 7.5, sum(LAY_HOLDER_Y) / 2), (LAYSHAFT_X + 7.5, sum(LAY_HOLDER_Y) / 2)]   # D53: 7.5 (was 7): 1 mm of wall between the nut pocket and the lower window


# --- electronics (envelopes: x0, y0, z0, sx, sy, sz) --------------------------
# D58.3: on the 258.5 mm chassis the pack sits 6 mm further forward. The rear axle moved 4.52 mm toward a centre of mass that
# did not move, so the front share fell from 47.93 % to 47.53 % (the edge of the owner's 48/52 +-0.5 band); 5.8 mm of pack
# puts it back (rnd/d58/wheelbase_u258.md). The end stops and the corridor wall follow the box; the straps stay put.
BATTERY_DX = {"u258": -6.0}.get(VARIANT, 0.0)
BATTERY_BOX = (79.5 + BATTERY_DX, 20.5, FLOOR_TOP + 3, 132.0, 43.2, 29.5)   # D52: height 29.5 (was 25.5): Zeee's 2-pack listing of this pack says 132*43*29 and 25 mm would make it denser than 12 comparable packs (rnd/market/deep_d52/battery_charger.md); 29.5 clears chassis and shell as built (rnd/tools/d52_fit.py).    # D51: a 4 mm move aft (to hold 48/52 with the speed meter fitted) was tried and REVERTED: the shell is cut 1 mm round this position and the pack touched it (rnd/tests/test_tech.py R16); it needs a body rebuild. D47 48/52: aft past the lay holder (outboard of its M5 end, Y 19.5); was (28.3, 10.3); X 74 -> 69.5 after the source-shell weigh (47.7 -> 48.0 %)   # D46: bay for the Zeee 3S 5200 soft case (132 x 43 x 25, listing) on 3 mm TPU pads,
                                                               # between the front shock (x 27.1) and the lay holder (x 160.7); was CNHL 3S 2200 at x 45
BATTERY_PACK, BATTERY_MASS_G = "3S 5200 soft", 343.0          # D46: rnd/power/pack_options.csv row; G2 30 min (R30)
ESC_BOX = (184.0, -52.0, FLOOR_TOP + 3, 52.0, 39.0, 39.0)      # D52 (owner: "Keep the Surpass"): the Surpass KK 60A case is LISTED 51.5 x 38.5 x 38.5 mm (maker table, rnd/market/deep_d52/power.md); the bay was 50 x 35 x 34. Grown 4 mm toward the tub edge (-Y), so the belt-corridor wall stays 6.8 mm from the rear belt; top at z 51, 1 mm under the deck. The SHELL on disk is still cut round the old box: body rebuild needed. Was (184.0, -48.0, z, 50.0, 35.0, 34.0)      # D47 48/52: turned 90 deg into the empty right-rear bay behind the spur; was (84.5, -61) 35 x 50       # combo ESC, transverse (D34: 1.5 mm forward for the fan heat sink)
SERVO_BOX = (36.0, -62.0, FLOOR_TOP, 40.5, 40.0, 20.0)         # DS3218 on its side, shaft +Y
MOTOR_D, MOTOR_L = 36.0, 50.0
HEATSINK_D, HEATSINK_L = 44.0, 40.0   # D34: bought 36 mm fan heat sink on the can (BOM cooling line) [unverified] envelope; gauge: it slides on the can by hand and the deck clears it by 3+ mm (risk K24)
FAN_BOX = (30.0, 40.0, 9.0)           # D34: its twin 5 V fans on top (X, Y, Z) [unverified] envelope; gauge: the body goes on over it (risk K24)
MOTOR_Y0 = -16.0                # DESIGN: motor face plane (bosses of the printed plate touch it)
SERVO_TAB_Y = -34.0             # MEASURE: tab plane (12 mm behind the shaft face)
SERVO_TAB_HOLES_X = (31.75, 80.75)  # 49 mm along the case
SERVO_TAB_HOLES_DZ = 10.0
BATTERY_REAR_STOP_Y0 = LAY_HOLDER_Y[1] + 1.5   # D46: the rear end stop starts 1.5 mm past the lay holder (it sat on it: 82 mm3, check_fit)
BATTERY_STRAP_X = (110.0, 193.0)  # D47: clear of the lay holder + M5 end (x 158..184)
RX_BOX = (212.0, -10.0, DECK_Z + DECK_T, 35.0, 20.0, 13.0)    # D52: DumboRC P6FG / X6FG gyro receiver is 35 x 20 x 13 mm (rnd/market/deep_d52/tyres_servo_radio.md); was 30 x 20 x 11 at x 214    # D47 48/52: on the rear deck (was x 62)      # D34: receiver + steering gyro on the deck top (D36: snap cradle, no tape)
# ---- D51 tech pack (owner 2026-11-18: "make it the best and lets add some tech in here"). A car computer (throttle current
# ceiling, logger), a GPS and a gyro, plus a pocket for the SkyRC GSM020 speed meter the hobby accepts as proof, on a printed
# tray over the mid deck. The tray is a flat plate on three 3 mm deck bosses, held by three M3 x 6 screws into heat-set
# inserts in those bosses (the car's standard fixing). First drawn with snap legs through the deck windows: printed upright
# they bend across the layers at ~33 MPa when snapped on, against 18 MPa interlayer strength, so they were dropped.
# Sizes: rnd/market/tech_parts_d51.md.
TECH_PACK = True
TECH_TRAY_X = (34.0, 125.5)              # the last 7.5 mm overhangs the deck's waist
TECH_BOSS_H = 4.5                        # D53: 4.5 (was 3.0) so the square nut sits in the boss, not in the 3 mm deck; room under the boards for solder joints and wires
TECH_TRAY_Z = DECK_Z + DECK_T + TECH_BOSS_H
TECH_TRAY_T = 3.0
TECH_SCREWS = ((47.5, -2.0), (112.0, 22.5), (112.0, -22.5))   # three points, so the plate cannot rock: one on the deck rib at X 46-49 between the board pockets, two beside the meter
TECH_BOSS_D = 11.5                       # D53: 11.5 (was 7.0): a 5.8 mm square nut pocket keeps 1.0 mm of wall at its corners in a round boss
# board envelopes on the tray: name -> (x0, y0, length X, width Y, height, pocket depth, open under it)
TECH_BOARDS = {
    # the 38 g meter sits at the back of the tray, nearest the centre of gravity (X 137), so fitting it moves the weight split least
    "gsm020":       (83.5, -19.5, 40.0, 39.0, 16.0, 1.2, False),   # SkyRC GSM020 40 x 39 x 16 mm, 38 g (listing) [unverified shape: corner radii not published]
    "car_computer": (36.0, -26.2, 23.5, 18.0, 5.0, 1.8, True),     # Waveshare ESP32-S3-Zero 23.5 x 18 (height [unverified])
    "gps":          (36.0, 4.3, 22.0, 22.0, 8.2, 1.8, True),       # GEPRC GEP-M10 22 x 22 x 8.2, on the side away from the servo
    "imu":          (61.5, -12.8, 17.8, 25.6, 4.6, 1.8, True),     # Adafruit LSM6DSOX 25.6 x 17.8 x 4.6, turned 90 deg
}
TECH_SENSOR_BOX = (180.0, -10.0, DECK_Z + DECK_T, 23.0, 20.0, 23.0)   # ENVELOPE: the current sensor on the battery lead where it crosses the rear deck. D51b: the part is now the Pololu 5291 board, LISTED 17.8 x 20.3 mm; the box (sized for the first-choice 23 x 20 x 23 sensor) is kept as the room reserved for the board with the lead soldered to it. No mount is drawn for it yet (open item in the report)
TECH_MASS_G = dict(boards=3.0 + 7.8 + 1.7, sensors=1.0 + 6.0, wiring=12.0, gsm020=38.0)   # listings (D51b: Pololu current sensor 1.0 g, was 7.0); wiring 6 g + 2 thermistor probes with cut leads 6 g [estimate]
TECH_LID_H = 15.1                        # room over the tray top: the GSM020 stands 14.8 mm proud of it

# --- D53 rear underbody ------------------------------------------------------------
# The rear mount sits 3 mm up on a flange (rear_mount zb = FLOOR_TOP + 3). The GT-1 diffuser that was that flange retired
# in D37 and left the mount floating with its floor screws short of their nuts; cad/aero.py rear_spacer() fills the gap
# again, and carries the D53 diffuser's front edge when one is fitted. Candidates: rnd/aero/diffuser_d53.py (CFD study).
DIFFUSER_CANDS = {
    "a": dict(deg=8.0, hw=50.0, strakes=()),
    "b": dict(deg=13.0, hw=50.0, strakes=(25.0,)),
    "c": dict(deg=10.0, hw=58.0, strakes=(15.0, 35.0)),
}
DIFFUSER = None              # None until the CFD keeps one (rnd/foam/d53_diffuser.sh); then "a", "b" or "c"
DIFFUSER_L, DIFFUSER_T, DIFFUSER_FIN = 52.0, 1.6, 1.6
SPACER_X = (WB + 26.5, TUB_X1)          # flange under the rear-mount bar, on the floor top (the bar spans BMI_R_X +- 7)
SPACER_HW = 30.0
DIFF_PAD = (TUB_X1, TUB_X1 + 14.0)      # the diffuser's front 14 mm is a pad clamped under the spacer's block by 2 flat-heads
DIFF_SCREW_X = TUB_X1 + 10.0           # behind the rear-mount bar (it ends at BMI_R_X + 7 = 303.5), where the block can be tall enough for a nut
DIFF_PAD_Y = 18.0
DIFF_PAD_T = 3.0                        # plate thickness under the pad (countersinks), 1.6 mm behind it

# --- body mount interface BMI-1 ------------------------------------------------
BMI_F_X, BMI_F_Y, BMI_F_Z = -39.0, 40.0, 30.0      # front hook lip center (lips X -43..-35 ahead of the beam, underside Z)
BMI_F_LIP_T = 4.0                                 # lip thickness (holds a 3.2 mm magnet pocket)
BMI_F_SLIDE = 9.5                                 # body slides REARWARD this far to engage (tongues under the lips)
BMI_R_X, BMI_R_Y, BMI_R_Z = WB + 33.5, 45.0, 40.0  # rear quarter-turn locks (post top at Z)
BMI_INTAKE_X, BMI_INTAKE_Y, BMI_INTAKE_Z = 63.0, -36.0, 64.0   # body hood intake (D34: open duct; the shroud is gone, the collar blows onto the ESC fan)
BMI_INTAKE_W, BMI_INTAKE_L = 28.0, 34.0         # Y width, X length of the upward-facing port
MOTOR_DUCT = False                     # D40 ram-air duct hood intake -> motor fans; OFF since D45 (no hood intake)
HOOD_INTAKE = False                    # D45 (owner 2026-11-17: "we don't want the random bonnet intake near the glass.. only the
                                       # hood scoop being inlet from the front grill"): the D34/D40 port + collar is not cut
NOSE_SDUCT = True                      # D45: the D42 kidney -> plenum -> bonnet scoop duct is THE design (cad/nose_duct.py)
NOSE_KIDNEY_CUT = "slots"   # D50, see below. Was False (D49):                # D49 (owner: "keep our front grill there... only the holes in the hood"): the kidney
                                       # grille stays exactly as the owner's STL; only the two bonnet-scoop floors are cut
NOSE_PLENUM = True    # D50, see below. Was False (D49):                    # D49: False = scoops open into the nose bay; True = the D42 plenum kept under them as a
                                       # sealed pocket (no kidney inlet). Chosen by OpenFOAM (car_d49h_sc vs car_d49h_bl)
# D50 (owner: "the duct can be made behind the grill as the grill is not solid"): NOSE_KIDNEY_CUT = "slots" cuts the
# nose_duct.KID_SLOTS bands through the kidney grille (its bars stay and are thickened to 2.1 mm), and the D42 plenum
# goes back behind it, up to the two hood outlets. True = the old wide-open kidneys (D42-D48); False = grille closed (D49).
SHELL_SPLITTER_BLADE = 12                # D49 (owner: "our front splitter is really aggressive"): blade 12 mm ahead of the nose lip
                                       # (was 20, D31). OpenFOAM at speed: front -2.36 N vs -3.12 N, drag -0.20 N (car_d48h_sp12)
SHELL_SPLITTER = "shell_splitter" if SHELL_SPLITTER_BLADE == 12 else "shell_splitter20"   # rnd/aero/out/print/<name>.stl
BUMPER_BLANK = True                    # D48: 1.6 mm blanking plates behind the bumper's lower and corner intakes, printed as part of
#   the front body panels (as race cars blank unused intakes). OpenFOAM car_sdblanknih_of: front axle -2.10 N, drag
#   -0.31 N at 100 mph vs the open intakes (rnd/foam/compare_nose.py; plates as rnd/aero/bumper_air.py).
BUMPER_BLANK_PLATES = (                # (x0, x1, |y|0, |y|1, z0, z1), mirrored left/right
    (-58.0, -56.4, 30.0, 59.0, 18.0, 30.0),      # behind the lower intake (skin face at x <= -59)
    (-40.0, -38.4, 70.0, 96.0, 12.0, 32.0),      # across the front of the wheel well, behind the corner intake
)
DESIGN_MPH = 88.0                      # D55: 88 (was 86, D48): the 35T best case is 87.0 mph, so every at-speed check runs above it. The speed every "at top speed" safety check uses (lift, ride height, tyre growth,
#   retention, panel suction). = the car's best case on a fresh pack (4.10 V/cell under load, low end of the drag band):
#   rnd/tests/test_power.py checks the model's best case stays <= this.
BODY_MAX_L, BODY_MAX_W = 470.0, 194.0   # D27: L follows the 263 mm wheelbase (endurance body 466)
BODY_SKIRT_Z = 9.0
BODY_T = 0.9                    # shell wall (D18: was 1.3; 2 walls of 0.45)
CARRIER_T = 4.0                 # carrier plate thickness (magnet pocket 3.2 + 0.8 skin)

# --- hardware ------------------------------------------------------------------
M3_CLEAR = 3.4
FASTEN = "nut"                  # D53 (owner: "square nuts instead of heated inserts"): every threaded point is a captive DIN 562
                                # M3 square nut in a printed slot (cad/anchors.py); "insert" restores the D52 heat-set pilots
M3_INSERT_D = 4.0               # heat-set insert pilot (M3 x 4-5.7): kept for FASTEN = "insert" and any site no nut layout fits
M3_INSERT_L = 6.0
M3_HEAD_D = 6.2
M3_CSK_D = 6.4                  # flat-head countersink diameter (underside screws)
MAGNET_D, MAGNET_T = 10.2, 3.2  # 10x3 pocket with clearance

# --- materials (for print table) ----------------------------------------------
PETG_CF, PETG, TPU, PLA_CF = "PETG-CF", "PETG", "TPU 95A", "PLA-CF"


# ---- D30 suspension spec (rnd/suspension/concepts.py, CFD aero loads; GT3 ride frequencies scaled 1:10.6) ----
RIDE_HZ = (11.0, 13.0)          # DESIGN: front / rear ride frequency (a GT3's 3.4 / 4.0 Hz x sqrt(10.6))
SPRING_RATE = 6.48              # LISTED (D48b): Century Spring 71891, 37 lbf/in = 6.48 N/mm, $8.65 each; second source Lee Spring
#   LC 063HJ 03M (37.1 lbf/in, same size). Chosen for the car's REAL mass (2084 g sliced): 11/13 Hz needs 6.30 / 6.54 N/mm.
#   Was 5.3 N/mm (D33), a design value with no product behind it ("Hot Racing TR50TRF06M" could not be found) and sized
#   for the 1.9 kg estimate; McMaster 9657K317 (5.60 N/mm, $8.03 for 6) is the cheap alternative, 6-8 % soft.
SPRING_ID = 13.59               # LISTED (71891): OD 16.76 mm (0.66 in), ID 13.59 mm (0.535 in)
SPRING_WIRE, SPRING_COILS, SPRING_FREE = 1.5875, 2.88, 22.35   # LISTED wire 0.0625 in, free length 0.88 in; 4.88 coils listed,
#   closed and ground ends, so 2.88 active. Listed solid height 7.87 mm, max deflection 13 mm.
SPRING_OD = SPRING_ID + 2 * SPRING_WIRE                    #   (G d^4 / 8 D^3 n, rnd/tests/test_suspension.py); OD 17.2
DROOP_FRONT = 0.3               # DESIGN: mm of wheel droop past static, front (printed droop rings on the bought shock's shaft):
                                #   the nose cannot rise when the body + wing lift it at speed
DROOP_REAR = 3.0                # DESIGN: rear keeps droop for traction over joints
