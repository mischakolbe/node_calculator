# node_calculator
Create Maya node-network by entering a math-formula.

### Why use it?
Turn those long lists of cmds.createNode, cmds.setAttr & cmds.connectAttr into readable math formulas.

### Features:
* Supports 
  * basic math operators: +, -, *, /, **
  * conditions
  * length
  * average
  * dot- & cross-product
  * blend
  * remap
  * clamp
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
Simply save the node_calculator.py to your \Documents\maya\scripts folder

###Usage
In a Python-tab in Maya's Script Editor execute

```
import node_calculator as noca

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

### To Do:
* Reduce connections of compound-attributes (plusMinusAverage, etc.)
* Node-name independence -> PyMel

### Think this is useful? Share the love and buy me a hot chocolate :)
[![Donate](https://img.shields.io/badge/Donate-PayPal-green.svg)](https://paypal.me/mischakolbe1)
