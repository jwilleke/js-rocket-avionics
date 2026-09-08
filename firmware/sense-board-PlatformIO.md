# Seeed XIAO ESP32-S3 Sense under PlatformIO

__Checked against the board definition, 2026-09-08.__ This page started as a vendor-flavoured setup recipe pasted in from the sources at the foot. Every claim in it has now been read against the actual `seeed_xiao_esp32s3.json` in `platform-espressif32@55.3.35`, which is what these projects build with, and the answer is worth knowing before anyone copies the recipe again:

> __Every `board_build.*` line the recipe tells you to add is already in the board definition.__ `memory_type = qio_opi`, `partitions = default_8MB.csv`, `f_cpu = 240000000L`, `f_flash = 80000000L` — all defaults. So are all three `-D` flags: `BOARD_HAS_PSRAM`, `ARDUINO_USB_MODE=1` and `ARDUINO_USB_CDC_ON_BOOT=1` ship in the board's `extra_flags`.

That does not make the recipe wrong, it makes it __a description of the defaults__, and copying it wholesale is how a project ends up overriding one of them by accident. Which is exactly what had happened here.

## What it cost us, and what changed

__[`bringup-cam`](bringup-cam/) and [`soak-power`](soak-power/) both carried `board_build.partitions = huge_app.csv`, and both were wrong to.__ The comment justifying it read *"the camera + SD_MMC + Arduino core does not fit the default app partition"* — true of a 4 MB board, where the default leaves about 1.3 MB. This board is not that board:

| | app space | coredump partition |
|---|---|---|
| `huge_app.csv` (what we set) | 3.00 MB | __no__ |
| `default_8MB.csv` (the board's own default) | __3.34 MB__ | __yes__, 64 KB |

Both images are __under 0.5 MB__, so the override bought nothing and cost the coredump partition. On [`soak-power`](soak-power/) that is the wrong thing to give away: it exists to catch resets, and __somewhere for a panic to land is the difference between "it reset" and "it reset here"__. Both overrides are removed.

The `-D` flags are __kept__, redundant as they are. They are load-bearing, the board definition is not ours, and an upstream edit that dropped one would be silent — the failure it produces is a camera that will not initialise, which reads as a hardware fault and costs a bench session.

__Both projects now pin the platform:__ `platform = espressif32@55.3.35`. Unpinned, `espressif32` resolves to whatever a given machine's registry offers, and everything above — PSRAM, the OPI memory type, the partition table — comes out of that resolution rather than out of this repo. A build that depends on which machine ran it is the thing PlatformIO was adopted to stop; see [`firmware/README.md`](README.md).

## The part of the recipe that is not in the board definition

__Recovering a board that will not take an upload.__ The XIAO has no USB-to-serial chip — the ESP32-S3's native USB *is* the port — so the port disappears when the firmware crashes, sleeps, or holds the USB stack. That is not a broken board and not a cable:

1. Hold the __BOOT__ button down.
2. While holding it, plug the USB-C in — or tap __RESET__ if it is already plugged in.
3. Release BOOT. The chip is now in its ROM bootloader, which needs no working firmware, and the upload will go through.

__Expect to need this on [`soak-power`](soak-power/).__ A run that ends in repeated brownouts can leave the board unable to enumerate long enough to be flashed.

## Checking PSRAM on a board in hand

Both projects already report it — [`bringup-cam`](bringup-cam/src/main.cpp) prints `psramFound()` and the free bytes in its camera step, and [`soak-power`](soak-power/src/main.cpp) logs free PSRAM on every CSV line. There is no need for a separate sanity sketch, and one habit from the pasted version is worth __not__ copying:

```cpp
while (!Serial) { delay(10); }   // do NOT do this here
```

It waits forever when no monitor is attached. [`soak-power`](soak-power/) runs unplugged from USB by design — that is the entire point of the test — so a build that blocks on the serial port would sit there doing nothing while the operator waits for a CSV that never gets written. Both projects use a fixed short delay instead.

## Sources

The original text came from these. They describe the defaults correctly; they simply do not tell you they are defaults.

- [Seeed wiki — XIAO ESP32S3 getting started](https://wiki.seeedstudio.com/xiao_esp32s3_getting_started/)
- [Seeed wiki — ePaper with PlatformIO](https://wiki.seeedstudio.com/epaper_work_with_platformio/)
- [Seeed wiki — XIAO debug mate](https://wiki.seeedstudio.com/getting_started_with_xiao_debug_mate/)
- [Seeed forum — enabling PSRAM on the XIAO ESP32S3 Sense](https://forum.seeedstudio.com/t/how-to-enable-psram-on-xiao-esp32s3-sense/294389)
- [Seeed forum — XIAO ESP32-S3 Sense quality control](https://forum.seeedstudio.com/t/xiao-esp32-s3-sense-quality-control/271145)
- [KamranAghlami/XIAO-ESP32S3-Sense](https://github.com/KamranAghlami/XIAO-ESP32S3-Sense)
