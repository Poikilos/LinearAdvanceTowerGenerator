#!/usr/bin/env python3
"""
LinearAdvanceTowerGenerator
---------------------------
Generate a linear advance tower from an existing sliced G-code file.

After generating a tower, open readme.md in your favorite text editor
and follow the instructions. When you find the best layer than is
sharp but not bulged and smooth but not rounded, use the z value to
calculate the K value of that layer. Then in a 3D printer terminal
(such as Pronterface available as part of Printrun, or OctoPrint
Terminal), or by sending a one-line G-code file to your printer enter
the following G-code:

M900 Kv ; (where v is a number, the K value you calculated)
; Then you can run the following G-code to save the value for every
; session (K should be calibrated for each filament generally, but is
; often the same or close for each type of filament even if using
; different brands):
M500  ; save settings to firmware (preserve K on reboot)
; Use the "M900" command without any options to check your current K.

Usage:
python run.pyw [options]

Options:
--help (or /?)  Show this help screen.
--first         K ([value] for M900 K[value]; M500 ;to save) on layer 1
                (not including  raft layers)
--last          K on last layer
--step          K change per l
--raft_height   Raft height in your input G-code
--raft_air_gap  Assume first layer z is this much higher than top of
                  raft (the real difference may be smaller than the
                  air gap in your slicer settings due to settling)
layer_height    The height of each layer
"""
from __future__ import print_function
import sys
import os
import decimal
from decimal import Decimal


def echo0(*args, **kwargs):
    print(*args, file=sys.stderr, **kwargs)
    return True


def echo1(*args, **kwargs):
    if verbosity < 1:
        return False
    print(*args, file=sys.stderr, **kwargs)
    return True


def echo2(*args, **kwargs):
    if verbosity < 2:
        return False
    print(*args, file=sys.stderr, **kwargs)
    return True


MODULE_PATH = os.path.dirname(os.path.realpath(__file__))
DATA_PATH = os.path.join(MODULE_PATH, "data")
REPO_PATH = os.path.dirname(MODULE_PATH)
REPOS_PATH = os.path.dirname(REPO_PATH)
try_modules_path = os.path.join(REPOS_PATH, "TemperatureTowerProcessor")
if os.path.isfile(os.path.join(try_modules_path, "gcodefollower.py")):
    sys.path.insert(0, try_modules_path)
elif os.path.isdir(os.path.join(try_modules_path, "gcodefollower")):
    sys.path.insert(0, try_modules_path)

assert os.path.isdir(DATA_PATH)

try:
    import gcodefollower
except ImportError as ex:
    # echo0(str(ex))
    echo0("Error: This program requires the gcodefollower module from TemperatureTowerProcessor.")
    raise ex

from gcodefollower import (
    get_cmd_meta,
    cmd_meta_dict,
    changed_cmd,
    round_nearest_d,
)

options = {
    'first': Decimal(0.00),  # LIN_ADVANCE_K on first layer
    'last': Decimal(round_nearest_d(Decimal(2), 2)), # LIN_ADVANCE_K (rounded)
    'step': Decimal(.02),  # change LIN_ADVANCE_K per layer
    'raft_height': Decimal(.94),
    'raft_air_gap': Decimal(.0), # ^ Cura default=.3 but editing cancels that for accurate measurement
    # TODO: The way air gap seems to work is that the first layer is air-printed but
    #   the second layer is printed +layer_height from where layer 1 would've been
    #   without the air gap.
    'layer_height': Decimal(.2),
    'before_start': "; -- START GCODE --",
    'after_start': "; -- end of START GCODE --",
    'before_end': "; -- END GCODE --",
    'after_end': "; -- end of END GCODE --",
    'tower_shape': "square",
    'material': "PLA",  # TPU
    'before_layer': (
        ";MESH:square 40x40, .48 border (.4 x 1.2overextrusion).stl\n"
        # "G0 F9000 X27.781 Y32.781 Z{z}\n"
        "G0 F5400 X27.966 Y28.76 Z{z}\n"
        ";TYPE:WALL-OUTER\n"
    ),
    # ^ normally "G0 F5400 X27.966 Y28.76 Z{z}" for PLA
    # ^   # {z} changed using precision later
    'precision': 5,
}

"""
options_help = {
    'first': "K ([value] for M900 K[value]; M500 ;to save) on first layer",
    'last': "K on last layer",
    'step': "K change per l",
    'raft_height': "Raft height in your input G-code",
    'raft_air_gap': ("Assume first layer z is this much higher than raft"
                     " (real difference may be smaller than slicer air gap"
                     " due to settling)"),
    'layer_height': "The height of each layer",
}
"""

def usage():
    echo0(__doc__)
    """
    for key, value in options:
        help_s = options_help.get(key)
        if help_s is not None:
            echo0("{} -- {}".format(key, help_s))
    """


chunk_order = [
    "prep",
    "start",
    "before_raft",
    "raft",
    "before_meshes",
    "<tower>",
    "after_meshes",
    "end",
    "post",
]


last_raft_E = 0


def get_e(gcode):
    '''
    Get the last E value in the gcode, otherwise None if there is no
    extrusion command.

    Sequential arguments:
    gcode -- The command string or list of commands.
    '''
    E = None
    if isinstance(gcode, str):
        gcode = [gcode]
    elif (not isinstance(gcode, list)) and (not isinstance(gcode, tuple)):
        raise ValueError("gcode must be a string or list/tuple of strings.")
    for rawL in gcode:
        line = rawL.strip()
        if line.startswith(";"):
            continue
        if len(line) == 0:
            continue
        meta = get_cmd_meta(line)
        '''
        if meta is None:
            # blank line
            continue
        '''
        if len(meta) < 1:
            continue
        if meta[0] != ["G", "1"]:
            continue
        for pair in meta:
            if pair[0] == "E":
                E_str = pair[1]
                E = Decimal(E_str)
    return E


