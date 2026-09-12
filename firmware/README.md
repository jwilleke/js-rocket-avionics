# Firmware

__PlatformIO projects. No `.ino` files__ (operator, 2026-09-08).

A sketch carries its build configuration in IDE menu state — which board, whether PSRAM is on, which partition table. None of that is in the file, so a sketch that works on one machine fails on the next and the failure looks like a hardware fault. A `platformio.ini` puts every one of those settings in the repo, next to the code, under version control.

| Project | For | State |
|---|---|---|
| [`bringup-cam/`](bringup-cam/) | [XIAO-ESP32S3-cam](../hardware/XIAO-ESP32S3-cam/XIAO-ESP32S3-cam.md) + [Sense-camera-board](../hardware/Sense-camera-board/Sense-camera-board.md) bench bring-up, [#7](https://github.com/jwilleke/js-rocket-avionics/issues/7) | __run 2026-09-12, all pass__: I2C, IMU, a camera frame, 5 s of video, and a 1 MB PSRAM log flushed and read back. SD over SPI at 20 MHz, CS on GPIO21. Prints its device name, `mj-cam` |
| [`stack-load-test/`](../hardware/camera-stack/stack-load-test/) — __lives with [camera-stack](../hardware/camera-stack/camera-stack.md)__ | the camera stack at flight load: IMU + baro sampled into PSRAM while video records, all at once — design.md Verification item 4 | __run 2026-09-12__: zero dropped IMU samples in 60 s; 4.8% of frames dropped on purpose; worst card stall 1 191 ms |
| [`i2c-find/`](i2c-find/) | when `bringup-cam` finds nothing on the bus: which XIAO pins carry the I2C pull-ups, and on which pair the sensors answer | __run 2026-09-12__ — found the wires on D3/D4 |
| [`soak-power/`](soak-power/) | the shared-battery load test, [#8](https://github.com/jwilleke/js-rocket-avionics/issues/8) — drives capture + SD write bursts and logs every cycle and every reset to the card | __run 2026-09-12__: 67 minutes on the shared battery, 82 925 cycles, no reset on either board. Keeps a reset history in NVS as well as on the card |
| [`gps-check/`](gps-check/) | the [L76K-GNSS](../hardware/L76K-GNSS/L76K-GNSS.md) read directly, no Meshtastic, [#6](https://github.com/jwilleke/js-rocket-avionics/issues/6) — fix, satellites in view, best SNR, time to first fix. __Flashed onto XIAO-ESP32S3-cam__, so a GPS with no position in Meshtastic can be split into "module or antenna" against "Meshtastic not reading D6/D7" | __untested — no hardware has run it__ |

__Unplug XIAO-ESP32S3-lora before any upload.__ PlatformIO uploads to the first port it finds, and with both boards on USB that can be the one that must only ever carry stock Meshtastic.

```sh
cd firmware/bringup-cam
pio run -t upload && pio device monitor
```

__`soak-power` is flashed the same way and then run with the USB unplugged__, because USB-C powers the board and a monitored run measures the bench supply rather than the battery. Its record is `/soak-power.csv` on the card, read after the run.

__None of this is flight firmware.__ Bring-up proves the parts are alive and talking. Apogee, staging and landing detection need the flight profile settled first — see [design.md](../docs/design.md).

__[XIAO-ESP32S3-lora](../hardware/XIAO-ESP32S3-lora/XIAO-ESP32S3-lora.md) has no project here and must not get one.__ It runs stock Meshtastic, pre-flashed, and that is the entire reason there are two modules: a recovery beacon that cannot be broken by our own bugs. Writing firmware for it would throw that away. Updating it to a newer __stock__ release is allowed, on purpose and by a set procedure: [the firmware rule](../hardware/XIAO-ESP32S3-lora/XIAO-ESP32S3-lora.md#firmware--stock-meshtastic-only-updated-on-purpose-frozen-for-flight).

__Board settings come from the board definition, not from this repo__, and both projects pin `platform = espressif32@55.3.35` so that stays true across machines. What is a default, what is deliberately restated, and how to recover a board that will not take an upload: [sense-board-PlatformIO.md](sense-board-PlatformIO.md).

Procedure for running any of this: [bench-bringup.md](../docs/bench-bringup.md).
