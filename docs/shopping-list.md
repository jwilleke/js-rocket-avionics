# Shopping list — avionics purchases

__What to buy and what it cost. Nothing else.__

__Part numbers and weights are in [BOM.md](BOM.md), which is the single source of truth for both.__ Do not restate either here — a number in two places is a number that will disagree with itself. What each part *is* and why it was chosen is there too.

__Costs on this page are from order confirmations, not estimates__ — except where a row says otherwise. Status is as of __2026-08-14__. __Every ordered part is now in hand.__

## Orders placed

| Order | Vendor | Date | Total | Status |
|---|---|---|---|---|
| __4000564800__ | Seeed | 2026-08-07 | __$35.65__ | __Delivered 2026-08-11.__ USPS `420430509261290198196828213362`, US warehouse |
| __4000564803__ | Seeed | 2026-08-07 | __$18.72__ | __Delivered 2026-08-13__, four days ahead of the earliest estimate. YanWen `UL400424782YP`, handed to USPS as `4204305014989219790323596301191013`. Left port 2026-08-09 09:05 |
| __3722796-7493495579__ | Adafruit | 2026-08-06 | __$50.11__ | __Delivered 2026-08-10__, a day early. UPS `1Z71EY050394397600` |
| | | | __$104.48__ | |

Both Seeed orders carry AIG insurance covering 100% of item value, __claimable within 7 days of the estimated delivery date__ — so check the boxes on arrival rather than when you get round to breadboarding.

## Bought

__Part numbers are in [BOM.md](BOM.md)__ — order from there, not from this page.

