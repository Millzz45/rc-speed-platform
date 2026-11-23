# 7. Tuning

> Generated from the CAD and BOM data (counts are taken from the model, not typed). Numbers marked [estimate] are modelled or unverified; everything else is counted from the model or read from a seller's page.

## Gearing

The motor plate is slotted for 30-38T pinions on the 66T spur (48 pitch). Modelled at 3S:

| Option | mph mid / high drag / best | A at top | Runway m | Motor can °C |
|---|---|---|---|---|
| GT-2 body: Surpass 3650 3900KV + KK 60A, 3S 5200, 33T (D56 design) | 81.5 / 81.1 / 86.7 | 31.5 | 107 | 50.3 |
| same, 34T | 83.4 / 83.0 / 88.8 | 33.6 | 113 | 50.9 |
| same, 35T (on GT-2 its full-pack best case passes the 88 mph design speed) | 85.3 / 84.9 / 90.7 | 35.9 | 119 | 51.5 |
| GT-2 body: same motor + ESC on 2S 3500 (Turnigy 60C), 33T | 55.6 / 55.4 / 59.2 | 17.2 | 48 | 42.0 |
| same motor + ESC on 2S 3500 (Turnigy 60C), 35T | 58.5 / 58.3 / 62.2 | 19.5 | 53 | 42.7 |
| same motor + ESC on 2S 3500 (Turnigy 60C), 38T | 62.6 / 62.3 / 66.6 | 23.1 | 62 | 43.6 |
| same motor + ESC on 3S 5200, 30T | 75.4 / 75.1 / 80.3 | 25.5 | 90 | 48.5 |

## Belt launch limit

The 3 mm belts are rated below the hardest full-throttle launch. With the tech pack's current ceiling ("run" map) the
launch model keeps every one of its Monte-Carlo launches at or above 1.0× the belt rating (median 1.27×); with no ceiling
a full-throttle stab reaches 0.42× [estimate, launch model]. **Without the tech pack, set the ESC's punch to its lowest
setting and roll into the throttle from a standstill.** The launch model (`tools/launch_sim.py`) is the source.

## Ride height and droop

Ride height 5 mm, set with the spring collars. Droop rings (`droop_front` / `droop_rear`) plus 0.5 mm shims
(`droop_spacer_05`) set how far each wheel can drop.

## Coupon tests

- **C2 nut pull:** hang 400 N (8 × 5 L water jugs) from each boss of `C2_insert_block` (boss 1: nut on a washer, boss 2: bare
  nut) for a minute. Pass: no pull-through.
- **C5 hex torque:** 4.7 kg on a cord round a finished wheel for a minute. Pass: the pen line across axle, hex and rim stays
  unbroken.
