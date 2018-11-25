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
print(a)


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
print(a.ty.get())
print(a.t.get())


# Tab5
# BASICS

import node_calculator.core as noca

# Attribute connection
b = noca.Node("B_geo")
a.translateX = b.scaleY
