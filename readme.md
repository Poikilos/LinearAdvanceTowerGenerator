# LinearAdvanceTowerGenerator
Did you ever wonder why the corners of your models are either bulged or rounded off? Generate a hollow square tower and calibrate linear advance the old-fashioned way. This method is as accurate as your ability to count layers and look at how good the layers are, so it is up to 100% accurate. Marlin's line by line (flat) test didn't work for me with flexible filament because the perception of what was happening seemed to have other factors (past a certain value, all of the lines looked the same but uneven until getting to very high values where they were wider on the right but not the middle as is supposed to happen), and the result from that left cut corners on real models.

There is totally different tower using the same technique as LinearAdvanceTowerGenerator at the URL below, but it is not suitable for TPU etc. due to the temperature, speed, and K value range.

> If LA is set too low you’ll see "dog bone" bulges in corners rather than neat squares.
> If LA is set too high, corners will look rounded off.

-[Calibrating linear advance with PrusaSlicer](https://projects.ttlexceeded.com/3dprinting_techniques_calibrating_LA.html)

## How to use
- Generate the test gcode file by running "python3 run.py" in a GNU-like Terminal (or Windows Command Prompt).
  - Take note of the file's name that appears.
- Open the file in Pronterface, Cura, OctoPrint, or some other software that can send raw g-code to your 3D Printer.
- After printing completes, visually find the height that seems the most accurate, not having either the bulging or rounding issue above.  An estimate midpoint may provide a value that is theoretically more precise than the resolution.
- Measure to the height using calipers, preferably using digital calipers, placing the stem on the raft and the base at the height you chose above.
- Divide the number by .2 to get the number of increments. You can use a value not divisible by .2 to try to estimate a more precise value.
- Multiply the result by .4 (or rather `options['step']` if differs) to get the K value.
- Enter your K value as follows:
  - Connect your printer via USB then Download and Run Pronterface (or send the following commands via OctoPrint).
  - In the command prompt, send each of the following commands separately:
    - `M900 K...` but replace "..." with the K value you found earlier.
    - If you get an invalid command error, you have to compile/get Marlin firmware that has LIN_ADVANCE enabled and re-flash your 3D printer (unplug the LCD first if using JGAURORA A3S) then redo the step above. Potentially, you can set LIN_ADVANCE_K in the Configuration.h file. Otherwise, continue below.
    - `M500` to save settings to firmware.

Example results:
- JGAURORA A3S with upgraded 1.9mm ID bowden tube (680mm long) by TECBOSS
  - ATARAXIA ART Flexible PLA+: `M900 K4.32`
