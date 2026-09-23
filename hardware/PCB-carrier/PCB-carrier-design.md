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

__Every number — size, stations, clearances, the battery's position — is in [PCB-carrier.md](PCB-carrier.md), the carrier's one source of truth.__ This page is the discussion: why each choice was made, and what is decided but not yet drawn. Where the two disagree, PCB-carrier.md wins.

### What makes it work

__1. Every part sits in its own holes, and no hole meets another across the two sides.__ The L76K-GNSS already has its pins soldered, so it takes its own footprint on the tall side between the two XIAOs. The sensors run __lengthwise__ on the low side, parallel to the tall-side modules' rows. Turned 90°, they would cross. The LSM6DSO32 is slid sideways to clear XIAO-ESP32S3-cam's real rows ([#33](https://github.com/jwilleke/js-rocket-avionics/issues/33); where, in [PCB-carrier.md](PCB-carrier.md#low-side--faces-90-the-web)). `gen_carrier.py` checks every through-hole against every other on each run.

__2. The sensors stand ~1 mm proud on their pins__, header plastic up against the sensor, so the plastic clears the tall side's solder joints on the low face.

__3. The standoffs are soldered to the board and the screws come in from the web side.__ Würth WA-SMSI M3 standoffs, 10 mm, on the low side; two M3 plastic screws, M3 × 10, through the web into them. Nothing fastens through to the tall side, so __no screw head is ever under a module__. Neither standoff is under a module either: each has a 4.4 mm hole through the board, so standoff 1 sits at the aft end, under the USB-C plug room, clear of XIAO-ESP32S3-cam and the BAT pigtail beneath it (operator, 2026-09-11).

__4. The board does not touch the web.__ It hangs 10 mm off it, so there are no printed pads, no filed tails and no slots.

## Across the bore

The table is in [PCB-carrier.md](PCB-carrier.md#across-the-bore). __Why the board grew toward 270° at 1.6 mm:__ its low face has to stay at r 0.5, where the standoffs put it against the web, so the extra 0.6 mm (1.0 until 2026-09-15) went toward 270° and took the tall side with it. That cost the camera pad 0.6 mm: 2.3 mm over the cam stack, where [#89](https://github.com/jwilleke/js-rocket/issues/89) was designed with 2.9.

__The bridge__ was to stand its fins beside the board's edges and carry the camera pad over the cam stack. __It is left out of the ElectronicsSled fit article__ (2026-09-15): the pad sits in the carrier's path as the carrier goes onto its standoffs from the 270° side. How the camera is held is open.

## Electrically

__One regulator per load.__ XIAO-ESP32S3-cam feeds the +3V3 plane and the sensors; XIAO-ESP32S3-lora feeds only the L76K-GNSS, on its own net, off the plane. __One board means no battery link__ between boards: the JST feeds both XIAOs' BAT pigtail pads directly. The connection table is in the [README](../../README.md#connections).

### Charging on the carrier — a charger chip on an adapter, no cut-off switches

__Tracked in [#30](https://github.com/jwilleke/js-rocket-avionics/issues/30)__, under the battery-charging epic [#32](https://github.com/jwilleke/js-rocket-avionics/issues/32); it blocks the carrier order, [#11](https://github.com/jwilleke/js-rocket-avionics/issues/11). Charging in the nose did not work with XIAO-ESP32S3-cam's built-in charger alone: XIAO-ESP32S3-lora kept drawing from the battery and out-drew the ~115 mA charger, and the battery fell 3.5 → 3.4 V in 1 h 25 min ([#8](https://github.com/jwilleke/js-rocket-avionics/issues/8)). The fix is more charge current, not less load. The circuit is on [charge-circuit.md](../charge-circuit/charge-circuit.md).

#### A faster charger chip

__Decided, operator 2026-09-13.__ The XIAO's own charger is fixed at ~115–120 mA, ~4½ hours from empty. A single-cell linear charger chip on the carrier, fed from XIAO-ESP32S3-cam's `5V` pin, cuts that to __~1½–2 hours__ — the bench times it ([charging-bench.md](../../docs/bench-work/charging-bench.md)).

| | Chosen 2026-09-13 — from Microchip's datasheet, DS20001984H |
|---|---|
| __The charger chip__ | __MCP73831T-2ACI/OT__ — SOT-23-5, 4.20 V, 15–500 mA. Pins: 1 `STAT`, 2 `VSS`, 3 `VBAT`, 4 `VDD`, 5 `PROG` |
| __Current resistor__ | set on [charge-circuit.md](../charge-circuit/charge-circuit.md), which owns the value and the current. I = 1000 V ÷ R |
| __Capacitors__ | 4.7 µF on `VDD` and 4.7 µF on `VBAT` — the datasheet's minimum for each |
| `STAT` | not connected — a light inside a closed nose is seen by nobody |

- __Why the current is capped:__ the battery's maker says charge it "at a rate of 500mA or less" (Adafruit 1578 listing), and the chip charges alongside XIAO-ESP32S3-cam's own charger. The sum stays under 500 mA at the top of the chip's tolerance — numbers on [charge-circuit.md](../charge-circuit/charge-circuit.md)
- __The `5V` pin can feed it — checked on Seeed's schematic (XIAO ESP32S3 v1.2).__ Header pin 7 (`5V`) is the `VBUS` net itself: copper straight from the USB-C's `VBUS` pins, no fuse and no diode between. So nothing in the path limits the current; its copper and the USB-C connector carry XIAO-ESP32S3-cam's own draw plus ~0.4 A. Seeed writes no rating for it, so the bench reads the pin's voltage under load
- __The USB source must give ~0.6 A.__ The XIAO's USB-C has 5.1 kΩ on both `CC` pins, so a USB-C charger or power bank sees a device and gives its full current; an old USB-A port through an A-to-C cable promises 500 mA, and may sag. For [using-avionics.md](../../docs/using-avionics.md) once it is built
- __Heat:__ at the start of a charge the chip burns (5.0 − 3.5 V) × 0.33 A ≈ __0.5 W__. Microchip gives the SOT-23-5 230 °C/W with minimal copper and ~130 °C/W or better with a large copper area — a die __65–115 °C above ambient__. So it will likely hit its __thermal regulation__, which cuts the current to hold the die temperature (shutdown at 150 °C). That costs charge time, not safety. On the adapter it has only six pins to shed heat into, so expect it to throttle
- __On an adapter, not on the carrier__ (operator, 2026-09-16). The chip is soldered to a 6-pad SOT-23-to-DIP adapter on the bench, and that adapter stands on header pins in the carrier — "module footprints, not bare chips" ([PCB-carrier.md](PCB-carrier.md)). The same part is proven on the breadboard and flown, and the carrier carries no fine-pitch footprint

#### No cut-off switches

__Decided, operator 2026-09-16 ([#30](https://github.com/jwilleke/js-rocket-avionics/issues/30)).__

- __Not for XIAO-ESP32S3-cam's built-in charger.__ It charges alongside the charger chip, and the chip's resistor keeps the two under the battery's 500 mA. A FET to take it off would have cost a part and raised an unchecked question: whether XIAO-ESP32S3-cam resets while `VBUS` falls slowly at unplug
- __Not for XIAO-ESP32S3-lora.__ A FET taking it off the battery while USB is in was the answer to #8 when the only charger gave ~115 mA. With the chip, the lora side takes its share and the rest still charges. Leaving it on keeps the beacon and GPS running while charging, saves a part, and removes a trap: a data link could have powered a switched-off XIAO-ESP32S3-lora through its pins. The cost is a slower charge that never terminates while USB is in; the bench measures how much slower

__This should have been caught at design time.__ [LiPo-500mAh.md](../LiPo-500mAh/LiPo-500mAh.md#two-chargers-on-one-battery) wrote down on 2026-09-10 that the net charge "may be near zero" and deferred it to a measurement, instead of designing it out. The measurement found it before copper; it should not have needed to.

### The XIAO pigtails go through holes behind each XIAO — decided, in the generator

__Operator, 2026-09-13 ([#14](https://github.com/jwilleke/js-rocket-avionics/issues/14)).__ Each XIAO's battery pigtail — soldered to its underside BAT pads before it goes onto its headers, ~10 mm long, leaving at the end away from the USB-C — __goes through two holes directly behind that XIAO and is soldered on the far (low) side__, with the holes labelled. The XIAO pads, a miserable job, are never re-soldered; the bench JST plug is cut off.

__The holes are already in the generator__ (`WIRE_PADS`, `TestPoint_THTPad_D2.0mm_Drill1.0mm`), just past each XIAO's forward end:

| | XIAO's forward end | Holes |
|---|---|---|
| XIAO-ESP32S3-cam | y 28.5 | `TP_CAM_BAT_P` (8.8, 30.0), `TP_CAM_BAT_N` (12.0, 30.0) |
| XIAO-ESP32S3-lora | y 78.5 | `TP_LORA_BAT_P` (10.4, 80.8), `TP_LORA_BAT_N` (13.6, 80.8) |

- __Labelled on both sides__ — `BAT`, `+` and `-` at each pair, mirrored on the low side so it reads from there (`BAT_LABELS` in `gen_carrier.py`, 2026-09-13; DRC 0 violations). Each module's name is also on the board under it, on its own side — `XIAO-ESP32S3 / cam`, `L76K-GNSS`, `XIAO-ESP32S3 / lora` on the tall side, `LSM6DSO32` and `BMP388` mirrored on the low side (`MODULE_LABELS`) — so the carrier says what goes where during assembly
- __Assembly order — the LSM6DSO32 sits over XIAO-ESP32S3-cam's holes on the low side__, ~1 mm off the carrier, so that pigtail is soldered __before the sensor goes on__ and its joints trimmed flush. XIAO-ESP32S3-lora's holes lie under the battery, which is 5.25 mm off the board in the sled's cage
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

__Operator: behind the carrier on 2026-09-14, layout B2 on 2026-09-15.__ The battery lies behind the carrier's __low face__, between the board and the moved web, long axis along the sled, 29 mm across (2.5 mm past each board edge). __Its position is in [PCB-carrier.md](PCB-carrier.md#low-side--faces-90-the-web)__, which owns it.

__It moved once more on 2026-09-15.__ B2 first drew it on a 1 mm insulating pad against the board. It was then set __against the web__ instead, in a cage, and 1.2 mm further aft so the cage's forward wall clears the BMP388. [PCB-carrier.md](PCB-carrier.md#low-side--faces-90-the-web) records the position; the ElectronicsSled's cage ([js-rocket#99](https://github.com/jwilleke/js-rocket/issues/99)) is built to it.

__Why behind the board.__ It is the only place beside the carrier that passes the 40 mm door ([Across the bore](PCB-carrier.md#across-the-bore)). Everywhere else beside the board a 29 mm battery reaches r 22–23. The old spot — on the sled's D-flat at nose z 125–161 — put its forward corners __~1.2 mm into the Nosecone wall__, read off `nosecone.stl` on 2026-09-13 ([js-rocket#99](https://github.com/jwilleke/js-rocket/issues/99#issuecomment-5654142688)).

__Why B2, and not the first drawing.__ The first drawing (2026-09-14) put the battery at nose z 101–137 with both sensors slid 20 mm aft. `gen_carrier.py`'s clearance check rejected it: the BMP388's two M2 legs, 20.6 mm apart ([its 2026-09-11 mounting](../BMP388-barometer/BMP388-barometer.md)), landed on the L76K-GNSS's header joints. Both legs have to fall in the gaps between the tall side's header rows and clear the JST, which leaves the BMP388 very few places. B2 moves the LSM6DSO32 aft and the BMP388 forward, and the battery takes the low side between them. The other way — the BMP388 on its header alone, keeping the battery at 101–137 — was offered and not chosen.

__Layout B2 — in the generator, 2026-09-15.__ `verify_clearances()` passes (72 through-holes clear of each other, the standoffs and the BMP388 legs); kicad-cli DRC 0 violations, 10 unconnected items — the unrouted nets, as before. B2 lengthened the board from 90.4 mm, moved the LSM6DSO32 aft and the BMP388 and the forward standoff forward, and put the battery on the low side between the sensors. __Where everything now is: [PCB-carrier.md](PCB-carrier.md#layout).__

__Owed before the carrier is ordered:__

1. __Stability.__ The battery's centre is now __~56 mm aft__ of the old D-flat spot, and aft mass is expensive ([configurations.md](https://github.com/jwilleke/js-rocket/blob/main/docs/configurations.md#where-the-ballast-goes-and-why-placement-matters)). Re-derive the nose's CG and re-run the flight-3 stability numbers
2. __Stiffness.__ The standoffs are further apart than the 81 mm the board was first judged at. The battery no longer loads the span: it rides the sled, in its cage. The board is __1.6 mm__ since 2026-09-15 — OSH Park's only 4-layer thickness — about 4× as stiff as the 1.0 mm it was judged at. Still check it; the fit mock is a first look, not an answer
3. __Retention.__ The sled's cage holds it: three-sided, taped on its open sides ([js-rocket#99](https://github.com/jwilleke/js-rocket/issues/99)). __Never clamp the pouch__
4. __The joints under the battery__ — the L76K-GNSS's and XIAO-ESP32S3-lora's header joints and XIAO-ESP32S3-lora's BAT pigtail joints — face 5.25 mm of air, not the pouch. Trim them flush anyway
5. __The charger chip ([#30](https://github.com/jwilleke/js-rocket-avionics/issues/30)) goes clear of the battery__ — where that is, and the clear stretch on the tall side, is in [PCB-carrier.md](PCB-carrier.md#layout)
6. __The battery lead__ reaches the JST on the tall side around the board's edge — right at the battery's forward end
7. __The GNSS patch__ sits in a pocket in the sled's forward disc, off the carrier ([js-rocket#99](https://github.com/jwilleke/js-rocket/issues/99))

Drawing: [`nose-assembly-6e81cfc.html`](https://github.com/jwilleke/js-rocket/blob/main/docs/designs/nose-assembly-6e81cfc.html) — it draws the one carrier in PCB-carrier.md.

## What changes in the sled — js-rocket#99

__Built 2026-09-15 as the ElectronicsSled fit article__ ([js-rocket#99](https://github.com/jwilleke/js-rocket/issues/99), js-rocket `6d7ba00`). The web moves to r 10.5–13.5 toward 90°. The two M3 holes are printed at the standoffs, not drilled. It adds the battery cage, a ballast cup, and a 2 mm GNSS patch pocket in the forward disc. There are no pads, no slots and no board-to-web contact. __Left out: #89's camera pad__, which blocks the carrier going on. The sled's own page owns its numbers: [payload-sled.md](https://github.com/jwilleke/js-rocket/blob/main/docs/3d-printed-parts/payload-sled.md).

## Checks owed before building

1. __The standoff part__: Würth WA-SMSI M3, 10 mm (9774100360) — confirm it is stocked
2. __JST pin 1 against the battery's red lead__
Settled by the generator rather than owed: every sensor's pin order on the back of the board, and every hole's clearance across the two sides.

__Settled on the bench, 2026-09-11:__ stock Meshtastic reads the GPS on D6/D7 — its startup log names GPIO43/44 and detects the L76K ([#6](https://github.com/jwilleke/js-rocket-avionics/issues/6#issuecomment-5639176943)). So the carrier's `GPS_TX`/`GPS_RX` nets stand as drawn.

## How it got here

The first layout, one board with parts on both faces, was derived from a camera-port drawing that put the board and the sled's web in the same place. When that surfaced ([#13](https://github.com/jwilleke/js-rocket-avionics/issues/13)), the session wrongly turned the operator's "prefer one board" into two identical boards, one on each web face, and built on it. This design goes back to what was asked for: one board, the web moved out of its way, both stacks on one side.
