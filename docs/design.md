# Design record

**Why this payload is built the way it is.** The decisions and the reasoning behind them, so the *why* survives into the work.

This project is **one candidate payload** for the js-rocket [payload bay](https://github.com/jwilleke/js-rocket/blob/main/docs/payload-bay.md). The bay's interface — 40.0 mm bore × 150 mm, an M3 × 55 retainer at nose z 15, a ~50 g mass ceiling, an optional 8 mm camera port — is the rocket's business and is not restated here beyond what constrains the design.

Related: [BOM.md](BOM.md) (parts and masses) · [shopping-list.md](shopping-list.md) (what was bought) · [module-pinouts.md](module-pinouts.md) (footprint inputs) · [README.md](../README.md) (the carrier's frozen interface)

## Decisions locked

| Decision | Value | Why |
|---|---|---|
| MCU | **Two** XIAO ESP32S3 — one plain (**A**), one **Sense** (**B**) | Restores a zero-firmware recovery beacon and isolates it from flight-firmware failure |
| Interconnect | **One carrier PCB** on the sled's centre plane, parts on both faces, 1.0 mm FR4, 4-layer, **24 × 95 mm** | A XIAO stack is 15 mm tall, which no 11 mm face channel holds |
| Board A firmware | **Stock Meshtastic**, pre-flashed by Seeed. No code written | The Wio-SX1262 + XIAO ESP32S3 kit is a supported Meshtastic device out of the box |
| Board B firmware | Custom — camera, sensors, PSRAM logging, Wi-Fi | Not yet started |
| Camera | **OV2640** on the Sense expansion board | Estes AstroCam was considered and dropped |
| Barometric static port | **Dropped** | See below |
| Apogee method | **Inertial primary**; GPS anchor by **offline timestamp merge**, not real time | The cost of putting GPS on the stock-Meshtastic board |
| Flight log storage | **Buffer in PSRAM during flight, flush after landing** | Both flash and microSD stall the 500 Hz sampler mid-boost |
| Power | **One cell** to a carrier JST, distributed to each XIAO's **underside BAT pads by soldered pigtail**. **Charge through one USB port at a time** | BAT is not on the castellated edge, so it cannot come through the headers. Avoids adding a charge IC |
| Arming | Reed switch **in the battery line**, not on a GPIO | Physically cuts power; zero pins; no hole in the nose. **Polarity and switching topology are open** — see below |
| Antennas | **Both off-board on U.FL** — GPS patch forward-facing, LoRa 82 mm whip up the ogive | A GPS patch needs a 30–40 mm ground plane; a 24 mm board never will be |

## Why two boards, after settling on one

A single board collapsed everything into one custom firmware image: DVP camera, microSD, PSRAM buffer, I2C sensors, SX1262 on non-standard pins, Wi-Fi, OTA. **No stock image does any of that**, which meant:

- first flight gated on firmware being *finished*, not merely working — the beacon **is** the recovery system;
- a boot-loop at the pad requires removing the M3 × 55, the nose and the sled, with a laptop present, because USB is unreachable assembled and OTA needs firmware that boots;
- stock Meshtastic could not be flashed as a rescue, because the radio would be on custom pins.

Two boards restore the fallback and, as a side effect, dissolve two other problems: board B sheds LoRa (4 pads) and GPS UART (2), so **an I2C GPIO expander is no longer needed**, and board B's SPI carries only the microSD, so **a "no transmit while recording" scheduling rule is unnecessary** — different MCU, different bus.

Two boards cost **~3 g** against a single-MCU design, and buy the zero-firmware beacon, failure isolation, the end of pin scarcity, and the end of SPI contention.

## Why the barometric port is dropped

1. **No legal location.** Ports need a straight section ≥1 caliber clear of any transition. Caliber is 56.7 mm; the longest straight run above the sled is the 56.7 body at **18.6 mm = 0.33 cal**.
2. **Cannot be built.** Extending that body to a full caliber costs **+38 mm** against **15.9 mm** of P2S build headroom — the ogive would shorten and 3:1 fineness breaks.
3. **Unrepeatable.** Hand-drilled into a part with no generator that takes 2 h 48 m to print.
4. **Drags a pressure bulkhead in with it** — a new part and a new failure mode.
5. **Decisive: nothing consumes the number.** No pyro channels; ejection is the motor delay. Apogee is data, not deployment.

A **barometer is still carried, unported and demoted** to ejection-event timestamp and landing detection. A **contamination bulkhead** (foam/plate, no sealing duty) still belongs at the sled base to keep black-powder particulate off the boards.

Side benefit: this frees the contested nose wall for the camera lens.

## The carrier PCB

**One board on the sled's centre plane, parts on both faces.** This replaced an earlier "one design built twice" plan, which did not survive contact with the real XIAO footprint. The board's frozen dimensions are in the [README](../README.md); this section is why they are what they are.

### Why the twin-PCB idea died

The twin plan assumed each XIAO could sit flat on its own card, with a **cutout** in the card to clear the expansion board underneath. Measuring KiCad's Seeed XIAO footprint (which cites Seeed's own package spec) kills that:

```text
14 pads, 3 x 2 mm
x = +/-8.5 mm       rows 17.0 mm apart, pad inner edges at +/-7.0
y = -7.62..+7.62    7 per row, 2.54 mm pitch
board 17.5 x 21 mm
```

The expansion board — Sense or Wio-SX1262 — is the **same XIAO outline, ±8.75 mm**. So the thing needing clearance is **wider than the pads are apart**. Any cutout large enough to pass the expansion board removes the copper the pads solder to. **No cutout geometry satisfies both.**

Seeed's own figure confirms the stack: **21 × 17.5 × 15 mm** with the expansion board fitted.

### So: tall stacking headers, and a centre-plane card

The XIAO mounts on **2×7 headers with ~14 mm standoff**, the expansion board hanging in the gap, ~**15 mm** total above the carrier. Checked against the bore:

```text
at the XIAO's edge (x = +/-8.75 from centre):
  available depth = sqrt(19.7^2 - 8.75^2) = 17.6 mm each side

two stacks + carrier = 15 + 1.0 + 15 = 31.0 mm
available            = 2 x 17.6        = 35.2 mm     fits, ~2 mm margin
```

### Population

| Face | Carries |
|---|---|
| Top | XIAO ESP32S3 (plain) + Wio-SX1262 beneath it; **L76K GNSS** — in the XIAO stack, **not on the carrier** |
| Bottom | XIAO ESP32S3 Sense + camera/microSD board beneath it; LSM6DSO32; BMP388; buzzer |
| Either | Battery JST, reed switch in the cell line, mounting holes |

Net list is small — roughly **9 nets**: GPS TX, GPS RX, SDA, SCL, buzzer, 3V3, GND, BAT+, BAT−. The wiring table is in the [README](../README.md).

### The board could not stay 24 × 70

The two XIAOs cannot overlap in plan view. They mount on **through-hole** headers, so the holes pass through the card, and XIAO A uses D6/D7 for the GPS UART while XIAO B uses D4/D5 for I2C — different nets on the same holes. They sit end to end:

```text
top face     XIAO A 21 + GPS in the stack, not end to end     = 21 mm
bottom face  XIAO B 21 + LSM6DSO32 25.5 + BMP388 25.5 + buzzer = 84 mm
```

At 24 mm wide against 17.8 mm sensors, no two parts sit side by side. **24 × 95 mm**, costing 1.1 g, and still inside the sled with room to spare. XIAO B centres at carrier y = 18 mm so the camera lands at nose z 30..45.

**The bottom face sets the length.** The top-face figure once read `XIAO A 21 + GPS ~25 = 46 mm`, from a MAX-M10S breakout that would have sat on the carrier end to end. That part is gone and the L76K rides the XIAO stack instead, so the top face needs only its 21 mm — but 84 mm on the bottom still drives the board, so **nothing about the frozen interface moves and the sled does not reprint**.

### The GPS is an L76K, not a MAX-M10S

The MAX-M10S was rejected on 2026-08-06: **44.2 × 30.5 mm, wider than the 24 mm carrier, and ~$60**. Seeed's **L76K GNSS for XIAO (109100021)** is 18 × 21 mm, $11.99, active antenna included, and talks UART on **D6/D7** — already the carrier's netlist.

**It plugs onto the XIAO's own 14 pads rather than presenting a header to the carrier**, so:

- **No GPS footprint is needed.** `GPS_TX`/`GPS_RX` remain in the netlist — the same node the L76K meets in the stack — but nothing is placed for them.
- **It moves the risk from layout to stack height.** Whether the L76K clears the Wio-SX1262 on the B2B is open, against the ~2 mm of bore margin computed above. **If it cannot ride the stack it returns to the carrier as a footprint**, needing ~21 mm the 95 mm board has. Settle at the breadboard stage.

### Power, and the pigtail constraint

**BAT+/BAT− are underside pads on the XIAO** (footprint pads 16/17, 2.3 × 1.3 mm at x = −4.5), not brought out to the castellated edge — so the cell **cannot** reach a XIAO through the headers.

- Cell lands on a **JST-PH on the carrier**; short **soldered pigtails** run to each XIAO's BAT pads.
- **Solder those pigtails before fitting the expansion board.** Seeed's wiki implies the pads are inaccessible afterwards.
- **On battery power there is no voltage on the 5V pin**, so nothing can be fed from a XIAO's 5V rail.
- Both XIAO chargers sit in parallel on one cell. **Charge through one USB port at a time.**

### Arming — the reed switch, and two things not yet decided

**The problem it solves is access, not convenience.** Once the nose is assembled there is no way in: USB is unreachable, Wi-Fi is off, and the status LED is sealed inside. A slide switch would need another hand-drilled hole in a part with no generator. A reed switch responds to a magnet **through** the PLA, so the switch lives inside and the magnet stays outside — no hole, no connector, no pin.

It sits **in series in the battery line**, between the cell and the carrier's JST. That means it **physically cuts power** rather than setting a firmware state a boot-loop could defeat, it costs **zero GPIO**, and it **cuts both boards at once** — arming is all-or-nothing, including the beacon.

> **OPEN 1 — polarity. Does the magnet arm or safe?** Not decided, and it inverts the field procedure and the part number.
>
> **Normally-closed, magnet safes** is the standard model-rocket pattern and the one to adopt unless there is a reason not to: a magnet taped to the nose holds the contacts open, and pulling it off at the pad arms the rocket. It **fails safe**, and the magnet doubles as a visible remove-before-flight tag. The alternative — normally-open, magnet arms — would need the magnet held on for the whole flight and is unworkable.
>
> **This decides what to order.** Normally-closed reeds are much less common than normally-open, so a switch bought before this is settled is likely to be the wrong one. It is currently an unordered ~$2 part with an unspecified type.
>
> **OPEN 2 — contact rating against camera inrush.** A typical small reed switches around **0.5 A**. Steady draw is ~300 mA, which is comfortable. **The OV2640 powering up is the question**: reed contacts are small and can weld under inrush, and **a welded reed is an armed rocket that cannot be safed** — which is the failure mode that matters, because it happens on the pad with people nearby.
>
> **The fix is standard and cheap: let the reed switch a MOSFET rather than the load.** The reed carries milliamps into the gate; the FET carries the current. One extra part, and the concern disappears. Decide this before the carrier is routed, since it adds a footprint.

**Both are unresolved.** The decision recorded in the table above — *reed switch in the battery line, not on a GPIO* — is the architecture. Neither the part type nor the switching topology follows from it.

### RF

Both antennas leave via **U.FL on the modules themselves** — the L76K and the Wio-SX1262 each carry their own connector — so **no RF crosses the carrier at all**. It is a purely digital and power board, which is what makes the layout tractable.

**GPS: active patch on U.FL** at the sled's forward end, facing up, satisfying the "no metal above the patch" rule. **LoRa: U.FL to the 82 mm whip** up the ogive. **Separate them by ≥50 mm** — 915 MHz TX desenses a 1575 MHz front end by broadband noise, not harmonics (2 × 915 = 1830 MHz, clear of GPS).

### Build rules

- **4-layer, solid ground plane.** A few dollars more at this size; fixes return paths and coupling from the camera's DVP flex.
- **1.0 mm FR4.** The carrier is the sled's structural span — the printed web is only 3 mm and is *not* the structural member.
- **Module footprints, not bare chips.** A bare LSM6DSO32 is an LGA-14 at 2.5 × 3 mm and is not hand-solderable. Soldering breakouts down still gives one rigid assembly with no flying wires — apart from the two battery pigtails, which are unavoidable.
- **Shock.** Solder or clamp the headers — no loose sockets. Battery straps to the sled, never hangs off the JST. Conformal coat after bench testing.
- **Silkscreen which face is which**, and mark the pigtail polarity — reversing a LiPo into a XIAO destroys it.

## Data path — why the log lives in PSRAM

**The camera is not on SPI.** The OV2640 uses a **DVP parallel bus** (14 GPIO) plus I2C/SCCB for control, with frames landing in PSRAM by DMA. What touches SPI is *writing those frames to the microSD*.

**SD latency is unbounded.** Cards run wear-levelling and garbage collection at will; a normally-2 ms write can take **100–250 ms**, spec-legally.

**Internal flash is worse.** Writing ESP32 internal flash **disables the instruction cache**. A 4 KB sector erase takes ~20–40 ms, during which code executing *from* flash stalls, including ISRs not marked `IRAM_ATTR`. At 500 Hz the sample period is 2 ms, so one erase silently drops **10–20 samples** — during boost, where the data matters most.

**So: buffer in PSRAM, flush after landing.**

```text
500 Hz x ~30 B x 60 s  =  900 KB
ESP32-S3R8 PSRAM       =  8 MB
```

The whole flight fits roughly nine times over. Zero flash writes and zero SD writes during flight; the landing detector triggers the flush.

## Sensor rationale

- **17.6 g peak on a D12.** 32.90 N peak thrust / 0.190 kg liftoff mass. **±16 g phone-grade IMUs clip during boost**, and a clipped boost integral destroys the velocity estimate for the whole flight. This is why TeleMega carries an ADXL375, and why **LSM6DSO32 (±32 g)** was chosen. Cost: less resolution in coast.
- **The gyro is not the apogee sensor.** The accelerometer is. The gyro exists so body-frame acceleration can be rotated into the earth frame and gravity subtracted off the correct axis as the rocket tips over.
- **Use the IMU's FIFO — do not poll at 500 Hz.** The LSM6DSO32 carries a 9 KB FIFO. Batch-reading cuts ISR load, relieves the PSRAM path, and means a brief stall queues samples in the sensor instead of losing them. **Treat a FIFO as a hard requirement on any substitute.**
- **The buzzer does three jobs.** (1) Last-20-metre locator — GPS lands you in a 3–10 m circle and a white PLA rocket vanishes in tall grass at 2 m. (2) **The only status channel on the pad** — with the nose assembled, USB is unreachable, Wi-Fi is off, and the GPIO21 LED is sealed inside, so beep patterns are the only way the rocket reports booted / armed / sensors alive. (3) Beeping apogee in digits after landing, needing no phone.
- **The buzzer is *passive*, PWM-driven from D0.** An earlier revision specified an active self-oscillating part, because the buzzer then hung off an I2C GPIO expander where a ~3 kHz tone meant 6000 bus transactions a second. Two boards freed the pins, the expander went, and a real GPIO can PWM a passive element directly — giving **multiple tones** rather than one, which is what makes beep patterns readable as distinct codes.
- **The buzzer is not radio redundancy** — it shares board B's MCU. Only a self-powered beeper with its own cell (~5 g, zero pins) is immune to firmware and MCU failure. Not adopted; revisit if recovery confidence matters more than grams.
- **Sound must escape a sealed PLA cone.** A piezo in a closed cavity loses 20–30 dB. Mount the disc **against the nose wall** so the shell acts as a soundboard; the camera port is a free acoustic leak, and the bay is open at its base.
- **The barometer is interchangeable.** With the static port dropped it is not the altimeter. **BMP388** shares the BMP3xx driver so it is a drop-in for the out-of-stock BMP390, and a generic BMP280 would serve.

### IMU substitutes — the ±16 g trap

Anything with a ±16 g full scale **clips** against the 17.6 g boost peak. That rules out almost every cheap module on the market — **MPU6050, LSM6DS3, ICM-20948, ICM-42688-P, ADXL345 are all ±16 g and all unusable here**, however attractive the price.

| Part | Range | Gyro | Note |
|---|---|---|---|
| **LSM6DSO32** | ±32 g | yes | The chosen part. Adafruit 4692, or a clone — same STEMMA QT layout as the BMP388 |
| **BMI088** | **±24 g** | yes | Bosch drone/robotics part, widely stocked, ~$12. 36% margin over 17.6 g |
| **MPU6050 + ADXL375** | ±16 g + ±200 g | yes | Two chips: one for coast and attitude, one for boost |
| **MPU6050 + H3LIS331DL** | ±16 g + ±400 g | yes | Same split, more headroom |

The two-chip split is where this design began, before it was consolidated to a single LSM6DSO32 to save a gram. **Reverting costs +1 g and one I2C address — no extra pins.** A cheap fallback rather than a compromise.

**Integrated 10DOF modules were evaluated and rejected.** The DFRobot Gravity 10DOF (BMI323 + BMM350 + BMP581, $19.90) is representative: its BMI323 maxes at ±16 g. It is also 32 × 27 mm — wider than the carrier — uses a PH2.0 flying lead, and carries a magnetometer this design deliberately excludes.

## The camera, and the port it needs

**The OV2640's real FOV is ~50°, not the 65–68° commonly quoted.** Active area diagonal is √(3.590² + 2.684²) = **4.482 mm**; with the stock **f = 4.8 mm** lens that gives `2·atan(4.482/9.6)` = **50.1° diagonal** (HFOV 41°, VFOV 31°). The sensor's **25° chief ray angle** independently confirms it — a 25° half-angle *is* a 50° full cone. The 65–68° figure is inconsistent with both and should be disregarded.

Vignetting is governed by `FOV_cleared = 2·atan(D / (2·(L+S)))`, where L is wall thickness and **S is lens standoff behind the inner wall face**. Standoff, not wall thickness alone, is the constraint:

| Hole D | Standoff budget @ 50° | @ 68° (pessimistic) |
|---|---|---|
| 6 mm | 2.23 mm | 0.25 mm |
| **8 mm** | **4.38 mm** | **1.73 mm** |
| 10 mm | 6.52 mm | 3.21 mm |

**8 mm it is**, and the assembly constraint that follows: keep the lens front element **within ~4.4 mm of the bore's inner face**. Where that hole may be drilled, and the rules for drilling it, are the rocket's business — [payload-bay.md](https://github.com/jwilleke/js-rocket/blob/main/docs/payload-bay.md#the-camera-port).

- **Do not fit the wide-angle lens.** The 120–160° M7 option cannot match the 25° CRA, producing severe corner vignetting and colour crosstalk, and it would need a far larger hole in a load-bearing collar.
- **Focus is adjustable** via the M5/M6 lens thread. Hyperfocal at f/2.8 with a ~4.4 µm circle of confusion is ~1.9 m, so everything past ~1 m is sharp.
- **Do not extend the camera flex** — the DVP bus runs a ~20 MHz XCLK. Board B's position on the carrier is what puts the XIAO at nose z 30..45 instead.

## PCB staging

Fab-ready Gerbers are the *output* of a routed board, not something authored directly.

| Stage | Deliverable | State |
|---|---|---|
| 2a | Board outline, mounting holes, stackup | **done**, DRC clean |
| 2b | Nets and footprints | **partial** — XIAOs placed and netted; sensors, buzzer, JST deferred |
| 2c | Placement — module positions, keepouts, ≥50 mm antenna separation | blocked on confirming real module pinouts |
| 2d | Routing — 4-layer. Autorouting is wrong here; needs interactive KiCad | not started |
| 2e | Gerber RS-274X + Excellon drill export | chain proven; needs a finished board |

**The PCB outline and mounting-hole pattern had to be frozen before the sled generator was written**, since the sled's rail bosses derive from them.

**Do not order copper before breadboarding.** A layout error costs ~$33 and two weeks; a wiring error costs minutes.

### Supplier: OSH Park

| Supplier | Fit for this board |
|---|---|
| **OSH Park** | Quoted **$26.00 for 3 copies** of the 24 × 70 mm 4-layer board, ENIG standard, **free US shipping**, no customs. Three copies is right: two populated plus a spare. **Recommended** |
| JLCPCB | Cheaper per unit but **minimum 5**, and shipping (~$20) erases the saving at this size. Right choice if a PCBA service is ever wanted |
| PCBWay | More flexible quoting, generally above JLCPCB's economy tier for simple SMT |

OSH Park wins because we already chose **hand-soldered module footprints**, so assembly service — JLCPCB's real advantage — buys nothing. ENIG also suits the U.FL connectors better than HASL. Trade-off: ~2 week lead versus JLCPCB express.

**Confirmed by upload, not estimated.** OSH Park accepted the generated `.kicad_pcb` **directly**, detecting 4 layers and the outline unaided — so the Gerber export is not in the ordering path at all. The 95 mm board is 3.53 in² and should land near **$33**; re-confirm at order time.

## Firmware

**Board A needs none** — the Seeed kit arrives pre-flashed with Meshtastic, and that is the entire premise of the two-board split.

**Board B's flight firmware does not exist yet.** Camera, sensors, PSRAM buffering, landing detection and the post-landing flush all live there, and nothing has been written.

## Flight sequencing

Do not fly all the variables at once.

```text
flight 1   board A only, stock Meshtastic, no camera
           validates: airframe, recovery, GPS lock through PLA, LoRa range from altitude
flight 2   + board B flight recorder (sensors, PSRAM log)
flight 3   + video
```

Each flight adds one thing, and the recovery beacon is proven before anything expensive rides on it. **This is only possible because board A needs no firmware.**

## Verification

1. **Bench prototype before layout.** Breadboard both populations. Prove board A enumerates as a Meshtastic device untouched, and that board B boots with camera, SD and I2C sensors live, with the strapping pins (GPIO3, 43, 44) behaving.
2. **Confirm the silicon matches the label** before designing footprints round it — see [module-pinouts.md](module-pinouts.md).
3. **PCB bring-up** — power, then board A: GPS UART and LoRa; then board B: I2C enumeration and camera. **Measure GPS lock time with the LoRa transmitting**, since desense cannot be reasoned about from a schematic.
4. **Sample-rate integrity under load** — run board B's 500 Hz sampler with the camera recording to SD and confirm **zero dropped samples** by checking timestamp deltas, not by trusting the loop.
5. **Shared-cell behaviour** — confirm the camera's inrush on board B does not brown out board A, and that charging through one USB port with both BAT pads connected behaves.
6. **Buzzer audibility, assembled** — beep inside a closed Nosecone and listen from 20 m. A sealed cavity costs 20–30 dB; couple the disc harder to the shell before considering a dedicated sound hole.
7. **Mass** — weigh the loaded sled and hand the real number to the rocket's stability re-run, [#9](https://github.com/jwilleke/js-rocket/issues/9). **Do not fly on the estimate.**

## Risks

- **One board carries both MCUs.** A layout bug takes the beacon and the recorder together — the cost of a single carrier. Firmware and MCU failures are still isolated; only the copper is shared.
- **No real-time GPS anchor for the inertial log.** GPS sits on the stock-Meshtastic board, which broadcasts position at a low rate and will not set the `airborne <4g` dynamic model, so lock may drop under boost. Altitude integration is anchored by an **offline timestamp merge**, which is weaker. Cross-linking a UART would fix it and would stop board A being stock, defeating the purpose.
- **A PSRAM-only log is lost if board B resets.** Nothing is on non-volatile media until the landing flush. A brownout, watchdog reset or hard landing costs the whole flight's telemetry while the SD video survives. Mitigate with checkpoint flushes during the low-rate descent phase, never during boost.
- **The PCB is on the critical path.** Sled geometry derives from its outline and mounting holes, so a layout revision reprints the sled. Freeze the outline early; breadboard before committing to copper.
- **GPS desense from the LoRa transmitter** cannot be reasoned away on paper. ≥50 mm antenna separation and both antennas on U.FL are the mitigations; verification step 3 is the proof.
- **Shared cell couples the boards.** A camera brownout could disturb board A. Separate cells would isolate them at +8 g, which the mass budget cannot afford.
- **A welded reed switch is an armed rocket that cannot be safed.** Contacts are small and the camera's inrush is unquantified; the mitigation is to switch a MOSFET rather than the load. Unresolved — see [Arming](#arming--the-reed-switch-and-two-things-not-yet-decided).
- **Estimated masses run heavy.** The first estimate replaced by a scale came in **80% over** — see [BOM.md](BOM.md).
- **The rocket's stability re-run ([#9](https://github.com/jwilleke/js-rocket/issues/9)) is P0 and blocking.** This payload can be built and bench-tested now, but **it cannot be flown** until that clears.
