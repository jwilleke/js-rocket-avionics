# Next electronics: what to change, and what can be bought

__A starting point for the next electronics revision, written 2026-10-13 after flight 4's design work.__ It records what the current build taught us, and what ready-built rocket electronics could do the same job. Nothing here changes flight 4. The current design is [design.md](design.md); its parts are in [BOM.md](BOM.md).

## What the electronics are for

Four jobs. Every part has to answer to one of them:

1. __Flight profile__ — altitude, speed and acceleration over time, logged on board
2. __Live telemetry__ — altitude, position and flight state on the ground during the flight
3. __Finding the rocket__ — its landing position on a phone or receiver map
4. __Video__ — a sideways or down-the-body view

Limits: a __Ø40 mm__ bore; about __50 g__ for everything, battery included (today's build is 49.3 g, [BOM.md](BOM.md)); no pyro, because ejection is the motor's; ready-built modules, __no SMD soldering__; licence-free radio (no ham licence).

## What the current build taught us

__1. Write the jobs down before choosing parts.__ They were never written as requirements, so the barometer's role drifted between "altimeter", "ejection timestamp" and "data" over several days. The list above is that page.

__2. Put the electronics in a straight body section, not the Nosecone.__ Nearly every hard problem of flight 4 came from the location:

- __No legal static port.__ The nose has no straight run a full body-width long ([design.md](design.md#why-the-barometric-port-is-dropped))
- __No sound hole.__ It cannot be sealed from inside, so it was deferred ([js-rocket#118](https://github.com/jwilleke/js-rocket/issues/118))
- __The camera needed a socket and a replaceable window insert__ in the nose's collar
- __Service access needed workarounds__: a USB slot through the sled's PORT disc, and the battery lead routed below the sled

A short avionics bay between two tube sections, with a band around its outside, is the standard hobby layout. Static ports, the buzzer hole, an arming switch and a charge port all go through the band, where hands can reach them and the air pressure is clean.

__3. One computer, not two cooperating ones.__ Stock Meshtastic on the second XIAO is why the GPS is not saved on the rocket, cannot use its airborne mode, and reports position only every so often, and why the board needs two data-link jumpers whose pins are still undecided ([#26](https://github.com/jwilleke/js-rocket-avionics/issues/26)). One microcontroller running our own firmware could read the GPS directly, log everything, and send altitude and speed over LoRa once or twice a second.

__Keep:__ through-hole modules on a carrier; one battery on a Y-cable with an external charger; the generator-driven layout with its pin and clearance checks, which caught real errors; the buzzer; printed fit mocks before real parts.

## What can be bought (researched 2026-10-13)

Checked against each maker's own page unless noted. __Amazon blocked automated reads__, so on Amazon only the listing's existence is confirmed, not price, stock or Prime. "—" means the maker does not publish it.

### Trackers with live telemetry

Only three are licence-free (900 MHz) and ready-built. Each needs its own ground station; none talks straight to a phone in flight.

| Product | Jobs | Mass | Fits Ø40 | Live data | Ground station | Price | Sold |
|---|---|---|---|---|---|---|---|
| [Featherweight Swift](https://www.featherweightaltimeters.com/swift-tracker.html) | 2, 3; GPS-only log | board —; 400 mAh battery 9 g | yes, 33.5 × 20.3 mm | __10 Hz__ GPS: position, altitude, vertical and horizontal speed | Swift ground station $195, phone app over Bluetooth (iOS, Android) | __$365__ system; tracker $170 | maker store, in stock |
| [BigRedBee BRB900L](https://shop.bigredbee.com/collections/900mhz-tx-and-rx) | 2, 3; GPS + baro log | — | — | __1 Hz__; LCD receiver needs no phone; watches two transmitters (two-stage) | included; Android app, iOS "soon" | __$358__ package | maker store |
| [Silicdyne Reperix](https://silicdyne.net/shop/reperix-bundle/) | 1, 2, 3 | __5.9 g__ | yes, 40 × 12 mm | rate —; 3D map and voice via SteadyBlue | SteadyBlue €109; app is an Android beta | __€289__ bundle | France only, no US dealer. Battery pigtail must be soldered (wire, not SMD) |

__Ruled out:__

- __Altus Metrum TeleGPS and BigRedBee 433 MHz units__ use 70 cm and need a ham licence
- __Eggtimer__ sells kits with SMD parts, and its range is being replaced (LR-Series, end of 2026)
- __Featherweight's original GPS Tracker__ is being replaced by the Swift; its ground stations are sold out
- __RAK WisMesh Tag__ and __SenseCAP T1000-E__ do not fit the bore

### Flight-profile loggers, no telemetry

| Product | Mass | Fits | Logs | Data out | Price |
|---|---|---|---|---|---|
| [Featherweight Blue Jay2 Minus](https://www.featherweightaltimeters.com/blue-jay-altimeter.html) | __4.7 g__ + battery | yes, 37 × 16.5 mm | __baro, ±32 g accelerometer and gyro, all at 50 Hz__ | Bluetooth app: "go for launch" on the pad, downloads when you walk up to the rocket | __$75__, + $29 power kit |
| [Jolly Logic AltimeterTwo](https://www.jollylogic.com/products/altimetertwo/) | 9.9 g with battery | yes | baro 25 Hz, accelerometer > 250 Hz | __summary numbers on its screen only, no curve__ | $79.95; also on Amazon |
| PerfectFlite Pnut | 7.4 g with battery | yes | baro 20 Hz | USB kit $24.95 | $64.95, __out of stock__ |
| [Altus Metrum EasyMini](https://altusmetrum.org/EasyMini/) | 6.5 g | yes | baro | USB | $80 |

The Jolly Logic AltimeterThree (the Bluetooth model) appears discontinued.

### Cameras

| Camera | Mass | Fits Ø40 | Power | Video | Price |
|---|---|---|---|---|---|
| [RunCam Thumb Pro](https://shop.runcam.com/runcam-thumb-pro/) | __16 g__ | yes, 25.5 × 21 mm section | __no battery: needs 5 V, ≤ 500 mA__ | 4K30, 1080p120, gyro for stabilising afterwards; 155° | $99.99 |
| RunCam Thumb 2 | 27 g | tight, 37.8 mm diagonal | no battery: 5 V, ≤ 700 mA | 4K60 | $119.99 |
| Insta360 GO 3S | 39.1 g | yes, 4 mm to spare | built in, 38 min | 4K30 | about $240; Insta360's own page not reachable, figures from a review |

Caddx Peanut and Mobius Mini are discontinued.

## Packages that cover all four jobs

| | A: Swift + Blue Jay2 + Thumb Pro | B: Reperix + Thumb Pro | C: BRB900L + Thumb Pro |
|---|---|---|---|
| Profile log | Blue Jay2, 50 Hz baro + IMU | Reperix, 10 Hz GPS + IMU, __no baro stated__ | BRB, GPS + baro |
| Live | 10 Hz GPS to app | map and voice, rate — | __1 Hz__ |
| Mass | likely 45–55 g; two boards unpublished | about 35 g | — |
| Cost | about __$570__ + camera power | __€289 + $100__ + import | about __$460__ + camera power |
| Weak spots | three batteries; live altitude is GPS, the baro curve comes after landing | import, iOS unclear, solder the pigtail | 1 Hz is coarse for a boost under 2 s |

Common to all: __GPS lags during boost__, so the speed and acceleration curve has to come from the baro and IMU log; the __Thumb cameras need a 5 V supply__ — a battery and boost module, the one part of each package that is not ready-built; and __every package is several times the cost__ of the parts in the current build.

## The cheap step that would help now

__Nothing records flight data yet__: the camera XIAO's flight program is not written ([#24](https://github.com/jwilleke/js-rocket-avionics/issues/24)). A __Blue Jay2 Minus__ — $75, 4.7 g, 50 Hz baro, accelerometer and gyro, downloaded by phone — would give a full flight profile on its own, alongside the Meshtastic beacon for finding the rocket. It still needs a vented bay to read altitude well ([js-rocket#118](https://github.com/jwilleke/js-rocket/issues/118)). A RunCam Thumb Pro would do the same for video. Whether that replaces the custom recorder or flies beside it is a decision, not made here.

## Sources

Fetched 2026-10-13: featherweightaltimeters.com (Swift, original tracker, Blue Jay, store); shop.bigredbee.com (900 MHz collection, LoRa overview); silicdyne.net (Reperix bundle, docs, dealers); altusmetrum.org and shop.gag.com; eggtimerrocketry.com (Eggfinder, LR FAQ); jollylogic.com (products, AltimeterTwo); perfectflite.com and perfectflitedirect.com; shop.runcam.com (Thumb Pro, Thumb Pro W, Thumb 2); maisondudrone.com (Insta360 GO 3S review); apple.com/airtag; heltec.org (Wireless Tracker). Amazon listings: [AltimeterTwo B0069Z6YCI](https://www.amazon.com/dp/B0069Z6YCI), [RunCam Thumb 2 B0DGTMKVNL](https://www.amazon.com/dp/B0DGTMKVNL), [Insta360 GO 3S B0D7F8SWK3](https://www.amazon.com/dp/B0D7F8SWK3) — existence only.
