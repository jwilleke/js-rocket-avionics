# Shopping list — avionics purchases

**What to buy and what it cost. Nothing else.**

**Part numbers and weights are in [BOM.md](BOM.md), which is the single source of truth for both.** Do not restate either here — a number in two places is a number that will disagree with itself. What each part _is_ and why it was chosen is there too.

**Costs on this page are from order confirmations, not estimates** — except where a row says otherwise. Status is as of **2026-08-14**. **Every ordered part is now in hand.**

## Orders placed

| Order | Vendor | Date | Total | Status |
|---|---|---|---|---|
| **4000564800** | Seeed | 2026-08-07 | **$35.65** | **Delivered 2026-08-11.** USPS `420430509261290198196828213362`, US warehouse |
| **4000564803** | Seeed | 2026-08-07 | **$18.72** | **Delivered 2026-08-13**, four days ahead of the earliest estimate. YanWen `UL400424782YP`, handed to USPS as `4204305014989219790323596301191013`. Left port 2026-08-09 09:05 |
| **3722796-7493495579** | Adafruit | 2026-08-06 | **$50.11** | **Delivered 2026-08-10**, a day early. UPS `1Z71EY050394397600` |
| | | | **$104.48** | |

Both Seeed orders carry AIG insurance covering 100% of item value, **claimable within 7 days of the estimated delivery date** — so check the boxes on arrival rather than when you get round to breadboarding.

## Bought

**Part numbers are in [BOM.md](BOM.md)** — order from there, not from this page.

| Part | Vendor | Order | Cost | Status |
|---|---|---|---|---|
| **XIAO ESP32S3 & Wio-SX1262 Kit** for Meshtastic & LoRa — **antennas included** | Seeed | 4000564803 | **$10.90** | **In hand 2026-08-13** |
| **XIAO ESP32-S3 Sense** — OV2640 + microSD | Seeed | 4000564800 | **$13.99** | **In hand 2026-08-11** |
| **L76K GNSS Module for XIAO** — active antenna included | Seeed | 4000564800 | **$11.99** | **In hand 2026-08-11** |
| **LSM6DSO32** 6-DoF, ±32 g | Adafruit | 3722796 | **$12.50** | **In hand 2026-08-10** |
| **Piezo buzzer** PS1240, passive | Adafruit | 3722796 | **$1.50** | **In hand 2026-08-10** |
| **LiPo 3.7 V 500 mAh** | Adafruit | 3722796 | **$7.95** | **In hand 2026-08-10** |
| **BMP388** barometer, STEMMA QT clone | [DIYmall](https://www.amazon.com/dp/B0GSYYT1K5) | — | ~$6–12 est. | **In hand.** Measured 2026-08-08 |
| **microSD** | already held | — | — | **In hand** — several. See the note below on why the A1/A2 spec no longer binds |

Freight and tax are not in the rows above: Seeed shipping **$7.82**, Adafruit **UPS Ground $24.77 + $3.39 tax**.

> **The A1/A2 requirement was written for a design that no longer exists.** It came from the era when the 500 Hz sampler wrote to the card _during flight_, where a 100–250 ms stall dropped samples. **PSRAM buffering removed that**: nothing touches the card until after landing. What remains is **sequential video write**, which is a speed-class question (Class 10 / U1 / V10), not the random-IOPS question A1/A2 answers. **Any reasonable card is very likely fine** — check the class marking rather than buying.
>
> **Shipping cost more than the parts.** $24.77 of freight against $21.95 of Adafruit goods. The project's ~$136 budget assumed nothing for it. Consolidate future orders.

**Every part is now on a receipt.** Nothing on this page is inferred.

> **Seeed order 4000564800 was a blind spot for two days.** Seeed never sent an invoice email for it — and that is the only mail carrying line items, so the order-received, tracking and insurance mails all showed a $35.65 charge against nothing. **The line items came off the account page, not the mail.** If a Seeed order ever looks contents-free again, go straight to "My Orders" rather than searching the inbox harder.

Its two items are the **Sense ($13.99)** and the **L76K ($11.99)** — $25.98 of goods against a $35.65 charge, so **$9.67 of shipping and insurance**.

**It landed well before the other Seeed box, as predicted.** 4000564800 went USPS out of a **US warehouse** and arrived **2026-08-11**; 4000564803 is YanWen out of China, left port 2026-08-09, 7–15 working days quoted at **2026-08-17 to 08-26** — and it arrived **2026-08-13**, four days inside the earliest date. **Nothing ordered is outstanding.**

**Claim the AIG insurance window on both Seeed boxes now if at all** — 7 days from the _estimated_ delivery date, and 4000564803's estimate has not even started yet. Check the kit's contents against the listing (board, Wio-SX1262, both antennas) before that window is a question.

## Still to buy

| Part | Est. | Note |
|---|---|---|
| **Carrier PCB** — 3 copies, 4-layer, OSH Park | **~$33** | **Blocked.** Do not order before breadboarding — see below |
| **Pull-pin + subminiature microswitch** | ~$5 | Arming, in the battery line. **Superseded the reed switch 2026-08-15** — smallest hole, snap action, no printed mechanism. **Do not order yet**: no part chosen, and the sled can rotate, so where the pin enters is unresolved. See [the arming brainstorm](resources/2026-08-15-arming-and-access-brainstorm.md) and avionics #1/#2 |
| **MOSFET**, low-Vgs logic-level | ~$1 | **Only if** the switch drives a gate rather than the load. Still open — a 3.5 mm jack's normalled contact is signal-rated even though its tip and sleeve are not. Adds a carrier footprint |
| 2× 2×7 stacking headers, ~14 mm | — | Believed already held. Verify before the flight build |
| Solder, flux, PET window, zip ties, standoffs | ~$15 | Consumables |

## What is actually blocking

**Nothing is on a truck any more.** Every ordered part is on the bench as of **2026-08-13**. **Shipping has stopped being the blocker; bench work is.** The copper order is now gated on the breadboard and on one caliper reading, both of which are available today.

### What can be done now, without waiting

1. **Breadboard board B in full.** Sense, BMP388, LSM6DSO32, buzzer and cell are all here. Qwiic cables ship with both sensors, so the I2C bus needs no soldering. Confirm the camera, the microSD slot and both sensors enumerate, and that the strapping pins (GPIO3, 43, 44) behave.
2. **Measure and photograph every header** before drawing a footprint — see [module-pinouts.md](module-pinouts.md). Only the BMP388 has been through this. **A wrong pin order scraps a board rather than costing a re-solder.**
3. **Check the L76K's own geometry.** It is documented as plugging onto the XIAO's 14 pads rather than presenting a header to the carrier, which is why no GPS footprint is planned. That claim can be checked against the part directly.

### What the radio's arrival unblocks

1. **The L76K against the Wio-SX1262 on the B2B.** **This is the one measurement the layout waits on, and it can be taken now.** If the two will not share the XIAO stack, the GPS returns to the carrier as a footprint and the top face needs ~21 mm back. The 95 mm board has the room either way, so this decides layout, not size.
2. **Board A bring-up** — it should enumerate as a Meshtastic device untouched, with no firmware written.
3. **Then** place, route, and order copper.

**Nothing above is gated on a parcel any more.** The whole sequence is bench time.

**A layout error costs ~$33 and two weeks. A wiring error costs minutes.** That is the whole reason for this sequence.

**Board B's firmware does not exist yet** and is not on any critical path above — but it is what turns a breadboard into a flight recorder, and nothing has been written.
