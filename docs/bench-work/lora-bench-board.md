---
title: The lora bench board — power it up
description: Step by step, from a wired breadboard to a GPS fix in Meshtastic, for XIAO-ESP32S3-lora with the Wio-SX1262 and the L76K-GNSS.
---

# The lora bench board — power it up

__This page takes the board in the photograph from unpowered to a GPS position on a screen.__ It is the first half of [#6](https://github.com/jwilleke/js-rocket-avionics/issues/6). What each wire should be, and why, is owned by [bench-wiring.md](../bench-wiring.md#the-lora-board); this page is the procedure.

![The lora bench board: XIAO-ESP32S3-lora with the Wio-SX1262 on top at the head of the breadboard, USB-C up; the L76K-GNSS lower down across the channel, its GNSS antenna off the board at the top; the LoRa antenna lead running off to the right; the battery pigtail ending in an unplugged JST](../resources/bench-board-lora.jpg)

## What this board does

Two jobs, joined by the XIAO in the middle:

```text
satellites -> GNSS antenna -> L76K-GNSS  --UART, D6/D7-->  XIAO-ESP32S3-lora  --B2B-->  Wio-SX1262 -> LoRa antenna -> air
              (the square       (works out                  (runs stock                   (the 915 MHz
               cream tile)       the position)               Meshtastic)                   radio)
```

- __GNSS — finding where it is.__ The [GNSS antenna](../../hardware/Antennas/Antennas.md) hears the satellites. The [L76K-GNSS](../../hardware/L76K-GNSS/L76K-GNSS.md) turns them into a position and sends it to the XIAO as lines of text, once a second, over two wires. __It only listens; it never transmits.__ It needs to see the sky
- __LoRa — telling someone.__ Meshtastic on the XIAO takes that position and sends it out through the [Wio-SX1262](../../hardware/Wio-SX1262-LoRa/Wio-SX1262-LoRa.md), a long-range, low-speed radio. __Something has to be listening__: a second Meshtastic node, with a phone on it. There is none yet — [#23](https://github.com/jwilleke/js-rocket-avionics/issues/23)

__No code is written for this board, ever.__ It runs [stock Meshtastic](../../hardware/XIAO-ESP32S3-lora/XIAO-ESP32S3-lora.md), pre-flashed, and only ever stock Meshtastic. Everything below is settings, changed from the Meshtastic app.

## 1 — Look before power

Nothing is connected to USB or the battery yet.

__First: the XIAO under the Wio-SX1262 must be the Meshtastic one.__ The two XIAOs look identical, and on 2026-09-11 they were the wrong way round — the Wio-SX1262 sat on the factory-demo XIAO, which is why the phone found no Bluetooth. How to tell them apart, and which is which: [XIAO-ESP32S3-lora.md](../../hardware/XIAO-ESP32S3-lora/XIAO-ESP32S3-lora.md#which-xiao-is-this-one). Check it in step 3.

Both antennas plug on the same way: a thin black cable ending in a tiny gold snap-on plug, a __U.FL__, pressed onto a tiny round gold socket on the board. It clicks on; it is fragile, so pull it off straight up by the plug, never by the cable.

- __The LoRa antenna is plugged into the Wio-SX1262__ — the top board at the head of the breadboard. Its socket is at the bottom right corner of the Wio-SX1262, and in the photograph its black cable runs off to the right. __Never power the board without it.__ A radio that transmits into no antenna can damage itself
- __The GNSS antenna is plugged into the L76K-GNSS.__ The GNSS antenna is the square cream-coloured tile at the top of the photograph, marked `1584R-A`. Its socket is at the top left corner of the L76K, beside the words `ANT 50mA MAX`
- __The GNSS antenna lies cream face up__ — the side with the gold border and the round silver dot, toward the sky
- __The battery is unplugged__ at the white JST. Today is USB only
- __Nothing joins this breadboard to the cam board__

## 2 — Check the six jumpers

Read off the photograph — __confirm each one on the board__, by the pin's name, not by counting holes. The XIAO sits USB-C up; the L76K sits antenna end up.

| Wire in the photo | From | To |
|---|---|---|
| short red, top right | XIAO `3V3`, 3rd pin down on the right | the `+` rail, beside the red line |
| short grey, top right | XIAO `GND`, 2nd pin down on the right | the `−` rail, beside the blue line |
| red, at the L76K | L76K `3V3` | the same `+` rail |
| grey, at the L76K | L76K `GND` | the same `−` rail |
| orange | XIAO `D6`, bottom pin on the left | L76K `D6`, top pin on the left |
| long grey loop | XIAO `D7`, bottom pin on the right | L76K `D7`, top pin on the right |

- __Same name to same name.__ D6 goes to the pad labelled for D6, D7 to D7. Seeed's `RX`/`TX` labels will tell you otherwise; ignore them — [bench-wiring.md](../bench-wiring.md#the-lora-board) says why
- __Nothing on the L76K's `5V`__
- __The photograph's layout is not the drawing's__ — USB-C up and the L76K below, where [the drawing](bench-breadboard-lora.svg) has them side by side. The wiring is the same; only the placement moved

## 3 — Power it

1. __USB-C into the XIAO__, with a cable that carries data — a charge-only cable powers the board and shows no port
2. __Check the Mac sees it:__

   ```sh
   ls /dev/cu.usbmodem*
   ```

   One line back means it enumerated. Nothing back: another cable, another port. __Stop here if it still does not appear__ — nothing below will work
3. __Check it is the right XIAO, from the name.__ A __long__ name ending `CA481` is the Meshtastic XIAO: carry on. A __short__, digits-only name such as `usbmodem31101` is the factory-demo XIAO: unplug, and move the Wio-SX1262 onto the other one — [which is which](../../hardware/XIAO-ESP32S3-lora/XIAO-ESP32S3-lora.md#which-xiao-is-this-one)

__Do not press Upload in PlatformIO with this board plugged in.__ PlatformIO's Serial Monitor is safe; Upload would overwrite Meshtastic.

## 4 — Talk to it

Either works:

- __In Chrome on the Mac:__ open <https://client.meshtastic.org>, choose __New Connection → Serial__, pick the `usbmodem` port
- __On the phone:__ the Meshtastic app, over Bluetooth. A board with no screen pairs on the default PIN, `123456`

__One connection at a time.__ While the phone is connected over Bluetooth, the board ignores USB — the Mac sees the port and gets no answer, and that looks like a hung board. Turn the phone's Bluetooth off, or disconnect in the app, before working over USB (seen 2026-09-11).

__It is alive if it shows a node__ with a name and a firmware version. __Write the version down__ for #6.

> __Do not take the phone app's "update firmware" offer mid-test.__ Updates are done on purpose, from the Mac, by [the firmware rule](../../hardware/XIAO-ESP32S3-lora/XIAO-ESP32S3-lora.md#firmware--stock-meshtastic-only-updated-on-purpose-frozen-for-flight) — stock releases only, settings backed up first. Loading anything that is not stock Meshtastic is the one thing this design rules out.

## 5 — A private channel, then the region

__The channel first.__ With a region set and a GPS fix, the node broadcasts its position — on Meshtastic's __default public channel__ unless told otherwise, where any node in range reads it and one that uplinks to MQTT can put it on public maps. On the bench, that position is where you live.

1. __Channels → the primary channel__: your own name, and __generate a new random key__, 256-bit. __The key is what makes it private, not the name__ — a short key such as `AQ==` is the published default
2. On that channel: __MQTT uplink off, MQTT downlink off, position enabled at full precision__ — recovery needs the exact spot, and the key keeps it to us
3. __Keep the key and the channel's QR code out of this repo.__ They belong in `private/`, which git ignores. The ground receiver ([#23](https://github.com/jwilleke/js-rocket-avionics/issues/23)) joins by that QR code

__Then the region: Settings → LoRa → Region → `US`.__ Until this is set the radio stays off; from now on it transmits, which is why the antennas were checked in step 1. The board restarts; the channel survives it. Leave the modem preset at its default, `LONG_FAST` — the receiver must match it.

Done on 2026-09-11: private primary channel, own 256-bit key, both MQTT links off, full precision, region `US`, `LONG_FAST`.

## 6 — Get a GPS fix

1. __Settings → Position → GPS mode → Enabled__, if it is not already
2. __Take it to a window, better outdoors__, GNSS antenna face up, on USB from a laptop or a power bank. Indoors, deep in a building, it may never get a fix
3. __Wait for the node to show a position__ in the app. A first fix after power-up can take minutes

__Done on 2026-09-11: a fix outdoors, on the Meshtastic app over Bluetooth.__

__If no position appears after 15 minutes with open sky__, the question is whether the module or Meshtastic is at fault. [`firmware/gps-check/`](../../firmware/gps-check/) answers it on the __cam__ board, which may be reflashed — unplug this one first.

> __The position on your screen is where you live.__ Do not paste it, a screenshot of the map, or the raw GPS text into an issue or a commit. This repo is public.

## 7 — Power down

Unplug the USB. Nothing else to do: no battery is connected.

## Record on #6

- Enumerated, and the port name
- Meshtastic firmware version
- A fix outdoors — yes or no

__Still open on #6 after this page__, and not covered here:

- __The range check__ — needs the receiver, [#23](https://github.com/jwilleke/js-rocket-avionics/issues/23)
- __Desense__ — whether the radio transmitting spoils the GPS. __Tested in the assembled nose, not here:__ on the bench the two antennas lie wherever their leads fall, so a bench result says little about the flight layout
- __On the battery__ — [bench-bringup.md](../bench-bringup.md), and [#8](https://github.com/jwilleke/js-rocket-avionics/issues/8) for both boards on one battery
