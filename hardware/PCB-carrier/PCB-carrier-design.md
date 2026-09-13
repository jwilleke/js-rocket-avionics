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

__Board: 24 × 90.4 mm, nose z 25.4 → 115.8, ~4.1 g.__ Station lists for both sides are in [PCB-carrier.md](PCB-carrier.md#layout).

### What makes it work

__1. Every part sits in its own holes, and no hole meets another across the two sides.__ The L76K-GNSS already has its pins soldered, so it takes its own footprint on the tall side between the two XIAOs. The sensors run __lengthwise__ on the low side, their pin rows 2.15 mm inboard of the tall-side modules' rows and parallel to them. Turned 90°, they would cross. `gen_carrier.py` checks every through-hole against every other on each run.

__2. The sensors stand ~1 mm proud on their pins__, header plastic up against the sensor, so the plastic clears the tall side's solder joints on the low face.

__3. The standoffs are soldered to the board and the screws come in from the web side.__ Würth WA-SMSI M3 standoffs, 10 mm, on the low side; two M3 plastic screws, M3 × 10, through the web into them. Nothing fastens through to the tall side, so __no screw head is ever under a module__. Neither standoff is under a module either: each has a 4.4 mm hole through the board, so standoff 1 sits at the aft end, under the USB-C plug room, clear of XIAO-ESP32S3-cam and the BAT pigtail beneath it (operator, 2026-09-11).

__4. The board does not touch the web.__ It hangs 10 mm off it, so there are no printed pads, no filed tails and no slots.

## Across the bore

Looking forward, 270° down; r from the sled's centre line.

| | r | Clearance |
|---|---|---|
| Board | −0.5 to +0.5 | on the centre line |
| Cam stack top | 11.2 toward 270° | __2.9 mm__ to the camera pad floor — as [#89](https://github.com/jwilleke/js-rocket/issues/89) was designed |
| Lora stack top | 12.3 toward 270° | ~5.6 mm to the bore at its corners |
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

- __Its gate reads XIAO-ESP32S3-cam's `5V` pin__, through a resistor, with a pull-down (~100 kΩ) to `GND`. `5V` carries USB power whenever USB is in, and nothing on the battery. USB in: gate at 5 V, above the battery, Q1 off. USB out: gate pulled low, Q1 on. No wire added to the service pigtail
- __Body diode points the safe way__: with Q1 off, the battery cannot feed XIAO-ESP32S3-lora through it
- __It must never cut XIAO-ESP32S3-lora in flight.__ With no USB nothing pulls the gate up; the one way it could is the pull-down failing open, leaving the gate floating. Choose a resistor that fails safe, and bench-test before copper
- __The two `5V` pins still never meet__ — a sense connection to the gate, not a power path
- __Q1 cannot cover both XIAOs.__ Moved to where the battery feed splits, the two XIAOs would share its far side, and XIAO-ESP32S3-cam's own charger would power XIAO-ESP32S3-lora through that shared node — it would not go off. (Written that way on 2026-09-13 and corrected the same day.)

#### A faster charger chip

__Decided, operator 2026-09-13.__ The XIAO's own charger is fixed at ~115–120 mA, ~4½ hours from empty. A single-cell linear charger chip on the carrier — __MCP73831-class__, SOT-23-5, ~$0.50–1 plus a current-setting resistor and two capacitors, __~$1 a board__ — fed from XIAO-ESP32S3-cam's `5V` pin at __~400 mA__ (0.8C) takes it to __~1½ hours__.

- __Heat:__ a linear charger burns (5 − 3.7 V) × 0.4 A ≈ __0.5 W__ at the start of a charge, in a closed nose. ~400 mA is the ceiling; give it copper to spread into, and check its thermal regulation
- __Open — two chargers on the battery.__ XIAO-ESP32S3-cam's own charger cannot be disabled and stays connected, so with the chip, two chargers charge together from the one USB. Both stop at 4.2 V, which is probably benign, but not assumed. The alternative is a second FET, Q2, taking XIAO-ESP32S3-cam's feed off the battery while USB is in — whose body diode would still let the cam's charger into the battery, so it needs working through. __Settle it at the bench check, before copper__

__This should have been caught at design time.__ [LiPo-500mAh.md](../LiPo-500mAh/LiPo-500mAh.md#two-chargers-on-one-battery) wrote down on 2026-09-10 that the net charge "may be near zero" and deferred it to a measurement, instead of designing it out. The measurement found it before copper; it should not have needed to.

### The XIAO pigtails plug into the carrier — decided, not yet in the generator

> __Under review, 2026-09-13 — sockets on the board may not fit.__ Each pigtail is ~10 mm and leaves its XIAO at the end away from the USB-C, which on the carrier is the forward end: XIAO-ESP32S3-cam's at y 28.5, with a 5.0 mm gap before the L76K-GNSS; XIAO-ESP32S3-lora's at y 78.5, where the battery JST and standoff 2 leave ~3.9 mm. A JST-PH socket is ~6 × 4.5 mm. The alternative being weighed: short leads soldered to carrier pads, each ending in a JST socket the pigtail plugs into. __Do not build from the line above until this is settled__ ([#14](https://github.com/jwilleke/js-rocket-avionics/issues/14)).

__Operator, 2026-09-13 ([#14](https://github.com/jwilleke/js-rocket-avionics/issues/14)).__ Each XIAO's battery pigtail — soldered to its underside BAT pads before it goes onto its headers, and ending in a JST-PH plug — __plugs into a JST-PH socket on the carrier__, in place of the solder wire pads the generator draws today. Nothing is soldered to the carrier, and the XIAO pads, a miserable job, are never re-soldered.

- __Three JST-PH sockets on the tall side__: the battery's (already drawn), XIAO-ESP32S3-cam's pigtail, XIAO-ESP32S3-lora's pigtail — the last fed through Q1
- __Polarity differs:__ the pigtail sockets are wired opposite to the battery socket, because the battery's plug and the pigtails' plugs disagree (the bench harness crosses its wires for exactly this). Silkscreen `+` at each, and meter each against its plug before the first power-up
- __Room is not yet shown.__ A JST-PH socket is ~6 × 4.5 mm and ~6 mm tall. Beside XIAO-ESP32S3-cam there is ~4.5 mm to the L76K-GNSS; beside XIAO-ESP32S3-lora the space is shared with the battery socket and standoff 2. `gen_carrier.py` has to fit them, and its checks prove they fit
- __Retention:__ each plug gets a dab of hot glue or tape once seated — a JST-PH holds by friction, and boost is 17.6 g

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

## What changes in the sled — js-rocket#99

- __Web offset__ to r 10.5–13.5 toward 90° (its centre 12.0 mm off the axis), still 3 mm and one piece. The D-flat, discs and clocking loop do not move
- __Two M3 clearance holes__ through the web, at the standoffs: nose z 29.4 on the board's centre line, and nose z 110.6, 4.5 mm off it. Screws from the web's 90° face
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
