# 9. Troubleshooting

> Generated from the CAD and BOM data (counts are taken from the model, not typed). Numbers marked [estimate] are modelled or unverified; everything else is counted from the model or read from a seller's page.

| Symptom | Likely cause | Fix |
|---|---|---|
| Nut spins when tightening | slot printed oversize or nut not seated | back out, push the nut fully home; reprint the part if the hex is rounded |
| Nut will not enter its slot | pocket undersize for your printer | check `C1`; change `POCKET_S` in `cad/anchors.py` and rebuild |
| Clicking under throttle | belt skipping | check belt deflection; lower ESC punch; fit the tech pack's current ceiling |
| Whine, pinion wears fast | mesh too tight | loosen the motor, reset with a paper strip |
| Car pulls one way | unequal steering lock or toe | re-pick the servo link; check the tie rods |
| Front lifts at speed | missing body or aero part | do not run at speed without the body |
| Motor too hot to touch (> 60 °C) | fans unpowered or gearing too tall | power the fans; drop one pinion tooth |
| ESC cuts out | LiPo cut-off or over-current | charge the pack; check the cut-off cell count |
| Car runs on with the transmitter off | fail-safe not set | **stop**: set fail-safe to neutral before any run |
