# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# GLOBALS
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

# Available operations in dnMathOps-node (Order important; corresponds with node-index)
DN_MATH_OPERATORS = [
    # "sin", "cos", "tan",
    # "asin", "acos", "atan",
    # "sqrt", "exp",
    # "ln", "log2", "log10",
    # "pow",
    # "normalise",
    # "hypot",
    # "atan2",
    # "modulus",
    # "abs",
]

# Available operations in dnMinMax-node (Order important; corresponds with node-index)
DN_MIN_MAX_OPERATORS = [
    # "min", "max",
    # "min_abs", "max_abs",
    # "abs_min_abs", "abs_max_abs",
]

# All attribute types that can be created by the node_calculator and their default creation values

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


# All metadata concatenation strings
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
        "symbol": "=",
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


# Dict of all available operations: used node-type, inputs, outputs, etc.
NODE_LOOKUP_TABLE = {}


# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# OPERATORS
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
class NodeLookupTableMetaClass(object):
    """
    Base class for node_calculator operators: Everything that goes beyond basic operators (+-*/)

    A meta-class was used, because many methods of this class are created on the fly
    in the __init__ method. First I simply instantiated the class, but a metaclass
    is more elegant (thanks, @sbi!).

    Note:
        Instead of adding each dnMath/dnMinMax/.. operator separately they're
        created on the fly via a closure!
    """

    def __init__(self, name, bases, body):
        """
        Operator-class constructor

        Note:
            name, bases, body are necessary for metaClass to work properly
        """
        # Initialize the NODE_LOOKUP_TABLE_dictionary with all available operations
        self._initialize_node_lookup_table()

    def _initialize_node_lookup_table(self):
        """
        Fill the global NODE_LOOKUP_TABLE-dictionary with all available operations

        Note:
            NODE_LOOKUP_TABLE is a dict that holds the data for each available operation:
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
        global NODE_LOOKUP_TABLE
        global DN_MATH_OPERATORS
        global DN_MIN_MAX_OPERATORS

        NODE_LOOKUP_TABLE = {
            "blend": {
                "node": "blendColors",
                "inputs": [
                    ["color1R", "color1G", "color1B"],
                    ["color2R", "color2G", "color2B"],
                    ["blender"],
                ],
                "output": ["outputR", "outputG", "outputB"],
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
            "clamp": {
                "node": "clamp",
                "inputs": [
                    ["inputR", "inputG", "inputB"],
                    ["minR", "minG", "minB"],
                    ["maxR", "maxG", "maxB"],
                ],
                "output": ["outputR", "outputG", "outputB"],
            },
            "remap": {
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
            "angle_between": {
                "node": "angleBetween",
                "inputs": [
                    ["vector1X", "vector1Y", "vector1Z"],
                    ["vector2X", "vector2Y", "vector2Z"],
                ],
                "output": ["angle"],
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
            "inverse_matrix": {
                "node": "inverseMatrix",
                "inputs": [
                    ["inputMatrix"],
                ],
                "output": ["outputMatrix"],
            },
            "transpose_matrix": {
                "node": "transposeMatrix",
                "inputs": [
                    ["inputMatrix"],
                ],
                "output": ["outputMatrix"],
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
            "normalize_vector": {
                "node": "vectorProduct",
                "inputs": [
                    ["input1X", "input1Y", "input1Z"],
                    ["normalizeOutput"],
                ],
                "output": ["outputX", "outputY", "outputZ"],
                "operation": 0,
            }
        }

        # Fill NODE_LOOKUP_TABLE with condition operations
        for i, condition_operator in enumerate(["eq", "ne", "gt", "ge", "lt", "le"]):
            NODE_LOOKUP_TABLE[condition_operator] = {
                "node": "condition",
                "inputs": [
                    ["firstTerm"],
                    ["secondTerm"],
                ],
                # The condition node is a special case!
                # It gets created during the magic-method-comparison and fully connected after
                # being passed on to the cond()-method in this OperatorMetaClass
                "output": [
                    None
                ],
                "operation": i,
            }

        # Fill NODE_LOOKUP_TABLE with +,- operations
        for i, add_sub_operator in enumerate(["add", "sub"]):
            NODE_LOOKUP_TABLE[add_sub_operator] = {
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

        # Fill NODE_LOOKUP_TABLE with *,/,** operations
        for i, mult_div_operator in enumerate(["mul", "div", "pow"]):
            NODE_LOOKUP_TABLE[mult_div_operator] = {
                "node": "multiplyDivide",
                "inputs": [
                    ["input1X", "input1Y", "input1Z"],
                    ["input2X", "input2Y", "input2Z"],
                ],
                "output": ["outputX", "outputY", "outputZ"],
                "operation": i + 1,
            }

        # Fill NODE_LOOKUP_TABLE with vectorProduct operations
        for i, vector_product_operator in enumerate(["dot", "cross"]):
            NODE_LOOKUP_TABLE[vector_product_operator] = {
                "node": "vectorProduct",
                "inputs": [
                    ["input1X", "input1Y", "input1Z"],
                    ["input2X", "input2Y", "input2Z"],
                    ["normalizeOutput"],
                ],
                "output": ["outputX", "outputY", "outputZ"],
                "operation": i + 1,
            }

        # Fill NODE_LOOKUP_TABLE with dnMinMax operations
        for i, dn_min_max_operator in enumerate(DN_MIN_MAX_OPERATORS):
            NODE_LOOKUP_TABLE[dn_min_max_operator] = {
                "node": "dnMinMax",
                "inputs": [
                    [
                        "input3D[{multi_index}].input3D0",
                        "input3D[{multi_index}].input3D1",
                        "input3D[{multi_index}].input3D2"
                    ],
                ],
                "is_multi_index": True,
                "output": ["output3D0", "output3D1", "output3D2"],
                "operation": i,
            }

        # Fill NODE_LOOKUP_TABLE with dnMath operations
        for i, dn_math_operator in enumerate(DN_MATH_OPERATORS):
            NODE_LOOKUP_TABLE[dn_math_operator] = {
                "node": "dnMathOps",
                "inputs": [
                    ["inFloatX", "inFloatY", "inFloatZ"],
                ],
                "output": ["outFloatX", "outFloatY", "outFloatZ"],
                "operation": i,
            }


class NodeLookupTable(object):
    """ Create NODE_LOOKUP_TABLE from NodeLookupTableMetaClass """
    __metaclass__ = NodeLookupTableMetaClass
