# Firmware

__PlatformIO projects. No `.ino` files__ (operator, 2026-09-08).

A sketch carries its build configuration in IDE menu state — which board, whether PSRAM is on, which partition table. None of that is in the file, so a sketch that works on one machine fails on the next and the failure looks like a hardware fault. A `platformio.ini` puts every one of those settings in the repo, next to the code, under version control.

| Project | For | State |
|---|---|---|
| [`bringup-cam/`](bringup-cam/) | [XIAO-ESP32S3-cam](../hardware/XIAO-ESP32S3-cam.md) + [Sense-camera-board](../hardware/Sense-camera-board.md) bench bring-up, [#7](https://github.com/jwilleke/js-rocket-avionics/issues/7) | __untested — no hardware has run it__ |
| [`soak-power/`](soak-power/) | the shared-battery load test, [#8](https://github.com/jwilleke/js-rocket-avionics/issues/8) — drives capture + SD write bursts and logs every cycle and every reset to the card | __untested — no hardware has run it__ |

```sh
cd firmware/bringup-cam
pio run -t upload && pio device monitor
```

__`soak-power` is flashed the same way and then run with the USB unplugged__, because USB-C powers the board and a monitored run measures the bench supply rather than the battery. Its record is `/soak-power.csv` on the card, read after the run.

__None of this is flight firmware.__ Bring-up proves the parts are alive and talking. Apogee, staging and landing detection need the flight profile settled first — see [design.md](../docs/design.md).

__[XIAO-ESP32S3-lora](../hardware/XIAO-ESP32S3-lora.md) has no project here and must not get one.__ It runs stock Meshtastic, pre-flashed, and that is the entire reason there are two modules: a recovery beacon that cannot be broken by our own bugs. Writing firmware for it would throw that away.

__Board settings come from the board definition, not from this repo__, and both projects pin `platform = espressif32@55.3.35` so that stays true across machines. What is a default, what is deliberately restated, and how to recover a board that will not take an upload: [sense-board-PlatformIO.md](sense-board-PlatformIO.md).

Procedure for running any of this: [bench-bringup.md](../docs/bench-bringup.md).
