---
title: TODO
description: Pointer to the combined backlog, which is ranked in js-rocket.
last_updated: "2026-09-06"
---

# TODO

__This repo's backlog is ranked in [js-rocket's `TODO.md`](https://github.com/jwilleke/js-rocket/blob/main/TODO.md), not here.__

Issues from this repository appear there prefixed __`aelc-#N`__, interleaved into the same priority bands as the airframe's. Unprefixed numbers are js-rocket.

## Why one file and not two

__Flight 3's camera runs through both repositories.__ The Nosecone port is cut in js-rocket ([#88](https://github.com/jwilleke/js-rocket/issues/88)) and the sled shelf that decides its size is there too ([#89](https://github.com/jwilleke/js-rocket/issues/89)) — but the lens standoff that dimensions both is measured here ([#9](https://github.com/jwilleke/js-rocket-avionics/issues/9)), behind the header height ([#10](https://github.com/jwilleke/js-rocket-avionics/issues/10)). __A backlog showing only half of that hides the critical path.__

Two files ranking the same work drift apart, and the drift is silent. So this one holds no bands.

## The relationships are on GitHub, not in a list here

Both epics in this repo are __sub-issues of the flight-3 epic__, [js-rocket#63](https://github.com/jwilleke/js-rocket/issues/63), and each owns its own children:

- [#4](https://github.com/jwilleke/js-rocket-avionics/issues/4) — __[EPIC] Power the avionics on the bench__, parent of [#5](https://github.com/jwilleke/js-rocket-avionics/issues/5) [#6](https://github.com/jwilleke/js-rocket-avionics/issues/6) [#7](https://github.com/jwilleke/js-rocket-avionics/issues/7) [#8](https://github.com/jwilleke/js-rocket-avionics/issues/8) [#9](https://github.com/jwilleke/js-rocket-avionics/issues/9) [#10](https://github.com/jwilleke/js-rocket-avionics/issues/10)
- [#11](https://github.com/jwilleke/js-rocket-avionics/issues/11) — __[EPIC] Everything needed before the carrier PCB is ordered__, parent of [#1](https://github.com/jwilleke/js-rocket-avionics/issues/1) [#2](https://github.com/jwilleke/js-rocket-avionics/issues/2) [#12](https://github.com/jwilleke/js-rocket-avionics/issues/12) [#13](https://github.com/jwilleke/js-rocket-avionics/issues/13) [#14](https://github.com/jwilleke/js-rocket-avionics/issues/14) [#15](https://github.com/jwilleke/js-rocket-avionics/issues/15) [#16](https://github.com/jwilleke/js-rocket-avionics/issues/16)

__#4 gates #11.__ Nothing is ordered until the bench has run.

Session history for this repo stays in `private/project_log.md`.
