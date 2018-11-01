# EXAMPLE: Dynamic colors

import node_calculator.core as noca


"""Task:
Drive color based on translate x, y, z values:
The further into the x/y/z plane: The more r/g/b.
Values below zero/threshold should default to black.
"""

# Easy, but incomplete, due to: minus * minus = positive
b = noca.Node("geo")
b_mat = noca.Node("mat")
multiplier = b.add_float("multiplier", value=0.25, max=0.5)
r_value = b.ty * b.tz * multiplier
g_value = b.tx * b.tz * multiplier
b_value = b.tx * b.ty * multiplier
b_mat.color = [r_value, g_value, b_value]

# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

# Prototype red first.
b = noca.Node("geo")
b_mat = noca.Node("mat")
multiplier = b.add_float("multiplier", value=0.25, max=0.5)
r_value = b.ty * b.tz * multiplier
b_mat.colorR = noca.Op.condition(b.ty > 0, noca.Op.condition(b.tz > 0, r_value, 0), 0)

# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

# Doesn't display correctly in viewport!
b = noca.Node("geo")
b_mat = noca.Node("mat")

multiplier = b.add_float("multiplier", value=0.25, max=0.5)
threshold = 1

tx_zeroed = b.tx - threshold
ty_zeroed = b.ty - threshold
tz_zeroed = b.tz - threshold

r_value = ty_zeroed * tz_zeroed * multiplier
g_value = tx_zeroed * tz_zeroed * multiplier
b_value = tx_zeroed * ty_zeroed * multiplier

black = 0
with noca.Tracer(pprint_trace=True):
    b_mat.color = [
        noca.Op.condition(b.ty > threshold, noca.Op.condition(b.tz > threshold, r_value, black), black),
        noca.Op.condition(b.tz > threshold, noca.Op.condition(b.tx > threshold, g_value, black), black),
        noca.Op.condition(b.tx > threshold, noca.Op.condition(b.ty > threshold, b_value, black), black),
    ]
