# microSD card

__Video only, and already in hand.__ Rides the Sense expansion board on XIAO-ESP32S3-cam's SPI.

## What it holds

__Video only.__ Nothing else is written to the card during flight — the flight log buffers in PSRAM and flushes after landing. That makes this a __sequential write__ job and a speed-class question; __no A1/A2 or pSLC rating is needed__.

__It cannot carry the flight log.__ SD write latency is unbounded — wear-levelling and garbage collection make a normally-2 ms write take __100–250 ms__, spec-legally. At 500 Hz that is hundreds of samples lost during boost.

## On the bench

__2026-09-12__, in the Sense camera board's slot, FAT32: `bringup-cam` mounted it and wrote `/bringup.jpg` ([#7](https://github.com/jwilleke/js-rocket-avionics/issues/7)).

__Mount it over SPI, CS on GPIO21__ — `SPI.begin(7, 8, 9, 21)` then `SD.begin(21)`, as Seeed's own examples do. The first `bringup-cam` used `SD_MMC` in 1-bit mode on 7/9/8, which leaves the card's CS/DAT3 line to chance at power-up; it was switched before it ever ran. Write speed has not been measured — it matters for video, and is [#8](https://github.com/jwilleke/js-rocket-avionics/issues/8)'s and [#24](https://github.com/jwilleke/js-rocket-avionics/issues/24)'s to find.

> __The card is the more durable of the two records.__ If XIAO-ESP32S3-cam resets in flight the PSRAM log is gone entirely and __the SD video survives__. Worth remembering when deciding what the firmware writes and when.

---

Part numbers, vendors and masses live in [BOM.md](../../docs/BOM.md), which is the single source of truth for both. Purchase history is in [shopping-list.md](../../docs/shopping-list.md); the reasoning is in [design.md](../../docs/design.md).
