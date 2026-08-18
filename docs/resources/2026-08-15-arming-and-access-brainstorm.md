# Arming and access — brainstorm, 2026-08-15

__Working notes, not decisions.__ Nothing here supersedes [design.md](../design.md) until it is moved there deliberately. Recorded because the session that produced it covered ground that would otherwise be lost, and because one item __replaces an architecture__ rather than adjusting it.

__Context that drove all of it:__ the rocket repo now states the objective as [a rapidly reusable rocket flown by a 14-year-old](https://github.com/jwilleke/js-rocket/blob/main/README.md#what-it-is-for). Anything resting on a judgement call — *is this tape tight enough, did the magnet actuate?* — is worse than something that is either seated or not.

---

## 0. Where this landed — pull-pin and a microswitch

__Direction chosen 2026-08-15: a pin / pull-tab holding a subminiature snap-action microswitch.__ Pin in, plunger held, circuit open, __SAFE__. Pin out, plunger releases, circuit closed, __ARMED__. Remove-before-flight streamer on the pin.

It beats both the reed (§1) and the jack (§1) on the constraint measured in §4:

| | Hole | Intrusion into the cord path |
|---|---|---|
| USB-C aperture | 9 × 3.2 mm | ~5 mm |
| 3.5 mm jack | ~6 mm | 12–14 mm |
| __Pull-pin + microswitch__ | __~2–3 mm__ | __a few mm__ |

- __Snap action gives defined make/break with no chatter__, and avoids the oxidation that plagues DIY leaf contacts.
- __Many subminiature microswitches are rated 3–5 A__, above the ~300 mA steady draw and the camera inrush, so __the pin may switch the load directly__.
- __The pin is a printed rod with no mechanism.__ Unlike a twist-key it does not depend on printed tolerances — which matters here, because __this project has abandoned two printed mechanisms already__: the Nosecone's bayonet lug (removed at v7.0.0) and printed snap fingers for the motor hook (three attempts, 865 / 591 / 6 non-manifold edges).
- __Radial mounting already satisfies the G-force rule.__ A port in the adapter's side puts a ~12 g launch acceleration perpendicular to the pin's axis, so it cannot be pulled out. __Stated explicitly so nobody later "improves" it into an axial plug in the nose tip.__

> ### Blocker nobody had noticed: the sled can rotate
>
> __This applies to the pin, the jack and USB-C equally.__ The pin arrives radially at one fixed azimuth, but the sled is held by __four crush ribs that centre it and do not clock it__. Nothing fixes its rotation in the bore, so __the microswitch could end up anywhere on the circle relative to the hole.__
>
> Three ways out, none chosen:
>
> 1. __Key the sled rotationally__ — its __D-flat already exists__, and a matching flat or rib in the Nosecone bore would clock it. Costs geometry on a part with no generator.
> 2. __Mount the switch to the airframe__, reached by a flying lead. Always aligned, but the lead must disconnect to pull the sled.
> 3. __Make the contact azimuth-independent__ — a ring or circumferential contact. More design, no keying.
>
> __This decides whether the fix lands on the sled, the Nosecone or the carrier, so it wants settling before anything is cut.__

## 1. Superseded proposal: replace the reed switch with a removable plug

__Kept for the reasoning, which still applies. The jack is no longer the proposal — see §0.__

__`design.md` settles arming as a reed switch in the battery line, magnet through the PLA. This proposes replacing it with a physical key.__

__A switched 3.5 mm jack does the job natively.__ Standard panel-mount switched jacks carry a normalled contact that is __closed with no plug inserted and opens when a plug goes in__:

- __Plug in → circuit broken → SAFE__
- __Plug out → circuit closed → ARMED__

__The plug carries no wires.__ It is a dummy — a physical key with the remove-before-flight flag tied to it.

### What it dissolves rather than answers

| Reed problem | With a plug |
|---|---|
| Magnet orientation is critical — same magnet, wrong axis, no actuation | Gone |
| Carrier sits on the centre plane of a 40 mm bore, so ~20 mm of field gap | Gone |
| 32 g steel ballast nut distorting the field | Gone |
| __Welded contacts = an armed rocket that cannot be safed__ | __Gone__ — a plug physically breaks the circuit |
| Needs a MOSFET so the reed does not carry camera inrush | __Not gone — this was wrong.__ See the correction below |
| Armed state is invisible | __Visible and tactile__ |
| No confirmation it actuated | You feel it seat |

> __Correction — only one of the two dissolves.__ This section originally claimed a jack's contacts "handle amps" and that both open questions in [design.md § Arming](../design.md) stop existing. __The tip and sleeve conductors carry current, but the normalled switch contact — the one that does the arming — is signal-rated, typically around 0.5 A__, the same order as a reed. __NC vs NO dissolves; the MOSFET does not.__ A __microswitch__ rated 3–5 A is what actually removes it (§0), by a different route.

__Chatter is a better argument against the reed than welding.__ With normally-closed / magnet-safes the reed sits __closed in flight__, so vibration or landing impact can momentarily open it and brown out both boards mid-flight. __Welding is a pad-safety problem; chatter is a data-loss problem, and it happens every flight or not at all.__ A latching circuit fixes it — another part.

### What it costs

- __It needs a hole.__ No hole was the reed's entire justification. __But a hole is already being considered for USB-C__ (§3), so the marginal cost is small.
- __The plug must be tethered.__ Losing it means no way to safe the rocket.
- __It protrudes into the bore.__ A jack body is ~12–14 mm in a 40 mm bore __with the recovery cord running through it__ — a hard edge where bungee whips past at ejection. Slimmer than USB-C, but not nothing.

### If the reed is kept anyway

Recorded because it constrains carrier layout and is currently unwritten:

- __Edge-mount the reed__, hard against the bore wall. Mid-board is ~20 mm from the wall plus PLA, against a typical reed actuation range of 10–25 mm. Edge-mounting roughly halves the gap.
- __Key the magnet pocket for orientation__ so it cannot be inserted wrong, and align the reed's long axis with it.
- __Normally-closed, magnet safes__ — then the magnet *is* the RBF tag, and armed state is visible from ten feet.
- __Chirp the buzzer on arm.__ The PS1240 is already in the BOM. Without it, arming is an invisible act with no feedback, and a reed that failed to actuate reads identically to a flat battery.
- __Keep the reed aft__, away from the ballast nut.

---

## 2. The sled's D-flat is a ready-made cable conduit

__The flat takes 20% off the disc height, leaving a segment roughly 8 mm deep and 31 mm wide running the sled's full 134 mm.__

That is a clear route from the carrier, past the sled, down to the PayloadAdapter — for an arming plug, a USB port, or both. __It exists for printability, not for this__, so it costs nothing.

---

## 3. Post-assembly access — the problem the reed does not solve

Tracked as [#1](https://github.com/jwilleke/js-rocket-avionics/issues/1). Summary: __arming is one of four things that need reaching after the nose is closed__, and it is the only one solved.

| Need | Solved |
|---|---|
| Arm / safe | __Yes__ |
| Charge the battery | No |
| Get flight data off | No |
| See status / confirm it is alive | No |

__And the way out is expensive__: the M3 × 55 joint pin pins the Nosecone, anchors the recovery cord *and* retains the payload, so pulling the sled releases the recovery train.

__A USB-C port would solve three of the four at once.__

---

## 4. Where a port can physically go — measured, 2026-08-15

Probed off `payload-adapter.stl`. The adapter is 70 mm long and __most of it is buried__:

| Adapter z | What |
|---|---|
| 0–30 | Tenon, 39.77 OD — __inside the Tube__ |
| 30–53 | __Exposed__, 44.40 OD, 40 mm bore, ~2.2 mm wall |
| 53.2–70 | Socket, 44.40 ID — __filled by the Nosecone tenon__ |

__Usable exposed band: about 13 mm__ (z 40–53).

### Consequences

- __A 12 mm round hole does not fit.__ A [12 mm lightsaber USB-C adapter](https://www.saberbay.com/products/usb-c-port-adapter-for-12mm-switch-holes) in a 13 mm band leaves half a millimetre either side. __A bare USB-C aperture is ~9 × 3.2 mm and fits__ with the long axis circumferential — model it rather than adapt a hole size chosen for lightsaber hilts.
- __A 3.5 mm jack needs ~6 mm__ and fits comfortably.
- __The adapter has a generator (`gen-payload-adapter.py`); the Nosecone does not__ ([js-rocket#27](https://github.com/jwilleke/js-rocket/issues/27)). Apertures there can be __modelled__; in the Nosecone they are hand-cut into 29,000 triangles.

### The trade nobody had stated

| | PayloadAdapter | Nosecone |
|---|---|---|
| Modelled or hand-cut | __Modelled__ | Hand-drilled |
| Room | 13 mm band, workable | Plenty |
| __Recovery cord path__ | __Runs right through it__ | __Clear__ — cord only exists below the joint pin |
| Wire run from the sled | Crosses the joint pin, so unplug it to pull the sled | None — the sled is in that bay |

__The Nosecone is harder to cut and structurally clear. The adapter is easier to cut and sits in the cord's way.__

---

## 5. What to measure before any of this is decided

__Time a full sled cycle on the bench__: pin out, sled out, sled in, pin in, cord re-rigged, nut back on.

__That number decides whether any of this is worth building.__ If a swap is two minutes, the access problem is not a problem and the reed can stay. If it is a re-rig every flight, the architecture is fighting the objective. __Nobody has the number, and everything above is speculation until it exists.__
