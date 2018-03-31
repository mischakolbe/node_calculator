# node_calculator
Create Maya node-network by entering a math-formula.

### Why use it?
Turn those long lists of cmds.createNode, cmds.setAttr & cmds.connectAttr into readable math formulas.

### Attention:
Major change merged on 30th of March 2018. Changing from a single file to a module (folder).

Before:
import node_calculator as noca
Now:
from node_calculator import core as noca

### Features:
* Supports
  * basic math operators: +, -, *, /, **
  * conditions
  * length
  * average
  * dot- & cross-product
  * vector normalization
  * multiply matrix
  * compose & decompose matrix
  * blend
  * remap
  * clamp
  * choice
* Add attributes on the fly
  * add_bool
  * add_int
  * add_float
  * add_enum
* Easy to add proprietary nodes
* Tracer
* Container (this is pretty useless until Maya revamps them!)

### Tutorial:
* [Introduction](https://vimeo.com/242716233)
* [Basics](https://vimeo.com/242716219)
* [Math](https://vimeo.com/242716234)
* [Tracer](https://vimeo.com/242716237)
* [Expanding it](https://vimeo.com/242716230)
* [Example](https://vimeo.com/242716227)


### Install:
Simply save the node_calculator folder to your \Documents\maya\scripts folder

### Usage:
Make sure you have these 2 nodes in your scene: "testA_geo" and "testB_geo" and run some of the example Python code:

```
from node_calculator import core as noca

# Valid Node instantiation
a = noca.Node("testA_geo")
b = noca.Node("testB_geo")

# Attribute setting
a.tx = 7
a.tx.set(3)
a.t = [1, 2, 3]

# Attribute query
print a.ty.get()
print a.t.get()

# Attribute connection
a.t = b.s

# Math
b.ty = a.tx * 2 + 3

# Additional operations via Op-class
a.t = noca.Op.condition(2 - b.ty > 3, b.t, [0, 3, 0])
```

### Tested with:
* Maya 2016

### Think this is useful? Share the love and buy me a hot chocolate :)
[![Donate](https://img.shields.io/badge/Donate-PayPal-green.svg)](https://paypal.me/mischakolbe1)