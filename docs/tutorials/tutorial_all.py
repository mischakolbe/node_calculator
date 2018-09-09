import node_calculator.core as noca

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# INTRODUCTION


import node_calculator.core as noca

# Initiate Node-objects for all test-geos
a_geo = noca.Node("A_geo")
b_geo = noca.Node("B_geo")
c_geo = noca.Node("C_geo")

# Average all directions of the A-translation
translate_a_average = noca.Op.average(a_geo.tx, a_geo.ty, a_geo.tz)
# Create a "floor collider" based on the height of B
b_height_condition = noca.Op.condition(b_geo.ty > 0, b_geo.ty, 0)

# Drive C-translation by different example-formula for each direction
c_geo.translate = [b_geo.tx / 2 - 2, b_height_condition * 2, translate_a_average]


# ~~~ VS ~~~


from maya import cmds

# Average all directions of the A-translation
var1 = cmds.createNode("plusMinusAverage", name="A_translate_average")
cmds.setAttr(var1 + ".operation", 3)
cmds.connectAttr("A_geo.tx", var1 + ".input3D[0].input3Dx", force=True)
cmds.connectAttr("A_geo.ty", var1 + ".input3D[1].input3Dx", force=True)
cmds.connectAttr("A_geo.tz", var1 + ".input3D[2].input3Dx", force=True)

# Create a "floor collider" based on the height of B
var2 = cmds.createNode("condition", name="height_condition")
cmds.setAttr(var2 + ".operation", 2)
cmds.connectAttr("B_geo.ty", var2 + ".firstTerm", force=True)
cmds.setAttr(var2 + ".secondTerm", 0)
cmds.connectAttr("B_geo.ty", var2 + ".colorIfTrueR", force=True)
cmds.setAttr(var2 + ".colorIfFalseR", 0)

# Drive C-translation by different example-formula for each direction
var3 = cmds.createNode("multiplyDivide", name="half_B_tx")
cmds.setAttr(var3 + ".operation", 2)
cmds.connectAttr("B_geo.tx", var3 + ".input1X", force=True)
cmds.setAttr(var3 + ".input2X", 2)
var4 = cmds.createNode("plusMinusAverage", name="offset_half_b_tx_by_2")
cmds.setAttr(var4 + ".operation", 2)
cmds.connectAttr(var3 + ".outputX", var4 + ".input3D[0].input3Dx", force=True)
cmds.setAttr(var4 + ".input3D[1].input3Dx", 2)
var5 = cmds.createNode("multiplyDivide", name="double_height_condition")
cmds.setAttr(var5 + ".operation", 1)
cmds.connectAttr(var2 + ".outColorR", var5 + ".input1X", force=True)
cmds.setAttr(var5 + ".input2X", 2)
cmds.connectAttr(var4 + ".output3Dx", "C_geo.translateX", force=True)
cmds.connectAttr(var5 + ".outputX", "C_geo.translateY", force=True)
cmds.connectAttr(var1 + ".output3Dx", "C_geo.translateZ", force=True)


# DL from github.com/mischakolbe/node_calculator
# Save to C:\Users\Mischa\Documents\maya\scripts


# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Tab1
# BASICS

import node_calculator.core as noca

# Valid Node instantiations
a = noca.Node("A_geo")
a = noca.Node("A_geo.tx")
a = noca.Node("A_geo", ["ty", "tz", "tx"])
a = noca.Node("A_geo", attrs=["ty", "tz", "tx"])
a = noca.Node(["A_geo.ty", "B_geo.tz", "A_geo.tx"])
# Numbers and lists work as well
a = noca.Node(7)
a = noca.Node([1, 2, 3])

# Created NcNode has a node-& attrs-part
a = noca.Node("A_geo.tx")
print a


# Tab2
# BASICS

import node_calculator.core as noca

# Valid Node instantiations
a = noca.Node("A_geo")

# Attribute setting
a.tx = 7
a.translateX = 6
a.tx.set(3)
a.t = 5
a.t = [1, 2, 3]

# Even if an attribute was specified at initialization...
a = noca.Node("A_geo.ty")
# ...any attribute can be set!
a.sx = 2

# Any attribute works
a.tx = 12
a.translateX = 12
a.visibility = 0
a.thisIsMyAttr = 6


# Tab3
# BASICS

import node_calculator.core as noca

