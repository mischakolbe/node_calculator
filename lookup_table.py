"""Various lookup tables used in the NodeCalculator initialization and evaluation.

:author: Mischa Kolbe <mischakolbe@gmail.com>
"""


# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# GLOBALS
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# All attribute types that can be created by the NodeCalculator and their default creation values
DEFAULT_ATTR_FLAGS = {
    # General settings - Applies to ALL attribute types!
    "keyable": True,
}

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
    # "In most cases the -dt version will not display in the attribute editor as
    # it is an atomic type and you are not allowed to change individual parts of it."
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
OPERATOR_LOOKUP_TABLE = {}


# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# OPERATORS
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
class OperatorLookupTableMetaClass(object):
    """Base class for NodeCalculator operators:
    Everything that goes beyond basic operators (+-*/)

    Note:
        A meta-class was used, because many methods of this class are created
        on the fly in the __init__ method (possibly even with closures).
    """

    def __init__(self, name, bases, body):
        """Operator-class constructor

        Note:
            name, bases, body are necessary for metaClass to work properly
        """
        # Initialize the OPERATOR_LOOKUP_TABLE_dictionary
        self._initialize_operator_lookup_table()

    def _initialize_operator_lookup_table(self):
        """Fill OPERATOR_LOOKUP_TABLE-dictionary with all available operations.

        Note:
            OPERATOR_LOOKUP_TABLE is a dict that holds the data for each available operation:
            the necessary node-type, its inputs, outputs, etc.
            This unified data enables to abstract node creation, connection, etc.

            possible flags:
            - node: Type of Maya node necessary
            - inputs: input attributes (list of lists)
            - output: output attributes (list)
            - is_multi_index: does node take any number of input attributes (array attr)
            - operation: set operation-attr for different modes of a node
            - output_is_predetermined: should output attrs ALWAYS be given in full?
        """
        global OPERATOR_LOOKUP_TABLE

        OPERATOR_LOOKUP_TABLE = {
            "angle_between": {
                "node": "angleBetween",
                "inputs": [
                    ["vector1X", "vector1Y", "vector1Z"],
                    ["vector2X", "vector2Y", "vector2Z"],
                ],
                "output": ["angle"],
            },

            "average": {
                "node": "plusMinusAverage",
                "inputs": [
                    [
                        "input3D[{multi_index}].input3Dx",
                        "input3D[{multi_index}].input3Dy",
                        "input3D[{multi_index}].input3Dz"
                    ],
                ],
                "is_multi_index": True,
                "output": ["output3Dx", "output3Dy", "output3Dz"],
                "operation": 3,
            },

            "blend": {
                "node": "blendColors",
                "inputs": [
                    ["color1R", "color1G", "color1B"],
                    ["color2R", "color2G", "color2B"],
                    ["blender"],
                ],
                "output": ["outputR", "outputG", "outputB"],
            },

            "choice": {
                "node": "choice",
                "inputs": [
                    [
                        "input[{multi_index}]",
                    ],
                ],
                "is_multi_index": True,
                "output": ["output"],
            },

            "clamp": {
                "node": "clamp",
                "inputs": [
                    ["inputR", "inputG", "inputB"],
                    ["minR", "minG", "minB"],
                    ["maxR", "maxG", "maxB"],
                ],
                "output": ["outputR", "outputG", "outputB"],
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
                "output": ["outputMatrix"],
            },

            "decompose_matrix": {
                "node": "decomposeMatrix",
                "inputs": [
                    ["inputMatrix"],
                ],
                "output": [
                    "outputTranslateX", "outputTranslateY", "outputTranslateZ",
                    "outputRotateX", "outputRotateY", "outputRotateZ",
                    "outputScaleX", "outputScaleY", "outputScaleZ",
                    "outputShearX", "outputShearY", "outputShearZ",
                ],
                "output_is_predetermined": True,
            },

            "inverse_matrix": {
                "node": "inverseMatrix",
                "inputs": [
                    ["inputMatrix"],
                ],
                "output": ["outputMatrix"],
            },

            "length": {
                "node": "distanceBetween",
                "inputs": [
                    ["point1X", "point1Y", "point1Z"],
                    ["point2X", "point2Y", "point2Z"],
                ],
                "output": ["distance"],
            },

            "matrix_distance": {
                "node": "distanceBetween",
                "inputs": [
                    ["inMatrix1"],
                    ["inMatrix2"],
                ],
                "output": ["distance"],
            },

            "mult_matrix": {
                "node": "multMatrix",
                "inputs": [
                    [
                        "matrixIn[{multi_index}]"
                    ],
                ],
                "is_multi_index": True,
                "output": ["matrixSum"],
            },

            "normalize_vector": {
                "node": "vectorProduct",
                "inputs": [
                    ["input1X", "input1Y", "input1Z"],
                    ["normalizeOutput"],
                ],
                "output": ["outputX", "outputY", "outputZ"],
                "operation": 0,
            },

            "point_matrix_mult": {
                "node": "pointMatrixMult",
                "inputs": [
                    ["inPointX", "inPointY", "inPointZ"],
                    ["inMatrix"],
                    ["vectorMultiply"],
                ],
                "output": ["outputX", "outputY", "outputZ"],
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
                "output": ["outValue"],
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
                "output": ["outValueX", "outValueY", "outValueZ"],
            },

            "transpose_matrix": {
                "node": "transposeMatrix",
                "inputs": [
                    ["inputMatrix"],
                ],
                "output": ["outputMatrix"],
            },
        }

        # Fill OPERATOR_LOOKUP_TABLE with condition operations
        for i, condition_operator in enumerate(["eq", "ne", "gt", "ge", "lt", "le"]):
            OPERATOR_LOOKUP_TABLE[condition_operator] = {
                "node": "condition",
                "inputs": [
                    ["firstTerm"],
                    ["secondTerm"],
                ],
                # The condition node is a special case!
                # It gets created during the magic-method-comparison and fully connected after
                # being passed on to the condition()-method in this OperatorMetaClass
                "output": [
                    None
                ],
                "operation": i,
            }

        # Fill OPERATOR_LOOKUP_TABLE with +,- operations
        for i, add_sub_operator in enumerate(["add", "sub"]):
            OPERATOR_LOOKUP_TABLE[add_sub_operator] = {
                "node": "plusMinusAverage",
                "inputs": [
                    [
                        "input3D[{multi_index}].input3Dx",
                        "input3D[{multi_index}].input3Dy",
                        "input3D[{multi_index}].input3Dz"
                    ],
                ],
                "is_multi_index": True,
                "output": ["output3Dx", "output3Dy", "output3Dz"],
                "operation": i + 1,
            }

        # Fill OPERATOR_LOOKUP_TABLE with *,/,** operations
        for i, mult_div_operator in enumerate(["mul", "div", "pow"]):
            OPERATOR_LOOKUP_TABLE[mult_div_operator] = {
                "node": "multiplyDivide",
                "inputs": [
                    ["input1X", "input1Y", "input1Z"],
                    ["input2X", "input2Y", "input2Z"],
                ],
                "output": ["outputX", "outputY", "outputZ"],
                "operation": i + 1,
            }

        # Fill OPERATOR_LOOKUP_TABLE with vectorProduct operations
        for i, vector_product_operator in enumerate(["dot", "cross"]):
            OPERATOR_LOOKUP_TABLE[vector_product_operator] = {
                "node": "vectorProduct",
                "inputs": [
                    ["input1X", "input1Y", "input1Z"],
                    ["input2X", "input2Y", "input2Z"],
                    ["normalizeOutput"],
                ],
                "output": ["outputX", "outputY", "outputZ"],
                "operation": i + 1,
            }


class OperatorLookupTable(object):
    """Create OPERATOR_LOOKUP_TABLE from OperatorLookupTableMetaClass"""
    __metaclass__ = OperatorLookupTableMetaClass


# Little snippet to update the docString of core.py with all the available Operators
# basic_ops = [
#     "add", "sub",
#     "div", "mul",
#     "pow",
#     "le", "eq", "ge", "gt", "lt", "ne",
# ]
# for op in sorted(OPERATOR_LOOKUP_TABLE.keys()):
#     if op not in basic_ops:
#         print(op)
