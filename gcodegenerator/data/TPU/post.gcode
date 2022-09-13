M82 ;absolute extrusion mode
M104 S0
;End of Gcode
;SETTING_3 {"global_quality": "[general]\\nversion = 4\\nname = 3shell TPU based
;SETTING_3  on Siepie Small-Minis\\ndefinition = jgaurora_a3s\\n\\n[metadata]\\n
;SETTING_3 type = quality_changes\\nquality_type = normal\\nsetting_version = 20
;SETTING_3 \\n\\n[values]\\nadhesion_type = raft\\nlayer_height = 0.2\\nlayer_he
;SETTING_3 ight_0 = 0.2\\nsupport_enable = True\\nsupport_structure = tree\\nsup
;SETTING_3 port_type = buildplate\\n\\n", "extruder_quality": ["[general]\\nvers
;SETTING_3 ion = 4\\nname = 3shell TPU based on Siepie Small-Minis\\ndefinition
;SETTING_3 = jgaurora_a3s\\n\\n[metadata]\\ntype = quality_changes\\nquality_typ
;SETTING_3 e = normal\\nintent_category = default\\nposition = 0\\nsetting_versi
;SETTING_3 on = 20\\n\\n[values]\\nacceleration_travel = 5000\\nbottom_layers =
;SETTING_3 =999999 if infill_sparse_density == 100 else math.ceil(round(bottom_t
;SETTING_3 hickness / resolveOrValue('layer_height'), 4))\\nbottom_thickness = 0
;SETTING_3 .47\\nbrim_width = 4\\nconnect_skin_polygons = True\\ncool_fan_full_a
;SETTING_3 t_height = 0\\ninfill_line_distance = =0 if infill_sparse_density ==
;SETTING_3 0 else (infill_line_width * 100) / infill_sparse_density * (2 if infi
;SETTING_3 ll_pattern == 'grid' else (3 if infill_pattern == 'triangles' or infi
;SETTING_3 ll_pattern == 'trihexagon' or infill_pattern == 'cubic' or infill_pat
;SETTING_3 tern == 'cubicsubdiv' else (2 if infill_pattern == 'tetrahedral' or i
;SETTING_3 nfill_pattern == 'quarter_cubic' else (1 if infill_pattern == 'cross'
;SETTING_3  or infill_pattern == 'cross_3d' else (1.6 if infill_pattern == 'ligh
;SETTING_3 tning' else 1)))))\\ninfill_pattern = lines\\ninfill_sparse_density =
;SETTING_3  20\\nmaterial_print_temperature = =default_material_print_temperatur
;SETTING_3 e\\noptimize_wall_printing_order = True\\nraft_margin = 8\\nraft_spee
;SETTING_3 d = 20.0\\nretraction_enable = False\\nskin_monotonic = True\\nspeed_
;SETTING_3 infill = 20.0\\nspeed_print = 20.0\\nspeed_support = 15.0\\nspeed_tra
;SETTING_3 vel = 200\\nsupport_line_width = 0.8\\ntop_bottom_pattern = zigzag\\n
;SETTING_3 top_layers = =0 if infill_sparse_density == 100 else math.ceil(round(
;SETTING_3 top_thickness / resolveOrValue('layer_height'), 4))\\nwall_line_count
;SETTING_3  = 3\\n\\n"]}