# Caution!
bad = noca.Node("A_geo.tx")
bad = 2.5
good = noca.Node("A_geo")
good.tx = 2.5

a = noca.Node("A_geo.tx")
a.attrs = 3.5
a = noca.Node("A_geo", ["tx", "ty"])
a.attrs = 1
a.attrs = [2, 3]


# Tab4
# BASICS

import node_calculator.core as noca

# Attribute query
print a.ty.get()
print a.t.get()


# Tab5
# BASICS

import node_calculator.core as noca

# Attribute connection
b = noca.Node("B_geo")
a.translateX = b.scaleY


# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Tab1
# MATH

import node_calculator.core as noca

a = noca.Node("A_geo")
b = noca.Node("B_geo")
c = noca.Node("C_geo")

# Simple math operation
a.tx + 2

# Nodes are setup automatically
a.tx - 2

# Multiple math operations
a.tx * 2 + 3

# Assignment of math operation result
c.ty = a.tx * 2 + 3


# Tab2
# MATH

import node_calculator.core as noca

a = noca.Node("A_geo")
b = noca.Node("B_geo")
c = noca.Node("C_geo")

# Correct order of operations. Thanks, Python!
c.ty = a.tx + b.ty / 2
c.ty = (a.tx + b.ty) / 2

# Works with 1D, 2D & 3D. Mixes well with 1D attrs!
c.t = b.t * a.t - [1, 2, 3]
c.t = b.t * a.ty

# Intermediate results ("bad" isn't necessarily bad)
a_third = a.t / 3
c.t = a_third


# Tab3
# MATH

import node_calculator.core as noca

a = noca.Node("A_geo")
b = noca.Node("B_geo")
c = noca.Node("C_geo")

# Additional operations via Op-class
c.tx = noca.Op.length(a.t, b.t)

# Available Operators
help(noca.Op)
noca.Op.available(full=False)
help(noca.Op.length)

# Conditionals are fun
c.t = noca.Op.condition(2 - b.ty > 3, b.t, [0, 3, 0])

# Warning: It's Python!
# Or: "The reason for Nodes of values/lists".
c.t = [a.ty, a.tx, 2] - 5
c.t = [a.ty, a.tx, 2] * [1, 4, b.tx]


# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Tab1
# CONVENIENT EXTRAS

import node_calculator.core as noca

a = noca.Node("A_geo")
b = noca.Node("B_geo")
c = noca.Node("C_geo")

# Keywords (see cheatSheet!)
add_result = a.t + [1, 2, 3]
print add_result.node
print add_result.attrs
print add_result.attrs_list
print add_result.plugs

noca_list = noca.Node([a.tx, c.tx, b.tz])
print noca_list.nodes


# Tab2
# CONVENIENT EXTRAS

import node_calculator.core as noca

# Create nodes as NcNode instances
my_transform = noca.transform("myTransform")
my_locator = noca.locator("myLocator")
my_xy = noca.create_node("nurbsCurve", "myCurve")

# Add attributes
my_transform.add_separator()
offset = my_transform.add_float("offsetValue", min=0, max=3)
space_switch = my_transform.add_enum("spaceSwitch", cases=["local", "world"])
my_locator.t = noca.Op.condition(
    space_switch == 0,
    my_transform.ty * 2 - offset,
    0
)


# Tab3
# CONVENIENT EXTRAS

import node_calculator.core as noca

# NcNodes as iterables
some_node = noca.Node("A_geo", ["tx", "ty"])
for index, item in enumerate(some_node):
    print type(item), item
    item.attrs = index

# Attributes can be accessed via index
some_node[1].attrs = 7

# Work around issue of array-attributes
plus_minus = noca.create_node(
    "plusMinusAverage",
    name="test",
    attrs=["input3D[0].input3Dx"]
)
plus_minus.attrs = 3


# Tab4
# CONVENIENT EXTRAS

import node_calculator.core as noca

# Convert to PyNode
my_locator = noca.locator("myLocator", attrs=["tx", "ty", "tz"])
pm_my_locator = my_locator.to_py_node()

pm_my_locator = my_locator.to_py_node(attrs=False)
pm_my_locator = my_locator[1].to_py_node()
print type(pm_my_locator), pm_my_locator

for attr in my_locator:
    pm_my_locator = attr.to_py_node()
    print type(pm_my_locator), pm_my_locator


# Tab5
# CONVENIENT EXTRAS