def save_starting_e(gcode):
    global last_raft_E
    E = get_e(gcode)
    if E is None:
        return
    last_raft_E = Decimal(E)


def save_tower(out_path, options):
    done_tower = False
    tower_layer_gcode_lines = None
    z = 0
    material_path = os.path.join(DATA_PATH, options.get('material'))
    print('material_path="{}"'.format(material_path))
    if not os.path.isdir(material_path):
        echo0('Error: There is no material profile "{}"'
              ''.format(material_path))
        return 2
    precision = options['precision']
    before_layer_fmt = options['before_layer'].replace(
        "{z}",
        "{z:."+str(precision)+"f}"
    )
    with open(out_path, 'w') as outs:
        for chunk in chunk_order:
            generic_key = chunk
            in_name = chunk + ".gcode"
            if chunk == "<tower>":
                in_name = options['tower_shape'] + ".gcode"
                generic_key = "meshes"

            before_key = 'before_' + generic_key
            before = options.get(before_key)
            if before is not None:
                if not before.endswith("\n"):
                    before += "\n"
                outs.write(before)

            in_path = os.path.join(material_path, in_name)
            if chunk == "<tower>":
                if tower_layer_gcode_lines is None:
                    with open(in_path, 'r') as ins:
                        tower_layer_gcode_lines = []
                        for rawL in ins:
                            line = rawL
                            tower_layer_gcode_lines.append(line)
                z = options['raft_height']
                z += options['raft_air_gap']
                # ^ ok since incremented before any extrusion below
                K = options['first'] - options['step']
                layer_no = -1
                before_layer_E = last_raft_E
                abs_E = before_layer_E
                while K < options['last']:
                    layer_no += 1
                    outs.write(";LAYER:{}\n".format(layer_no))
                    z += options['layer_height']
                    K += options['step']
                    K_fmt = "M900 K{:." + str(precision) + "f}"
                    this_K_line = K_fmt.format(K)
                    if not this_K_line.endswith("\n"):
                        this_K_line += "\n"
                    outs.write(this_K_line)
                    before_this = options['before_layer'].format(z=round_nearest_d(z, precision))
                    if not before_this.endswith("\n"):
                        before_this += "\n"
                    outs.write(before_this)
                    for rawL in tower_layer_gcode_lines:
                        line = rawL.strip()
                        if not line.startswith(";"):
                            meta = get_cmd_meta(line)
                            meta_dict = cmd_meta_dict(meta)
                            E = Decimal(meta_dict.get('E'))
                            if E is not None:
                                relative_E = E - last_raft_E
                                abs_E = before_layer_E + relative_E
                                line = changed_cmd(line, 'E', abs_E, precision=precision)
                        if not line.endswith("\n"):
                            line += "\n"
                        outs.write(line)
                    before_layer_E = abs_E
                    # Write square.gcode (or other) multiple times then
                    #   continue to the next chunk.
                done_tower = True
                continue
            with open(in_path, 'r') as ins:
                for rawL in ins:
                    line = rawL
                    if not done_tower:
                        save_starting_e(line)
                    if not line.endswith("\n"):
                        line += "\n"
                    outs.write(line)
            after_key = 'after_' + generic_key
            after = options.get(after_key)
            if after is not None:
                if not after.endswith("\n"):
                    after += "\n"
                outs.write(after)
                if not done_tower:
                    save_starting_e(after.split("\n"))
        h = z + options['layer_height']
        print("height={}".format(h))
        sys.stderr.write('wrote "{}"\n'.format(os.path.realpath(out_path)))
        return 0
    sys.stderr.write("failed\n")
    return 1


def main():
    options_changed = False
    key = None
    for argi in range(1, len(sys.argv)):
        arg = sys.argv[argi]

        if arg in ["--help", "/?"]:
            usage()
            return 0
        elif arg.startswith("--"):
            if key is not None:
                # Show the missing value after key error (after loop)
                break
            if "=" in arg:
                echo0(
                    "Error: Specify an option value after space: --option value"
                )
                return 1
            key = arg[2:]
            if key not in options:
                usage()
                echo0(
                    "Error: '{}' is not a valid option.".format(key)
                )
                return 1
        elif key is not None:
            options_changed = True
            if isinstance(options[key], str):
                options[key] = arg
            elif isinstance(options[key], Decimal):
                options[key] = Decimal(arg)
            elif isinstance(options[key], int):
                options[key] = int(arg)
            else:
                raise NotImplementedError(
                    "Option input doesn't account for setting {} since"
                    " its type is {}."
                    "".format(key, type(options[key]).__name__)
                )
            key = None
    if key is not None:
        echo0(
            "Error: You must specify a space then a value after"
            " --{}".format(key)
        )
        return 1

    del key
    out_path = (
        "tower20x20 +{}raft+{}gap lh={} linewidth=.48"
        " (LA K={}to{} step={}).gcode"
        "".format(
            round_nearest_d(Decimal(options['raft_height']), 2),
            round_nearest_d(Decimal(options['raft_air_gap']), 2),
            round_nearest_d(Decimal(options['layer_height']), 2),
            round_nearest_d(Decimal(options['first']), 2),
            round_nearest_d(Decimal(options['last']), 2),
            round_nearest_d(Decimal(options['step']), 2),
        )
    )
    code = save_tower(out_path, options)
    if code == 0:
        if not options_changed:
            echo0("Specify --help or /? after the command to see all options.")
    return code


if __name__ == "__main__":
    sys.exit(main())
