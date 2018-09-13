"""Basic NodeCalculator settings."""


# Node preferences ---
NODE_PREFIX = "nc"  # Name prefix for all nodes created by the NodeCalculator.


# Attribute preferences ---
DEFAULT_SEPARATOR_NAME = "________"  # Default NiceName for separator-attributes.
DEFAULT_SEPARATOR_VALUE = "________"  # Default value for separator-attributes.
DEFAULT_ATTR_FLAGS = {  # Defaults for add_float(), add_enum(), ... attribute creation.
    "keyable": True,
}


# Connection preferences ---
GLOBAL_AUTO_CONSOLIDATE = True  # Reduce plugs to parent plug, if possible.
GLOBAL_AUTO_UNRAVEL = True  # Expand plugs into their child components. I recommend using True!


# Tracer preferences ---
VARIABLE_PREFIX = "var"  # Prefix for variables in the Tracer-stack (created nodes).
VALUE_PREFIX = "val"  # Prefix for values in the Tracer-stack (queried values).


# Extension preferences ---
EXTENSION_PATH = ""  # Without a path the NodeCalculator will check for the extension(s) locally.
# All extension files must live in the same location!
EXTENSION_NAMES = []  # Names of the extension python files (without .py).
