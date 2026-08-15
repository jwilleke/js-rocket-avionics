# Arming and access — brainstorm, 2026-08-15

**Working notes, not decisions.** Nothing here supersedes [design.md](../design.md) until it is moved there deliberately. Recorded because the session that produced it covered ground that would otherwise be lost, and because one item **replaces an architecture** rather than adjusting it.

**Context that drove all of it:** the rocket repo now states the objective as [a rapidly reusable rocket flown by a 14-year-old](https://github.com/jwilleke/js-rocket/blob/main/README.md#what-it-is-for). Anything resting on a judgement call — *is this tape tight enough, did the magnet actuate?* — is worse than something that is either seated or not.

---

## 1. The big one: replace the reed switch with a removable plug

**`design.md` settles arming as a reed switch in the battery line, magnet through the PLA. This proposes replacing it with a physical key.**

**A switched 3.5 mm jack does the job natively.** Standard panel-mount switched jacks carry a normalled contact that is **closed with no plug inserted and opens when a plug goes in**:

- **Plug in → circuit broken → SAFE**
- **Plug out → circuit closed → ARMED**

**The plug carries no wires.** It is a dummy — a physical key with the remove-before-flight flag tied to it.

### What it dissolves rather than answers

| Reed problem | With a plug |
|---|---|
| Magnet orientation is critical — same magnet, wrong axis, no actuation | Gone |
| Carrier sits on the centre plane of a 40 mm bore, so ~20 mm of field gap | Gone |
| 32 g steel ballast nut distorting the field | Gone |
| **Welded contacts = an armed rocket that cannot be safed** | **Gone** — a plug physically breaks the circuit |
| Needs a MOSFET so the reed does not carry camera inrush | **Gone** — a jack's contacts handle amps |
| Armed state is invisible | **Visible and tactile** |
| No confirmation it actuated | You feel it seat |

**Both open questions in [design.md § Arming](../design.md) — NC vs NO, and reed-switches-a-MOSFET — stop existing.** That is the strongest argument for it.

### What it costs

- **It needs a hole.** No hole was the reed's entire justification. **But a hole is already being considered for USB-C** (§3), so the marginal cost is small.
- **The plug must be tethered.** Losing it means no way to safe the rocket.
- **It protrudes into the bore.** A jack body is ~12–14 mm in a 40 mm bore **with the recovery cord running through it** — a hard edge where bungee whips past at ejection. Slimmer than USB-C, but not nothing.

### If the reed is kept anyway

Recorded because it constrains carrier layout and is currently unwritten:

- **Edge-mount the reed**, hard against the bore wall. Mid-board is ~20 mm from the wall plus PLA, against a typical reed actuation range of 10–25 mm. Edge-mounting roughly halves the gap.
- **Key the magnet pocket for orientation** so it cannot be inserted wrong, and align the reed's long axis with it.
- **Normally-closed, magnet safes** — then the magnet *is* the RBF tag, and armed state is visible from ten feet.
- **Chirp the buzzer on arm.** The PS1240 is already in the BOM. Without it, arming is an invisible act with no feedback, and a reed that failed to actuate reads identically to a flat battery.
- **Keep the reed aft**, away from the ballast nut.

---

## 2. The sled's D-flat is a ready-made cable conduit

**The flat takes 20% off the disc height, leaving a segment roughly 8 mm deep and 31 mm wide running the sled's full 134 mm.**

That is a clear route from the carrier, past the sled, down to the PayloadAdapter — for an arming plug, a USB port, or both. **It exists for printability, not for this**, so it costs nothing.

---

## 3. Post-assembly access — the problem the reed does not solve

Tracked as [#1](https://github.com/jwilleke/js-rocket-avionics/issues/1). Summary: **arming is one of four things that need reaching after the nose is closed**, and it is the only one solved.

| Need | Solved |
|---|---|
| Arm / safe | **Yes** |
| Charge the battery | No |
| Get flight data off | No |
| See status / confirm it is alive | No |

**And the way out is expensive**: the M3 × 55 joint pin pins the Nosecone, anchors the recovery cord *and* retains the payload, so pulling the sled releases the recovery train.

**A USB-C port would solve three of the four at once.**

---

## 4. Where a port can physically go — measured, 2026-08-15

Probed off `payload-adapter.stl`. The adapter is 70 mm long and **most of it is buried**:

| Adapter z | What |
|---|---|
| 0–30 | Tenon, 39.77 OD — **inside the Tube** |
| 30–53 | **Exposed**, 44.40 OD, 40 mm bore, ~2.2 mm wall |
| 53.2–70 | Socket, 44.40 ID — **filled by the Nosecone tenon** |

**Usable exposed band: about 13 mm** (z 40–53).

### Consequences

- **A 12 mm round hole does not fit.** A [12 mm lightsaber USB-C adapter](https://www.saberbay.com/products/usb-c-port-adapter-for-12mm-switch-holes) in a 13 mm band leaves half a millimetre either side. **A bare USB-C aperture is ~9 × 3.2 mm and fits** with the long axis circumferential — model it rather than adapt a hole size chosen for lightsaber hilts.
- **A 3.5 mm jack needs ~6 mm** and fits comfortably.
- **The adapter has a generator (`gen-payload-adapter.py`); the Nosecone does not** ([js-rocket#27](https://github.com/jwilleke/js-rocket/issues/27)). Apertures there can be **modelled**; in the Nosecone they are hand-cut into 29,000 triangles.

### The trade nobody had stated

| | PayloadAdapter | Nosecone |
|---|---|---|
| Modelled or hand-cut | **Modelled** | Hand-drilled |
| Room | 13 mm band, workable | Plenty |
| **Recovery cord path** | **Runs right through it** | **Clear** — cord only exists below the joint pin |
| Wire run from the sled | Crosses the joint pin, so unplug it to pull the sled | None — the sled is in that bay |

**The Nosecone is harder to cut and structurally clear. The adapter is easier to cut and sits in the cord's way.**

---

## 5. What to measure before any of this is decided

**Time a full sled cycle on the bench**: pin out, sled out, sled in, pin in, cord re-rigged, nut back on.

**That number decides whether any of this is worth building.** If a swap is two minutes, the access problem is not a problem and the reed can stay. If it is a re-rig every flight, the architecture is fighting the objective. **Nobody has the number, and everything above is speculation until it exists.**
