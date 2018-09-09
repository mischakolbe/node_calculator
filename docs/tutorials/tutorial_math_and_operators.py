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
