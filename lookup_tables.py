# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# GLOBALS
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

# Available operations in dnMathOps-node (Order important; corresponds with node-index)
DN_MATH_OPERATORS = [
    "sin", "cos", "tan",
    "asin", "acos", "atan",
    "sqrt", "exp",
    "ln", "log2", "log10",
    "pow",
    "normalise",
    "hypot",
    "atan2",
    "modulus",
    "abs",
]

# Available operations in dnMinMax-node (Order important; corresponds with node-index)
DN_MIN_MAX_OPERATORS = [
    # "min", "max",
    # "min_abs", "max_abs",
    # "abs_min_abs", "abs_max_abs",
]

# All attribute types that can be created by the node_calculator and their default creation values
ATTR_LOOKUP_TABLE = {
    # General settings - Applies to ALL attribute types!
    "base_attr": {
        "keyable": True,
    },
    # Individual settings - Applies only to that specific type
    "bool": {
        "attributeType": "bool",
    },
    "int": {
        "attributeType": "long",
    },
    "float": {
        "attributeType": "double",
    },
    "enum": {
        "attributeType": "enum",
    },
}

# Dict of all available operations: used node-type, inputs, outputs, etc.
NODE_LOOKUP_TABLE = {}


# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# OPERATORS
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
class LookupTableMetaClass(object):
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
                "multi_index": True,
                "output": ["output3Dx", "output3Dy", "output3Dz"],
                "operation": 3,
            },
            "mult_matrix": {
                "node": "multMatrix",
                "inputs": [
                    [
                        "matrixIn[{multi_index}]"
                    ],
                ],
                "multi_index": True,
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
            "choice": {
                "node": "choice",
                "inputs": [
                    [
                        "input[{multi_index}]",
                    ],
                ],
                "multi_index": True,
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
                "multi_index": True,
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
                "multi_index": True,
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


class LookupTable(object):
    """ Create NODE_LOOKUP_TABLE from LookupTableMetaClass """
    __metaclass__ = LookupTableMetaClass
