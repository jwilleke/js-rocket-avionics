# Carrier PCB

__The only part here that is also structure.__ One board on the sled's centre plane, parts on both faces — and __the sled's structural span__, because the printed web is only 3 mm and is explicitly *not* the structural member.

The frozen interface is in [README.md](../README.md). This page is what the board is and what is still missing from it.

## The shape is forced, not chosen

| | |
|---|---|
| Size | __24 × 95 mm__ |
| Stackup | __4-layer__, solid ground plane |
| Thickness | __1.0 mm FR4__ |
| Nets | ~__9__ — GPS TX, GPS RX, SDA, SCL, buzzer, 3V3, GND, BAT+, BAT− |

## Three voltages, and only one of them is on this board

| Rail | Volts | Where it comes from | On the carrier? |
|---|---|---|---|
| __USB / VBUS__ | __5.0__ | A USB-C lead, only while one is plugged in | __No__ — it exists on each XIAO's `5V` pin (pin 14) and nowhere else. [LiPo-500mAh.md](LiPo-500mAh.md) notes the consequence: *on battery power there is no voltage on the 5V pin* |
| __Cell__ | __3.7 nominal__ | The [LiPo](LiPo-500mAh.md), to a JST, then by soldered pigtail to each XIAO's underside __BAT pads__ | Only as `BAT+` / `BAT−` at the JST. It does __not__ reach the headers |
| __Logic__ | __3.3__ | Each XIAO's own regulator, out of its `3V3` pin (pin 12) | __Yes — this is the board's power net.__ It supplies the sensors and the buzzer |

__So the carrier is a 3.3 V board.__ 5 V appears on it only if something is wired to a XIAO's `5V` pin, and nothing should be: the [LSM6DSO32](LSM6DSO32.md) and [BMP388](BMP388-barometer.md) are 3.3 V parts, and [module-pinouts.md](../docs/module-pinouts.md) records that the BMP388 in hand is __marked 3 V__ with 5 V no longer a documented fallback.

__Charging is 5 V, and it is not this board's business.__ Both XIAOs carry their own charger and sit in parallel on the one battery — charge through one USB port at a time. No charge IC is added here.

## How power actually reaches everything

__Nothing on this board is powered by the battery. Everything is powered by a XIAO.__ The carrier is wiring, not a power supply — it carries no regulator. The 3.3 V travels __out__ of the microcontrollers and __into__ the board, which is backwards from how a carrier usually reads and is why this section exists.

```text
  LiPo 3.7 V
     |
     |  2 wires
     v
  JST-PH on this board ---- BAT+ / BAT-
     |
     +-- soldered pigtail --> XIAO-ESP32S3-cam    underside BAT pads
     +-- soldered pigtail --> XIAO-ESP32S3-lora   underside BAT pads
                                    |
                           each XIAO has its own charger
                           and its own 3.3 V regulator
                                    |
                                    v
                           3V3 pin 12  --+
                           GND pin 13  --+  back OUT through the header
                                          |
                                          v
                              this board's +3V3 and GND planes
                                          |
                              +-----------+-----------+
                              v                       v
                         LSM6DSO32                 BMP388
```

__Why the pigtails exist.__ `BAT+`/`BAT−` are __centre pads on the XIAO's underside__ ([module-pinouts.md](../docs/module-pinouts.md#xiao-esp32s3--read-off-the-underside-2026-09-08)), not on the castellated edge, so the battery cannot reach a XIAO through the header. Two soldered wires are forced, not chosen.

__What the +3V3 plane actually feeds: two parts.__ [LSM6DSO32](LSM6DSO32.md) and [BMP388](BMP388-barometer.md). The [PS1240 buzzer](PS1240-buzzer.md) is not on that list — a passive piezo is driven straight off `D0` and GND and takes no supply rail.

__Everything else is powered by the XIAO it plugs onto__, through that module's B2B connector, and never touches this board:

