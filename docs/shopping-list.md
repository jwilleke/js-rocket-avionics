# Shopping list — avionics purchases

The receipts. What each part **is** and why it was chosen is in [BOM.md](BOM.md); this page is only what was bought, what it cost and where it is.

**Costs on this page are from order confirmations, not estimates** — except where a row says otherwise. Status is as of **2026-08-09**.

## Orders placed

| Order | Vendor | Date | Total | Status |
|---|---|---|---|---|
| **4000564803** | Seeed | 2026-08-07 | **$18.72** | **Shipped 2026-08-07.** AIG insurance active. China warehouse, 7–15 working days |
| **4000564800** | Seeed | 2026-08-07 | **$35.65** | **Contents unconfirmed** — see below |
| **3722796-7493495579** | Adafruit | 2026-08-06 | **$50.11** | In transit. UPS `1Z71EY050394397600`, **ETA 2026-08-11** |
| | | | **$104.48** | |

## Bought

| Part | Board | SKU | Vendor | Order | Cost | Status |
|---|---|---|---|---|---|---|
| **XIAO ESP32S3 & Wio-SX1262 Kit** for Meshtastic & LoRa — **antennas included** | **A** | **102010611** | Seeed | 4000564803 | **$10.90** | **Shipped 2026-08-07** |
| **LSM6DSO32** 6-DoF, ±32 g | **B** | **4692** | Adafruit | 3722796 | **$12.50** | **ETA 2026-08-11** |
| **Piezo buzzer** PS1240, passive | **B** | **160** | Adafruit | 3722796 | **$1.50** | **ETA 2026-08-11** |
| **LiPo 3.7 V 500 mAh** | shared | **1578** | Adafruit | 3722796 | **$7.95** | **ETA 2026-08-11** |
| **BMP388** barometer, STEMMA QT clone | **B** | — | unrecorded | — | ~$6–12 est. | **In hand.** Measured 2026-08-08 |

Freight and tax are not in the rows above: Seeed shipping **$7.82**, Adafruit **UPS Ground $24.77 + $3.39 tax**.

> **Shipping cost more than the parts.** $24.77 of freight against $21.95 of Adafruit goods. The project's ~$136 budget assumed nothing for it. Consolidate future orders.

## Unconfirmed

**Seeed order 4000564800, $35.65.** Placed one minute before 4000564803 and charged to the card, but **Seeed sent no invoice email for it and no shipping notice** — only the contents-free "order received" template. So there is no evidence of what is in it.

The two parts the BOM still needs from Seeed are the **XIAO ESP32S3 Sense (113991115)** and the **L76K GNSS for XIAO (109100021)**, and their list prices plus shipping land near $35.65. **That is arithmetic, not a receipt.** Check "My Orders" on seeedstudio.com and replace this section with the real line items.

Until then, **board B has no MCU on record.**

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

1. **2026-08-11** — the Adafruit box lands. That brings the **LSM6DSO32**, whose header pin order is the last unknown blocking sensor footprints. With the BMP388 already here, both I2C sensors can go on the bench the same day. Qwiic cables ship with both, so **no soldering is needed to breadboard them**.
2. **~2026-08-17 to 08-26** — the Seeed shipment, 7–15 working days from 2026-08-07. That brings **board A**, which needs **no firmware at all** — it should enumerate as a Meshtastic device untouched.
3. **Then** measure the L76K against the Wio-SX1262 on the B2B. If it will not ride the XIAO stack, it returns to the carrier as a footprint.
4. **Then** place, route, and order.

**A layout error costs ~$33 and two weeks. A wiring error costs minutes.** That is the whole reason for this order.

**Board B's firmware does not exist yet** and is not on any critical path above — but it is what turns a breadboard into a flight recorder, and nothing has been written.
