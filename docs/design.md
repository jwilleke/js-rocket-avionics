# Design record

__Why this payload is built the way it is.__ The decisions and the reasoning behind them, so the *why* survives into the work.

This project is __one candidate payload__ for the js-rocket [payload bay](https://github.com/jwilleke/js-rocket/blob/main/docs/payload-bay.md). The bay's interface — 40.0 mm bore × 150 mm, an M3 × 55 retainer at nose z 15, a ~50 g mass ceiling, an optional 8 mm camera port — is the rocket's business and is not restated here beyond what constrains the design.

Related: [BOM.md](BOM.md) (parts and masses) · [shopping-list.md](shopping-list.md) (what was bought) · [module-pinouts.md](module-pinouts.md) (footprint inputs) · [README.md](../README.md) (the carrier's frozen interface)

## Decisions locked

| Decision | Value | Why |
|---|---|---|
| MCU | __Two__ XIAO ESP32S3, told apart by the expansion board on each — __XIAO-ESP32S3-lora__ and __XIAO-ESP32S3-cam__ | Restores a zero-firmware recovery beacon and isolates it from flight-firmware failure |
| Interconnect | __One carrier PCB__ on the sled's centre plane, parts on both faces, 1.0 mm FR4, 4-layer, __24 × 95 mm__ | A XIAO stack is 15 mm tall, which no 11 mm face channel holds |
| XIAO-ESP32S3-lora firmware | __Stock Meshtastic__, pre-flashed by Seeed. No code written | The Wio-SX1262 + XIAO ESP32S3 kit is a supported Meshtastic device out of the box |
| XIAO-ESP32S3-cam firmware | Custom — camera, sensors, PSRAM logging, Wi-Fi | Not yet started |
| Camera | __OV3660__ on the Sense expansion board — __confirmed off the ribbon 2026-09-06__, having been recorded as an OV2640 throughout | Estes AstroCam was considered and dropped |
| Barometric static port | __Dropped__ | See below |
| Apogee method | __Inertial primary__; GPS anchor by __offline timestamp merge__, not real time | The cost of putting GPS on the stock-Meshtastic board |
| Flight log storage | __Buffer in PSRAM during flight, flush after landing__ | Both flash and microSD stall the 500 Hz sampler mid-boost |
| Power | __One battery__ to a carrier JST, distributed to each XIAO's __underside BAT pads by soldered pigtail__. __Charge through one USB port at a time__ | BAT is not on the castellated edge, so it cannot come through the headers. Avoids adding a charge IC |
| Arming | __In the battery line__, not on a GPIO — and __flight 3 flies without one__ (2026-09-08). Mechanism and status: [Arming-switch.md](../hardware/Arming-switch.md) | Physically cuts power; zero pins; cuts both modules at once. Deferred rather than replaced: __nothing else takes the role__ |
| Antennas | __Both off-board on U.FL__ — GPS patch forward-facing, LoRa 82 mm whip up the ogive | A GPS patch needs a 30–40 mm ground plane; a 24 mm board never will be |

## Why two boards, after settling on one

A single board collapsed everything into one custom firmware image: DVP camera, microSD, PSRAM buffer, I2C sensors, SX1262 on non-standard pins, Wi-Fi, OTA. __No stock image does any of that__, which meant:

- first flight gated on firmware being *finished*, not merely working — the beacon __is__ the recovery system;
- a boot-loop at the pad requires removing the M3 × 55, the nose and the sled, with a laptop present, because USB is unreachable assembled and OTA needs firmware that boots;
- stock Meshtastic could not be flashed as a rescue, because the radio would be on custom pins.

Two boards restore the fallback and, as a side effect, dissolve two other problems: XIAO-ESP32S3-cam sheds LoRa (4 pads) and GPS UART (2), so __an I2C GPIO expander is no longer needed__, and XIAO-ESP32S3-cam's SPI carries only the microSD, so __a "no transmit while recording" scheduling rule is unnecessary__ — different MCU, different bus.

Two boards cost __~3 g__ against a single-MCU design, and buy the zero-firmware beacon, failure isolation, the end of pin scarcity, and the end of SPI contention.

## Why the barometric port is dropped

1. __No legal location.__ Ports need a straight section ≥1 caliber clear of any transition. Caliber is 56.7 mm; the longest straight run above the sled is the 56.7 body at __18.6 mm = 0.33 cal__.
2. __Cannot be built.__ Extending that body to a full caliber costs __+38 mm__ against __15.9 mm__ of P2S build headroom — the ogive would shorten and 3:1 fineness breaks.
3. __Unrepeatable.__ Hand-drilled into a part with no generator that takes 2 h 48 m to print.
4. __Drags a pressure bulkhead in with it__ — a new part and a new failure mode.
5. __Decisive: nothing consumes the number.__ No pyro channels; ejection is the motor delay. Apogee is data, not deployment.

A __barometer is still carried, unported and demoted__ to ejection-event timestamp and landing detection. A __contamination bulkhead__ (foam/plate, no sealing duty) still belongs at the sled base to keep black-powder particulate off the boards.

Side benefit: this frees the contested nose wall for the camera lens.

## The carrier PCB

__One board on the sled's centre plane, parts on both faces.__ This replaced an earlier "one design built twice" plan, which did not survive contact with the real XIAO footprint. The board's frozen dimensions are in the [README](../README.md); this section is why they are what they are.

### Why the twin-PCB idea died

The twin plan assumed each XIAO could sit flat on its own card, with a __cutout__ in the card to clear the expansion board underneath. Measuring KiCad's Seeed XIAO footprint (which cites Seeed's own package spec) kills that:

```text
14 pads, 3 x 2 mm
x = +/-8.5 mm       rows 17.0 mm apart, pad inner edges at +/-7.0
y = -7.62..+7.62    7 per row, 2.54 mm pitch
board 17.5 x 21 mm
```

The expansion board — Sense or Wio-SX1262 — is the __same XIAO outline, ±8.75 mm__. So the thing needing clearance is __wider than the pads are apart__. Any cutout large enough to pass the expansion board removes the copper the pads solder to. __No cutout geometry satisfies both.__

Seeed's own figure confirms the stack: __21 × 17.5 × 15 mm__ with the expansion board fitted.

### So: headers, and a centre-plane card

__The expansion board — Sense or Wio-SX1262 — mates to the XIAO's __front face__, on the B2B connector beside the U.FL socket, and sits __above__ the XIAO.__ The XIAO sits on __two 7-pin headers__, one down each long edge, onto the carrier.

__This section was right and the Population table below was wrong__, which is why they disagreed for so long. Settled 2026-09-08 against Seeed's front and back pinouts and an end-on photograph of the assembled stack — breadboard, header pins, XIAO, B2B block, expansion board, camera. See [XIAO-ESP32S3-cam.md](../hardware/XIAO-ESP32S3-cam.md#which-face-carries-what--settled-off-seeeds-two-drawings-and-the-stack-itself).

__The back face stays open__, carrying `BAT+`/`BAT−`. The expansion board never covers them; the __carrier__ does, at 2.50 mm, which is why the pigtail is soldered before the XIAO goes onto its headers.

__Measured on the assembled stacks__ — heights from the bottom of the XIAO's PCB, camera excluded, with the headers' 2.50 mm added:

```text
at the XIAO's edge (x = +/-8.75 from centre):
  available depth = sqrt(19.7^2 - 8.75^2) = 17.6 mm each side

XIAO-ESP32S3-cam  = 8.22 + 2.50 headers = 10.72 mm
XIAO-ESP32S3-lora = 9.32 + 2.50         = 11.82 mm
total             = 10.72 + 1.0 carrier + 11.82 = 23.54 mm
available         = 2 x 17.6                    = 35.30 mm     11.76 mm spare
```

> __An earlier revision of this section had the expansion board hanging __below__ the XIAO in a ~14 mm header gap, giving a 15 mm stack and 31.0 mm total.__ That is not how the parts assemble. The kit's standard 7-pin headers — ~2.50 mm standoff — are adequate, no tall stacking headers are needed, and __the bore margin is 11.8 mm rather than ~4__.

The camera hangs off the expansion board __on a flexible ribbon__, so its position is not fixed by the stack.

### Population

| Face | Carries |
|---|---|
| Top | XIAO ESP32S3 (plain) + Wio-SX1262 __above it, on its front-face B2B__; __L76K GNSS__ — in the XIAO stack, __not on the carrier__ |
| Bottom | XIAO ESP32S3 Sense + camera/microSD board beneath it; LSM6DSO32; BMP388; buzzer |
| Either | Battery JST, mounting holes. An arming switch would be inline in the battery lead and takes no footprint — __flight 3 carries none__ |

Net list is small — roughly __9 nets__: GPS TX, GPS RX, SDA, SCL, buzzer, 3V3, GND, BAT+, BAT−. The wiring table is in the [README](../README.md).

### The board could not stay 24 × 70

The two XIAOs cannot overlap in plan view. They mount on __through-hole__ headers, so the holes pass through the card, and XIAO-ESP32S3-lora uses D6/D7 for the GPS UART while XIAO-ESP32S3-cam uses D4/D5 for I2C — different nets on the same holes. They sit end to end:

```text
top face     XIAO-ESP32S3-lora 21 + GPS in the stack, not end to end    = 21 mm
bottom face  XIAO-ESP32S3-cam 21 + LSM6DSO32 25.5 + BMP388 25.5 + buzzer = 84 mm
```

At 24 mm wide against 17.8 mm sensors, no two parts sit side by side. __24 × 95 mm__, costing 1.1 g, and still inside the sled with room to spare. XIAO-ESP32S3-cam centres at carrier y = 18 mm so the camera lands at nose z 30..45.

__The bottom face sets the length.__ The top-face figure once read `XIAO-ESP32S3-lora 21 + GPS ~25 = 46 mm`, from a MAX-M10S breakout that would have sat on the carrier end to end. That part is gone and the L76K rides the XIAO stack instead, so the top face needs only its 21 mm — but 84 mm on the bottom still drives the board, so __nothing about the frozen interface moves and the sled does not reprint__.

### The GPS is an L76K, not a MAX-M10S

The MAX-M10S was rejected on 2026-08-06: **44.2 × 30.5 mm, wider than the 24 mm carrier, and ~$60**. Seeed's **L76K GNSS for XIAO (109100021)** is 18 × 21 mm, $11.99, active antenna included, and talks UART on __D6/D7__ — already the carrier's netlist.

__It plugs onto the XIAO's own 14 pads rather than presenting a header to the carrier__, so:

- __No GPS footprint is needed.__ `GPS_TX`/`GPS_RX` remain in the netlist — the same node the L76K meets in the stack — but nothing is placed for them.
- __It moves the risk from layout to stack height.__ Whether the L76K clears the Wio-SX1262 on the B2B is open, against the __11.76 mm of spare computed above__ — the L76K is *not* in that 9.32 mm figure, which is the XIAO and the radio only, so what the dry stack has to show is whether the GPS fits inside that spare. __If it cannot ride the stack it returns to the carrier as a footprint__, needing ~21 mm the 95 mm board has. Settle at the breadboard stage.

### Power, and the pigtail constraint

__BAT+/BAT− are underside pads on the XIAO__ (footprint pads 16/17, 2.3 × 1.3 mm at x = −4.5), not brought out to the castellated edge — so the battery __cannot__ reach a XIAO through the headers.

- Battery lands on a __JST-PH on the carrier__; short __soldered pigtails__ run to each XIAO's BAT pads.
- __Solder those pigtails before fitting the expansion board.__ Seeed's wiki implies the pads are inaccessible afterwards.
- __On battery power there is no voltage on the 5V pin__, so nothing can be fed from a XIAO's 5V rail.
- Both XIAO chargers sit in parallel on one battery. __Charge through one USB port at a time.__

### Arming

__Flight 3 carries no arming switch__ (operator, 2026-09-08) — see [Arming-switch.md](../hardware/Arming-switch.md). The part is deferred, not replaced, and __nothing else is promoted into the role__: power is made and broken at the battery's JST, which is a connector and stays one.

__The architecture below is what this document owns, and it has survived every revision of the mechanism__ — it is what any later flight's switch has to satisfy. The switch sits __in series in the battery line__, between the battery and the carrier's JST. It physically cuts power rather than setting a firmware state a boot-loop could defeat, it costs __zero GPIO__, and it __cuts both modules at once__ — arming is all-or-nothing, including the beacon.

__Everything else about it belongs to [Arming-switch.md](../hardware/Arming-switch.md)__ — which mechanism, what is still open, and why the reed switch, the magnet-polarity question and the MOSFET that used to live in this section are all gone. The short of it: this payload has no pyro, so an "armed" rocket here is one that is recording video, and the switch buys __turnaround, not safety__.

### RF

Both antennas leave via __U.FL on the modules themselves__ — the L76K and the Wio-SX1262 each carry their own connector — so __no RF crosses the carrier at all__. It is a purely digital and power board, which is what makes the layout tractable.

__GPS: active patch on U.FL__ at the sled's forward end, facing up, satisfying the "no metal above the patch" rule. __LoRa: U.FL to the 82 mm whip__ up the ogive. __Separate them by ≥50 mm__ — 915 MHz TX desenses a 1575 MHz front end by broadband noise, not harmonics (2 × 915 = 1830 MHz, clear of GPS).

### Build rules

- __4-layer, solid ground plane.__ A few dollars more at this size; fixes return paths and coupling from the camera's DVP flex.
- __1.0 mm FR4.__ The carrier is the sled's structural span — the printed web is only 3 mm and is *not* the structural member.
- __Module footprints, not bare chips.__ A bare LSM6DSO32 is an LGA-14 at 2.5 × 3 mm and is not hand-solderable. Soldering breakouts down still gives one rigid assembly with no flying wires — apart from the two battery pigtails, which are unavoidable.
- __Shock.__ Solder or clamp the headers — no loose sockets. Battery straps to the sled, never hangs off the JST. Conformal coat after bench testing.
- __Silkscreen which face is which__, and mark the pigtail polarity — reversing a LiPo into a XIAO destroys it.

## Data path — why the log lives in PSRAM

__The camera is not on SPI.__ The OV3660 uses a __DVP parallel bus__ (14 GPIO) plus I2C/SCCB for control, with frames landing in PSRAM by DMA. What touches SPI is *writing those frames to the microSD*.

__SD latency is unbounded.__ Cards run wear-levelling and garbage collection at will; a normally-2 ms write can take __100–250 ms__, spec-legally.

__Internal flash is worse.__ Writing ESP32 internal flash __disables the instruction cache__. A 4 KB sector erase takes ~20–40 ms, during which code executing *from* flash stalls, including ISRs not marked `IRAM_ATTR`. At 500 Hz the sample period is 2 ms, so one erase silently drops __10–20 samples__ — during boost, where the data matters most.

__So: buffer in PSRAM, flush after landing.__

```text
500 Hz x ~30 B x 60 s  =  900 KB
ESP32-S3R8 PSRAM       =  8 MB
```

The whole flight fits roughly nine times over. Zero flash writes and zero SD writes during flight; the landing detector triggers the flush.

## Sensor rationale

- __17.6 g peak on a D12.__ 32.90 N peak thrust / 0.190 kg liftoff mass. __±16 g phone-grade IMUs clip during boost__, and a clipped boost integral destroys the velocity estimate for the whole flight. This is why TeleMega carries an ADXL375, and why __LSM6DSO32 (±32 g)__ was chosen. Cost: less resolution in coast.
- __The gyro is not the apogee sensor.__ The accelerometer is. The gyro exists so body-frame acceleration can be rotated into the earth frame and gravity subtracted off the correct axis as the rocket tips over.
- __Use the IMU's FIFO — do not poll at 500 Hz.__ The LSM6DSO32 carries a 9 KB FIFO. Batch-reading cuts ISR load, relieves the PSRAM path, and means a brief stall queues samples in the sensor instead of losing them. __Treat a FIFO as a hard requirement on any substitute.__
- __The buzzer does three jobs.__ (1) Last-20-metre locator — GPS lands you in a 3–10 m circle and a white PLA rocket vanishes in tall grass at 2 m. (2) __The only status channel on the pad__ — with the nose assembled, USB is unreachable, Wi-Fi is off, and the GPIO21 LED is sealed inside, so beep patterns are the only way the rocket reports booted / armed / sensors alive. (3) Beeping apogee in digits after landing, needing no phone.
- __The buzzer is *passive*, PWM-driven from D0.__ An earlier revision specified an active self-oscillating part, because the buzzer then hung off an I2C GPIO expander where a ~3 kHz tone meant 6000 bus transactions a second. Two boards freed the pins, the expander went, and a real GPIO can PWM a passive element directly — giving __multiple tones__ rather than one, which is what makes beep patterns readable as distinct codes.
- __The buzzer is not radio redundancy__ — it shares XIAO-ESP32S3-cam's MCU. Only a self-powered beeper with its own battery (~5 g, zero pins) is immune to firmware and MCU failure. Not adopted; revisit if recovery confidence matters more than grams.
- __Sound must escape a sealed PLA cone.__ A piezo in a closed cavity loses 20–30 dB. Mount the disc __against the nose wall__ so the shell acts as a soundboard; the camera port is a free acoustic leak, and the bay is open at its base.
- __The barometer is interchangeable.__ With the static port dropped it is not the altimeter. __BMP388__ shares the BMP3xx driver so it is a drop-in for the out-of-stock BMP390, and a generic BMP280 would serve.

### IMU substitutes — the ±16 g trap

Anything with a ±16 g full scale __clips__ against the 17.6 g boost peak. That rules out almost every cheap module on the market — __MPU6050, LSM6DS3, ICM-20948, ICM-42688-P, ADXL345 are all ±16 g and all unusable here__, however attractive the price.

| Part | Range | Gyro | Note |
|---|---|---|---|
| __LSM6DSO32__ | ±32 g | yes | The chosen part. Adafruit 4692, or a clone — same STEMMA QT layout as the BMP388 |
| __BMI088__ | __±24 g__ | yes | Bosch drone/robotics part, widely stocked, ~$12. 36% margin over 17.6 g |
| __MPU6050 + ADXL375__ | ±16 g + ±200 g | yes | Two chips: one for coast and attitude, one for boost |
| __MPU6050 + H3LIS331DL__ | ±16 g + ±400 g | yes | Same split, more headroom |

The two-chip split is where this design began, before it was consolidated to a single LSM6DSO32 to save a gram. __Reverting costs +1 g and one I2C address — no extra pins.__ A cheap fallback rather than a compromise.

__Integrated 10DOF modules were evaluated and rejected.__ The DFRobot Gravity 10DOF (BMI323 + BMM350 + BMP581, $19.90) is representative: its BMI323 maxes at ±16 g. It is also 32 × 27 mm — wider than the carrier — uses a PH2.0 flying lead, and carries a magnetometer this design deliberately excludes.

## The camera, and the port it needs

> __The part is an OV3660, not an OV2640__ (confirmed 2026-09-06). The analysis below was written for a 2640 and __survives almost intact__: the OV3660's active area is 2048 × 1536 at 1.75 µm = 3.584 × 2.688 mm, a __4.480 mm__ diagonal against the 2640's 4.482 — two microns apart, the same optical format. __What would move the cone is a different focal length__, which a 3 MP module may well carry: at f 4.0 the cone is 58.5°, at f 3.6 it is 63.8°, at f 3.0 it is 73.5°.
>
> __A wider cone makes the port harder.__ At 50° the full cone already needs Ø14.2 mm outside a 15.0 mm collar; at 70° it needs Ø21.3. It was unbuildable from a board-mounted lens and it gets worse. __The standoff fix holds across the whole range__ — with the lens at r 19 the port is Ø4.9 at 50° and Ø7.3 at 70° — which is why bringing the lens to the wall was the right answer rather than a bigger hole.
>
> __Measure the cone rather than looking the lens up.__ Photograph a ruler at a known distance and compute the captured angle. That settles it for the real lens, and this project has already had one argument with a datasheet over this exact number.

__The OV2640's real FOV is ~50°, not the 65–68° commonly quoted.__ Active area diagonal is √(3.590² + 2.684²) = __4.482 mm__; with the stock __f = 4.8 mm__ lens that gives `2·atan(4.482/9.6)` = __50.1° diagonal__ (HFOV 41°, VFOV 31°). The sensor's __25° chief ray angle__ independently confirms it — a 25° half-angle *is* a 50° full cone. The 65–68° figure is inconsistent with both and should be disregarded.

Vignetting is governed by `FOV_cleared = 2·atan(D / (2·(L+S)))`, where L is wall thickness and __S is lens standoff behind the inner wall face__. Standoff, not wall thickness alone, is the constraint:

| Hole D | Standoff budget @ 50° | @ 68° (pessimistic) |
|---|---|---|
| 6 mm | 2.23 mm | 0.25 mm |
| __8 mm__ | __4.38 mm__ | __1.73 mm__ |
| 10 mm | 6.52 mm | 3.21 mm |

__8 mm it is__, and the assembly constraint that follows: keep the lens front element __within ~4.4 mm of the bore's inner face__. Where that hole may be drilled, and the rules for drilling it, are the rocket's business — [payload-bay.md](https://github.com/jwilleke/js-rocket/blob/main/docs/payload-bay.md#the-camera-port).

- __Do not fit the wide-angle lens.__ The 120–160° M7 option cannot match the 25° CRA, producing severe corner vignetting and colour crosstalk, and it would need a far larger hole in a load-bearing collar.
- __Focus is adjustable__ via the M5/M6 lens thread. Hyperfocal at f/2.8 with a ~4.4 µm circle of confusion is ~1.9 m, so everything past ~1 m is sharp.
- __Do not extend the camera flex__ — the DVP bus runs a ~20 MHz XCLK. XIAO-ESP32S3-cam's position on the carrier is what puts the XIAO at nose z 30..45 instead.

## PCB staging

Fab-ready Gerbers are the *output* of a routed board, not something authored directly.

| Stage | Deliverable | State |
|---|---|---|
| 2a | Board outline, mounting holes, stackup | __done__, DRC clean |
| 2b | Nets and footprints | __partial__ — XIAOs placed and netted, pin mapping now asserted on every generate ([#18](https://github.com/jwilleke/js-rocket-avionics/issues/18), closed `c2468eb`); sensors, buzzer, JST deferred |
| 2c | Placement — module positions, keepouts, ≥50 mm antenna separation | blocked on confirming real module pinouts |
| 2d | Routing — 4-layer. Autorouting is wrong here; needs interactive KiCad | not started |
| 2e | Gerber RS-274X + Excellon drill export | chain proven; needs a finished board |

__The PCB outline and mounting-hole pattern had to be frozen before the sled generator was written__, since the sled's rail bosses derive from them.

__Do not order copper before breadboarding.__ A layout error costs ~$33 and two weeks; a wiring error costs minutes.

### Supplier: OSH Park

| Supplier | Fit for this board |
|---|---|
| __OSH Park__ | Quoted __$26.00 for 3 copies__ of the 24 × 70 mm 4-layer board, ENIG standard, __free US shipping__, no customs. Three copies is right: two populated plus a spare. __Recommended__ |
| JLCPCB | Cheaper per unit but __minimum 5__, and shipping (~$20) erases the saving at this size. Right choice if a PCBA service is ever wanted |
| PCBWay | More flexible quoting, generally above JLCPCB's economy tier for simple SMT |

OSH Park wins because we already chose __hand-soldered module footprints__, so assembly service — JLCPCB's real advantage — buys nothing. ENIG also suits the U.FL connectors better than HASL. Trade-off: ~2 week lead versus JLCPCB express.

__Confirmed by upload, not estimated.__ OSH Park accepted the generated `.kicad_pcb` __directly__, detecting 4 layers and the outline unaided — so the Gerber export is not in the ordering path at all. The 95 mm board is 3.53 in² and should land near __$33__; re-confirm at order time.

## Firmware

__Board A needs none__ — the Seeed kit arrives pre-flashed with Meshtastic, and that is the entire premise of the two-board split.

__Board B's flight firmware does not exist yet.__ Camera, sensors, PSRAM buffering, landing detection and the post-landing flush all live there, and nothing has been written.

## Flight sequencing

Do not fly all the variables at once.

```text
flight 1   XIAO-ESP32S3-lora only, stock Meshtastic, no camera
           validates: airframe, recovery, GPS lock through PLA, LoRa range from altitude
flight 2   + XIAO-ESP32S3-cam flight recorder (sensors, PSRAM log)
flight 3   + video
```

Each flight adds one thing, and the recovery beacon is proven before anything expensive rides on it. __This is only possible because XIAO-ESP32S3-lora needs no firmware.__

## Verification

1. __Bench prototype before layout.__ Breadboard both populations. Prove XIAO-ESP32S3-lora enumerates as a Meshtastic device untouched, and that XIAO-ESP32S3-cam boots with camera, SD and I2C sensors live, with the strapping pins (GPIO3, 43, 44) behaving.
2. __Confirm the silicon matches the label__ before designing footprints round it — see [module-pinouts.md](module-pinouts.md).
3. __PCB bring-up__ — power, then XIAO-ESP32S3-lora: GPS UART and LoRa; then XIAO-ESP32S3-cam: I2C enumeration and camera. __Measure GPS lock time with the LoRa transmitting__, since desense cannot be reasoned about from a schematic.
4. __Sample-rate integrity under load__ — run XIAO-ESP32S3-cam's 500 Hz sampler with the camera recording to SD and confirm __zero dropped samples__ by checking timestamp deltas, not by trusting the loop.
5. __Shared-battery behaviour__ — confirm the camera's inrush on XIAO-ESP32S3-cam does not brown out XIAO-ESP32S3-lora, and that charging through one USB port with both BAT pads connected behaves.
6. __Buzzer audibility, assembled__ — beep inside a closed Nosecone and listen from 20 m. A sealed cavity costs 20–30 dB; couple the disc harder to the shell before considering a dedicated sound hole.
7. __Mass__ — weigh the loaded sled and hand the real number to the rocket's stability re-run, [#9](https://github.com/jwilleke/js-rocket/issues/9). __Do not fly on the estimate.__

## Risks

- __One board carries both MCUs.__ A layout bug takes the beacon and the recorder together — the cost of a single carrier. Firmware and MCU failures are still isolated; only the copper is shared.
- __No real-time GPS anchor for the inertial log.__ GPS sits on the stock-Meshtastic board, which broadcasts position at a low rate and will not set the `airborne <4g` dynamic model, so lock may drop under boost. Altitude integration is anchored by an __offline timestamp merge__, which is weaker. Cross-linking a UART would fix it and would stop XIAO-ESP32S3-lora being stock, defeating the purpose.
- __A PSRAM-only log is lost if XIAO-ESP32S3-cam resets.__ Nothing is on non-volatile media until the landing flush. A brownout, watchdog reset or hard landing costs the whole flight's telemetry while the SD video survives. Mitigate with checkpoint flushes during the low-rate descent phase, never during boost.
- __The PCB is on the critical path.__ Sled geometry derives from its outline and mounting holes, so a layout revision reprints the sled. Freeze the outline early; breadboard before committing to copper.
- __GPS desense from the LoRa transmitter__ cannot be reasoned away on paper. ≥50 mm antenna separation and both antennas on U.FL are the mitigations; verification step 3 is the proof.
- __Shared battery couples the boards.__ A camera brownout could disturb XIAO-ESP32S3-lora. Separate batteries would isolate them at +8 g, which the mass budget cannot afford.
- __A welded arming contact leaves the camera running.__ It was recorded here as "an armed rocket that cannot be safed", which is a pyro rocket's hazard and not this one's — the correction and the live constraint are in [Arming-switch.md](../hardware/Arming-switch.md).
- __Estimated masses were unreliable in both directions.__ Nine parts weighed 2026-08-17: the __L76K came in +184%__ and is now the heaviest object in the nose, while the Sense and the radio came in light. Net __+4.1 g__, putting the nose over its ~50 g target — see [BOM.md](BOM.md), which owns every weight.
- __The rocket's stability re-run ([#9](https://github.com/jwilleke/js-rocket/issues/9)) is P0 and blocking.__ This payload can be built and bench-tested now, but __it cannot be flown__ until that clears.
