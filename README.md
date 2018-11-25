# NodeCalculator
This OpenSource Python module allows you to create node networks in Autodesk Maya by writing math formulas.

### Why use it?
Turn those long lists of cmds.createNode, cmds.setAttr & cmds.connectAttr into readable math formulas.

### All you need: Tutorials, CheatSheet, etc.
[Documentation on ReadTheDocs](https://node-calculator.readthedocs.io/en/latest/)

### Install & Import
Download or clone this git-repo. Save the inner `node_calculator` folder to your `\Documents\maya\scripts` folder (Make sure the folder is called **node_calculator**, not node_calculator-master or so).

Also you can git clone the repo to a location of your choice then while in the top folder run `mayapy -m pip install .`
This will make sure it is installed in maya's site-packages directory.  Optionally you can install it in your userScripts:
`mayapy -m pip install . -t /path/to/your/userScriptsDirectory/`
Note: Make sure to run in a terminal/console that has administrator privileges if Maya is installed in a write-protected folder.

### Usage
Import it in Maya via

```python
import node_calculator.core as noca
```

### Tested with
* Maya 2018
* Maya 2017
* Maya 2016

### Run Tests
After installing node_calculator if you want to run the test suite just run:
`mayapy -m unittest discover path/to/node_calculator/tests`
Just make sure the path is the 'path/to/node_calculator/tests' is the tests directory inside the top level directory.

### Think this is useful? Share the love and buy me a hot chocolate ;P
[![Donate](https://img.shields.io/badge/Donate-PayPal-green.svg)](https://paypal.me/mischakolbe1)
