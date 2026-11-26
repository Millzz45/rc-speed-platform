# 6. First-run setup

> Generated from the CAD and BOM data (counts are taken from the model, not typed). Numbers marked [estimate] are modelled or unverified; everything else is counted from the model or read from a seller's page.

Run these in order. Do not go faster until the previous line passes.

| # | Test | Pass |
|---|---|---|
| 1 | Weigh the car ready to run (kitchen scale) | 80 mph: about 2055<!--D:mass_g=2055--> g [modelled]; 50 mph about 1880 g |
| 2 | Wheels up, 25 % throttle for 2 min, touch the motor plate | warm, not hot; no belt skip |
| 3 | Leaf blower at the nose, car on 2 kitchen scales | each axle loses ≤ 25 % of its weight |
| 4 | Same blower test with wool tufts taped under the wing: three times with the wing on, three with it unscrewed | rear scale reads heavier with the wing on than off; tufts lie straight back (limp or flapping forward = the wing is stalled: stay under 60 mph and open an issue) |
| 5 | Runway at a 50 % throttle end-point, phone GPS app | straight, no wobble |
| 6 | 5 passes with a 50 °C sticker on the motor plate | sticker has not turned |
| 7 | 100 % end-point, step up 10 mph a pass | 80 mph tier: about 81.9 mph modelled; 50 mph tier about 55.8 mph |
| 8 | 10 full-throttle launches, then look at both belts | no skipped or torn teeth |

Tests 3 and 4 show which way each scale moves, not the real loads: a blower's jet is narrower than the car. The
simulated downforce is not validated against a measurement, and the rear wing is its least certain part, so test 4
is the one check of it you can do at home.

**Radio setup before test 5:** fail-safe to neutral; throttle end-point 50 %; steering end-points so the servo never
pushes against the lock; ESC punch at its lowest setting; ESC LiPo cut-off for your cell count.
