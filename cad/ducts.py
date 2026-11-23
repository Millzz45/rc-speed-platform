"""D40 ram-air duct: hood intake -> motor heat-sink fans (owner prompt 2026-11-15, G3).

Why this path (rnd/tests/test_ducts.py, from the car_sp20_t CFD): the body cavity sits at Cp -0.26 (open underside),
the hood intake face at Cp -0.05 and the grille at Cp +0.9, but the grille slots total only 2.1 cm2 and the nose is
packed (5 mm under the bonnet over the front mount): the 9.5 cm2 hood intake carries about twice the grille's flow
potential (A * sqrt(dCp)). The motor is the hot part (R14 54 C, R13 mount 53 C of 55), the ESC has 48 K margin, so the
whole intake is ducted to the motor's twin fans. The rear vents stay capped: their Cp (-0.23) equals the cavity's, so
opening them adds no pull; the air leaves through the open underside to the diffuser, as it does now.

One PETG part, no glue (D36):
  - inlet SLEEVE inside the body's intake collar with 0.5 mm per side: the body lowers over it and lifts off;
  - DROP past the servo top (2 mm) and under the collar's rear wall (the throat), outboard of the deck edge;
  - CHANNEL over the ESC, outboard of the deck (1 mm), up to Z 76;
  - HOOD over the twin fans, skirt 1.2 mm clear of the fan box all round, open underneath;
  - 3 TABS on the deck top, each with an M3 heat-set insert; M3 x 8 screws come up through the deck (hidden,
    fitted on the bench before the deck goes on).
Prints top face (Z 76) on the bed: the floors are 21-25 mm bridges, the tabs are 37 deg gussets, no supports.
"""
from lib import box, cyl_z
import params as P

T = 1.2                      # wall: 3 perimeters of 0.4
TOP = 76.0                   # duct top (8 mm under the hood skin at the intake, 24+ mm under the cowl/roof elsewhere)
G_COLLAR = 0.5               # sleeve to collar, per side
ix, iy, iw, il = P.BMI_INTAKE_X, P.BMI_INTAKE_Y, P.BMI_INTAKE_W, P.BMI_INTAKE_L
SX0, SX1 = ix - il / 2 + G_COLLAR, ix + il / 2 - G_COLLAR            # sleeve outer X 46.5..79.5
SY0, SY1 = iy - iw / 2 + G_COLLAR, iy + iw / 2 - G_COLLAR            # sleeve outer Y -49.5..-22.5
DECK_TOP = P.DECK_Z + P.DECK_T                                       # 55
DECK_EDGE = -26.0                                                    # deck half width 26 over X 32..118
Y_IN = DECK_EDGE - 1.0                                               # inboard wall below deck level: 1 mm clear
SERVO_TOP = P.SERVO_BOX[2] + P.SERVO_BOX[5]                          # 29
Z_DROP = SERVO_TOP + 2.0                                             # 31
COLLAR_BOT = P.BMI_INTAKE_Z + 2.0                                    # 66: body collar walls end here
THROAT_X1 = ix + il / 2 + 1.6 + 1.4                                  # 83: just aft of the collar's rear wall (1.4 clear)
ESC_TOP = P.ESC_BOX[2] + P.ESC_BOX[5]                                # 51 since D52 (was 46)
Z_CH = ESC_TOP + 1.5                                                 # channel floor 47.5
CH_Y0 = -54.0                                                        # channel outboard wall
fx, fy, fz = P.FAN_BOX
FAN_X0, FAN_X1 = P.MOTOR_X - fx / 2, P.MOTOR_X + fx / 2               # 128.5..158.5
_yc = P.MOTOR_Y0 - P.MOTOR_L + P.HEATSINK_L / 2
FAN_Y0, FAN_Y1 = _yc - fy / 2, _yc + fy / 2                           # -66..-26
FAN_TOP = P.LAYSHAFT_Z + P.HEATSINK_D / 2 - 1 + fz                    # 57.5
G_FAN = 1.2                                                          # skirt to the [unverified] fan envelope
HX0, HX1 = FAN_X0 - G_FAN - T, FAN_X1 + G_FAN + T
HY0, HY1 = FAN_Y0 - G_FAN - T, FAN_Y1 + G_FAN + T
SKIRT_Z = FAN_TOP - 5.5                                              # skirt overlaps the fan box sides by 5.5 mm
TABS = [(60.0, SY1), (95.0, Y_IN), (112.0, Y_IN)]                    # (x, wall y): tab runs inboard from the wall
TAB_L, TAB_W, TAB_H = 9.5, 10.0, 8.0
DUCT_SCREWS = [(x, y + 4.5) for x, y in TABS]                        # insert axis, 4.5 mm inboard of the wall