import node_calculator.core as noca

a = noca.Node("A_geo")
b = noca.Node("B_geo")

# auto_unravel & auto_consolidate
a = noca.Node("A_geo", auto_unravel=False, auto_consolidate=False)
b = noca.Node("B_geo", auto_unravel=True, auto_consolidate=True)
a.t = b.tx

noca.set_global_auto_unravel(False)
noca.set_global_auto_consolidate(False)


# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Tab1
# TRACER

import node_calculator.core as noca

a = noca.Node("A_geo")
b = noca.Node("B_geo")
c = noca.Node("C_geo")

# This is our lovely formula, but it needs to be faster!
c.ty = a.tx + b.ty / 2


# Tab2
# TRACER
with noca.Tracer() as trace:
    c.ty = a.tx + b.ty / 2
print trace

with noca.Tracer(pprint_trace=True):
    current_val = a.tx.get()
    offset_val = (current_val - 1) / 3
    c.ty = a.tx + b.ty / offset_val


# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# CUSTOMIZE IT

from node_calculator.core import noca_op
from node_calculator.core import _create_operation_node


REQUIRED_EXTENSION_PLUGINS = ["lookdevKit"]

EXTENSION_OPERATORS = {
    "color_math_min": {
        "node": "colorMath",
        "inputs": [
            ["colorAR", "colorAG", "colorAB"],
            ["alphaA"],
            ["colorBR", "colorBG", "colorBB"],
            ["alphaB"],
        ],
        "outputs": [
            ["outColorR", "outColorG", "outColorB"],
            # ["outAlpha"], ?
        ],
        "operation": 4,
    },
}


@noca_op
def color_math_min(color_a, alpha_a=0.25, color_b=(0, 0, 1), alpha_b=0.75):
    created_node = _create_operation_node(
        'color_math_min', color_a, alpha_a, color_b, alpha_b
    )
    return created_node


# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Tab1
# UNDER THE HOOD


import node_calculator.core as noca

_node = noca.Node("A_geo")
print 'Type of noca.Node("A_geo"):', type(_node)

_attr = noca.Node("A_geo").tx
print 'Type of noca.Node("A_geo").tx:', type(_attr)

_node_list = noca.Node(["A_geo", "B_geo"])
print 'Type of noca.Node(["A_geo", "B_geo"]):', type(_node_list)

_int = noca.Node(7)
print 'Type of noca.Node(7):', type(_int)

_float = noca.Node(1.2)
print 'Type of noca.Node(1.2):', type(_float)

_list = noca.Node([1, 2, 3])
print 'Type of noca.Node([1, 2, 3]):', type(_list)


# Tab2
# UNDER THE HOOD

# NcNode vs NcAttrs
nc_node = noca.Node("A_geo.translateX")

nc_attr = nc_node.scaleY
nc_attr.extra
# or:
nc_node.scaleY.extra


plus_minus = noca.create_node("plusMinusAverage", "test")
plus_minus = noca.Node(plus_minus, "input3D[0]")
plus_minus.attrs.input3Dx = 8


# Tab3
# UNDER THE HOOD

# NcValues
# This does NOT work:
normal_int = 1
normal_int.marco = "polo"

# This works:
noca_int = noca.Node(1)
noca_int.marco = "polo"
noca_int.metadata
noca_int.created_by_user

# Keeping track of origin of values:
scale = cmds.getAttr("A_geo.scaleX")
translate = cmds.getAttr("A_geo.translateX")
print scale.metadata
print translate.metadata
# vs
a_geo = noca.Node("A_geo")
with noca.Tracer():
    scale = a_geo.scaleX.get()
    translate = a_geo.translateX.get()

    a_geo.tx = scale + translate

print scale.metadata
print translate.metadata


# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# EXAMPLE: nodeCalculatorExample_cogsA_v001
import node_calculator.core as noca

"""
Drive all cogs by an attribute on the ctrl.
"""

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


# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# EXAMPLE: Dynamic colors
import node_calculator.core as noca
reload(noca)

"""
Drive color based on translate x, y, z values:
The further into the x/y/z plane: The more r/g/b.
Values below zero/threshold should default to black.
"""

# Easy, but minus * minus = positive allows negative areas.
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


# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# EXAMPLE: nodeCalculatorExample_cogsB_v002
import node_calculator.core as noca

"""
Drive all cogs by an attribute on the ctrl.
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















