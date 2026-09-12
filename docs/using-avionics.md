---
title: Using the avionics
description: For the people flying the rocket, not building it — what the electronics do, and what to do before, during and after a flight.
---

# Using the avionics

__This page is for flying the rocket, not building it.__ No code, no wiring. If something here is wrong or unclear, it is a bug — say so on the [issues](https://github.com/jwilleke/js-rocket-avionics/issues).

## What is in the nose

Two small computers and one battery:

| | What it does | You will see it as |
|---|---|---|
| __The beacon__ ([XIAO-ESP32S3-lora](../hardware/XIAO-ESP32S3-lora/XIAO-ESP32S3-lora.md)) | Knows where the rocket is (GPS) and radios it out, so you can find it | a node in the __Meshtastic__ phone app |
| __The camera computer__ ([XIAO-ESP32S3-cam](../hardware/XIAO-ESP32S3-cam/XIAO-ESP32S3-cam.md)) | Records video and the flight — acceleration, spin, altitude — to a memory card | `mj-cam` |
| __The battery__ | Powers both, from the moment it is plugged in | — |

__The rocket flies fine without any of it.__ The electronics find it and record it; they do not steer it and cannot fire anything.

## What works today, and what does not yet

| | Today |
|---|---|
| Finding the rocket — position on your phone's map | __works on the bench__. Needs the ground receiver, which is ordered ([#23](https://github.com/jwilleke/js-rocket-avionics/issues/23)) |
| Recording video and flight data | __proven on the bench, not written as a flight program yet__ ([#24](https://github.com/jwilleke/js-rocket-avionics/issues/24)) |
| Status on the pad — "ready", "recording" | __not decided__: beeps, or a phone screen ([#25](https://github.com/jwilleke/js-rocket-avionics/issues/25)) |
| Getting the video off without opening the nose | __planned__ — phone over Bluetooth, then Wi-Fi ([#1](https://github.com/jwilleke/js-rocket-avionics/issues/1)) |
| Charging without opening the nose | __not solved__ ([#1](https://github.com/jwilleke/js-rocket-avionics/issues/1)) |

__Until those rows say "works", treat the rest of this page as the plan.__

## What you need on the ground

- __Your phone__ with the __Meshtastic__ app
- __The ground receiver__ — a second Meshtastic radio, in its case, with its antenna — and a __USB power bank__ for it
- The receiver must be on __the same private channel__ as the rocket. That is done once, by scanning a QR code in the app; whoever set up the rocket has it. __Never post that QR code or a screenshot of the map anywhere public__ — the map shows where the rocket is, which on the bench means where you live

## Before launch day

1. __Charge the battery__ — through the camera computer's USB-C port only, __never both boards at once__. Today that means before the nose is assembled
2. __Leave the battery unplugged.__ Plugging it in turns everything on, and the clock starts
3. __Charge the receiver's power bank__ and your phone
4. __Check the receiver works__: power it, open the app, and see the rocket's node when the rocket is powered

## At the pad

__There is no on/off switch on this rocket. Plugging in the battery is "on".__

1. __Plug the battery in last__, on the pad, then load the electronics into the nose and close it. From this moment you have roughly __100 minutes__ before the battery runs down — an estimate, not yet measured. __Do not plug in early and then wait__
2. __Power the receiver__ and open the Meshtastic app. The rocket's node should appear, and once its GPS has the sky, its position
3. __Check the rocket is alive__ — how, exactly, is not decided yet ([#25](https://github.com/jwilleke/js-rocket-avionics/issues/25)). The planned answer is a status you can read on your phone, not only beeps
4. __Launch.__ If the launch is delayed past about an hour, the battery is the problem: getting it out means opening the nose, which also unhooks the recovery cord

## During the flight

__You do not need to do anything.__ The camera records from the moment the battery goes in until landing, then stops so the battery that is left keeps the beacon talking. The beacon sends the rocket's position every so often — expect a position or two on the way up and down, not a live track.

## Finding it

1. __Watch the rocket's node on the app's map__ after it lands. The last position is where to walk
2. __Use the app's compass__ on the rocket's node — it points at the rocket and gives the distance
3. __The last few metres__: GPS is good to a few metres, and a white rocket disappears in grass. The rocket will beep — __but its beeps are high-pitched, and not everyone can hear them__. Look as well as listen
4. __Go soon.__ The beacon keeps talking only as long as the battery lasts

## After you have it back

1. __Unplug the battery__ as soon as it is safe to open the nose — everything stays on otherwise
2. __Get the video and flight data__ — today, take the microSD card out of the camera computer and read it on a computer; the video plays in VLC. The plan is to download it to your phone over Wi-Fi without opening the nose
3. __Recharge__ before the next flight

## Battery safety

- __Never let the two battery wires touch.__ A LiPo battery has no fuse and can catch fire
- __Red to red, black to black.__ Plugged in backwards, it destroys a board instantly
- __Do not run it flat__, and do not charge a battery that is puffed up or damaged
- __Charge through one USB port at a time__

---

For builders: how it is designed is in [design.md](design.md), what it is made of in [BOM.md](BOM.md), and the bench work in [bench-bringup.md](bench-bringup.md).
