# LiPo battery

__One battery feeds both MCUs.__ Over an hour against a ~300 mA draw.

## The part

| | |
|---|---|
| Body | __29 × 36 × 4.75 mm__ — verified against the part, 2026-09-07 |
| Mass | __10.9 g__ with its pigtail — weighed. Adafruit's label says 10.5 |
| Leads | __80 mm__ measured, JST-PH. Adafruit's page says 102 — __the 80 is what governs__, and it is the number the JST's position on the carrier is set by |
| Output | 500 mAh at 3.7 V nominal |
| Vendor | [Adafruit 1578](https://www.adafruit.com/product/1578) |

__It is the largest single object in the nose__, and until 2026-09-07 this page recorded no dimension at all, so nothing about packaging could be settled.

### Where it goes — OPEN. Two candidates, neither chosen

__Nothing here is decided.__ Both positions below are live as of 2026-09-07 and the arithmetic for each is recorded so the choice can be made on numbers. The two differ on __access versus stability__, and they pull opposite ways.

#### Candidate A — on the carrier's top face, inside the Nosecone

The face carries only XIAO-ESP32S3-lora's 21 mm of the carrier's 95, so __74.0 mm is clear__. A 29 mm wide object has __13.34 mm__ of radial room from the centre plane; the battery needs 0.5 + 4.75 = __5.25__, against the lora stack's 12.32. It sits alongside, not on top of anything.

- __Keeps the mass forward__, at station ~184–220, which is where the stability case wants it
- __29 mm wide on a 24 mm web__ means 2.5 mm of overhang each side. The straps carry it, but the battery is wider than the thing it straps to
- __Costs access.__ Changing the battery means pulling the sled: out comes the M3 × 55, off comes the nose, and the sled is pushed out from below with a rod — which re-cycles the rib crush, disturbs the 8.5 mm camera ribbon and loses the camera's aim. That is the complaint in [#1](https://github.com/jwilleke/js-rocket-avionics/issues/1)

#### Candidate B — in the PayloadAdapter's bore, below the nose joint

About __adapter z 2..38__ — nose z −38..−2, station __242..278__ from the tip. __It fits with room to spare__: the adapter's bore is __Ø35.75__ over adapter z 0..30, opening to Ø39.98 at z 34..40, so a 29 mm wide slab has __20.91 mm__ of thickness available against the battery's 4.75, and the 36 mm length sits inside the ~40 mm of clear bore below the Nosecone's tenon.

- __Buys the access outright.__ Pull the nose, unclip the JST, battery out, __sled untouched__ — [#1](https://github.com/jwilleke/js-rocket-avionics/issues/1) answered rather than mitigated
- __Takes arming off the sled with it.__ Flight 3 carries __no [arming switch](Arming-switch.md)__, so there is nothing on the sled to take off it; any later switch sits __in series in the battery line between the battery and the carrier JST__, so it follows the battery onto the airframe, and the sled's 180° flip — which [js-rocket#90](https://github.com/jwilleke/js-rocket/issues/90)'s loop reduced but did not remove — stops bearing on arming at all
- __Nothing retains it.__ The M3 × 55 cross-bar is at adapter z 55, __17 mm above__ the battery's top, so it does not hold it down, and below the battery the bore runs straight through into the Tube. The Nosecone page already records the general case — *"the bay is open at its base, so with the nose fitted a payload drops through into the Tube. Needs a retainer (plug, foam, tape) or a lip"*
- __It sits in the recovery cord's path.__ The M3 is the cord's upper anchor and the cord runs down that bore, so ejection whips the bungee past exactly where the battery is. A LiPo pouch is 4.75 mm of soft foil, and a crushed or punctured battery is a fire inside a sealed nose on a rocket that has to be picked up by hand. __Any retainer here must also shield it from the cord__ — a sleeve, a tube or a hard divider — not merely stop it falling
- __It contradicts [`payload-adapter.md`](https://github.com/jwilleke/js-rocket/blob/main/docs/3d-printed-parts/payload-adapter.md)__, which states twice that *"it is an adapter, not a payload bay — the payload lives entirely in the Nosecone."* That sentence has to be replaced deliberately, not simply overtaken

#### What decides it

__Access is worth a lot and the mass move is not free.__ B shifts 10.9 g from station ~184–220 to __242–278__, aft of the sled's own aft end at 223.1. The lever is already measured on the sled: ballast at its forward end needs __30.9 g__ and at its aft end __62.7 g__ for the same 1.5 cal — the requirement doubles over 134 mm. So 10.9 g moved 40–90 mm aft is not negligible in the currency this project already uses, and __the separated sustainer is the binding case at 0.34 cal__, needing 59.6 g at station 100.

Nose mass would drop 10.9 g under B, taking the nose total from 54.6 to 43.7 and under the ~50 g target — __but the mass has not left the rocket, only moved aft__, so that is bookkeeping rather than a saving.

__Re-run [`stability-flight3.py`](https://github.com/jwilleke/js-rocket/blob/main/rocket/scripts/stability-flight3.py) with the battery at station ~260__ and the trade becomes a number instead of a direction ([js-rocket#66](https://github.com/jwilleke/js-rocket/issues/66)). That is the missing input, and it is cheap.

### The 80 mm lead, and what it constrains under each candidate

__Under A__ the run is short and 80 mm imposes nothing.

__Under B__ it is the binding dimension. The lead climbs the bore, passes the M3 cross-bar at nose z 15, and has to get through the sled's aft end disc — 39.4 mm with ribs to 40.2 in a 40.0 mm bore, effectively sealed. __The only gap is the D-flat crescent at azimuth 180__, so that crescent would be not a convenient wire route but the only one, fixing the pigtail's azimuth. Battery top would sit at __nose z −2__; allowing 15–25 mm for the bends and that route, 80 mm reaches __nose z 53..63__, against a carrier spanning roughly nose z 20..115.

> __So B puts the JST in the aft third of the carrier__, within about __35–45 mm of its aft end__. A is indifferent. __Placing the JST aft satisfies both__, which makes it the cheap hedge while the position is open — and it is free now and a respin to discover later ([#14](https://github.com/jwilleke/js-rocket-avionics/issues/14), stage 2c).

__An inline arming switch would eat into the same 80 mm under B — and flight 3 has none__ ([Arming-switch.md](Arming-switch.md), 2026-09-08), so the 80 mm is the JST's alone and __its position is decided on its own__. If a later flight adds a switch, this coupling comes back and the two are decided together.

### Ruled out on geometry, under either candidate

__Behind the sled's D-flat.__ The crescent between the flat and the bore looks like the obvious home — 8.00 mm deep, 32.00 mm across at its mouth — but it is a circular segment and closes fast. At the battery's own 4.75 mm of thickness the chord is down to __21.86 mm__, and a 29 mm width survives only __1.77 mm__ of depth. No orientation rescues it: 36 mm is worse than 29, and standing it on edge needs 29 mm of depth against 8.00 available. The crescent's use is wiring, the arming pin and the buzzer's air path.

__The free web.__ The web is 124.0 mm and the carrier takes 95.0, leaving __29.0 mm__ against a 36 mm battery.

## Distribution

The battery lands on a __JST-PH on the carrier__ — put it in the carrier's aft third, which serves both candidate positions above — and short __soldered pigtails__ run to each XIAO's underside BAT pads. That indirection is forced, not chosen: __BAT+/BAT− are not on the castellated edge__, so the battery cannot reach a XIAO through the headers.

- __Solder the pigtails before the XIAO goes onto its headers.__ Not before the expansion board — that mates to the *front* face and never covers the pads. What covers them is the __carrier__, at the header's 2.50 mm, and the breadboard does the same on the bench. Faces and evidence in [XIAO-ESP32S3-cam.md](XIAO-ESP32S3-cam.md#which-face-carries-what--settled-off-seeeds-two-drawings-and-the-stack-itself)
- __Both XIAO chargers sit in parallel on one battery — charge through one USB port at a time.__ This avoids adding a charge IC
- __On battery power there is no voltage on the 5V pin__
- __Reversing a LiPo into a XIAO destroys it__ — [design.md](../docs/design.md) requires the pigtail polarity be silkscreened
- __The battery is mechanically restrained, never hangs off the JST.__ On the sled that is the straps; in the adapter nothing does it yet. __The JST is a connector, not a mount__, whichever position wins

### The pigtail is the fragile part, and the solder joint must not be the anchor

__`BAT+`/`BAT−` are 2.3 × 1.3 mm pads.__ That is an electrical connection, not a structural one. If the joint is what holds the wire, boost and landing put the load into the pad, and __the pad lifts__ — taking the copper with it and leaving nothing to re-solder to.

So the wire is anchored to the board, and the joint carries current only:

- __28–30 AWG fine-stranded, silicone insulated. Never solid core.__ Solid wire work-hardens and snaps at exactly this kind of joint; stranded silicone stays flexible and takes vibration without transmitting it
- __Bond the wire to the PCB 3–5 mm from the pad__, with UV-cure or two-part epoxy. __This is the actual fix__ — everything else on this list is secondary to it. It puts the flex point in the free wire instead of on the copper
- __Leave a service loop.__ Slack, so nothing is ever in tension. A taut pigtail is a pigtail under load whenever anything moves
- __Dress it through the 2.50 mm gap__ between the XIAO's back face and the carrier — clear of the header pins, and not lying on carrier copper. Route and tack it __before__ the XIAO goes down; there is no access afterwards
- __Conformal coat over the finished joint__, after bench testing, with the rest of the board
- __Polarity silkscreened at the JST__ — reversing a LiPo into a XIAO destroys it

> __A broken pigtail is silent.__ With both `3V3` pins on the same plane, the surviving regulator back-feeds the dead module and the rocket still works — so the first failure hides the fault and only the second one grounds you. __Inspect both joints as a step, rather than waiting to be told about them.__ It is also the strongest argument for keeping the plane tie until [#8](https://github.com/jwilleke/js-rocket-avionics/issues/8) says otherwise.

__No connector at the pad end.__ A connector there would put mass and leverage on the weakest joint in the assembly, which is the opposite of what is wanted. The disconnect belongs at the far end and already exists — the JST.

## The known risk, still unobserved

[BOM.md](../docs/BOM.md) accepts a coupling failure in writing: __*"a camera brownout on B can disturb A."*__ [design.md](../docs/design.md) repeats it — separate batteries would isolate the boards but cost ~8 g the mass budget cannot afford.

__That is a prediction, not a measurement, and the thing it threatens is the radio link.__ A camera write that resets XIAO-ESP32S3-lora mid-descent costs the rocket, not the video. Settling it is [#8](https://github.com/jwilleke/js-rocket-avionics/issues/8) — run both boards off one battery with the camera active, on a __partially discharged battery__ where sag is worst, and produce a verdict: acceptable, needs decoupling on the carrier, or needs the second battery after all.

__If decoupling is the answer it lands in the layout before the board is ordered__, not after.

## Rejected

__An 18650__ would put nose mass near the ~65 g weathercock limit.

---

Part numbers, vendors and masses live in [BOM.md](../docs/BOM.md), which is the single source of truth for both. Purchase history is in [shopping-list.md](../docs/shopping-list.md); the reasoning is in [design.md](../docs/design.md).
