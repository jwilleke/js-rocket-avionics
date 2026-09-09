# GNSS-stack

__The arrangement that was considered and rejected.__ There is no GNSS stack: the [L76K](../L76K-GNSS/L76K-GNSS.md) mounts flat on the [carrier](../PCB-carrier/PCB-carrier.md). This page exists so the idea is not proposed a third time.

## What was proposed

The L76K is a XIAO-format board, so its pin rows line up with a [XIAO-ESP32S3-x](../XIAO-ESP32S3-cam/XIAO-ESP32S3-cam.md)'s own 14 castellated pads __when the L76K is inverted__. That allows a single set of long header pins to do three jobs at once: soldered at the XIAO, passing through the inverted L76K, and continuing down into a socket soldered to the carrier.

It was dry-assembled and photographed on 2026-09-09. The technique works.

## Why it was rejected anyway

__Operator decision, 2026-09-09.__ It is not that the pins would not have worked.

- __The clearance had never been measured.__ Whether the L76K and the [Wio-SX1262](../Wio-SX1262-LoRa/Wio-SX1262-LoRa.md) could share the space above one XIAO was the open half of [#6](https://github.com/jwilleke/js-rocket-avionics/issues/6), and the two parcels had arrived weeks apart — nobody had ever put them together
- __It stacked four boards on header pins__, cantilevered, in a rocket that boosts and then lands. The MCU, the radio and the GNSS ended up in one mechanical column with one failure path
- __It bought almost nothing.__ Riding the pads saved a footprint on a face that was 21 mm used out of 95

__Flat on the carrier deletes the question instead of answering it.__ No dry-stack gate before soldering, no tall headers to source, no clearance to preserve through every later revision of either board. The top face goes 21 → 42 mm, the bottom face's 84 mm still sets the board length, and __the sled does not reprint__.

## What it left behind

__The L76K now needs a pin order and has never had one.__ It took no carrier footprint until this decision, so it was never photographed on the grid or read off the part — the only module in stage 2c without a reading. An unread pin order is the specific thing that scraps a board. [#14](https://github.com/jwilleke/js-rocket-avionics/issues/14).

> __The dry-assembly photograph was deleted at the operator's request__, the arrangement being one nobody should build from. The description above is the record.
