# Shopping list — avionics purchases

The receipts. What each part **is** and why it was chosen is in [BOM.md](BOM.md); this page is only what was bought, what it cost and where it is.

**Costs on this page are from order confirmations, not estimates** — except where a row says otherwise. Status is as of **2026-08-09**.

## Orders placed

| Order | Vendor | Date | Total | Status |
|---|---|---|---|---|
| **4000564800** | Seeed | 2026-08-07 | **$35.65** | **Delivered 2026-08-11.** USPS `420430509261290198196828213362`, US warehouse |
| **4000564803** | Seeed | 2026-08-07 | **$18.72** | **Shipped 2026-08-07 from the China warehouse.** YanWen `UL400424782YP`, handed to USPS as `4204305014989219790323596301191013`. **Port of departure 2026-08-09 09:05** |
| **3722796-7493495579** | Adafruit | 2026-08-06 | **$50.11** | **Delivered 2026-08-10**, a day early. UPS `1Z71EY050394397600` |
| | | | **$104.48** | |

Both Seeed orders carry AIG insurance covering 100% of item value, **claimable within 7 days of the estimated delivery date** — so check the boxes on arrival rather than when you get round to breadboarding.

## Bought

| Part | Board | SKU | Vendor | Order | Cost | Status |
|---|---|---|---|---|---|---|
| **XIAO ESP32S3 & Wio-SX1262 Kit** for Meshtastic & LoRa — **antennas included** | **A** | **102010611** | Seeed | 4000564803 | **$10.90** | **Shipped 2026-08-07.** Left port 2026-08-09 |
| **XIAO ESP32-S3 Sense** — OV2640 + microSD | **B** | **113991115** | Seeed | 4000564800 | **$13.99** | **In hand 2026-08-11** |
| **L76K GNSS Module for XIAO** — active antenna included | **A** | **109100021** | Seeed | 4000564800 | **$11.99** | **In hand 2026-08-11** |
| **LSM6DSO32** 6-DoF, ±32 g | **B** | **4692** | Adafruit | 3722796 | **$12.50** | **In hand 2026-08-10** |
| **Piezo buzzer** PS1240, passive | **B** | **160** | Adafruit | 3722796 | **$1.50** | **In hand 2026-08-10** |
| **LiPo 3.7 V 500 mAh** | shared | **1578** | Adafruit | 3722796 | **$7.95** | **In hand 2026-08-10** |
| **BMP388** barometer, STEMMA QT clone | **B** | — | [DIYmall B0GSYYT1K5](https://www.amazon.com/dp/B0GSYYT1K5) | — | ~$6–12 est. | **In hand.** Measured 2026-08-08 |
| **microSD** | **B** | — | already held | — | — | **In hand** — several. See the note below on why the A1/A2 spec no longer binds |

Freight and tax are not in the rows above: Seeed shipping **$7.82**, Adafruit **UPS Ground $24.77 + $3.39 tax**.

> **The A1/A2 requirement was written for a design that no longer exists.** It came from the era when the 500 Hz sampler wrote to the card *during flight*, where a 100–250 ms stall dropped samples. **PSRAM buffering removed that**: nothing touches the card until after landing. What remains is **sequential video write**, which is a speed-class question (Class 10 / U1 / V10), not the random-IOPS question A1/A2 answers. **Any reasonable card is very likely fine** — check the class marking rather than buying.
>
> **Shipping cost more than the parts.** $24.77 of freight against $21.95 of Adafruit goods. The project's ~$136 budget assumed nothing for it. Consolidate future orders.

**Every part is now on a receipt.** Nothing on this page is inferred.

> **Seeed order 4000564800 was a blind spot for two days.** Seeed never sent an invoice email for it — and that is the only mail carrying line items, so the order-received, tracking and insurance mails all showed a $35.65 charge against nothing. **The line items came off the account page, not the mail.** If a Seeed order ever looks contents-free again, go straight to "My Orders" rather than searching the inbox harder.

Its two items are the **Sense ($13.99)** and the **L76K ($11.99)** — $25.98 of goods against a $35.65 charge, so **$9.67 of shipping and insurance**.

**It landed well before the other Seeed box, as predicted.** 4000564800 went USPS out of a **US warehouse** and arrived **2026-08-11**; 4000564803 is YanWen out of China, left port 2026-08-09, 7–15 working days quoted — so **board A's radio is the last thing outstanding**.

## Still to buy

| Part | Board | Est. | Note |
|---|---|---|---|
| **Carrier PCB** — 3 copies, 4-layer, OSH Park | both | **~$33** | **Blocked.** Do not order before breadboarding — see below |
| **Reed switch** | shared | ~$2 | Arming, in the battery line. **Do not order yet** — normally-open vs normally-closed is undecided, and NC is the one this needs. See [design.md § Arming](design.md#arming--the-reed-switch-and-two-things-not-yet-decided) |
| **MOSFET**, low-Vgs logic-level | shared | ~$1 | **Only if** the reed switches a gate rather than the load — the likely answer, and it adds a carrier footprint |
| 2× 2×7 stacking headers, ~14 mm | both | — | Believed already held. Verify before the flight build |
| Solder, flux, PET window, zip ties, standoffs | — | ~$15 | Consumables |

## What is actually blocking

**Everything except board A's radio is on the bench.** The only outstanding parcel is Seeed **4000564803** — YanWen from China, out of port 2026-08-09, 7–15 working days quoted, so roughly **2026-08-17 to 08-26**.

### What can be done now, without waiting

1. **Weigh the four new parts.** The Sense, L76K, LSM6DSO32 and cell are all estimates in [BOM.md](BOM.md), and together they are most of the **51.4 g** nose-mass figure the rocket's ballast decision rests on. The one estimate already replaced by a scale — the BMP388 — came in **80% over**. **This is the highest-value half hour available**, and it feeds straight into [js-rocket#9](https://github.com/jwilleke/js-rocket/issues/9)'s ballast numbers.
2. **Breadboard board B in full.** Sense, BMP388, LSM6DSO32, buzzer and cell are all here. Qwiic cables ship with both sensors, so the I2C bus needs no soldering. Confirm the camera, the microSD slot and both sensors enumerate, and that the strapping pins (GPIO3, 43, 44) behave.
3. **Measure and photograph every header** before drawing a footprint — see [module-pinouts.md](module-pinouts.md). Only the BMP388 has been through this. **A wrong pin order scraps a board rather than costing a re-solder.**
4. **Check the L76K's own geometry.** It is documented as plugging onto the XIAO's 14 pads rather than presenting a header to the carrier, which is why no GPS footprint is planned. That claim can be checked against the part now, even without the radio.

### What still waits on the China parcel

1. **The L76K against the Wio-SX1262 on the B2B.** **This is the one measurement the layout waits on.** If the two will not share the XIAO stack, the GPS returns to the carrier as a footprint and the top face needs ~21 mm back.
2. **Board A bring-up** — it should enumerate as a Meshtastic device untouched, with no firmware written.
3. **Then** place, route, and order copper.

**The copper order is gated on the slow parcel, not the fast one** — but the four steps above it are no longer gated on anything.

**A layout error costs ~$33 and two weeks. A wiring error costs minutes.** That is the whole reason for this sequence.

**Board B's firmware does not exist yet** and is not on any critical path above — but it is what turns a breadboard into a flight recorder, and nothing has been written.
