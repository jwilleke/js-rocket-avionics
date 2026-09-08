# Firmware

__PlatformIO projects. No `.ino` files__ (operator, 2026-09-08).

A sketch carries its build configuration in IDE menu state — which board, whether PSRAM is on, which partition table. None of that is in the file, so a sketch that works on one machine fails on the next and the failure looks like a hardware fault. A `platformio.ini` puts every one of those settings in the repo, next to the code, under version control.

| Project | For | State |
|---|---|---|
| [`bringup-cam/`](bringup-cam/) | [XIAO-ESP32S3-cam](../hardware/XIAO-ESP32S3-cam.md) + [Sense-camera-board](../hardware/Sense-camera-board.md) bench bring-up, [#7](https://github.com/jwilleke/js-rocket-avionics/issues/7) | __untested — no hardware has run it__ |

```sh
cd firmware/bringup-cam
pio run -t upload && pio device monitor
```

__None of this is flight firmware.__ Bring-up proves the parts are alive and talking. Apogee, staging and landing detection need the flight profile settled first — see [design.md](../docs/design.md).

__[XIAO-ESP32S3-lora](../hardware/XIAO-ESP32S3-lora.md) has no project here and must not get one.__ It runs stock Meshtastic, pre-flashed, and that is the entire reason there are two modules: a recovery beacon that cannot be broken by our own bugs. Writing firmware for it would throw that away.

Procedure for running any of this: [bench-bringup.md](../docs/bench-bringup.md).
