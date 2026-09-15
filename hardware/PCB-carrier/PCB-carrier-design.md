# PCB-carrier — design brief

__Status: adopted, operator 2026-09-11.__ This is the design record for the carrier; [PCB-carrier.md](PCB-carrier.md) is what the generated board is. It replaces the "two identical boards" layout, which was never the operator's decision and was recorded as one in error.

## What the operator asked for

- __One board__ — one physical PCB-carrier, not two
- __Both XIAO stacks on the same side of the board__, one at each end — the tall parts together
- __The web offset between the discs__, out of the board's way
- __Two screws__, for precise alignment, and the board __removable from the sled__ as one unit
- __The camera mounts on the bridge__
- __The GNSS antenna mounts on the ElectronicsSled__

## The design

![PCB-carrier from both sides, forward up, generated from the board](PCB-carrier-layout.svg)

__One two-sided board on the sled's centre line.__ The __tall side__ faces 270°, the camera port: XIAO-ESP32S3-cam aft, under the camera; the L76K-GNSS; XIAO-ESP32S3-lora forward; the JST. The __low side__ faces 90°, the web: the LSM6DSO32 and BMP388, and two standoffs. The web is moved toward 90°, clear of the low side, and the board hangs off it. Take out two screws and the whole board comes off the sled.

