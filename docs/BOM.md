# Bill of materials

Every part the avionics sled needs, as a standalone list. Nothing here is required to fly the rocket — [js-rocket](https://github.com/jwilleke/js-rocket) flies with ballast alone and the sled is payload.

**Where things live.** The *design record* — every decision and the reasoning behind it — is [`js-rocket/docs/planing/electronics-plan.md`](https://github.com/jwilleke/js-rocket/blob/main/docs/planing/electronics-plan.md). The *printed sled* that carries these boards is a rocket part and stays there too, as is the [PayloadAdapter](https://github.com/jwilleke/js-rocket/blob/main/docs/3d-printed-parts/payload-adapter.md) the sled loads through. The carrier PCB, its Gerbers and the firmware are here.

**The mass budget is the hard constraint.** Target is **~50 g of nose mass** including the printed sled; past ~65 g the rocket goes over-stable and weathercocks. A payload gram displaces only **0.78 g** of ballast, so overruns cost more than they look — see [payload-ballast.md](https://github.com/jwilleke/js-rocket/blob/main/docs/payload-ballast.md).

## Parts

Costs are estimates from the design record, not receipts.

| Item | Spec | Qty | Sourced | Cost | Status |
|---|---|---|---|---|---|
| **BMP388 barometer** | STEMMA QT form factor, 0x77 | 1 | [DIYmall B0GSYYT1K5](https://www.amazon.com/dp/B0GSYYT1K5) | $6–12 | **In hand and measured 2026-08-08** |
| Seeed **102010611** | XIAO ESP32S3 + Wio-SX1262 kit — board A, **pre-flashed Meshtastic**, antennas included | 1 | Seeed | $16 | To buy |
| Seeed **113991115** | XIAO ESP32S3 **Sense** — board B, OV2640 + microSD | 1 | Seeed | $14 | To buy |
| Seeed **109100021** | L76K GNSS for XIAO, active antenna included | 1 | Seeed | $12 | To buy |
| Adafruit **4692** | LSM6DSO32, ±32 g accel + gyro | 1 | Adafruit | $12.50 | To buy — **measure it, do not trust the datasheet dimensions** |
| Adafruit **160** | passive piezo buzzer, PWM-driven | 1 | Adafruit | $1.50 | To buy |
| Adafruit **1578** | LiPo 500 mAh | 1 | Adafruit | $7.95 | To buy |
| **Reed switch** | arming, in the battery line — not on a GPIO | 1 | any | $2 | To buy |
| **microSD** | A2-rated or industrial pSLC, 32 GB | 1 | any | $10 | To buy |
| **Carrier PCB** | 24 × 95 mm, 1.0 mm, 4-layer, 3 copies | 1 | OSH Park | ~$33 (quoted $26) | **Do not order** — footprints and routing incomplete |
| Solder, flux, PET window, zip ties, standoffs | assembly consumables | — | any | $15 | To buy |
| **Total** | | | | **~$136** | Budget **$150–200** |

**Buy the Seeed kit rather than the two parts separately** — it guarantees the matched B2B variant and arrives pre-flashed with Meshtastic, which is the entire premise of board A.

## Mass

From the design record. Masses are estimates unless a row says otherwise.

| Part | Board | Mass (g) |
|---|---|---|
| XIAO ESP32S3 (plain) | A | 3.5 |
| Wio-SX1262 (ESP32S3 / B2B kit version) | A | 4.5 |
| U.FL 82 mm whip antenna | A | 1.0 |
| L76K GNSS for XIAO | A | 5.0 |
| XIAO ESP32S3 Sense | B | 7.5 |
| LSM6DSO32 | B | 1.0 |
| **BMP388 — measured 2026-08-08** | B | **1.8** |
| Passive piezo buzzer | B | 2.0 |
| Carrier PCB | ×1 | 4.3 |
| 2× 2×7 stacking headers | — | 1.0 |
| Reed switch, battery pigtails, wiring | — | 1.5 |
| LiPo 500 mAh | — | 9.0 |
| **Avionics subtotal** | | **42.1** |
| Printed sled — measured | | 9.3 |
| **Nose total** | | **51.4** |

**The first estimate to meet a scale came in 80% heavy** — the BMP388 was budgeted at 1.0 g and weighs 1.8 g. The other eleven rows are still guesses, so treat 51.4 g as optimistic.

## The BMP388, measured off the part

Full BOM, rationale and rejected alternatives in [electronics-plan.md](https://github.com/jwilleke/js-rocket/blob/main/docs/planing/electronics-plan.md). Ordered so far:

- **Barometer** — DIYmall BMP388, STEMMA QT form factor ([shopping list](#parts)). **In hand and measured 2026-08-08.** 25.5 × 17.8 mm, address **0x77** (ADDR jumper for 0x76), two Qwiic cables included at **110 mm** each. Pin order confirmed from the part: **1 VIN, 2 3Vo, 3 GND, 4 SCL, 5 SDO, 6 SDA, 7 CS, 8 INT** — we use 1, 3, 4, 6. Header ships **loose**. Measured: **1.8 g**, **4.79 mm** thick over the Qwiic connectors, mounting holes **Ø2.35 mm at 20.58 mm spacing** on the edge opposite the header. Photos: [front](https://github.com/jwilleke/js-rocket/blob/main/docs/resources/PXL_20260808_193009460.jpg), [back](https://github.com/jwilleke/js-rocket/blob/main/docs/resources/PXL_20260808_192959846.jpg)

Three cautions on that board, each of which has cost someone an evening:

- **Power to VIN, never 3Vo.** `3Vo` is the on-board regulator's *output*; back-feeding it kills the LDO. **The board in hand is marked 3 V, not the `3-5VDC` this page previously claimed** — that figure came from Adafruit's text, which the listing copies. **Treat it as a 3.3 V part** and do not feed it 5 V until the back silkscreen is read cleanly. The design runs it at +3V3 either way, so nothing changes except the assumption that 5 V was available as a fallback
- **The seller's wiring diagram is SPI, not I2C.** It wires SCL/SDO/SDA/CS to Arduino 13/12/11/10 — SCK, MISO, MOSI, SS. On BMP3xx the pins are dual-purpose; this design uses I2C, four wires
- **If it does not enumerate at 0x77, check CS first.** CS low selects SPI; it must be HIGH for I2C. Verify the silicon too — `reg 0x00` returns **0x50 for BMP388**, 0x60 for BMP390, and a BMP280 answers 0x58 at `reg 0xD0`. Clone listings copy Adafruit's text verbatim and the chip does not always match

**Qwiic cables are bench-only.** They make breadboarding solder-free, but JST-SH is friction-fit and will shake loose under boost — the flight build solders to the 0.1 in header holes.

Still to order: the two Seeed XIAO boards, the L76K GNSS, the LSM6DSO32, the LiPo, the buzzer, a microSD and a reed switch.
