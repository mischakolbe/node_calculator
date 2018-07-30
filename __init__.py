import sys

# Optionally specify the folder where the noca_extension.py file is located, if
# it is moved outside of the node_calculator module.
EXTENSION_PATH = ""
if EXTENSION_PATH and EXTENSION_PATH not in sys.path:
    sys.path.insert(0, EXTENSION_PATH)
