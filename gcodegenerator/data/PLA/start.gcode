G21                     ;set units to millimetres
G90                     ;set to absolute positioning
M106 S0                 ;set fan speed to zero (turned off)
G28                     ;home all axis
G92 E0                  ;zero the extruded length
G1 Z1 F1000             ;move up slightly
G1 X60.0 Z0 E9.0 F1000.0;intro line
G1 X100.0 E21.5 F1000.0 ;continue line
G92 E0                  ;zero the extruded length again
