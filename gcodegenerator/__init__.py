#!/usr/bin/env python3
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
)

options = {
    'start': 0.00,  # LIN_ADVANCE_K on first layer
    'end': 12,  # LIN_ADVANCE_K on last layer
    'delta': .4,  # change LIN_ADVANCE_K per layer
    'raft_height': .94,
    'raft_air_gap': .3,
    # ^ Cura default=.3 but g-code editing cancels that for accurate measurement
    'layer_height': .2,
    'before_start': "; -- START GCODE --",
    'after_start': "; -- end of START GCODE --",
    'before_end': "; -- END GCODE --",
    'after_end': "; -- end of END GCODE --",
    'tower_shape': "square",
    'material': "TPU",
    'before_layer': (
        ";MESH:square 40x40, .48 border (.4 x 1.2overextrusion) 2layers.stl\n"
        "G0 F9000 X27.781 Y32.781 Z{z:.5f}\n"
        ";TYPE:WALL-OUTER\n"
    ),
}

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
    last_raft_E = E


def main():
    done_tower = False
    out_path = ("tower20x20 1layer+raft lh=.2+raft linewidth=.48"
                " (LA K={}to{}).gcode"
                "".format(options['start'], options['end']))
    tower_layer_gcode_lines = None
    z = 0
    material_path = os.path.join(DATA_PATH, options.get('material'))
    if not os.path.isdir(material_path):
        echo0('Error: There is no material profile "{}"'
              ''.format(material_path))
        return 2
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
                K = options['start'] - options['delta']
                layer_no = -1
                before_layer_E = last_raft_E
                abs_E = before_layer_E
                while K < options['end']:
                    layer_no += 1
                    outs.write(";LAYER:{}\n".format(layer_no))
                    z += options['layer_height']
                    K += options['delta']
                    this_K_line = "M900 K{:.5f}".format(K)
                    if not this_K_line.endswith("\n"):
                        this_K_line += "\n"
                    outs.write(this_K_line)
                    before_this = options['before_layer'].format(z=z)
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
                                line = changed_cmd(line, 'E', abs_E)
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


if __name__ == "__main__":
    sys.exit(main())
