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

## Height

__10.72 mm__ from the bottom of the XIAO's PCB — 8.22 mm of assembled stack plus the headers' 2.50 mm, camera excluded. That is the figure the nose bore budget in [design.md](../../docs/design.md) is built on.

---

Part numbers, vendors and masses live in [BOM.md](../../docs/BOM.md), which is the single source of truth for both. Purchase history is in [shopping-list.md](../../docs/shopping-list.md); the reasoning is in [design.md](../../docs/design.md).
