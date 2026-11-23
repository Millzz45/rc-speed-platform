# 4. Wiring

> Generated from the CAD and BOM data (counts are taken from the model, not typed). Numbers marked [estimate] are modelled or unverified; everything else is counted from the model or read from a seller's page.

## Car (every tier)

| From | To | Note |
|---|---|---|
| Battery (T-plug or XT60) | ESC battery leads | red to red; 2S on the 50 mph tier, 3S on the 80 mph tier |
| ESC 3 motor leads | motor 3 bullets | if the motor runs backwards, swap any two |
| ESC signal lead | receiver CH2 (throttle) | the ESC's BEC powers the receiver and servo |
| Servo | receiver CH1 (steering) |  |
| Fan pair on the heat sink | a separate 5 V BEC (not on the BOM yet) | never on the receiver rail: it carries the servo |

Route the motor leads over the deck, away from the belts. Zip-tie nothing to a moving arm.

## Tech pack (optional)

All logic is 3.3 V: the ESP32-S3 is **not** 5 V tolerant (check the receiver's pulse height first).

| Signal | Board pin (GPIO) | Note |
|---|---|---|
| Receiver throttle CH2 in | 4 | the throttle passes THROUGH the car computer |
| ESC signal out | 6 |  |
| Receiver steering CH1 (tap, log only) | 5 | steering stays plugged straight into the servo |
| GPS TX / RX | 8 / 9 | GEPRC GEP-M10, 115200 baud |
| Gyro SDA / SCL | 10 / 11 | LSM6DSOX, I2C 0x6A |
| RPM sensor | 12 | on any two motor wires |
| Current sensor OUT | 1 | Pololu ACS37220 in the ESC battery + lead; VCC from 3V3 only |
| Pack voltage | 2 | 10 kΩ from battery + to the pin, 2.2 kΩ from the pin to ground |
| Motor / ESC thermistors | 3 / 7 | 10 kΩ probe from 3V3 to the pin, 10 kΩ pin to ground |

If the car computer stops, the ESC gets no pulses and falls back on its own signal-loss protection.
