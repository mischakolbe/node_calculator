# Tab1
# CONVENIENT EXTRAS

import node_calculator.core as noca

a = noca.Node("A_geo")
b = noca.Node("B_geo")
c = noca.Node("C_geo")

# Keywords (see cheatSheet!)
add_result = a.t + [1, 2, 3]
print(add_result.node)
print(add_result.attrs)
print(add_result.attrs_list)
print(add_result.plugs)

noca_list = noca.Node([a.tx, c.tx, b.tz])
print(noca_list.nodes)


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
    print(type(item), item)
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

pm_my_locator = my_locator.to_py_node(ignore_attrs=True)
pm_my_locator = my_locator[1].to_py_node()


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
