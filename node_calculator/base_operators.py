"""Basic NodeCalculator operators."""
# This is an extension that is loaded by default.

# The main difference to the base_functions is that operators are stand-alone
# functions that create a Maya node.

import math

from maya import cmds

from node_calculator.core import noca_op
from node_calculator.core import _create_operation_node
from node_calculator.core import NcNode
from node_calculator.core import Node
from node_calculator.core import NcBaseNode
from node_calculator.core import _unravel_item_as_list
from node_calculator.core import _unravel_and_set_or_connect_a_to_b
from node_calculator.core import _traced_set_attr
from node_calculator.core import LOG

# Any Maya plugin that should be loaded for the NodeCalculator
REQUIRED_EXTENSION_PLUGINS = ["matrixNodes"]


# Dict of all available operations: used node-type, inputs, outputs, etc.
EXTENSION_OPERATORS = {
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

    "dot": {
        "node": "vectorProduct",
        "inputs": [
            ["input1X", "input1Y", "input1Z"],
            ["input2X", "input2Y", "input2Z"],
            ["normalizeOutput"],
        ],
        "outputs": [
            ["outputX"],
        ],
        "operation": 1,
    },

    "cross": {
        "node": "vectorProduct",
        "inputs": [
            ["input1X", "input1Y", "input1Z"],
            ["input2X", "input2Y", "input2Z"],
            ["normalizeOutput"],
        ],
        "outputs": [
            ["outputX", "outputY", "outputZ"],
        ],
        "operation": 2,
    },
}


