# microSD card

__Video only, and already in hand.__ Rides the Sense expansion board on board B's SPI.

## The requirement got much weaker, and that was deliberate

An earlier revision demanded __A1/A2 or pSLC__ — written when the sampler wrote to the card in flight, where unbounded write latency would have dropped samples.

__PSRAM buffering removed that.__ Nothing is written to the card during flight; the flight log buffers in PSRAM and flushes after landing. What is left is __sequential video write__ — a speed-class question, not a random-IOPS one. [BOM.md](../docs/BOM.md) records the demotion.

## Why it cannot carry the flight log

__SD write latency is unbounded.__ Cards run wear-levelling and garbage collection at will, so a normally-2 ms write can take __100–250 ms__, spec-legally. At a 500 Hz sample rate that is hundreds of samples lost, during boost, where the data matters most.

Internal flash is worse — see [XIAO-ESP32S3-Sense.md](XIAO-ESP32S3-Sense.md).

> __The card is the more durable of the two records.__ If board B resets in flight the PSRAM log is gone entirely and __the SD video survives__. Worth remembering when deciding what the firmware writes and when.

## Open

- __Never written to__ — capturing video and reading it back is an acceptance criterion of [#7](https://github.com/jwilleke/js-rocket-avionics/issues/7)
- Mass is an estimate in [BOM.md](../docs/BOM.md); weigh it while the scale is out

---

Part numbers, vendors and masses live in [BOM.md](../docs/BOM.md), which is the single source of truth for both. Purchase history is in [shopping-list.md](../docs/shopping-list.md); the reasoning is in [design.md](../docs/design.md).
