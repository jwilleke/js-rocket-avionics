# PS1240 — piezo buzzer

__Passive, PWM-driven from D0.__ Named for the part number in [BOM.md](../../docs/BOM.md).

## It does three jobs

1. __Last-20-metre locator.__ GPS lands you in a 3–10 m circle, and a white PLA rocket vanishes in tall grass at 2 m
2. __The only status channel on the pad.__ With the nose assembled, USB is unreachable, Wi-Fi is off and the GPIO21 LED is sealed inside — __beep patterns are the only way the rocket reports booted / armed / sensors alive__
3. __Beeping apogee in digits after landing__, needing no phone

## Passive, not active

__A real GPIO PWMs a passive element directly__, which gives __multiple tones__ rather than one — and that is what makes beep patterns readable as distinct codes rather than a single undifferentiated noise. An active, self-oscillating part gives one tone and buys nothing here.

## On the bench — measured, not listened to

__2026-09-12__, on [XIAO-ESP32S3-cam](../XIAO-ESP32S3-cam/XIAO-ESP32S3-cam.md#on-the-bench): D0 driven at 1.2, 3 and 4 kHz, 50% duty, recorded by a webcam microphone a short way off and analysed by FFT in quarter-second windows. __It works, and D0 is wired right.__ Level is the tone's peak over the recording's median noise:

| Driven at | What came out |
|---|---|
| __4 kHz__ | __~55 dB__ over the noise, and the strongest frequency in the room. The part's sweet spot |
| 3 kHz | ~47 dB — but its __9 kHz__ third harmonic was the strongest frequency while it played |
| 1.2 kHz | the fundamental barely above the noise. What came out was its harmonics — 3.6, 6.0 and 8.4 kHz |

__So every tone this part makes lands between about 3.5 and 9 kHz.__ A "low" tone driven at 1.2 kHz is not low when it leaves the disc; distinct codes have to differ in rhythm and length, not only in pitch.

__Do not rely on someone hearing it.__ High frequencies are the first many adults stop hearing, and a person who cannot hear 3.5–9 kHz hears nothing at all from this part. A beep code only one person at the pad can hear is not a status channel. Whether jobs 1 and 2 above need another route is open.

## Sound has to escape a sealed PLA cone

__A piezo in a closed cavity loses 20–30 dB.__ The buzzer is soldered to the [carrier](../PCB-carrier/PCB-carrier.md#tall-side--faces-270-the-camera), at the forward end of its tall side ([#36](https://github.com/jwilleke/js-rocket-avionics/issues/36)), and faces the Nosecone's wall on the camera side. __For flight 4 that wall is closed__: the Nosecone already printed has no sound hole. A hole, and how to seal it, is deferred to a later flight with the static ports (operator, 2026-10-13, [js-rocket#118](https://github.com/jwilleke/js-rocket/issues/118)). The camera port is no leak either: its window disc is glued in. The payload bay is open at its base.

__So the loss is taken, and whether the beep still carries is untested.__ The [audibility test](../../docs/design.md#verification) — beep inside the closed Nosecone, listen from 20 m — is owed before flight 4, and matters more without a hole.

__The part is 12.2 × 6.5 mm__ (TDK's catalog; Adafruit lists 11.9 × 6.53), so on the carrier its top stands at r 7.6, far inside the Nosecone's inner wall at r 23.07. __Its two leads are 5.0 mm apart__, measured on the part in hand (2026-10-15) and matching TDK's catalog. They come through the carrier under the BMP388, so they are trimmed short before it goes on.

## What it is not

__It is not radio redundancy.__ It shares XIAO-ESP32S3-cam's MCU, so a firmware or MCU failure takes both. Only a __self-powered beeper with its own battery__ — ~5 g, zero pins — is immune to that. [BOM.md](../../docs/BOM.md) records it as considered and not adopted: *"revisit if recovery confidence outranks grams."*

---

Part numbers, vendors and masses live in [BOM.md](../../docs/BOM.md), which is the single source of truth for both. Purchase history is in [shopping-list.md](../../docs/shopping-list.md); the reasoning is in [design.md](../../docs/design.md).
