# js-rocket-avionics

Carrier PCB and flight firmware for the [js-rocket](https://github.com/jwilleke/js-rocket) electronics sled.

__This is one candidate payload for the rocket, not *the* payload.__ The rocket flies on ballast alone. The interface it has to satisfy — 40.0 mm bore × 150 mm, an M3 × 55 retainer at nose z 15, a ~50 g mass ceiling, an optional camera port — is [`js-rocket/docs/payload-bay.md`](https://github.com/jwilleke/js-rocket/blob/main/docs/payload-bay.md), and that is the only page in that repo this project depends on.

Separate from the rocket repo on purpose: `js-rocket` is geometry and documentation with no code, no package manager and no dependencies, and its `CLAUDE.md` says so explicitly. Copper, firmware and __the design record — every decision and why, in [docs/design.md](docs/design.md)__ — live here instead.

__Why it is built this way is in [docs/design.md](docs/design.md).__ __Every part this project needs is in [docs/BOM.md](docs/BOM.md), which is the single source of truth for part numbers and weights__ — plus what each part is, which board it serves, and what was rejected. __What was actually bought is in [docs/shopping-list.md](docs/shopping-list.md)__ — orders, costs, arrival status. The printed sled that carries these boards, and the [PayloadAdapter](https://github.com/jwilleke/js-rocket/blob/main/docs/3d-printed-parts/payload-adapter.md) it loads through, are rocket parts and stay in [js-rocket](https://github.com/jwilleke/js-rocket).

__Status: one two-sided board ([PCB-carrier-design.md](hardware/PCB-carrier/PCB-carrier-design.md)). Every footprint placed and netted, DRC 0 violations.__ The 10 unconnected items DRC reports are the signal nets, which are not routed yet (stage 2d, [#15](https://github.com/jwilleke/js-rocket-avionics/issues/15)). What the board is, both sides with a drawing, is [hardware/PCB-carrier/PCB-carrier.md](hardware/PCB-carrier/PCB-carrier.md).

> __Do not order it.__ It quotes cleanly, which is a toolchain check and nothing more. It is unrouted, and three checks are still owed (PCB-carrier-design.md, *Checks owed before building*).

## The interface to the sled

__One board on the PayloadSled's centre line__, hanging off the web on two standoffs: the tall side (both XIAO stacks) faces 270°, the camera port; the low side (sensors, standoffs) faces 90°, the web. The sled side is [js-rocket#99](https://github.com/jwilleke/js-rocket/issues/99), which moves the web toward 90° and drills it at the standoffs. __Change these and the sled changes.__

| | Value |
|---|---|
| Board | __24.0 × 90.4 mm__, aft end at nose z 25.4 |
| Thickness | __1.0 mm__, 4 copper layers |
| Corner radius | 2.0 mm |
| Standoffs | __2 × Würth WA-SMSI M3, 10 mm__ (9774100360), low side, at board (x, y) __(12.0, 18.0)__ and __(16.5, 85.2)__ — nose z 43.4 and 110.6. M3 plastic screws, __M3 × 10__, from the web's far face |
| XIAO-ESP32S3-cam centre | board y __18.0__ (nose z 43.4), under the camera pad |
| XIAO-ESP32S3-lora centre | board y __68.0__ (nose z 93.4) |

Board x runs across the board, y from the aft end, forward positive, in KiCad's top view (the tall side). Everything above is read out of the generated board by `gen_carrier.py`; the gerbers in `fab/` predate it ([#16](https://github.com/jwilleke/js-rocket-avionics/issues/16)).

__Why 24 mm wide.__ It matches the web. The sensors, 17.8 mm across when lengthwise, sit inside it.

__Why 90.4 mm long.__ The camera fixes the cam XIAO at the aft end, and the tall side then carries the L76K-GNSS, the lora XIAO and the JST end to end; the low side's sensors sit behind them. The battery, forward of the board, keeps its position with ~9 mm to spare.

__Why 1.0 mm.__ The board hangs off the web on two standoffs 67 mm apart; 1.0 mm FR4 is stiff enough over that span with the modules on it.

## The XIAO stack

__The expansion board — Sense or Wio-SX1262 — sits above the XIAO__, on the B2B connector on its front face. The XIAO stands on __two standard 7-pin headers__, ~2.50 mm, onto the board. No cutout and no tall stacking headers are needed. Stack heights and the fit across the bore are in [docs/design.md](docs/design.md#headers-and-the-expansion-board-on-top).

## Connections

There is __no schematic file__. Nets are assigned to pads directly in the generator, which is more robust than hand-authoring schematic s-expressions for 9 nets and keeps one generator as the single source of truth. The cost is no ERC and no drawn diagram — so this table *is* the wiring diagram. __Keep it in step with `gen_carrier.py`.__

| Net | From | Also reaches |
|---|---|---|
| `GND` | both XIAOs, pin 13 | In1 plane, every module, JST −, the `GND` wire pads |
| `+3V3` | XIAO-ESP32S3-cam pin 12 __only__ | In2 plane; LSM6DSO32 `VIN`; BMP388 `VIN` __and `CS`__ (I2C mode, [#19](https://github.com/jwilleke/js-rocket-avionics/issues/19)) |
| `+3V3_LORA` | XIAO-ESP32S3-lora pin 12 | the L76K-GNSS's `3V3` only — __kept off the plane__, so the two regulators are never paralleled |
| `SDA` | cam __D4__ (pin 5, GPIO5) | LSM6DSO32, BMP388 |
| `SCL` | cam __D5__ (pin 6, GPIO6) | LSM6DSO32, BMP388 |
| `BUZZER` | cam __D0__ (pin 1, GPIO1) | the buzzer wire pad; the PS1240 sits against the nose wall |
| `GPS_TX` | lora __D6__ (pin 7, GPIO43) | the L76K-GNSS's pad at the D6 position, which is the module's __RX__ |
| `GPS_RX` | lora __D7__ (pin 8, GPIO44) | the L76K-GNSS's pad at the D7 position, which is the module's __TX__ |
| `VBAT` | JST pin 1 | both XIAOs' BAT pigtail pads |

`GPS_TX` and `GPS_RX` are named from the XIAO's side. __Wire the L76K-GNSS by position, never by its silkscreen word__ — [L76K-GNSS.md](hardware/L76K-GNSS/L76K-GNSS.md#pinout--from-seeeds-schematic-not-the-listing).

### The pin map, and an error worth not repeating

The KiCad footprint numbers its pads 1–14 with no signal names, DIP-style — 1 at top-left, down to 7 at bottom-left, 8 at bottom-right, up to 14 at top-right. Seeed's pinout gives the meaning:

```text
pin  1  2  3  4  5  6  7   8  9  10  11   12   13   14
sig  D0 D1 D2 D3 D4 D5 D6  D7 D8 D9  D10  3V3  GND  5V
```

An earlier revision of the generator put GPS on pins 6/7 and I2C on 4/5 — which are __D5/D6 and D3/D4, every one off by one__. Caught by reading the mapping back out of the saved board rather than trusting the script's own output. The generator now names pins (`XIAO_PIN["D6"]`) so the numbers never appear by hand.

__Each 1×7 header numbers its own pads 1–7.__ The second row's pad 1 is XIAO pin 8, at the far end, so `xiao_pin = pad + 7` running back toward the USB-C. This file once said `15 − pad`, which is [#18](https://github.com/jwilleke/js-rocket-avionics/issues/18)'s mirrored row, written down as the rule.

## The GPS is an L76K

The MAX-M10S was rejected on 2026-08-06: __44.2 × 30.5 mm — wider than this 24 mm board — and ~$60__. The chosen part is Seeed's __L76K GNSS for XIAO (109100021)__ — 18 × 21 mm, UART on __D6/D7__. It takes its own footprint on the tall side, between the two XIAOs, and its antenna is a separate part on the sled. Pinout, power and orientation: [L76K-GNSS.md](hardware/L76K-GNSS/L76K-GNSS.md).

The same staleness once reached the barometer: __BMP390 → BMP388__, settled on 2026-08-06 when the 390 went out of stock. Same BMP3xx driver, same 25.5 × 17.8 mm STEMMA QT outline, address 0x77, and its pinout __confirmed off the physical part__.

## Battery — read before assembling

__BAT+/BAT− are underside pads on the XIAO__, not brought out to the castellated edge, so the battery cannot reach a XIAO through the headers. The battery lands on the JST at the board's forward end and reaches each XIAO by a short __soldered pigtail__.

- __Solder the pigtails before the XIAO goes onto its headers.__ The board, not the expansion board, is what covers the pads.
- __On battery power there is no voltage on the 5V pin__ — nothing can be fed from a XIAO's 5V rail.
- Both XIAO chargers sit in parallel on one battery. __Charge through one USB port at a time__, and read [why that is not sufficient on its own](hardware/LiPo-500mAh/LiPo-500mAh.md#two-chargers-on-one-battery).
- __Check JST pin 1 against the battery's red lead before soldering.__ The silkscreen marks `+`; reversing a LiPo into a XIAO destroys it.

## No RF on this board

The L76K and the Wio-SX1262 each carry their own U.FL connector, and both antennas mount on the sled, so __no RF ever crosses the carrier__. It is a purely digital and power board of 9 nets, which is what makes it tractable to generate and verify headlessly.

## Building

Requires KiCad 10. The generator uses KiCad's bundled Python so `pcbnew` matches the CLI exactly.

```bash
KPY=/Applications/KiCad/KiCad.app/Contents/Frameworks/Python.framework/Versions/3.9/bin/python3
CLI=/Applications/KiCad/KiCad.app/Contents/MacOS/kicad-cli

$KPY hardware/scripts/gen_carrier.py
$CLI pcb drc  --format json -o /tmp/drc.json hardware/PCB-carrier/PCB-carrier.kicad_pcb
$CLI pcb export gerbers -o fab/gerbers/ hardware/PCB-carrier/PCB-carrier.kicad_pcb
$CLI pcb export drill   -o fab/gerbers/ hardware/PCB-carrier/PCB-carrier.kicad_pcb
```

__The board is generated, not hand-edited.__ `.kicad_pcb` format shifts between KiCad releases; building it through `pcbnew` means the file is written by the same code that reads it. Edit `hardware/scripts/gen_carrier.py` and re-run — do not edit the board file directly, or the next run overwrites you.

`gen_outline.py` is the superseded 2a-only version, kept for reference.

DRC must report __0 violations__ before anything is ordered.

## Remaining stages

| Stage | State |
|---|---|
| 2a — outline, standoffs, stackup | __done__, one two-sided board |
| 2b — nets + footprints | __done__ — every footprint placed and netted |
| 2b — GND/+3V3 planes | __done__, In1 and In2 filled |
| 2c — placement | __done in the generator__, pending review of the drawing — [#14](https://github.com/jwilleke/js-rocket-avionics/issues/14) |
| 2d — signal routing | not started — [#15](https://github.com/jwilleke/js-rocket-avionics/issues/15) |
| 2e — Gerber + drill for fab | chain proven; needs a finished board |

__Do not order copper before breadboarding.__ A layout error costs ~$32 and two weeks; a wiring error costs minutes.

Fab target is __OSH Park__. The 24 × 70 mm version quoted **$26.00 for 3 copies** — $9.32/in² — so 24 × 90.4 mm (3.36 in²) should land near __$32__. Re-upload to confirm; three copies — one to fly, two spares.

__OSH Park accepts the `.kicad_pcb` directly__ — confirmed by upload, not assumed. It read the layer count and outline unaided, so `fab/gerbers/` is not in the ordering path and exists only as a check that the export chain works.
