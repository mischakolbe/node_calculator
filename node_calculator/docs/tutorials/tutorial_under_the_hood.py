# Tab1
# UNDER THE HOOD


import node_calculator.core as noca

_node = noca.Node("A_geo")
print('Type of noca.Node("A_geo"):', type(_node))

_attr = noca.Node("A_geo").tx
print('Type of noca.Node("A_geo").tx:', type(_attr))

_node_list = noca.Node(["A_geo", "B_geo"])
print('Type of noca.Node(["A_geo", "B_geo"]):', type(_node_list))

_int = noca.Node(7)
print('Type of noca.Node(7):', type(_int))

_float = noca.Node(1.2)
print('Type of noca.Node(1.2):', type(_float))

_list = noca.Node([1, 2, 3])
print('Type of noca.Node([1, 2, 3]):', type(_list))


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
from maya import cmds
scale = cmds.getAttr("A_geo.scaleX")
translate = cmds.getAttr("A_geo.translateX")
print(scale.metadata)
print(translate.metadata)
# vs
a_geo = noca.Node("A_geo")
with noca.Tracer():
    scale = a_geo.scaleX.get()
    translate = a_geo.translateX.get()

    a_geo.tx = scale + translate

print(scale.metadata)
print(translate.metadata)
