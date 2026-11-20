Where they go: look just above each black jumper cap, toward the buzzer. Each jumper has a pair of empty gold holes about 5 mm apart:

GPS jumper: both holes are visible, right next to it.
EVT jumper: one hole is visible and the other is under the cap.
The resistor lies flat with one lead in each hole, soldered like any other through-hole part.

What they do: each data link is a wire between two boards that pass messages:

GPS link: the camera XIAO listens to the GPS, so the flight log gets GPS position and altitude.
EVT link: the camera XIAO sends short messages like "launch" or "apogee" to the lora, which radios them out.
Each link runs through its jumper and then its resistor. The resistor is the protection: if firmware sets a pin wrong, the 1 kΩ limits the current, so one XIAO can't fight the other and can't drag the GPS line down for the beacon. Without the resistor the link has a gap, so nothing passes even with the cap on.

If you skip them:

The camera XIAO, the lora, the GPS beacon, the sensors and the buzzer all still work.
You lose only the GPS track in the flight log and the event messages over radio.
The design calls both links nice-to-have, and taking the caps off gives the same result.