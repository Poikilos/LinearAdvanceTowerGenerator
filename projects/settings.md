# Settings

To generate the gcode included in the data directory of the gcodegenerator module, the following Cura 5.1.0 settings were used.
- Printer: JGAURORA A3S


## Position of square20x20 model:
  - X: -49.815
  - Y: 54.021

## Material-specific profiles
### PLA folder
#### Profile
"Normal" except:
- layer height: .2
- retraction: None
- Extra Raft Margin 5 (default was 8)

### TPU folder
- Profile: Siepie Small-Minis profile except:
  - 20 (to make walls run at 10 mm/s which is 25 multiplied by .4 (.08/.2) due to higher layer height--TPU usually prints well at .08 layer height)
  - layer height: .2
  - 3 shells, infill=lines, infill spacing 2mm (N/A for this program since there is only 1 wall; similar to 3D Printing Pro's small minis profile)
  - Extra Raft Margin 5
  - retraction: None
  - Optimize Wall Printing Order
- Material: my "ATARAXIA ART Flexible PLA+" material setting which is generic PLA except:
  - retraction distance: 2.5 (N/A since retraction was off in the profile)
  - Default Printing Temperature: 190
  - Default Build Plate Temperature: 45
  - Density: 1.25 (N/A: only affects price calculation)
  - Filament Cost: 37.09 (N/A: only affects price calculation)
  - Standby Temperature: Unchanged in this g-code, but later changed to 165 since Flexible PLA+ documentation says the melting point is 170 C).
