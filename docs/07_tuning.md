# 7. Tuning

> Generated from the CAD and BOM data (counts are taken from the model, not typed). Numbers marked [estimate] are modelled or unverified; everything else is counted from the model or read from a seller's page.

## Gearing

The motor plate is slotted for 30-38T pinions on the 66T spur (48 pitch). Modelled at 3S:

| Option | mph mid / high drag / best | A at top | Runway m | Motor can °C |
|---|---|---|---|---|
| GT-2 body: Surpass 3650 3900KV + KK 60A, 3S 5200, 33T (D56 design) | 81.9 / 81.6 / 87.2 | 29.8 | 106 | 49.9 |
| same, 34T | 83.9 / 83.5 / 89.3 | 31.9 | 112 | 50.5 |
| same, 35T (on GT-2 its full-pack best case passes the 88 mph design speed) | 85.8 / 85.4 / 91.3 | 34.0 | 118 | 51.1 |
| GT-2 body: same motor + ESC on 2S 3500 (Turnigy 60C), 33T | 55.8 / 55.6 / 59.4 | 16.4 | 48 | 41.9 |
| same motor + ESC on 2S 3500 (Turnigy 60C), 35T | 58.7 / 58.5 / 62.5 | 18.5 | 53 | 42.6 |
| same motor + ESC on 2S 3500 (Turnigy 60C), 38T | 62.9 / 62.6 / 66.9 | 22.0 | 62 | 43.6 |
| same motor + ESC on 3S 5200, 30T | 75.7 / 75.5 / 80.6 | 24.2 | 89 | 48.2 |

## Belt launch limit

The 3 mm belts are rated below the hardest full-throttle launch. With the tech pack's current ceiling ("run" map) the
launch model keeps every one of its Monte-Carlo launches at or above 1.0× the belt rating (median 1.27×); with no ceiling
a full-throttle stab reaches 0.42× [estimate, launch model]. **Without the tech pack, set the ESC's punch to its lowest
setting and roll into the throttle from a standstill.** The launch model (`tools/launch_sim.py`) is the source.

## Ride height and droop

Ride height 5 mm, set with the spring collars. Droop rings (`droop_front` / `droop_rear`) plus 0.5 mm shims
(`droop_spacer_05`) set how far each wheel can drop.

## Grip: surface, shock oil, camber and toe

From a model of one corner of the car on a random road (`D61`) [estimate: tyre stiffness and the bought shock's piston
are not published; nothing here has been measured on a car].

- **Surface comes first.** A 1/10 car drives on a full-size road. On good asphalt at 82 mph the model has a front tyre
  carrying no load about 38<!--D:grip_air_A=38--> % of the time; on a very smooth surface about 2<!--D:grip_air_smooth=2--> %.
  Pick the smoothest surface you can before you change any setting.
- **Shock oil: pick it with a push test.** Start with the 400 cSt oil on the list. Push one end of the car down about
  4 mm and let go while a phone films it in slow motion. Right: the car rises past its rest height once and settles,
  with no second dip you can see. Rises and dips again: go one step thicker. Creeps back up with no rebound: go one
  step thinner. If it stops short of its rest height the shocks are sticking: rebuild them before you change the oil.
- **Camber: nothing to set.** The links are fixed printed parts and the car is drawn at 0°. The model keeps the outside
  tyre within 0.2<!--D:grip_camber=0.2-->° of upright at the grip limit.
- **Toe: 0° front and rear as drawn.** Touring cars usually run some rear toe-in [practice]; these rear uprights do not
  have it yet.

## Coupon tests

- **C2 nut pull:** hang 400 N (8 × 5 L water jugs) from each boss of `C2_insert_block` for a minute (boss 1: the ordinary
  nut on a washer; boss 2: the servo-post joint, where the washer slot opens through one face). Pass: no pull-through.
- **C5 hex torque:** 4.7 kg on a cord round a finished wheel for a minute. Pass: the pen line across axle, hex and rim stays
  unbroken.
- **G5 belt gap:** before ordering spare belts, try the fingers of `G5_belt_gap_gauge` between the two flanges of the diff's
  belt pulley. The widest finger that drops in to the teeth is the gap (1 notch = 3.5 mm, +0.5 mm a notch). 5.5 mm or more:
  a 5 mm S3M belt fits and is rated about 2.0× the hardest launch. 4.5 or 5.0 mm: a 4 mm belt, about 1.5×. Less: keep the
  3 mm belts and the launch rule above. The printed layshaft pulley is re-printed to the belt's width: 4 mm fits it with no
  other change; 5 mm also needs the rear belt moved 0.5 mm inboard, which is not drawn yet [no wider belt built or tested].
