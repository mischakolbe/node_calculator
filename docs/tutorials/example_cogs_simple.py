# EXAMPLE: cogs_simple

import node_calculator.core as noca

"""Task:
Drive all cogs by an attribute on the ctrl.
"""

# Solution 1:
# Direct drive rotation
ctrl = noca.Node("ctrl")
gear_5 = noca.Node("gear_5_geo")
gear_7 = noca.Node("gear_7_geo")
gear_8 = noca.Node("gear_8_geo")
gear_17 = noca.Node("gear_17_geo")
gear_22 = noca.Node("gear_22_geo")

driver = ctrl.add_float("cogRotation") * 10

gear_22.ry = driver / 22.0
gear_5.ry = driver / -5.0
gear_7.ry = driver / 7.0
gear_8.ry = driver / -8.0
gear_17.ry = driver / 17.0


# Solution 2:
# Chained rotation:
ctrl = noca.Node("ctrl")
gear_5 = noca.Node("gear_5_geo")
gear_7 = noca.Node("gear_7_geo")
gear_8 = noca.Node("gear_8_geo")
gear_17 = noca.Node("gear_17_geo")
gear_22 = noca.Node("gear_22_geo")

driver = ctrl.add_float("cogRotation", min=0)

gear_22.ry = driver
gear_8.ry = gear_22.ry * (-22/8.0)
gear_7.ry = gear_8.ry * (-8/7.0)
gear_5.ry = gear_7.ry * (-7/5.0)
gear_17.ry = gear_5.ry * (-5/17.0)
