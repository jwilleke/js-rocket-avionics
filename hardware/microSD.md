# microSD card

__Video only, and already in hand.__ Rides the Sense expansion board on board B's SPI.

## What it holds

__Video only.__ Nothing else is written to the card during flight — the flight log buffers in PSRAM and flushes after landing. That makes this a __sequential write__ job and a speed-class question; __no A1/A2 or pSLC rating is needed__.

__It cannot carry the flight log.__ SD write latency is unbounded — wear-levelling and garbage collection make a normally-2 ms write take __100–250 ms__, spec-legally. At 500 Hz that is hundreds of samples lost during boost.

> __The card is the more durable of the two records.__ If board B resets in flight the PSRAM log is gone entirely and __the SD video survives__. Worth remembering when deciding what the firmware writes and when.

---

Part numbers, vendors and masses live in [BOM.md](../docs/BOM.md), which is the single source of truth for both. Purchase history is in [shopping-list.md](../docs/shopping-list.md); the reasoning is in [design.md](../docs/design.md).