# Define EXTENSION_OPERATORS ---
def _extension_operators_init():
    """Fill EXTENSION_OPERATORS-dictionary with all available operations.

    Note:
        EXTENSION_OPERATORS holds the data for each available operation:
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
    global EXTENSION_OPERATORS

    # Fill EXTENSION_OPERATORS with condition operations
    cond_operators = ["eq", "ne", "gt", "ge", "lt", "le"]
    for i, condition_operator in enumerate(cond_operators):
        EXTENSION_OPERATORS[condition_operator] = {
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

    # Fill EXTENSION_OPERATORS with +,- operations
    for i, add_sub_operator in enumerate(["add", "sub"]):
        EXTENSION_OPERATORS[add_sub_operator] = {
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

    # Fill EXTENSION_OPERATORS with *,/,** operations
    for i, mult_div_operator in enumerate(["mul", "div", "pow"]):
        EXTENSION_OPERATORS[mult_div_operator] = {
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


_extension_operators_init()


# Define Operators ---
@noca_op
def angle_between(vector_a, vector_b=(1, 0, 0)):
    """Create angleBetween-node to find the angle between 2 vectors.

    Args:
        vector_a (NcNode or NcAttrs or int or float or list): Vector to
            consider for angle between
        vector_b (NcNode or NcAttrs or int or float or list): Vector to
            consider for angle between

    Returns:
        NcNode: Instance with angleBetween-node and output-attribute(s)

    Example:
        ::

            matrix = Node("pCube1").worldMatrix
            pt = Op.point_matrix_mult(
                [1, 0, 0], matrix, vector_multiply=True
            )
            Op.angle_between(pt, [1, 0, 0])
    """
    return _create_operation_node("angle_between", vector_a, vector_b)


@noca_op
def average(*attrs):
    """Create plusMinusAverage-node for averaging input attrs.

    Args:
        attrs (NcNode or NcAttrs or string or list): Inputs to be averaged

    Returns:
        NcNode: Instance with plusMinusAverage-node and output-attribute(s)

    Example:
        ::

            Op.average(Node("pCube.t"), [1, 2, 3])
    """
    return _create_operation_node("average", attrs)


@noca_op
def blend(attr_a, attr_b, blend_value=0.5):
    """Create blendColor-node.

    Args:
        attr_a (NcNode or NcAttrs or str or int or float): Plug or value to
            blend from
        attr_b (NcNode or NcAttrs or str or int or float): Plug or value to
            blend to
        blend_value (NcNode or str or int or float): Plug or value defining
            blend-amount

    Returns:
        NcNode: Instance with blend-node and output-attributes

    Example:
        ::

            Op.blend(1, Node("pCube.tx"), Node("pCube.customBlendAttr"))
    """
    return _create_operation_node("blend", attr_a, attr_b, blend_value)


@noca_op
def choice(inputs, selector=0):
    """Create choice-node to switch between various input attributes.

    Note:
        Multi index input seems to also require one "selector" per index.
        So we package a copy of the same selector for each input.

    Args:
        inputs (list): Any number of input values or plugs
        selector (NcNode or NcAttrs or int): Selector-attr on choice node
            to select one of the inputs based on their index.

    Returns:
        NcNode: Instance with choice-node and output-attribute(s)

    Example:
        ::

            option_a = Node("pCube1.tx")
            option_b = Node("pCube2.tx")
            switch = Node("pSphere1").add_bool("optionSwitch")
            choice_node = Op.choice([option_a, option_b], selector=switch)
            Node("pTorus1").tx = choice_node
    """
    choice_node_obj = _create_operation_node("choice", inputs, selector)

    return choice_node_obj


@noca_op
def clamp(attr_a, min_value=0, max_value=1):
    """Create clamp-node.

    Args:
        attr_a (NcNode or NcAttrs or str or int or float): Input value
        min_value (NcNode or NcAttrs or int or float or list): min-value
            for clamp-operation
        max_value (NcNode or NcAttrs or int or float or list): max-value
            for clamp-operation

    Returns:
        NcNode: Instance with clamp-node and output-attribute(s)

    Example:
        ::

            Op.clamp(Node("pCube.t"), [1, 2, 3], 5)
    """
    return _create_operation_node("clamp", attr_a, min_value, max_value)


@noca_op
def compose_matrix(**kwargs):
    """Create composeMatrix-node to assemble matrix from transforms.

    Args:
        kwargs (dict): Possible kwargs below. longName flags take
            precedence over the short names in [brackets]!
        translate (NcNode or NcAttrs or str or int or float): [t] translate
        rotate (NcNode or NcAttrs or str or int or float): [r] rotate
        scale (NcNode or NcAttrs or str or int or float): [s] scale
        shear (NcNode or NcAttrs or str or int or float): [sh] shear
        rotate_order (NcNode or NcAttrs or str or int): [ro] rot-order
        euler_rotation (NcNode or NcAttrs or bool): Euler rot or quaternion

    Returns:
        NcNode: Instance with composeMatrix-node and output-attribute(s)

    Example:
        ::

            in_a = Node("pCube1")
            in_b = Node("pCube2")
            decomp_a = Op.decompose_matrix(in_a.worldMatrix)
            decomp_b = Op.decompose_matrix(in_b.worldMatrix)
            Op.compose_matrix(r=decomp_a.outputRotate, s=decomp_b.outputScale)
    """
    # Using kwargs not to have a lot of flags in the function call
    translate = kwargs.get("translate", kwargs.get("t", 0))
    rotate = kwargs.get("rotate", kwargs.get("r", 0))
    scale = kwargs.get("scale", kwargs.get("s", 1))
    shear = kwargs.get("shear", kwargs.get("sh", 0))
    rotate_order = kwargs.get("rotate_order", kwargs.get("ro", 0))
    euler_rotation = kwargs.get("euler_rotation", True)

    compose_matrix_node = _create_operation_node(
        "compose_matrix",
        translate,
        rotate,
        scale,
        shear,
        rotate_order,
        euler_rotation
    )

    return compose_matrix_node


@noca_op
def condition(condition_node, if_part=False, else_part=True):
    """Set up condition-node.

    Note:
        condition_node can be a NcNode-instance of a Maya condition node.
        An appropriate NcNode-object gets automatically created when
        NodeCalculator objects are used in comparisons (==, >, >=, <, <=).
        Simply use comparison operators in the first argument. See example.

    Args:
        condition_node (NcNode or bool or int or float): Condition-statement.
            See note and example.
        if_part (NcNode or NcAttrs or str or int or float): Value/plug that
            is returned if the condition evaluates to true.
            Defaults to False.
        else_part (NcNode or NcAttrs or str or int or float): Value/plug
            that is returned if the condition evaluates to false.
            Defaults to True.

    Returns:
        NcNode: Instance with condition-node and outColor-attributes

    Example:
        ::

            condition_node = Node("pCube1.tx") >= 2
            pass_on_if_true = Node("pCube2.ty") + 2
            pass_on_if_false = 5 - Node("pCube2.tz").get()
            # Op.condition(condition-part, "if true"-part, "if false"-part)
            Op.condition(condition_node, pass_on_if_true, pass_on_if_false)
    """
    # Catch case where condition_node is a static boolean/int/... value
    if not isinstance(condition_node, NcBaseNode):
        if condition_node:
            return Node(if_part)
        else:
            return Node(else_part)

    # Make sure condition_node is of expected Node-type!
    if not isinstance(condition_node, NcBaseNode):
        LOG.warn("%s isn't NcBaseNode-instance.", condition_node)
    if cmds.objectType(condition_node.node) != "condition":
        LOG.warn("%s isn't of type condition.", condition_node)

    # Determine how many attrs were given & need to be connected
    max_dim = max(
        [len(_unravel_item_as_list(part)) for part in [if_part, else_part]]
    )

    # Connect the given if/else parts to the condition node
    cond_input_attrs = [
        ["colorIfTrueR", "colorIfTrueG", "colorIfTrueB"],
        ["colorIfFalseR", "colorIfFalseG", "colorIfFalseB"],
    ]
    node_name = condition_node.node
    for input_attrs, part in zip(cond_input_attrs, [if_part, else_part]):
        condition_input_list = [
            "{0}.{1}".format(node_name, attr)
            for attr in input_attrs[:max_dim]
        ]

        _unravel_and_set_or_connect_a_to_b(condition_input_list, part)

    # Return new NcNode instance with condition node and its output attrs.
    cond_output_attrs = ["outColorR", "outColorG", "outColorB"]
    return_value = NcNode(node_name, cond_output_attrs[:max_dim])
    return return_value


@noca_op
def cross(attr_a, attr_b=0, normalize=False):
    """Create vectorProduct-node for vector cross-multiplication.

    Args:
        attr_a (NcNode or NcAttrs or str or int or float or list): Vector A
        attr_b (NcNode or NcAttrs or str or int or float or list): Vector B
        normalize (NcNode or NcAttrs or boolean): Whether resulting vector
            should be normalized

    Returns:
        NcNode: Instance with vectorProduct-node and output-attribute(s)

    Example:
        ::

            Op.cross(Node("pCube.t"), [1, 2, 3], True)
    """
    return _create_operation_node("cross", attr_a, attr_b, normalize)


@noca_op
def decompose_matrix(in_matrix, return_all_outputs=False):
    """Create decomposeMatrix-node to disassemble matrix into transforms.

    Args:
        in_matrix (NcNode or NcAttrs or string): matrix attr to decompose
        return_all_outputs (boolean): Return all outputs, as an NcList.
            Defaults to False.

    Returns:
        NcNode or NcList: If return_all_outputs is set to True, an NcList is
            returned with all outputs. Otherwise only the first output
            (translate) is returned as an NcNode instance.

    Example:
        ::

            driver = Node("pCube1")
            driven = Node("pSphere1")
            decomp = Op.decompose_matrix(driver.worldMatrix)
            driven.t = decomp.outputTranslate
            driven.r = decomp.outputRotate
            driven.s = decomp.outputScale
    """
    return_value = _create_operation_node("decompose_matrix", in_matrix)

    if return_all_outputs:
        return return_value

    return return_value[0]


@noca_op
def dot(attr_a, attr_b=0, normalize=False):
    """Create vectorProduct-node for vector dot-multiplication.

    Args:
        attr_a (NcNode or NcAttrs or str or int or float or list): Vector A
        attr_b (NcNode or NcAttrs or str or int or float or list): Vector B
        normalize (NcNode or NcAttrs or boolean): Whether resulting vector
            should be normalized

    Returns:
        NcNode: Instance with vectorProduct-node and output-attribute(s)

    Example:
        ::

            Op.dot(Node("pCube.t"), [1, 2, 3], True)
    """
    return _create_operation_node("dot", attr_a, attr_b, normalize)


@noca_op
def exp(attr_a):
    """Raise attr_a to the base of natural logarithms.

    Args:
        attr_a (NcNode or NcAttrs or str or int or float): Value or attr

    Returns:
        NcNode: Instance with multiplyDivide-node and output-attr(s)

    Example:
        ::

            Op.exp(Node("pCube.t"))
    """
    return math.e ** attr_a


@noca_op
def inverse_matrix(in_matrix):
    """Create inverseMatrix-node to invert the given matrix.

    Args:
        in_matrix (NcNode or NcAttrs or str): Matrix to invert

    Returns:
        NcNode: Instance with inverseMatrix-node and output-attribute(s)

    Example:
        ::

            Op.inverse_matrix(Node("pCube.worldMatrix"))
    """
    return _create_operation_node("inverse_matrix", in_matrix)


@noca_op
def length(attr_a, attr_b=0):
    """Create distanceBetween-node to measure length between given points.

    Args:
        attr_a (NcNode or NcAttrs or str or int or float): Start point
        attr_b (NcNode or NcAttrs or str or int or float): End point

    Returns:
        NcNode: Instance with distanceBetween-node and distance-attribute

    Example:
        ::

            Op.len(Node("pCube.t"), [1, 2, 3])
    """
    return _create_operation_node("length", attr_a, attr_b)


@noca_op
def matrix_distance(matrix_a, matrix_b=None):
    """Create distanceBetween-node to measure distance between matrices.

    Args:
        matrix_a (NcNode or NcAttrs or str): Matrix defining start point.
        matrix_b (NcNode or NcAttrs or str): Matrix defining end point.

    Returns:
        NcNode: Instance with distanceBetween-node and distance-attribute

    Example:
        ::

            Op.len(Node("pCube.worldMatrix"), Node("pCube2.worldMatrix"))
    """
    if matrix_b is None:
        return _create_operation_node("matrix_distance", matrix_a)
    return _create_operation_node("matrix_distance", matrix_a, matrix_b)


@noca_op
def mult_matrix(*attrs):
    """Create multMatrix-node for multiplying matrices.

    Args:
        attrs (NcNode or NcAttrs or string or list): Matrices to multiply

    Returns:
        NcNode: Instance with multMatrix-node and output-attribute(s)

    Example:
        ::

            matrix_mult = Op.mult_matrix(
                Node("pCube1.worldMatrix"), Node("pCube2").worldMatrix
            )
            decomp = Op.decompose_matrix(matrix_mult)
            out = Node("pSphere")
            out.translate = decomp.outputTranslate
            out.rotate = decomp.outputRotate
            out.scale = decomp.outputScale
    """
    return _create_operation_node("mult_matrix", attrs)


@noca_op
def normalize_vector(in_vector, normalize=True):
    """Create vectorProduct-node to normalize the given vector.

    Args:
        in_vector (NcNode or NcAttrs or str or int or float or list): Vect.
        normalize (NcNode or NcAttrs or boolean): Turn normalize on/off

    Returns:
        NcNode: Instance with vectorProduct-node and output-attribute(s)

    Example:
        ::

            Op.normalize_vector(Node("pCube.t"))
    """
    # Making normalize a flag allows the user to connect attributes to it
    return_value = _create_operation_node(
        "normalize_vector",
        in_vector,
        normalize
    )
    return return_value


@noca_op
def pair_blend(
        translate_a=0,
        rotate_a=0,
        translate_b=0,
        rotate_b=0,
        weight=1,
        quat_interpolation=False,
        return_all_outputs=False):
    """Create pairBlend-node to blend between two transforms.

    Args:
        translate_a (NcNode or NcAttrs or str or int or float or list):
            Translate value of first transform.
        rotate_a (NcNode or NcAttrs or str or int or float or list):
            Rotate value of first transform.
        translate_b (NcNode or NcAttrs or str or int or float or list):
            Translate value of second transform.
        rotate_b (NcNode or NcAttrs or str or int or float or list):
            Rotate value of second transform.
        weight (NcNode or NcAttrs or str or int or float or list):
            Bias towards first or second transform.
        quat_interpolation (NcNode or NcAttrs or boolean):
            Use euler (False) or quaternions (True) to interpolate rotation
        return_all_outputs (boolean): Return all outputs, as an NcList.
            Defaults to False.

    Returns:
        NcNode or NcList: If return_all_outputs is set to True, an NcList is
            returned with all outputs. Otherwise only the first output
            (translate) is returned as an NcNode instance.

    Example:
        ::

            a = Node("pCube1")
            b = Node("pSphere1")
            blend_attr = a.add_float("blend")
            Op.pair_blend(a.t, a.r, b.t, b.r, blend_attr)
    """
    return_value = _create_operation_node(
        "pair_blend",
        translate_a,
        rotate_a,
        translate_b,
        rotate_b,
        weight,
        quat_interpolation,
    )

    if return_all_outputs:
        return return_value

    return return_value[0]


@noca_op
def point_matrix_mult(in_vector, in_matrix, vector_multiply=False):
    """Create pointMatrixMult-node to transpose the given matrix.

    Args:
        in_vector (NcNode or NcAttrs or str or int or float or list): Vect.
        in_matrix (NcNode or NcAttrs or str): Matrix
        vector_multiply (NcNode or NcAttrs or str or int or bool): Whether
            vector multiplication should be performed.

    Returns:
        NcNode: Instance with pointMatrixMult-node and output-attribute(s)

    Example:
        ::

            Op.point_matrix_mult(
                Node("pSphere.t"),
                Node("pCube.worldMatrix"),
                vector_multiply=True
            )
    """
    created_node = _create_operation_node(
        "point_matrix_mult",
        in_vector,
        in_matrix,
        vector_multiply
    )

    return created_node


@noca_op
def pow(attr_a, attr_b):
    """Raise attr_a to the power of attr_b.

    Args:
        attr_a (NcNode or NcAttrs or str or int or float): Value or attr
        attr_b (NcNode or NcAttrs or str or int or float): Value or attr

    Returns:
        NcNode: Instance with multiplyDivide-node and output-attr(s)

    Example:
        ::

            Op.pow(Node("pCube.t"), 2.5)
    """
    return attr_a ** attr_b


@noca_op
def remap_value(
        attr_a,
        output_min=0,
        output_max=1,
        input_min=0,
        input_max=1,
        values=None):
    """Create remapValue-node to remap the given input.

    Args:
        attr_a (NcNode or NcAttrs or str or int or float): Input value
        output_min (NcNode or NcAttrs or int or float or list): minValue
        output_max (NcNode or NcAttrs or int or float or list): maxValue
        input_min (NcNode or NcAttrs or int or float or list): old minValue
        input_max (NcNode or NcAttrs or int or float or list): old maxValue
        values (list): List of tuples in the following form;
            (value_Position, value_FloatValue, value_Interp)
            The value interpolation element is optional (default: linear)

    Returns:
        NcNode: Instance with remapValue-node and output-attribute(s)

    Raises:
        TypeError: If given values isn"t a list of either lists or tuples.
        RuntimeError: If given values isn"t a list of lists/tuples of
            length 2 or 3.

    Example:
        ::

            Op.remap_value(
                Node("pCube.t"),
                values=[(0.1, .2, 0), (0.4, 0.3)]
            )
    """
    created_node = _create_operation_node(
        "remap_value", attr_a, output_min, output_max, input_min, input_max
    )

    for index, value_data in enumerate(values or []):
        # value_Position, value_FloatValue, value_Interp
        # "x-axis", "y-axis", interpolation

        if not isinstance(value_data, (list, tuple)):
            msg = (
                "The values-flag for remap_value requires a list of "
                "tuples! Got {0} instead.".format(values)
            )
            raise TypeError(msg)

        elif len(value_data) == 2:
            pos, val = value_data
            interp = 1

        elif len(value_data) == 3:
            pos, val, interp = value_data

        else:
            msg = (
                "The values-flag for remap_value requires a list of "
                "tuples of length 2 or 3! Got {0} instead.".format(values)
            )
            raise RuntimeError(msg)

        # Set these attributes directly to avoid unnecessary unravelling.
        _traced_set_attr(
            "{0}.value[{1}]".format(created_node.node, index),
            (pos, val, interp)
        )

    return created_node


@noca_op
def set_range(
        attr_a,
        min_value=0,
        max_value=1,
        old_min_value=0,
        old_max_value=1):
    """Create setRange-node to remap the given input attr to a new min/max.

    Args:
        attr_a (NcNode or NcAttrs or str or int or float): Input value
        min_value (NcNode or NcAttrs or int or float or list): new min
        max_value (NcNode or NcAttrs or int or float or list): new max
        old_min_value (NcNode or NcAttrs or int or float or list): old min
        old_max_value (NcNode or NcAttrs or int or float or list): old max

    Returns:
        NcNode: Instance with setRange-node and output-attribute(s)

    Example:
        ::

            Op.set_range(Node("pCube.t"), [1, 2, 3], 4, [-1, 0, -2])
    """
    return_value = _create_operation_node(
        "set_range",
        attr_a,
        min_value,
        max_value,
        old_min_value,
        old_max_value
    )
    return return_value


@noca_op
def sqrt(attr_a):
    """Get the square root of attr_a.

    Args:
        attr_a (NcNode or NcAttrs or str or int or float): Value or attr

    Returns:
        NcNode: Instance with multiplyDivide-node and output-attr(s)

    Example:
        ::

            Op.sqrt(Node("pCube.tx"))
    """
    return attr_a ** 0.5


@noca_op
def transpose_matrix(in_matrix):
    """Create transposeMatrix-node to transpose the given matrix.

    Args:
        in_matrix (NcNode or NcAttrs or str): Plug or value for in_matrix

    Returns:
        NcNode: Instance with transposeMatrix-node and output-attribute(s)

    Example:
        ::

            Op.transpose_matrix(Node("pCube.worldMatrix"))
    """
    return _create_operation_node("transpose_matrix", in_matrix)
