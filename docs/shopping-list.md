# Shopping list — avionics purchases

The receipts. What each part **is** and why it was chosen is in [BOM.md](BOM.md); this page is only what was bought, what it cost and where it is.

**Costs on this page are from order confirmations, not estimates** — except where a row says otherwise. Status is as of **2026-08-09**.

## Orders placed

| Order | Vendor | Date | Total | Status |
|---|---|---|---|---|
| **4000564800** | Seeed | 2026-08-07 | **$35.65** | **Shipped 2026-08-07 from the US warehouse.** USPS `420430509261290198196828213362`, departed the DHL eCommerce facility 00:55 |
| **4000564803** | Seeed | 2026-08-07 | **$18.72** | **Shipped 2026-08-07 from the China warehouse.** YanWen `UL400424782YP`, handed to USPS as `4204305014989219790323596301191013`. **Port of departure 2026-08-09 09:05** |
| **3722796-7493495579** | Adafruit | 2026-08-06 | **$50.11** | In transit. UPS `1Z71EY050394397600`, **ETA 2026-08-11** |
| | | | **$104.48** | |

Both Seeed orders carry AIG insurance covering 100% of item value, **claimable within 7 days of the estimated delivery date** — so check the boxes on arrival rather than when you get round to breadboarding.

## Bought

| Part | Board | SKU | Vendor | Order | Cost | Status |
|---|---|---|---|---|---|---|
| **XIAO ESP32S3 & Wio-SX1262 Kit** for Meshtastic & LoRa — **antennas included** | **A** | **102010611** | Seeed | 4000564803 | **$10.90** | **Shipped 2026-08-07.** Left port 2026-08-09 |
| **XIAO ESP32-S3 Sense** — OV2640 + microSD | **B** | **113991115** | Seeed | 4000564800 | **$13.99** | **Shipped 2026-08-07** |
| **L76K GNSS Module for XIAO** — active antenna included | **A** | **109100021** | Seeed | 4000564800 | **$11.99** | **Shipped 2026-08-07** |
| **LSM6DSO32** 6-DoF, ±32 g | **B** | **4692** | Adafruit | 3722796 | **$12.50** | **ETA 2026-08-11** |
| **Piezo buzzer** PS1240, passive | **B** | **160** | Adafruit | 3722796 | **$1.50** | **ETA 2026-08-11** |
| **LiPo 3.7 V 500 mAh** | shared | **1578** | Adafruit | 3722796 | **$7.95** | **ETA 2026-08-11** |
| **BMP388** barometer, STEMMA QT clone | **B** | — | [DIYmall B0GSYYT1K5](https://www.amazon.com/dp/B0GSYYT1K5) | — | ~$6–12 est. | **In hand.** Measured 2026-08-08 |

Freight and tax are not in the rows above: Seeed shipping **$7.82**, Adafruit **UPS Ground $24.77 + $3.39 tax**.

> **Shipping cost more than the parts.** $24.77 of freight against $21.95 of Adafruit goods. The project's ~$136 budget assumed nothing for it. Consolidate future orders.

**Every part is now on a receipt.** Nothing on this page is inferred.

> **Seeed order 4000564800 was a blind spot for two days.** Seeed never sent an invoice email for it — and that is the only mail carrying line items, so the order-received, tracking and insurance mails all showed a $35.65 charge against nothing. **The line items came off the account page, not the mail.** If a Seeed order ever looks contents-free again, go straight to "My Orders" rather than searching the inbox harder.

Its two items are the **Sense ($13.99)** and the **L76K ($11.99)** — $25.98 of goods against a $35.65 charge, so **$9.67 of shipping and insurance**.

**It will land well before the other Seeed box.** 4000564800 went out of a **US warehouse** on USPS and cleared the DHL eCommerce facility on 2026-08-07; 4000564803 is YanWen out of China and only **left port on 2026-08-09**, with 7–15 working days quoted. So **board B's MCU and the GPS arrive first, and board A's radio last**.

## Still to buy

| Part | Board | Est. | Note |
|---|---|---|---|
| **Carrier PCB** — 3 copies, 4-layer, OSH Park | both | **~$33** | **Blocked.** Do not order before breadboarding — see below |
| **microSD**, A1/A2 or industrial pSLC, 32 GB | B | ~$10 | Cheap cards stall 100–250 ms on a write |
| **Reed switch** | shared | ~$2 | Arming, in the battery line |
| 2× 2×7 stacking headers, ~14 mm | both | — | Believed already held. Verify before the flight build |
| Solder, flux, PET window, zip ties, standoffs | — | ~$15 | Consumables |

## What is actually blocking

**Ordering copper is blocked on breadboarding, and breadboarding is blocked on parts arriving.**

1. **Any day now** — Seeed **4000564800**: the **XIAO ESP32-S3 Sense** and the **L76K GNSS**. Board B's MCU and the GPS, USPS out of the US warehouse since 2026-08-07.
2. **2026-08-11** — the Adafruit box lands. That brings the **LSM6DSO32**, whose header pin order is the last unknown blocking sensor footprints. With the BMP388 already here, both I2C sensors can go on the bench the same day. Qwiic cables ship with both, so **no soldering is needed to breadboard them**.
3. **~2026-08-17 to 08-26** — Seeed **4000564803**, YanWen from China, only out of port on 2026-08-09. That brings **board A**, which needs **no firmware at all** — it should enumerate as a Meshtastic device untouched.
4. **Then** measure the L76K against the Wio-SX1262 on the B2B. **This is the one measurement the layout waits on**, and it needs both boxes: the L76K arrives in step 1, the radio not until step 3. If the two will not share the XIAO stack, the GPS returns to the carrier as a footprint.
5. **Then** place, route, and order.

**Step 4 is the schedule.** Everything else can be bench-tested as it arrives, but the stack-collision question needs the last box off the slowest shipment — so the copper order is gated on the **China** parcel, not the fast one.

**A layout error costs ~$33 and two weeks. A wiring error costs minutes.** That is the whole reason for this order.

**Board B's firmware does not exist yet** and is not on any critical path above — but it is what turns a breadboard into a flight recorder, and nothing has been written.
