# 5. Firmware (tech pack only)

> Generated from the CAD and BOM data (counts are taken from the model, not typed). Numbers marked [estimate] are modelled or unverified; everything else is counted from the model or read from a seller's page.

> **Status:** the control core (`firmware/core/cc_core.c`) compiles and passes its simulations on a desktop. The ESP32 wrapper
> (`firmware/esp32/carcomputer/carcomputer.ino`) has **not yet been compiled or run on a board**. Treat the first flash as a
> bench test with the wheels off the ground.

## Build the core on a desktop (tests)

```bash
firmware/build_native.sh
```

## Flash the board (Waveshare ESP32-S3-Zero)

1. Install the Arduino IDE 2 (or `arduino-cli`) and the **esp32 by Espressif** board package, version 3.x.
2. Copy `firmware/core/cc_core.c` and `cc_core.h` into `firmware/esp32/carcomputer/`.
3. Keep the shipped `cc_config_car.h`: it holds the car's numbers (motor, gearing 33T / 66T, current ceiling) generated
   from the same model the simulations use. If you change the pinion, the ceiling no longer matches the gearing: keep the 33T pinion while the tech pack is fitted.
4. Board: *ESP32S3 Dev Module*, USB CDC on boot enabled, flash 8 MB (check your board). Upload.
5. Serial monitor at 115200: the board prints its sensor checks at start-up.

## First power-on

Wheels off the ground, transmitter on first. Unplug the car computer's supply lead at part throttle: the motor must stop
within a second.
