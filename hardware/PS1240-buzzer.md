# PS1240 — piezo buzzer

__Passive, PWM-driven from D0.__ Named for the part number in [BOM.md](../docs/BOM.md).

## It does three jobs

1. __Last-20-metre locator.__ GPS lands you in a 3–10 m circle, and a white PLA rocket vanishes in tall grass at 2 m
2. __The only status channel on the pad.__ With the nose assembled, USB is unreachable, Wi-Fi is off and the GPIO21 LED is sealed inside — __beep patterns are the only way the rocket reports booted / armed / sensors alive__
3. __Beeping apogee in digits after landing__, needing no phone

## Passive, not active — and the reason changed

An earlier revision specified an __active, self-oscillating__ part, because the buzzer then hung off an I2C GPIO expander where a ~3 kHz tone would have meant __6000 bus transactions a second__.

Splitting to two boards freed the pins, the expander went, and __a real GPIO can PWM a passive element directly__ — which gives __multiple tones__ rather than one. That is what makes beep patterns readable as distinct codes rather than a single undifferentiated noise.

## Sound has to escape a sealed PLA cone

__A piezo in a closed cavity loses 20–30 dB.__ Mount the disc __against the nose wall__ so the shell acts as a soundboard. The camera port is a free acoustic leak, and the payload bay is open at its base.

## What it is not

__It is not radio redundancy.__ It shares board B's MCU, so a firmware or MCU failure takes both. Only a __self-powered beeper with its own cell__ — ~5 g, zero pins — is immune to that. [BOM.md](../docs/BOM.md) records it as considered and not adopted: *"revisit if recovery confidence outranks grams."*

## Open

- __Never driven.__ At least two distinguishable beep patterns are an acceptance criterion of [#7](https://github.com/jwilleke/js-rocket-avionics/issues/7)
- __No footprint on the carrier yet__ — stage 2c, [#14](https://github.com/jwilleke/js-rocket-avionics/issues/14)
- __Acoustic coupling to the nose wall is untested__, and it depends on a Nosecone that has never been printed at its current revision

---

Part numbers, vendors and masses live in [BOM.md](../docs/BOM.md), which is the single source of truth for both. Purchase history is in [shopping-list.md](../docs/shopping-list.md); the reasoning is in [design.md](../docs/design.md).
