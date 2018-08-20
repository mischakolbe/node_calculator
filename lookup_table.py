"""Various lookup tables used in NodeCalculator initialization & evaluation.

:author: Mischa Kolbe <mischakolbe@gmail.com>
"""


# GLOBALS ---
# Any Maya plugin that should be loaded for the NodeCalculator
BASIC_REQUIRED_PLUGINS = ["matrixNodes"]

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


# Dict of all available operations: used node-type, inputs, outputs, etc.
BASIC_OPERATORS = {}


# BASIC_OPERATORS ---
def _basic_operators_init():
    """Fill BASIC_OPERATORS-dictionary with all available operations.

    Note:
        BASIC_OPERATORS holds the data for each available operation:
        the necessary node-type, its inputs, outputs, etc.
        This unified data enables to abstract node creation, connection, ..

        possible flags:
        - node: Type of Maya node necessary
        - inputs: input attributes (list of lists)
        - outputs: output attributes (list)
        - operation: set operation-attr for different modes of a node
        - output_is_predetermined: should always ALL output attrs be added?

        Use "{array}" in inputs or outputs to denote an array-attribute!
    """
    global BASIC_OPERATORS

    BASIC_OPERATORS = {
        "angle_between": {
            "node": "angleBetween",
            "inputs": [
                ["vector1X", "vector1Y", "vector1Z"],
                ["vector2X", "vector2Y", "vector2Z"],
            ],
            "outputs": [
                ["angle"],
            ],
        },

        "average": {
            "node": "plusMinusAverage",
            "inputs": [
                [
                    "input3D[{array}].input3Dx",
                    "input3D[{array}].input3Dy",
                    "input3D[{array}].input3Dz"
                ],
            ],
            "outputs": [
                ["output3Dx", "output3Dy", "output3Dz"],
            ],
            "operation": 3,
        },

        "blend": {
            "node": "blendColors",
            "inputs": [
                ["color1R", "color1G", "color1B"],
                ["color2R", "color2G", "color2B"],
                ["blender"],
            ],
            "outputs": [
                ["outputR", "outputG", "outputB"],
            ],
        },

        "choice": {
            "node": "choice",
            "inputs": [
                ["input[{array}]"],
                ["selector"],
            ],
            "outputs": [
                ["output"],
            ],
        },

        "clamp": {
            "node": "clamp",
            "inputs": [
                ["inputR", "inputG", "inputB"],
                ["minR", "minG", "minB"],
                ["maxR", "maxG", "maxB"],
            ],
            "outputs": [
                ["outputR", "outputG", "outputB"],
            ],
        },

        "compose_matrix": {
            "node": "composeMatrix",
            "inputs": [
                ["inputTranslateX", "inputTranslateY", "inputTranslateZ"],
                ["inputRotateX", "inputRotateY", "inputRotateZ"],
                ["inputScaleX", "inputScaleY", "inputScaleZ"],
                ["inputShearX", "inputShearY", "inputShearZ"],
                ["inputRotateOrder"],
                ["useEulerRotation"],
            ],
            "outputs": [
                ["outputMatrix"],
            ],
        },

        "decompose_matrix": {
            "node": "decomposeMatrix",
            "inputs": [
                ["inputMatrix"],
            ],
            "outputs": [
                ["outputTranslateX", "outputTranslateY", "outputTranslateZ"],
                ["outputRotateX", "outputRotateY", "outputRotateZ"],
                ["outputScaleX", "outputScaleY", "outputScaleZ"],
                ["outputShearX", "outputShearY", "outputShearZ"],
            ],
            "output_is_predetermined": True,
        },

        "inverse_matrix": {
            "node": "inverseMatrix",
            "inputs": [
                ["inputMatrix"],
            ],
            "outputs": [
                ["outputMatrix"],
            ],
        },

        "length": {
            "node": "distanceBetween",
            "inputs": [
                ["point1X", "point1Y", "point1Z"],
                ["point2X", "point2Y", "point2Z"],
            ],
            "outputs": [
                ["distance"],
            ],
        },

        "matrix_distance": {
            "node": "distanceBetween",
            "inputs": [
                ["inMatrix1"],
                ["inMatrix2"],
            ],
            "outputs": [
                ["distance"],
            ],
        },

        "mult_matrix": {
            "node": "multMatrix",
            "inputs": [
                [
                    "matrixIn[{array}]"
                ],
            ],
            "outputs": [
                ["matrixSum"],
            ],
        },

        "normalize_vector": {
            "node": "vectorProduct",
            "inputs": [
                ["input1X", "input1Y", "input1Z"],
                ["normalizeOutput"],
            ],
            "outputs": [
                ["outputX", "outputY", "outputZ"],
            ],
            "operation": 0,
        },

        "pair_blend": {
            "node": "pairBlend",
            "inputs": [
                ["inTranslateX1", "inTranslateY1", "inTranslateZ1"],
                ["inRotateX1", "inRotateY1", "inRotateZ1"],
                ["inTranslateX2", "inTranslateY2", "inTranslateZ2"],
                ["inRotateX2", "inRotateY2", "inRotateZ2"],
                ["weight"],
                ["rotInterpolation"],
            ],
            "outputs": [
                ["outTranslateX", "outTranslateY", "outTranslateZ"],
                ["outRotateX", "outRotateY", "outRotateZ"],
            ],
            "output_is_predetermined": True,
        },

        "point_matrix_mult": {
            "node": "pointMatrixMult",
            "inputs": [
                ["inPointX", "inPointY", "inPointZ"],
                ["inMatrix"],
                ["vectorMultiply"],
            ],
            "outputs": [
                ["outputX", "outputY", "outputZ"],
            ],
        },

        "remap_value": {
            "node": "remapValue",
            "inputs": [
                ["inputValue"],
                ["outputMin"],
                ["outputMax"],
                ["inputMin"],
                ["inputMax"],
            ],
            "outputs": [
                ["outValue"],
            ],
        },

        "set_range": {
            "node": "setRange",
            "inputs": [
                ["valueX", "valueY", "valueZ"],
                ["minX", "minY", "minZ"],
                ["maxX", "maxY", "maxZ"],
                ["oldMinX", "oldMinY", "oldMinZ"],
                ["oldMaxX", "oldMaxY", "oldMaxZ"],
            ],
            "outputs": [
                ["outValueX", "outValueY", "outValueZ"],
            ],
        },

        "transpose_matrix": {
            "node": "transposeMatrix",
            "inputs": [
                ["inputMatrix"],
            ],
            "outputs": [
                ["outputMatrix"],
            ],
        },
    }

    # Fill BASIC_OPERATORS with condition operations
    cond_operators = ["eq", "ne", "gt", "ge", "lt", "le"]
    for i, condition_operator in enumerate(cond_operators):
        BASIC_OPERATORS[condition_operator] = {
            "node": "condition",
            "inputs": [
                ["firstTerm"],
                ["secondTerm"],
            ],
            # The condition node is a special case! It gets created during
            # the magic-method-comparison and fully connected after being
            # passed on to the condition()-method in this OperatorMetaClass
            "outputs": [
                [None],
            ],
            "operation": i,
        }

    # Fill BASIC_OPERATORS with +,- operations
    for i, add_sub_operator in enumerate(["add", "sub"]):
        BASIC_OPERATORS[add_sub_operator] = {
            "node": "plusMinusAverage",
            "inputs": [
                [
                    "input3D[{array}].input3Dx",
                    "input3D[{array}].input3Dy",
                    "input3D[{array}].input3Dz"
                ],
            ],
            "outputs": [
                ["output3Dx", "output3Dy", "output3Dz"],
            ],
            "operation": i + 1,
        }

    # Fill BASIC_OPERATORS with *,/,** operations
    for i, mult_div_operator in enumerate(["mul", "div", "pow"]):
        BASIC_OPERATORS[mult_div_operator] = {
            "node": "multiplyDivide",
            "inputs": [
                ["input1X", "input1Y", "input1Z"],
                ["input2X", "input2Y", "input2Z"],
            ],
            "outputs": [
                ["outputX", "outputY", "outputZ"],
            ],
            "operation": i + 1,
        }

    # Fill BASIC_OPERATORS with vectorProduct operations
    for i, vector_product_operator in enumerate(["dot", "cross"]):
        BASIC_OPERATORS[vector_product_operator] = {
            "node": "vectorProduct",
            "inputs": [
                ["input1X", "input1Y", "input1Z"],
                ["input2X", "input2Y", "input2Z"],
                ["normalizeOutput"],
            ],
            "outputs": [
                ["outputX", "outputY", "outputZ"],
            ],
            "operation": i + 1,
        }


_basic_operators_init()


# Little helper to print all available Operators for the core.py-docString.
if __name__ == "__main__":
    AVAILABLE_BASIC_OPERATORS = [
        "add", "sub",
        "div", "mul",
        "pow",
        "le", "eq", "ge", "gt", "lt", "ne",
    ]
    for op in sorted(BASIC_OPERATORS.keys()):
        if op not in AVAILABLE_BASIC_OPERATORS:
            print(op)