| Part | Powered by |
|---|---|
| [Wio-SX1262](Wio-SX1262-LoRa.md) | XIAO-ESP32S3-lora |
| [L76K-GNSS](L76K-GNSS.md) | XIAO-ESP32S3-lora, riding the stack |
| [Sense-camera-board](Sense-camera-board.md) | XIAO-ESP32S3-cam |
| Camera module, [microSD](microSD.md) | the Sense board |

### Charge through the Sense stack, and only that one

__Operator, 2026-09-08.__ For charging alone it makes no difference — both XIAOs have a charger and both sit on the same battery. __The decision is about which port is permanently committed__, because [#1](https://github.com/jwilleke/js-rocket-avionics/issues/1)'s service pigtail occupies whichever one it is wired to:

- __[XIAO-ESP32S3-cam](XIAO-ESP32S3-cam.md), the Sense stack__ — the aft module, so the shortest cable run; the only one that reaches the microSD; and the one being reflashed constantly, since its firmware does not exist yet
- __[XIAO-ESP32S3-lora](XIAO-ESP32S3-lora.md)__ — runs __stock Meshtastic and must never be reflashed__. That is the whole reason there are two modules. A service port on it invites exactly what the two-module split exists to prevent

__So XIAO-ESP32S3-lora's USB-C is not used in the flight build.__ It is reachable only by taking the nose apart.

__And still one at a time.__ Two chargers on one battery will argue; nothing enforces this but the build order.

### Two regulators on one net, which nobody chose deliberately

Both XIAOs' `3V3` pins land on the __same +3V3 plane__, so their regulators run __in parallel__. Linear regulators do not share load: whichever holds the marginally higher output supplies everything until it current-limits, and if one module ever loses its pigtail the other back-feeds into its regulator output.

It will very likely be fine at these currents. __It is recorded here because it is a consequence of the layout rather than a decision__, and [#4](https://github.com/jwilleke/js-rocket-avionics/issues/4) is benching the shared battery anyway — it costs nothing to measure both rails in the same sitting. The regulator type is assumed rather than read off Seeed's schematic.

__Why not two smaller boards.__ The twin-PCB plan assumed each XIAO could sit flat on its own card with a cutout clearing the expansion board underneath. The XIAO's own footprint kills it: pads at __±8.5 mm__, expansion board at __±8.75 mm__. __The thing needing clearance is wider than the pads are apart__, so any cutout large enough to pass it removes the copper the pads solder to. No geometry satisfies both.

__Why not 24 × 70.__ The two XIAOs cannot overlap in plan view — they mount on __through-hole__ headers, and XIAO-ESP32S3-lora uses D6/D7 for the GPS UART where XIAO-ESP32S3-cam uses D4/D5 for I2C. Different nets, same holes. So they sit end to end, and at 24 mm wide against 17.8 mm sensors nothing sits side by side:

```text
top face     XIAO-ESP32S3-lora 21, GPS in the stack, not end to end  = 21 mm
bottom face  XIAO-ESP32S3-cam 21 + LSM6DSO32 25.5 + BMP388 25.5 + buzzer = 84 mm
```

__The bottom face sets the length.__ The top-face figure once read 46 mm, from a MAX-M10S that would have sat on the carrier; that part is gone and the L76K rides the XIAO stack instead. 84 mm on the bottom still drives the board, so __nothing about the frozen interface moves and the sled does not reprint__.

## Population

| Face | Carries |
|---|---|
| Top | XIAO ESP32S3 (plain) + Wio-SX1262 on its back face; __L76K in the XIAO stack, not on the carrier__ |
| Bottom | XIAO ESP32S3 Sense + camera/microSD board on its back face; LSM6DSO32; BMP388; buzzer |
| Either | Battery JST, arming switch in the battery line, mounting holes |

__XIAO B centres at carrier y = 18 mm__, which is what puts the camera at nose z 30..45.

## Build rules

- __4-layer, solid ground plane.__ A few dollars more at this size; fixes return paths and coupling from the camera's DVP flex
- __Module footprints, not bare chips.__ A bare LSM6DSO32 is an LGA-14 at 2.5 × 3 mm and is not hand-solderable. Soldering breakouts down still gives one rigid assembly with no flying wires — apart from the two battery pigtails, which are unavoidable
- __Solder or clamp the headers — no loose sockets.__ Battery straps to the sled, never hangs off the JST. Conformal coat after bench testing
- __Silkscreen which face is which__, and mark the pigtail polarity — reversing a LiPo into a XIAO destroys it
- __≥50 mm antenna separation__, through routing as well as placement

## Where it actually is

[README.md](../README.md) reports __2a complete, 2b partial, DRC clean at 0 violations, 0 unconnected__ — true, and easy to over-read. What exists is the outline, stackup, mounting holes, planes, and both XIAO positions with their nets.

| Stage | State |
|---|---|
| 2a — outline, mounting holes, stackup | __done__ |
| 2b — nets and footprints | __partial__ — XIAOs placed and netted, [#18](https://github.com/jwilleke/js-rocket-avionics/issues/18) fixed and closed 2026-09-08 (`c2468eb`: the +8.5 row unmirrored, and `verify_pins()` now asserts every net against the footprint's own pin table on each run). Sensors, buzzer and JST still deferred to [#14](https://github.com/jwilleke/js-rocket-avionics/issues/14) |
| 2c — placement | blocked on measured module pinouts — [#14](https://github.com/jwilleke/js-rocket-avionics/issues/14) |
| 2d — routing | __not started__. Autorouting is wrong here — [#15](https://github.com/jwilleke/js-rocket-avionics/issues/15) |
| 2e — gerber + drill export | chain proven; needs a finished board |

> __`fab/gerbers/` already holds a complete-looking set, and it is a partial board wearing a finished package.__ Generated by `hardware/scripts/gen_carrier.py` from a board with no sensor footprints, no `VBAT` and no routing. It is the single most likely way a wrong board gets ordered — it is complete, it is in the repo, and it looks done. __Regenerate, never reuse__ — [#16](https://github.com/jwilleke/js-rocket-avionics/issues/16).

## Read the board, not the script

An earlier generator revision put GPS on pins 6/7 and I2C on 4/5 — __D5/D6 and D3/D4, every one off by one__. It was caught by __reading the mapping back out of the saved board__, not by trusting the script's output. The generator now names pins (`XIAO_PIN["D6"]`) so the numbers never appear by hand.

> __It happened again, and this section is why that stings.__ [#18](https://github.com/jwilleke/js-rocket-avionics/issues/18), found 2026-09-08: the whole `+8.5 mm` row is mirrored end for end, so `+3V3` and `GND` land on __D9 and D8__ and `GPS_RX` on the __5V pin__. Naming the pins fixed the arithmetic and did nothing about the row order.
>
> __The read-back was written down as the check and never made routine.__ That is the actual defect — a check that only runs when someone remembers is a check that catches the first instance and not the second.
>
> __Now it runs.__ `c2468eb` closed [#18](https://github.com/jwilleke/js-rocket-avionics/issues/18) by unmirroring the row *and* adding `verify_pins()`, which asserts every placed net against `MCU_Seeed_ESP32C3`'s own pin coordinates on every generate — checking __both__ x and y, because pins 7 and 8 share a y and only x tells the two rows apart. A third instance fails the build rather than waiting for someone to read the board.

## Ordering

__Do not order copper before breadboarding.__ A layout error costs ~$33 and __two weeks__; a wiring error costs minutes. The gate is [#4](https://github.com/jwilleke/js-rocket-avionics/issues/4); the ordering epic is [#11](https://github.com/jwilleke/js-rocket-avionics/issues/11). Three copies from OSH Park.

__The outline and mounting-hole pattern were frozen before the sled generator was written__, since the sled's rail bosses derive from them. Moving them reprints a part.

---

Part numbers, vendors and masses live in [BOM.md](../docs/BOM.md), which is the single source of truth for both. Purchase history is in [shopping-list.md](../docs/shopping-list.md); the reasoning is in [design.md](../docs/design.md).
