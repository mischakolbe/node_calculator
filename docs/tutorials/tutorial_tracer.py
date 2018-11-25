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
print(trace)

with noca.Tracer(pprint_trace=True):
    current_val = a.tx.get()
    offset_val = (current_val - 1) / 3
    c.ty = a.tx + b.ty / offset_val