def _b(x0, x1, y0, y1, z0, z1):
    return box(x1 - x0, y1 - y0, z1 - z0, x0, y0, z0)


def _tab(x, yw):
    """Gusset tab: flat foot on the deck top, 37 deg underside in print (top face down), insert from below."""
    from build123d import Polygon, extrude, Plane
    # cross-section in the Y-Z plane, extruded along X
    yi = yw + TAB_L                                                   # inboard end (y increases inboard: walls are at -y)
    pts = [(yw, DECK_TOP), (yi, DECK_TOP), (yw + 3.0, DECK_TOP + TAB_H), (yw, DECK_TOP + TAB_H)]
    pl = Plane.YZ.offset(x - TAB_W / 2)
    s = extrude(pl * Polygon(*pts, align=None), TAB_W)
    s -= cyl_z(P.M3_INSERT_D, P.M3_INSERT_L, x, yw + 4.5, DECK_TOP - 0.01)
    return s


def outer_inner():
    O = (_b(SX0, SX1, SY0, SY1, DECK_TOP + 1.0, TOP)                  # sleeve, above the deck
         + _b(SX0, THROAT_X1, SY0, Y_IN, Z_DROP, COLLAR_BOT - 1.5)    # drop + throat, outboard of the deck
         + _b(THROAT_X1, HX0 + 0.01, CH_Y0, Y_IN, Z_CH, TOP)           # channel over the ESC
         + _b(HX0, HX1, HY0, HY1, SKIRT_Z, TOP))                      # hood over the fans
    I = (_b(SX0 + T, SX1 - T, SY0 + T, SY1 - T, DECK_TOP + 1.0 + T, TOP + 1)      # inlet open at the top
         + _b(SX0 + T, THROAT_X1 + T + 0.5, SY0 + T, Y_IN - T, Z_DROP + T, COLLAR_BOT - 1.5 - T)
         + _b(THROAT_X1 + T, HX0 + T + 0.5, CH_Y0 + T, Y_IN - T, Z_CH + T, TOP - T)
         + _b(THROAT_X1 - 0.5, THROAT_X1 + T + 1.0, SY0 + T, Y_IN - T, Z_CH + T, COLLAR_BOT - 1.5 - T)   # drop -> channel
         + _b(HX0 + T, HX1 - T, HY0 + T, HY1 - T, SKIRT_Z - 1, TOP - T))          # hood open underneath
    return O, I


def motor_duct():
    O, I = outer_inner()
    d = O - I
    for x, yw in TABS:
        d += _tab(x, yw)
        d -= cyl_z(P.M3_INSERT_D, P.M3_INSERT_L, x, yw + 4.5, DECK_TOP - 0.01)
    return d


def motor_duct_cfd(t_cfd=3.4):
    """CFD copy: same outside, walls thickened INWARD to t_cfd (2 lattice cells at 1.69 mm), so the solver sees a
    sealed duct; the passage is 4.4 mm narrower than printed (conservative for the flow)."""
    global T
    keep = T
    T = t_cfd
    try:
        O, I = outer_inner()
    finally:
        T = keep
    return O - I


def throat_area_mm2():
    """Smallest passage: the drop under the collar's rear wall vs the channel vs the sleeve."""
    sleeve = (SX1 - SX0 - 2 * T) * (SY1 - SY0 - 2 * T)
    throat = (COLLAR_BOT - 1.5 - Z_DROP - 2 * T) * (Y_IN - SY0 - 2 * T)
    channel = (TOP - Z_CH - 2 * T) * (Y_IN - CH_Y0 - 2 * T)
    return dict(intake=il * iw, sleeve=sleeve, throat=throat, channel=channel, hood=(HX1 - HX0 - 2 * T) * (HY1 - HY0 - 2 * T))
