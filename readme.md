# LinearAdvanceTowerGenerator
Did you ever wonder why the corners of your models are either bulged or rounded off? Generate a hollow square tower and calibrate linear advance the old-fashioned way. This method is as accurate as your ability to count layers and look at how good the layers are, so it is up to 100% accurate. Marlin's line by line (flat) test didn't work for me with flexible filament because the perception of what was happening seemed to have other factors (past a certain value, all of the lines looked the same but uneven until getting to very high values where they were wider on the right but not the middle as is supposed to happen), and the result from that left cut corners on real models.


> If LA is set too low you’ll see "dog bone" bulges in corners rather than neat squares.
> If LA is set too high, corners will look rounded off.

-[Calibrating linear advance with PrusaSlicer](https://projects.ttlexceeded.com/3dprinting_techniques_calibrating_LA.html)

- There is totally different tower using the same technique as LinearAdvanceTowerGenerator at the URL above, but it is not suitable for TPU etc. due to the temperature, speed, and K value range.
