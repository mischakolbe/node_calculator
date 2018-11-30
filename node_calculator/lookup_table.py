"""Various lookup tables used in NodeCalculator initialization & evaluation.

:author: Mischa Kolbe <mischakolbe@gmail.com>
"""


# GLOBALS ---
ATTR_TYPES = {
    # All attributeType attributes. From Maya docs:
    # "In general it is best to use the -at [...] for maximum flexibility."
    "bool": {
        "data_type": "attributeType",
    },
    "long": {
        "data_type": "attributeType",
    },
    "short": {
        "data_type": "attributeType",
    },
    "byte": {
        "data_type": "attributeType",
    },
    "char": {
        "data_type": "attributeType",
    },
    "enum": {
        "data_type": "attributeType",
    },
    "float": {
        "data_type": "attributeType",
    },
    "double": {
        "data_type": "attributeType",
    },
    "doubleAngle": {
        "data_type": "attributeType",
    },
    "doubleLinear": {
        "data_type": "attributeType",
    },
    "compound": {
        "data_type": "attributeType",
    },
    "message": {
        "data_type": "attributeType",
    },
    "time": {
        "data_type": "attributeType",
    },
    "fltMatrix": {
        "data_type": "attributeType",
    },
    "reflectance": {
        "data_type": "attributeType",
        "compound": True,
    },
    "spectrum": {
        "data_type": "attributeType",
        "compound": True,
    },
    "float2": {
        "data_type": "attributeType",  # Can also be "dataType"
        "compound": True,
    },
    "float3": {
        "data_type": "attributeType",  # Can also be "dataType"
        "compound": True,
    },
    "double2": {
        "data_type": "attributeType",  # Can also be "dataType"
        "compound": True,
    },
    "double3": {
        "data_type": "attributeType",  # Can also be "dataType"
        "compound": True,
    },
    "long2": {
        "data_type": "attributeType",  # Can also be "dataType"
        "compound": True,
    },
    "long3": {
        "data_type": "attributeType",  # Can also be "dataType"
        "compound": True,
    },
    "short2": {
        "data_type": "attributeType",  # Can also be "dataType"
        "compound": True,
    },
    "short3": {
        "data_type": "attributeType",  # Can also be "dataType"
        "compound": True,
    },

    # All dataType attributes. From Maya docs:
    # "In most cases the -dt version will not display in the attribute editor
    # as it is an atomic type and you are not allowed to change individual
    # parts of it."
    "string": {
        "data_type": "dataType",
    },
    "stringArray": {
        "data_type": "dataType",
    },
    "matrix": {
        "data_type": "dataType",
    },
    "reflectanceRGB": {
        "data_type": "dataType",
    },
    "spectrumRGB": {
        "data_type": "dataType",
    },
    "doubleArray": {
        "data_type": "dataType",
    },
    "floatArray": {
        "data_type": "dataType",
    },
    "Int32Array": {
        "data_type": "dataType",
    },
    "vectorArray": {
        "data_type": "dataType",
    },
    "nurbsCurve": {
        "data_type": "dataType",
    },
    "nurbsSurface": {
        "data_type": "dataType",
    },
    "mesh": {
        "data_type": "dataType",
    },
    "lattice": {
        "data_type": "dataType",
    },
    "pointArray": {
        "data_type": "dataType",
    },
}


# All NcValue concatenation strings
METADATA_CONCATENATION_TABLE = {
    "add": {
        "symbol": "+",
        "associative": True,
    },
    "sub": {
        "symbol": "-",
    },
    "mul": {
        "symbol": "*",
    },
    "div": {
        "symbol": "/",
    },
    "pow": {
        "symbol": "**",
    },
    "eq": {
        "symbol": "==",
    },
    "ne": {
        "symbol": "!=",
    },
    "gt": {
        "symbol": ">",
    },
    "ge": {
        "symbol": ">=",
    },
    "lt": {
        "symbol": "<",
    },
    "le": {
        "symbol": "<=",
    },
}


# All cmds.parent command flags
PARENT_FLAGS = [
    "a", "absolute",
    "add", "addObject",
    "nc", "noConnections",
    "nis", "noInvScale",
    "r", "relative",
    "rm", "removeObject",
    "s", "shape",
    "w", "world",
]
