# EXAMPLE: cogs_stepping

import node_calculator.core as noca

"""Task:
Drive all cogs by an attribute on the ctrl. All teeth but one were removed from
one of the cogs(!)

Uses maya_math_nodes extension!
"""

# Initialize nodes.
main_rot = noca.Node("ctrl.cogRot") * 100
cog_5 = noca.Node("gear_5_geo")
cog_7 = noca.Node("gear_7_geo")
cog_8 = noca.Node("gear_8_geo")
cog_22 = noca.Node("gear_22_geo")
cog_17 = noca.Node("gear_17_geo")

# Basic cog-rotation of small and big cog.
cog_5.ry = main_rot / 5.0
cog_7.ry = main_rot / -7.0
cog_22.ry = main_rot / -22.0

# Make rotation positive (cog_22 increases in negative direction).
single_tooth_rot = - cog_22.ry

# Dividing single_tooth_rot by 360deg and ceiling gives number of steps.
step_count = noca.Op.floor(noca.Op.divide(single_tooth_rot, 360))

single_tooth_degrees_per_step = 360 / 8.0
receiving_degrees_per_step = single_tooth_degrees_per_step / 17.0 * 8
stepped_receiving_rot = step_count * receiving_degrees_per_step
single_tooth_live_step_rotation = noca.Op.modulus_int(single_tooth_rot, single_tooth_degrees_per_step)
receiving_live_step_rotation = single_tooth_live_step_rotation / 17.0 * 8
rot_offset = 1

cog_17.ry = noca.Op.condition(
    # At every turn of the single tooth gear: Actively rotate the receiving gear during degrees_per_step degrees (45deg).
    noca.Op.modulus_int(single_tooth_rot, 360) < single_tooth_degrees_per_step,
    # When live rotation is happening the current step rotation is added to the accumulated stepped rotation.
    stepped_receiving_rot + receiving_live_step_rotation + rot_offset,
    # Static rotation if single tooth gear isn't driving. Needs an extra step since step_count is floored.
    stepped_receiving_rot + receiving_degrees_per_step + rot_offset
)

cog_8.ry = cog_17.ry / -8.0 * 17
