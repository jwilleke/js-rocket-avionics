# microSD card

__Video and the flight log's slices, and already in hand.__ Rides the Sense expansion board on XIAO-ESP32S3-cam's SPI.

## What it holds

__Video, from arming until landing, and the flight log in slices__ (operator, 2026-09-12, [#24](https://github.com/jwilleke/js-rocket-avionics/issues/24)). The sampler writes only PSRAM; a writer task copies the log to the card a slice at a time, alongside the video. Both are __sequential writes__ — a speed-class question; __no A1/A2 or pSLC rating is needed__.

__It cannot be in the sampler's path.__ SD write latency is unbounded — wear-levelling and garbage collection make a normally-2 ms write take __100–250 ms__, spec-legally, and __this card was measured stalling up to 1 191 ms__ ([on the bench](#on-the-bench)). At 500 Hz that is hundreds of samples lost during boost.

## On the bench

__2026-09-12__, in the Sense camera board's slot, FAT32: `bringup-cam` mounted it and wrote `/bringup.jpg` ([#7](https://github.com/jwilleke/js-rocket-avionics/issues/7)).

__Mount it over SPI, CS on GPIO21__ — `SPI.begin(7, 8, 9, 21)` then `SD.begin(21)`, as Seeed's own examples do. The first `bringup-cam` used `SD_MMC` in 1-bit mode on 7/9/8, which leaves the card's CS/DAT3 line to chance at power-up; it was switched before it ever ran. __Run the SPI clock at 20 MHz, not the library's 4 MHz default.__ Measured by `bringup-cam`, 800 × 600 JPEG frames and a 1 MB flush:

| SPI clock | Throughput | Video | Write per frame, mean / worst | 1 MB flush |
|---|---|---|---|---|
| 4 MHz (default) | 123 KB/s | 6.4 fps | 143 / __731 ms__ | 8.6 s |
| __20 MHz__ | __475 KB/s__ | __24.7 fps__ | 27 / __570 ms__ | __1.05 s__ |

__The worst stall is the design number__ — and it keeps growing: 570 and 731 ms here, then __798 ms and 1 191 ms__ under the full camera-stack load, the last on a freshly formatted card ([camera-stack.md](../camera-stack/camera-stack.md#at-flight-load--stack-load-test)). That is up to 5× the 100–250 ms design.md assumed. No sensible PSRAM queue covers it, so __a video recorder drops frames rather than waits__ ([#24](https://github.com/jwilleke/js-rocket-avionics/issues/24)); the flight log never touches the card until landing, which is why it is safe.

__Card in hand: 64 GB__ (SDXC), formatted FAT32 with 32 KB clusters — formatted in place by `mj-cam` on 2026-09-12, after two resets mid-write left it slow and then unmountable until power-cycled.

> __The card is the more durable of the two records.__ If XIAO-ESP32S3-cam resets in flight the PSRAM log is gone entirely and __the SD video survives__. Worth remembering when deciding what the firmware writes and when.

---

Part numbers, vendors and masses live in [BOM.md](../../docs/BOM.md), which is the single source of truth for both. Purchase history is in [shopping-list.md](../../docs/shopping-list.md); the reasoning is in [design.md](../../docs/design.md).
