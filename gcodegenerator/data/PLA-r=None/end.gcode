M104 S0                 ;turn off nozzle heater
M140 S0                 ;turn off bed heater
G91                     ;set to relative positioning
G1 E-10 F300            ;retract the filament slightly
G90                     ;set to absolute positioning
G28 X0                  ;move to the X-axis origin (Home)
G0 Y200 F600            ;bring the bed to the front for easy print removal
M84                     ;turn off stepper motors
