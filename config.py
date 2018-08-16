"""Basic NodeCalculator settings."""


# Node preferences ---
NODE_PREFIX = "nc"


# Attribute preferences ---
DEFAULT_SEPARATOR_NAME = "________"
DEFAULT_SEPARATOR_VALUE = "________"
DEFAULT_ATTR_FLAGS = {
    "keyable": True,
}


# Connection preferences ---
GLOBAL_AUTO_CONSOLIDATE = True
GLOBAL_AUTO_UNRAVEL = True


# Tracer preferences ---
VARIABLE_PREFIX = "var"
VALUE_PREFIX = "val"


# Extension preferences ---
# No path means the NodeCalculator will only check for the extension locally.
EXTENSION_PATH = ""
EXTENSION_NAME = "noca_extension"