__Board: 24 × 115.7 × 1.6 mm, nose z 25.4 → 141.1, ~8.3 g__ — the battery on its low face (2026-09-15). Station lists for both sides are in [PCB-carrier.md](PCB-carrier.md#layout).

### What makes it work

__1. Every part sits in its own holes, and no hole meets another across the two sides.__ The L76K-GNSS already has its pins soldered, so it takes its own footprint on the tall side between the two XIAOs. The sensors run __lengthwise__ on the low side, their pin rows 2.15 mm inboard of the tall-side modules' rows and parallel to them. Turned 90°, they would cross. `gen_carrier.py` checks every through-hole against every other on each run.

__2. The sensors stand ~1 mm proud on their pins__, header plastic up against the sensor, so the plastic clears the tall side's solder joints on the low face.

__3. The standoffs are soldered to the board and the screws come in from the web side.__ Würth WA-SMSI M3 standoffs, 10 mm, on the low side; two M3 plastic screws, M3 × 10, through the web into them. Nothing fastens through to the tall side, so __no screw head is ever under a module__. Neither standoff is under a module either: each has a 4.4 mm hole through the board, so standoff 1 sits at the aft end, under the USB-C plug room, clear of XIAO-ESP32S3-cam and the BAT pigtail beneath it (operator, 2026-09-11).

__4. The board does not touch the web.__ It hangs 10 mm off it, so there are no printed pads, no filed tails and no slots.

## Across the bore

Looking forward, 270° down; r from the sled's centre line. __The board's low face stays at r 0.5__, where the standoffs put it against the web, so at 1.6 mm (2026-09-15, 1.0 before) the extra 0.6 mm goes toward 270° and everything on the tall side moves with it.

| | r | Clearance |
|---|---|---|
| Board | −1.1 to +0.5 | low face 0.5 toward 90°, as at 1.0 mm |
| Cam stack top | 11.8 toward 270° | __2.3 mm__ to the camera pad floor (r 14.09) — 2.9 as [#89](https://github.com/jwilleke/js-rocket/issues/89) was designed, on a 1.0 mm board. Corners r 14.78, 5.2 mm inside the 40 mm door |
| Lora stack top | 12.9 toward 270° | corners r 15.67, __4.3 mm__ inside the door |
| Sensors top | 8.8 toward 90° | 1.7 mm to the web |
| __Web__ | __10.5–13.5 toward 90°__ | 24 mm wide; the bore is 29.5 mm wide at r 13.5 |

__The bridge__ is unchanged in principle: its fins stand beside the board's edges and carry the camera pad over the cam stack. They now root on a web 12 mm further toward 90°, so they are longer.

## Electrically

__One regulator per load.__ XIAO-ESP32S3-cam feeds the +3V3 plane and the sensors; XIAO-ESP32S3-lora feeds only the L76K-GNSS, on its own net, off the plane. __One board means no battery link__ between boards: the JST feeds both XIAOs' BAT pigtail pads directly. The connection table is in the [README](../../README.md#connections).

### Charging on the carrier — Q1, the charge-isolation FET, and a charger chip — decided, not yet in the generator

__Operator, 2026-09-12 and 2026-09-13 — tracked in [#30](https://github.com/jwilleke/js-rocket-avionics/issues/30)__, under the battery-charging epic [#32](https://github.com/jwilleke/js-rocket-avionics/issues/32); it blocks the carrier order, [#11](https://github.com/jwilleke/js-rocket-avionics/issues/11). Charging in the nose did not work: with USB in XIAO-ESP32S3-cam, XIAO-ESP32S3-lora kept drawing from the battery and out-drew the cam's ~115 mA charger — the battery fell 3.5 → 3.4 V in 1 h 25 min ([#8](https://github.com/jwilleke/js-rocket-avionics/issues/8)). That would have ended field charging through the service pigtail.

#### Q1 — the charge-isolation FET

__A P-channel MOSFET, high side, in XIAO-ESP32S3-lora's battery feed__ — source to `VBAT`, drain to XIAO-ESP32S3-lora's BAT pigtail pad. It is an electronic switch with nothing to operate: __USB decides it.__

| USB | Q1 | XIAO-ESP32S3-cam | XIAO-ESP32S3-lora | Battery |
|---|---|---|---|---|
| none — flight, pad | on (closed) | on the battery | on the battery | powers both |
| in XIAO-ESP32S3-cam, directly or through the service pigtail | __off (open)__ | on, from USB | __off__ — with the Wio-SX1262 and the L76K-GNSS, which draw through it | charges |

- __The part: AO3401A__ (AOS), P-channel, SOT-23 — −30 V, ±12 V gate, < 85 mΩ at a −2.5 V gate and < 60 mΩ at −4.5 V, threshold −0.5 to −1.3 V (AOS datasheet, rev 3.1). Fully on from a 3.0 V battery; at ~0.3 A it drops ~20 mV. Chosen 2026-09-13
- __Its gate reads XIAO-ESP32S3-cam's `5V` pin__, with a pull-down (~100 kΩ) to `GND`. `5V` carries USB power whenever USB is in, and nothing on the battery. USB in: gate at 5 V, above the battery, Q1 off. USB out: gate pulled low, Q1 on. No wire added to the service pigtail
- __Body diode points the safe way__: with Q1 off, the battery cannot feed XIAO-ESP32S3-lora through it
- __It must never cut XIAO-ESP32S3-lora in flight.__ With no USB nothing pulls the gate up; the one way it could is the pull-down failing open. __It has a second one already__: Seeed's schematic puts R9, 100 kΩ, from the XIAO's `VBUS` — which is the `5V` pin — to `GND`. Either resistor alone holds the gate low
- __Seeed's XIAO does the same thing inside__: its own Q1 (LP0404N3T5G, a P-channel FET) has its gate on `VBUS` with R9 pulling it down, and takes the XIAO's regulator off its battery while USB is in (XIAO ESP32S3 schematic v1.2)
- __A data-link shunt must not power it while it is off.__ With the mj-cam → lora shunt on ([below](#two-data-links-each-behind-an-open-jumper--decided-not-yet-in-the-generator)), a high output from XIAO-ESP32S3-cam would push ~3 mA through the 1 kΩ into an unpowered XIAO-ESP32S3-lora. Firmware holds that pin low while USB is in, or the shunt is off while charging
- __The two `5V` pins still never meet__ — a sense connection to the gate, not a power path
- __Q1 cannot cover both XIAOs.__ Moved to where the battery feed splits, the two XIAOs would share its far side, and XIAO-ESP32S3-cam's own charger would power XIAO-ESP32S3-lora through that shared node — it would not go off. (Written that way on 2026-09-13 and corrected the same day.)

#### A faster charger chip

__Decided, operator 2026-09-13.__ The XIAO's own charger is fixed at ~115–120 mA, ~4½ hours from empty. A single-cell linear charger chip on the carrier, fed from XIAO-ESP32S3-cam's `5V` pin, cuts that to __~1½–2 hours__ — the bench times it ([charging-bench.md](../../docs/bench-work/charging-bench.md)).

| | Chosen 2026-09-13 — from Microchip's datasheet, DS20001984H |
|---|---|
| __U1, the charger__ | __MCP73831T-2ACI/OT__ — SOT-23-5, 4.20 V, 15–500 mA. Pins: 1 `STAT`, 2 `VSS`, 3 `VBAT`, 4 `VDD`, 5 `PROG` |
| __Current resistor__ | __2.7 kΩ__ on `PROG`: I = 1000 V ÷ R = __370 mA__, and 333–407 mA across the datasheet's ±10% |
| __Capacitors__ | 4.7 µF on `VDD` and 4.7 µF on `VBAT` — the datasheet's minimum for each |
| `STAT` | not connected — a light inside a closed nose is seen by nobody |

- __Why 370 mA and not 400:__ the battery's maker says charge it "at a rate of 500mA or less" (Adafruit 1578 listing). 2.7 kΩ keeps even the top of the chip's tolerance under that
- __The `5V` pin can feed it — checked on Seeed's schematic (XIAO ESP32S3 v1.2).__ Header pin 7 (`5V`) is the `VBUS` net itself: copper straight from the USB-C's `VBUS` pins, no fuse and no diode between. So nothing in the path limits the current; its copper and the USB-C connector carry XIAO-ESP32S3-cam's own draw plus ~0.4 A. Seeed writes no rating for it, so the bench reads the pin's voltage under load
- __The USB source must give ~0.6 A.__ The XIAO's USB-C has 5.1 kΩ on both `CC` pins, so a USB-C charger or power bank sees a device and gives its full current; an old USB-A port through an A-to-C cable promises 500 mA, and may sag. For [using-avionics.md](../../docs/using-avionics.md) once it is built
- __Heat:__ at the start of a charge the chip burns (5.0 − 3.5 V) × 0.37 A ≈ __0.56 W__. Microchip gives the SOT-23-5 230 °C/W with minimal copper and ~130 °C/W or better with a large copper area — a die __72–128 °C above ambient__. So it will likely hit its __thermal regulation__, which cuts the current to hold the die temperature (shutdown at 150 °C). That costs charge time, not safety. __Give it copper__, away from the sensors
- __Hand-soldered.__ The carrier is bare boards from OSH Park, assembled by hand, and "module footprints, not bare chips" ([PCB-carrier.md](PCB-carrier.md)) was written for the LSM6DSO32's 2.5 × 3 mm LGA. Q1, Q2 and U1 are SOT-23s — 0.95 mm pin spacing, leads you can see — plus a few passives, to be drawn at a hand-solderable size. The bench soldering them onto adapters is the rehearsal; if that goes badly, the answer is a charger module footprint, before copper

#### Q2 — XIAO-ESP32S3-cam's charger off the battery — recommended, needs the operator's OK

__With U1 and no Q2, two chargers share the battery__ while USB is in: XIAO-ESP32S3-cam's own ~115–120 mA cannot be disabled. 370 + 120 = 490 mA, and up to ~527 mA at U1's tolerance — __over the battery's 500 mA__. Dropping U1 to 3.0 kΩ (333 mA) would keep the sum under, with two chargers still ending the charge together.

__Q2 takes XIAO-ESP32S3-cam's BAT pigtail off the battery while USB is in__, so U1 alone charges — same part as Q1, AO3401A, gate on the same `5V` pin and pull-down.

- __Q2 faces the other way from Q1: drain to `VBAT`, source to XIAO-ESP32S3-cam's BAT pigtail.__ Its body diode then conducts only from the battery toward XIAO-ESP32S3-cam. That is the working-through owed on 2026-09-13: facing Q1's way, the body diode would let XIAO-ESP32S3-cam's charger into the battery whenever the battery is under ~3.5 V (its 4.2 V less a diode drop) — the start of a charge, when the current is highest
- __Unplugging USB is the moment to watch.__ The battery reaches XIAO-ESP32S3-cam through Q2's body diode until Q2's channel is fully on — but `VBUS` falls slowly once U1 stops drawing (the two 100 kΩ pull-downs against ~5.7 µF, a time constant near 0.3 s), so for a moment Q2 is only partly on, and XIAO-ESP32S3-cam's supply sits a diode drop or two low. Whether it rides through without a reset is not worked out on paper; __the bench checks it__. If it resets, a smaller pull-down empties `VBUS` faster
- __Cost:__ one more AO3401A, from the same pack

__This page's recommendation is Q2__ — one part, a single charger ending the charge, and the full 370 mA.

__This should have been caught at design time.__ [LiPo-500mAh.md](../LiPo-500mAh/LiPo-500mAh.md#two-chargers-on-one-battery) wrote down on 2026-09-10 that the net charge "may be near zero" and deferred it to a measurement, instead of designing it out. The measurement found it before copper; it should not have needed to.

### The XIAO pigtails go through holes behind each XIAO — decided, in the generator

__Operator, 2026-09-13 ([#14](https://github.com/jwilleke/js-rocket-avionics/issues/14)).__ Each XIAO's battery pigtail — soldered to its underside BAT pads before it goes onto its headers, ~10 mm long, leaving at the end away from the USB-C — __goes through two holes directly behind that XIAO and is soldered on the far (low) side__, with the holes labelled. The XIAO pads, a miserable job, are never re-soldered; the bench JST plug is cut off.

__The holes are already in the generator__ (`WIRE_PADS`, `TestPoint_THTPad_D2.0mm_Drill1.0mm`), just past each XIAO's forward end:

| | XIAO's forward end | Holes |
|---|---|---|
| XIAO-ESP32S3-cam | y 28.5 | `TP_CAM_BAT_P` (8.8, 30.0), `TP_CAM_BAT_N` (12.0, 30.0) |
| XIAO-ESP32S3-lora | y 78.5 | `TP_LORA_BAT_P` (10.4, 80.8), `TP_LORA_BAT_N` (13.6, 80.8) — `VBAT` side fed through Q1 |

- __Labelled on both sides__ — `BAT`, `+` and `-` at each pair, mirrored on the low side so it reads from there (`BAT_LABELS` in `gen_carrier.py`, 2026-09-13; DRC 0 violations). Each module's name is also on the board under it, on its own side — `XIAO-ESP32S3 / cam`, `L76K-GNSS`, `XIAO-ESP32S3 / lora` on the tall side, `LSM6DSO32` and `BMP388` mirrored on the low side (`MODULE_LABELS`) — so the carrier says what goes where during assembly
- __Assembly order — the sensors sit over the holes on the low side.__ XIAO-ESP32S3-cam's holes are under the LSM6DSO32 (y 29.0–54.5), XIAO-ESP32S3-lora's under the end of the BMP388 (y 55.5–81.0), each standing ~1 mm off the carrier. So the pigtails are soldered __before the sensors go on__, and the joints trimmed flush so the sensor boards clear them
- __Polarity__ is fixed by the holes, not a connector: `+` to `+`, checked with a meter before first power-up
- __Superseded:__ JST sockets on the board for the pigtails (decided and dropped the same day — no room within the pigtail's ~10 mm)

### Two data links, each behind an open jumper — decided, not yet in the generator

__Operator, 2026-09-12 ([#26](https://github.com/jwilleke/js-rocket-avionics/issues/26)).__ Both are nice-to-have, so the copper is built now and the features are chosen later. Each link runs through a __standard 2-pin 2.54 mm header with a slide-on shunt__: shunt off, the boards are exactly as isolated as without the link; shunt on, the feature is available to firmware.

| Link | Direction | Gives, with the shunt on | In series |
|---|---|---|---|
| __GPS → mj-cam__ | the L76K's transmit line (`GPS_RX`, into lora `D7`) also to a spare XIAO-ESP32S3-cam input — __listen only__ | the GPS track, ~1 Hz with GPS altitude, in the flight log beside the barometer and IMU | ~1 kΩ at mj-cam's pin, so a firmware mistake there cannot pull the beacon's GPS line down |
| __mj-cam → lora__ | a spare XIAO-ESP32S3-cam output to a spare XIAO-ESP32S3-lora input, for Meshtastic's Serial module — __one way__ | event messages on the private channel — armed, launch, apogee, landed-here — a few per flight, rate-limited in mj-cam | ~1 kΩ, so neither side can drive the other hard |

- __Off is the safe state__, and the one a shaken-loose shunt fails to: a shunt lost under boost costs the feature, never the beacon. Dab it in place if a flight must have the feature
- __Height:__ header plus shunt stands ~8–9 mm, so both go on the __tall side__, where the XIAO stacks already reach 10.7–11.8 mm
- __Set before the nose is closed__ — the shunts are not reachable after
- __Owed before they are drawn:__ which spare pins — mj-cam's `D1` (GPIO2) is the clean choice for the GPS input, `D2` is a strapping pin; the lora side is whatever Meshtastic's `seeed-xiao-s3` variant leaves free beside the Wio-SX1262 — and a bench check that the Serial module does what is described on firmware `2.7.26` ([#26](https://github.com/jwilleke/js-rocket-avionics/issues/26))

## The battery sits behind the carrier — decided 2026-09-14, layout B2 2026-09-15

__Operator: behind the carrier on 2026-09-14, layout B2 on 2026-09-15.__ The battery lies on the carrier's __low face__, between the board and the moved web: __nose z 70.5–106.5__, long axis along the sled, 29 mm across (2.5 mm past each board edge), 4.75 mm thick on a __1 mm insulating pad__ — r 1.5 to 6.25 toward 90°. __This page owns the battery's position__; [payload-sled.md](https://github.com/jwilleke/js-rocket/blob/main/docs/3d-printed-parts/payload-sled.md) and [LiPo-500mAh.md](../LiPo-500mAh/LiPo-500mAh.md) point here.

__Why behind the board.__ It is the only place beside the carrier that passes the 40 mm door: corners at __r 15.79__, 4.2 mm inside it. Everywhere else beside the board a 29 mm battery reaches r 22–23. The old spot — on the sled's D-flat at nose z 125–161 — put its forward corners __~1.2 mm into the Nosecone wall__, read off `nosecone.stl` on 2026-09-13 ([js-rocket#99](https://github.com/jwilleke/js-rocket/issues/99#issuecomment-5654142688)).

__Why B2, and not the first drawing.__ The first drawing (2026-09-14) put the battery at nose z 101–137 with both sensors slid 20 mm aft. `gen_carrier.py`'s clearance check rejected it: the BMP388's two M2 legs, 20.6 mm apart ([its 2026-09-11 mounting](../BMP388-barometer/BMP388-barometer.md)), landed on the L76K-GNSS's header joints. Both legs have to fall in the gaps between the tall side's header rows and clear the JST, which leaves the BMP388 very few places. B2 moves the LSM6DSO32 aft and the BMP388 forward, and the battery takes the low side between them. The other way — the BMP388 on its header alone, keeping the battery at 101–137 — was offered and not chosen.

__Layout B2 — in the generator, 2026-09-15.__ `verify_clearances()` passes (72 through-holes clear of each other, the standoffs and the BMP388 legs); kicad-cli DRC 0 violations, 10 unconnected items — the unrouted nets, as before. Nose z = layout y + 25.4:

| | Was | B2 | Layout |
|---|---|---|---|
| Board length | 90.4 mm, ends nose z 115.8 | __115.7 mm, ends nose z 141.1__ — inside the web, which ends at 146 | `BOARD_H` 115.7 |
| LSM6DSO32 | nose z 54.4–79.9 | __33.4–58.9__ | `LSM_Y` 20.75 |
| Battery | on the sled, nose z 125–161 | __70.5–106.5__ — not a footprint | y 45.1–81.1 |
| BMP388 | nose z 80.9–106.4 | __107.25–132.75__ | `BMP_Y` 94.6 |
| Forward standoff | nose z 110.6 | __135.9__ — 5.2 mm from the board's end, as before, under no module | (16.5, 110.5) |
| Aft standoff | nose z 29.4 | unchanged | (12.0, 4.0) |

__Owed before the carrier is ordered:__

1. __Stability.__ The battery's centre is at nose z 88.5 — __54.5 mm aft__ of where it was documented, and aft mass is expensive ([payload-ballast.md](https://github.com/jwilleke/js-rocket/blob/main/docs/payload-ballast.md)). Re-derive the nose's CG and re-run the flight-3 stability numbers
2. __Stiffness.__ The standoffs are now __106.5 mm apart__ (81 before), with the battery's 10.9 g on the span. The board is __1.6 mm__ since 2026-09-15 — OSH Park's only 4-layer thickness — about 4× as stiff as the 1.0 mm it was judged at over 81 mm. Still check it; the fit mock is a first look, not an answer
3. __Retention.__ There are __4.25 mm__ of air between the battery and the web. A foam spacer, or ties to the board clear of the modules — __never clamp the pouch__ between board and web
4. __The pad covers every through-hole joint under it__: the L76K-GNSS's and XIAO-ESP32S3-lora's header joints and XIAO-ESP32S3-lora's BAT pigtail joints (nose z 106), trimmed flush
5. __The charger chip ([#30](https://github.com/jwilleke/js-rocket-avionics/issues/30)) goes outside nose z 70.5–106.5__ on either face — the tall side is clear from 113.7 to 141.1
6. __The battery lead__ reaches the JST (tall side, nose z 105–114) around the board's edge — right at the battery's forward end
7. __The GNSS patch is still open.__ The sled's forward end is free; flat on the forward disc it clears the nose by only 0.33 mm (js-rocket#99)

Drawing: [`nose-assembly-6e81cfc.html`](https://github.com/jwilleke/js-rocket/blob/main/docs/designs/nose-assembly-6e81cfc.html), layout *Battery behind the carrier*.

## What changes in the sled — js-rocket#99

- __Web offset__ to r 10.5–13.5 toward 90° (its centre 12.0 mm off the axis), still 3 mm and one piece. The D-flat, discs and clocking loop do not move
- __Two M3 clearance holes__ through the web — __modelled in the mesh, printed, not drilled__ (operator, 2026-09-14) — at the standoffs: nose z 29.4 on the board's centre line, and nose z 135.9, 4.5 mm off it. Screws from the web's 90° face
- __Bridge fins__ reach from the moved web, past the board's edges, to the camera pad
- __Battery unmoved.__ The web edge it partly rests on moves 12 mm toward 90°, still under the battery but off its centre line — check its tie wraps
- __GNSS antenna cradle__ unchanged: with the battery unmoved it keeps ~0.9 mm at its corners in the taper
- __No pads, no slots, no board-to-web contact__

## Checks owed before building

1. __The standoff part__: Würth WA-SMSI M3, 10 mm (9774100360) — confirm it is stocked
2. __JST pin 1 against the battery's red lead__
Settled by the generator rather than owed: every sensor's pin order on the back of the board, and every hole's clearance across the two sides.

__Settled on the bench, 2026-09-11:__ stock Meshtastic reads the GPS on D6/D7 — its startup log names GPIO43/44 and detects the L76K ([#6](https://github.com/jwilleke/js-rocket-avionics/issues/6#issuecomment-5639176943)). So the carrier's `GPS_TX`/`GPS_RX` nets stand as drawn.

## How it got here

The first layout, one board with parts on both faces, was derived from a camera-port drawing that put the board and the sled's web in the same place. When that surfaced ([#13](https://github.com/jwilleke/js-rocket-avionics/issues/13)), the session wrongly turned the operator's "prefer one board" into two identical boards, one on each web face, and built on it. This design goes back to what was asked for: one board, the web moved out of its way, both stacks on one side.
