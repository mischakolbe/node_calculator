import sys

EXTENSION_PATH = ""
if EXTENSION_PATH and EXTENSION_PATH not in sys.path:
    sys.path.insert(0, EXTENSION_PATH)
