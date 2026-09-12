# camera-stack

__[XIAO-ESP32S3-cam](../XIAO-ESP32S3-cam/XIAO-ESP32S3-cam.md) with the [Sense camera board](../Sense-camera-board/Sense-camera-board.md) mated__ — the assembly, rather than either part. It exists as its own page because the photographs below settle facts neither part page could show alone.

## What the stack is, bottom to top

![End-on view of the assembled stack seated in a breadboard](XIAO-ESP32S3-Sense-stack-end.jpg)

```text
camera, on a flexible ribbon
Sense camera board          <- white FPC socket for the ribbon, microSD slot
B2B connector
XIAO-ESP32S3-cam            <- USB-C at one end, U.FL and the B2B on the FRONT face
header pins, ~2.50 mm
whatever it stands on       <- breadboard now, the carrier later
```

![Side view of the same stack](XIAO-ESP32S3-Sense-stack-side.jpg)

## What these photographs settled

__The expansion board mates to the FRONT face and sits above the XIAO.__ Two pages had said "beneath" and one had said "above"; the end-on view ends the argument without needing a drawing. Confirmed against Seeed's front pinout, where the B2B connector sits along the bottom edge beside the U.FL socket.

__So the back face stays open__, and with it `BAT+`/`BAT−`. The expansion board never covers the battery pads — it can be mated and unmated with the pigtails already fitted. What covers them is the __carrier__, at the header's 2.50 mm, which is why the pigtail is soldered before the XIAO goes onto its headers. Full argument in [XIAO-ESP32S3-cam](../XIAO-ESP32S3-cam/XIAO-ESP32S3-cam.md).

__The camera is not fixed by the stack.__ It hangs off the expansion board on a flexible ribbon, so its position is set by where the ribbon is routed and clamped, not by the stack's geometry.

## At flight load — [`stack-load-test/`](stack-load-test/)

__A PlatformIO project for this assembly__, not one part: the LSM6DSO32 (accel and gyro at 833 Hz) and the BMP388 (25 Hz) sampled into PSRAM while the camera records 800 × 600 video to the card, all at once — [design.md](../../docs/design.md#verification)'s item 4. Flash it onto XIAO-ESP32S3-cam (`mj-cam`) with the Sense board and a card fitted, never with XIAO-ESP32S3-lora plugged in.

__2026-09-12, 60 s, freshly formatted 64 GB card:__

| | Result |
|---|---|
| __IMU while recording__ | __zero dropped__ — 47 762 accel + 47 762 gyro words at 796 Hz, no FIFO overrun, deepest FIFO 6 words, slowest loop 3 ms. BMP388 25.0 Hz |
| Video | 23.6 fps, 486 KB/s; __71 of 1 489 frames dropped on purpose__ when the card fell behind |
| Worst card write | __1 191 ms__ |
| Log flush after | 669 KB in 0.4 s, read back byte for byte |

__Three rules the recorder ([#24](https://github.com/jwilleke/js-rocket-avionics/issues/24)) inherits — each cost a reset to learn:__

1. __The card writer yields every frame.__ Draining a backlog back-to-back starved `IDLE0` and the task watchdog reset the board
2. __Never hold every camera buffer.__ Queue at most two fewer frames than the driver has; when the card falls behind, drop frames and count them. Holding them all left the driver spinning on `FB-OVF` until the watchdog fired
3. __A reset in the middle of a card write can leave the card dead until its power is cut__ — `f_mount failed: (3)` until the USB was unplugged. In flight, one reset can cost the video after it as well as the PSRAM log

__No buffer covers the card's stalls__ — 570 ms, 798 ms, then 1 191 ms on successive runs — so the recorder drops frames rather than waits. A fresh format did not stop them; it is the card.

## Height

__10.72 mm__ from the bottom of the XIAO's PCB — 8.22 mm of assembled stack plus the headers' 2.50 mm, camera excluded. That is the figure the nose bore budget in [design.md](../../docs/design.md) is built on.

---

Part numbers, vendors and masses live in [BOM.md](../../docs/BOM.md), which is the single source of truth for both. Purchase history is in [shopping-list.md](../../docs/shopping-list.md); the reasoning is in [design.md](../../docs/design.md).