| Part | Vendor | Order | Cost | Status |
|---|---|---|---|---|
| __XIAO ESP32S3 & Wio-SX1262 Kit__ for Meshtastic & LoRa — __antennas included__ | Seeed | 4000564803 | __$10.90__ | __In hand 2026-08-13__ |
| __XIAO ESP32-S3 Sense__ — camera + microSD. __Listed as OV2640; the board that arrived carries an OV3660__ (2026-09-06) | Seeed | 4000564800 | __$13.99__ | __In hand 2026-08-11__ |
| __L76K GNSS Module for XIAO__ — active antenna included | Seeed | 4000564800 | __$11.99__ | __In hand 2026-08-11__ |
| __LSM6DSO32__ 6-DoF, ±32 g | Adafruit | 3722796 | __$12.50__ | __In hand 2026-08-10__ |
| __Piezo buzzer__ PS1240, passive | Adafruit | 3722796 | __$1.50__ | __In hand 2026-08-10__ |
| __LiPo 3.7 V 500 mAh__ | Adafruit | 3722796 | __$7.95__ | __In hand 2026-08-10__ |
| __BMP388__ barometer, STEMMA QT clone | [DIYmall](https://www.amazon.com/dp/B0GSYYT1K5) | — | ~$6–12 est. | __In hand.__ Measured 2026-08-08 |
| __microSD__ | already held | — | — | __In hand__ — several. See the note below on why the A1/A2 spec no longer binds |
| __Ground receiver__ — XIAO ESP32S3 & Wio-SX1262 Meshtastic node, cased, 2 dBi SMA antenna. Ground equipment, [#23](https://github.com/jwilleke/js-rocket-avionics/issues/23) | [Amazon](https://www.amazon.com/dp/B0GY4QC6GN) | — | — | __In hand 2026-09-13__ — arrived running LoRaHUB, reflashed to Meshtastic ([#23](https://github.com/jwilleke/js-rocket-avionics/issues/23)) |

Freight and tax are not in the rows above: Seeed shipping __$7.82**, Adafruit **UPS Ground $24.77 + $3.39 tax__.

> __The A1/A2 requirement was written for a design that no longer exists.__ It came from the era when the 500 Hz sampler wrote to the card *during flight*, where a 100–250 ms stall dropped samples. __PSRAM buffering removed that__: nothing touches the card until after landing. What remains is __sequential video write__, which is a speed-class question (Class 10 / U1 / V10), not the random-IOPS question A1/A2 answers. __Any reasonable card is very likely fine__ — check the class marking rather than buying.
>
> __Shipping cost more than the parts.__ $24.77 of freight against $21.95 of Adafruit goods. The project's ~$136 budget assumed nothing for it. Consolidate future orders.

__Every part is now on a receipt.__ Nothing on this page is inferred.

> __Seeed order 4000564800 was a blind spot for two days.__ Seeed never sent an invoice email for it — and that is the only mail carrying line items, so the order-received, tracking and insurance mails all showed a $35.65 charge against nothing. __The line items came off the account page, not the mail.__ If a Seeed order ever looks contents-free again, go straight to "My Orders" rather than searching the inbox harder.

Its two items are the __Sense ($13.99)** and the **L76K ($11.99)__ — $25.98 of goods against a $35.65 charge, so __$9.67 of shipping and insurance__.

__It landed well before the other Seeed box, as predicted.__ 4000564800 went USPS out of a __US warehouse__ and arrived __2026-08-11__; 4000564803 is YanWen out of China, left port 2026-08-09, 7–15 working days quoted at __2026-08-17 to 08-26__ — and it arrived __2026-08-13__, four days inside the earliest date. __Nothing ordered is outstanding.__

__Claim the AIG insurance window on both Seeed boxes now if at all__ — 7 days from the *estimated* delivery date, and 4000564803's estimate has not even started yet. Check the kit's contents against the listing (board, Wio-SX1262, both antennas) before that window is a question.

## Still to buy

| Part | Est. | Note |
|---|---|---|
| __Carrier PCB__ — 3 copies, 4-layer, OSH Park, 24 × 115.7 mm | __~$40__ | __Blocked.__ Do not order before breadboarding — see below |
| __Pull-pin + subminiature microswitch__ | ~$5 | Arming, in the battery line. __Superseded the reed switch 2026-08-15__ — smallest hole, snap action, no printed mechanism. __Do not order yet__: no part chosen, and the sled can rotate, so where the pin enters is unresolved. See [the arming brainstorm](resources/2026-08-15-arming-and-access-brainstorm.md) and avionics #1/#2 |
| __MOSFET__, low-Vgs logic-level | ~$1 | __Only if__ the switch drives a gate rather than the load. Still open — a 3.5 mm jack's normalled contact is signal-rated even though its tip and sleeve are not. Adds a carrier footprint |
| M3 plastic machine screws, __M3 × 10__, ×2; Würth WA-SMSI M3 10 mm SMT standoffs (9774100360), ×2 | — | The carrier hangs off the web on the standoffs; screws from the web side. Longer than 10 mm pokes through the board's tall side ([PCB-carrier.md](../hardware/PCB-carrier/PCB-carrier.md)). The old "2×7 stacking headers, ~14 mm" line is gone: the kit's standard 7-pin headers are the flight part |
| Solder, flux, PET window, zip ties, standoffs | ~$15 | Consumables |

## The charging bench (#30) — ordered

__Ordered 2026-09-13 (operator).__ The MCP73831 is the last to land — its listing showed Sep 28–Oct 13 — and it is what the bench waits on.

__For [charging-bench.md](bench-work/charging-bench.md)__ — the carrier's charging circuit on a breadboard before it goes into copper ([#30](https://github.com/jwilleke/js-rocket-avionics/issues/30)). Part numbers are in [BOM.md](BOM.md); why each was chosen, in [PCB-carrier-design.md](../hardware/PCB-carrier/PCB-carrier-design.md#charging-on-the-carrier--q1-the-charge-isolation-fet-and-a-charger-chip--decided-not-yet-in-the-generator). __Prices, shipping and dates as the listings showed them on 2026-09-13, logged out__ — not receipts. __Read the shipping line on every listing before it goes in the cart__: the first pick for the chip, a $0.49 single, carried __$8.95 shipping each__ — $26.85 of freight on $1.47 of chips, and $26.85 of the $28.34 shipping charged at checkout; the other $1.49 was the 2.7 kΩ (operator, 2026-09-13).

| Part | Listing | Price | Shipping, date | Note |
|---|---|---|---|---|
| __AO3401A__ P-channel FET, SOT-23 — Q1 and Q2 | [100-pack](https://www.amazon.com/dp/B08RHFLH1K) | $6.95 | ships from Amazon, Sep 20–22 | Enough for the bench and every carrier |
| __MCP73831T-2ACI/OT__ charger, SOT-23-5 — U1 | [20-pack](https://www.amazon.com/dp/B0H332MZV5) | $7.50 | $1, Sep 28–Oct 13 | No Prime listing found. A marketplace chip can be a relabel — the bench's charge-current reading is the check |
| __SOT-23 to DIP adapters__, 6-pad | [20-pack](https://www.amazon.com/dp/B088M72B54) | $7.79 | free, Sep 23–28 | Fits SOT-23 and SOT-23-5. Header pins are not listed as included — any 2.54 mm male strip |
| __2.7 kΩ__, ¼ W, 1% | [100-pack](https://www.amazon.com/dp/B07DHH1DHF) | $9.09 | $1.49 | Sets U1's current, 370 mA |
| __100 kΩ__, ¼ W, 1% | [100-pack](https://www.amazon.com/dp/B07DHGY3VG) | $9.09 | $1.49 | The FETs' gate pull-down. __The bench does without it__: XIAO-ESP32S3-cam's own R9, 100 kΩ, already holds the gate low. The carrier gets one as a second |
| __4.7 µF__ ceramic, 50 V, 5.08 mm leads | [100-pack](https://www.amazon.com/dp/B0CN68WGZ6) | $9.24 | $1, Sep 22–Oct 1 | U1's two capacitors. __Skip if you have two__ of 4.7–10 µF |
| __JST-PH 2-pin pigtails__, male and female | [CHANZON, 30 pairs, 10 cm, 22 AWG](https://www.amazon.com/dp/B0B2DC8ST8) | — | __in hand__ (operator, 2026-09-13) | Battery and both XIAO pigtails onto the breadboard — the join harness has no place for the FETs. __Meter every one: [JST polarity is not fixed](../hardware/LiPo-500mAh/LiPo-500mAh.md#on-the-bench--the-join-harness)__ — the listing itself says not to trust the wire colour |

__All of it: $49.66 + $4.98 shipping. Without the 100 kΩ and the capacitors: $31.33 + $2.49.__ The carrier needs the same FETs and chip, from these packs, and its own small surface-mount resistors and capacitors; those go with the carrier order.

## What is actually blocking

__Nothing is on a truck any more.__ Every ordered part is on the bench as of __2026-08-13__. __Shipping has stopped being the blocker; bench work is.__ The copper order is now gated on the breadboard and on one caliper reading, both of which are available today.

### What can be done now, without waiting

1. __Breadboard XIAO-ESP32S3-cam in full.__ Sense, BMP388, LSM6DSO32, buzzer and battery are all here. Qwiic cables ship with both sensors, so the I2C bus needs no soldering. Confirm the camera, the microSD slot and both sensors enumerate, and that the strapping pins (GPIO3, 43, 44) behave.
2. __Measure and photograph every header__ before drawing a footprint — see [module-pinouts.md](module-pinouts.md). Only the BMP388 has been through this. __A wrong pin order scraps a board rather than costing a re-solder.__
3. __Measure and photograph the L76K's header.__ It mounts flat on the carrier as of 2026-09-09, so it takes a footprint like any other module and __its pin order has never been read__ — it did not need one while it rode the XIAO's pads. Grid photograph, outline and row order, same as the sensors.

### What the radio's arrival unblocks

1. __The L76K's own outline and pin order.__ The stack-clearance question this line used to carry is closed — the GPS goes flat on the carrier, so nothing has to share the XIAO stack. What the layout waits on now is the __footprint__: ~21 mm on a top face with 74 mm free, and a pin row nobody has read off the part.
2. __Board A bring-up__ — it should enumerate as a Meshtastic device untouched, with no firmware written.
3. __Then__ place, route, and order copper.

__Nothing above is gated on a parcel any more.__ The whole sequence is bench time.

__A layout error costs ~$33 and two weeks. A wiring error costs minutes.__ That is the whole reason for this sequence.

__Board B's firmware does not exist yet__ and is not on any critical path above — but it is what turns a breadboard into a flight recorder, and nothing has been written.
