# NodeCalculator
This OpenSource Python module allows you to create node networks in Autodesk Maya by writing math formulas.

### Why use it?
Turn those long lists of cmds.createNode, cmds.setAttr & cmds.connectAttr into readable math formulas.

### All you need: Tutorials, CheatSheet, etc.
[Documentation on ReadTheDocs](https://node-calculator.readthedocs.io/en/latest/)

### Install & Import
Download or clone this git-repo. Save the **inner** `node_calculator` folder (the one that contains core.py, etc.) to your `\Documents\maya\scripts` folder.

Also you can git clone the repo to a location of your choice then while in the top folder run `mayapy -m pip install .`
This will make sure it is installed in maya's site-packages directory.  Optionally you can install it in your userScripts:
`mayapy -m pip install . -t /path/to/your/userScriptsDirectory/`
Note: Make sure to run in a terminal/console that has administrator privileges if Maya is installed in a write-protected folder.

### Usage
Import it in Maya via

```python
import node_calculator.core as noca
```

### CI tested with:
* Maya 2020
* Maya 2019
* Maya 2018
* Maya 2017

(Thank you [Marcus Ottosson](https://github.com/mottosso) for your crazy helpful [Docker images](https://github.com/mottosso/docker-maya))

### Run Tests
If you are developing the NodeCalculator further, you can run the test suite to check whether the basic functionality is still intact.
To do so, navigate to the bin-folder in your Maya directory. For example:
`C:\Program Files\Autodesk\Maya2018\bin`
And run this command in a terminal:
`.\mayapy.exe -m unittest discover -s >path\to\node_calculator\tests< -v`

### Think this is useful? I won't say no, if you insist on buying me a hot chocolate ;P
[![Donate](https://img.shields.io/badge/Donate-PayPal-green.svg)](https://paypal.me/mischakolbe1)
