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
REQUIRED_EXTENSION_PLUGINS = ["matrixNodes", "quatNodes"]


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

    "closest_point_on_mesh": {
        "node": "closestPointOnMesh",
        "inputs": [
            ["inMesh"],
            ["inPositionX", "inPositionY", "inPositionZ"],
        ],
        "outputs": [
            ["positionX", "positionY", "positionZ"],
            ["parameterU", "parameterV"],
            ["normalX", "normalY", "normalZ"],
            ["closestVertexIndex"],
            ["closestFaceIndex"],
        ],
        "output_is_predetermined": True,
    },

    "closest_point_on_surface": {
        "node": "closestPointOnSurface",
        "inputs": [
            ["inputSurface"],
            ["inPositionX", "inPositionY", "inPositionZ"],
        ],
        "outputs": [
            ["positionX", "positionY", "positionZ"],
            ["parameterU", "parameterV"],
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
        "outputs": [
            ["outputMatrix"],
        ],
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

    "curve_info": {
        "node": "curveInfo",
        "inputs": [
            ["inputCurve"],
        ],
        "outputs": [
            ["arcLength"],
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

    "euler_to_quat": {
        "node": "eulerToQuat",
        "inputs": [
            ["inputRotateX", "inputRotateY", "inputRotateZ"],
            ["inputRotateOrder"],
        ],
        "outputs": [
            ["outputQuatX", "outputQuatY", "outputQuatZ", "outputQuatW"],
        ],
        "output_is_predetermined": True,
    },

    "four_by_four_matrix": {
        "node": "fourByFourMatrix",
        "inputs": [
            [
                "in00", "in01", "in02", "in03",
                "in10", "in11", "in12", "in13",
                "in20", "in21", "in22", "in23",
                "in30", "in31", "in32", "in33",
            ],
        ],
        "outputs": [
            ["output"],
        ],
    },

    "hold_matrix": {
        "node": "holdMatrix",
        "inputs": [
            ["inMatrix"],
        ],
        "outputs": [
            ["outMatrix"],
        ],
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

    "nearest_point_on_curve": {
        "node": "nearestPointOnCurve",
        "inputs": [
            ["inputCurve"],
            ["inPositionX", "inPositionY", "inPositionZ"],
        ],
        "outputs": [
            ["positionX", "positionY", "positionZ"],
            ["parameter"],
        ],
        "output_is_predetermined": True,
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

    "pass_matrix": {
        "node": "passMatrix",
        "inputs": [
            ["inMatrix"],
            ["inScale"],
        ],
        "outputs": [
            ["outMatrix"],
        ],
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

    "point_on_curve_info": {
        "node": "pointOnCurveInfo",
        "inputs": [
            ["inputCurve"],
            ["parameter"],
            ["turnOnPercentage"],
        ],
        "outputs": [
            ["positionX", "positionY", "positionZ"],
            ["normalX", "normalY", "normalZ"],
            ["normalizedNormalX", "normalizedNormalY", "normalizedNormalZ"],
            ["tangentX", "tangentY", "tangentZ"],
            ["normalizedTangentX", "normalizedTangentY", "normalizedTangentZ"],
            ["curvatureCenterX", "curvatureCenterY", "curvatureCenterZ"],
            ["curvatureRadius"],
        ],
        "output_is_predetermined": True,
    },

    "point_on_surface_info": {
        "node": "pointOnSurfaceInfo",
        "inputs": [
            ["inputSurface"],
            ["parameterU", "parameterV"],
            ["turnOnPercentage"],
        ],
        "outputs": [
            ["positionX", "positionY", "positionZ"],
            ["normalX", "normalY", "normalZ"],
            ["normalizedNormalX", "normalizedNormalY", "normalizedNormalZ"],
            ["tangentUx", "tangentUy", "tangentUz"],
            [
                "normalizedTangentUX",
                "normalizedTangentUY",
                "normalizedTangentUZ",
            ],
            ["tangentVx", "tangentVy", "tangentVz"],
            [
                "normalizedTangentVX",
                "normalizedTangentVY",
                "normalizedTangentVZ",
            ],
        ],
        "output_is_predetermined": True,
    },

    "quat_add": {
        "node": "quatAdd",
        "inputs": [
            ["input1QuatX", "input1QuatY", "input1QuatZ", "input1QuatW"],
            ["input2QuatX", "input2QuatY", "input2QuatZ", "input2QuatW"],
        ],
        "outputs": [
            ["outputQuatX", "outputQuatY", "outputQuatZ", "outputQuatW"],
        ],
        "output_is_predetermined": True,
    },

    "quat_conjugate": {
        "node": "quatConjugate",
        "inputs": [
            ["inputQuatX", "inputQuatY", "inputQuatZ", "inputQuatW"],
        ],
        "outputs": [
            ["outputQuatX", "outputQuatY", "outputQuatZ", "outputQuatW"],
        ],
        "output_is_predetermined": True,
    },

    "quat_invert": {
        "node": "quatInvert",
        "inputs": [
            ["inputQuatX", "inputQuatY", "inputQuatZ", "inputQuatW"],
        ],
        "outputs": [
            ["outputQuatX", "outputQuatY", "outputQuatZ", "outputQuatW"],
        ],
        "output_is_predetermined": True,
    },

    "quat_negate": {
        "node": "quatNegate",
        "inputs": [
            ["inputQuatX", "inputQuatY", "inputQuatZ", "inputQuatW"],
        ],
        "outputs": [
            ["outputQuatX", "outputQuatY", "outputQuatZ", "outputQuatW"],
        ],
        "output_is_predetermined": True,
    },

    "quat_normalize": {
        "node": "quatNormalize",
        "inputs": [
            ["inputQuatX", "inputQuatY", "inputQuatZ", "inputQuatW"],
        ],
        "outputs": [
            ["outputQuatX", "outputQuatY", "outputQuatZ", "outputQuatW"],
        ],
        "output_is_predetermined": True,
    },

    "quat_mul": {
        "node": "quatProd",
        "inputs": [
            ["input1QuatX", "input1QuatY", "input1QuatZ", "input1QuatW"],
            ["input2QuatX", "input2QuatY", "input2QuatZ", "input2QuatW"],
        ],
        "outputs": [
            ["outputQuatX", "outputQuatY", "outputQuatZ", "outputQuatW"],
        ],
        "output_is_predetermined": True,
    },

    "quat_sub": {
        "node": "quatSub",
        "inputs": [
            ["input1QuatX", "input1QuatY", "input1QuatZ", "input1QuatW"],
            ["input2QuatX", "input2QuatY", "input2QuatZ", "input2QuatW"],
        ],
        "outputs": [
            ["outputQuatX", "outputQuatY", "outputQuatZ", "outputQuatW"],
        ],
        "output_is_predetermined": True,
    },

    "quat_to_euler": {
        "node": "quatToEuler",
        "inputs": [
            ["inputQuatX", "inputQuatY", "inputQuatZ", "inputQuatW"],
            ["inputRotateOrder"],
        ],
        "outputs": [
            ["outputRotateX", "outputRotateY", "outputRotateZ"],
        ],
        "output_is_predetermined": True,
    },

    "remap_color": {
        "node": "remapColor",
        "inputs": [
            ["colorR", "colorG", "colorB"],
            ["outputMin"],
            ["outputMax"],
            ["inputMin"],
            ["inputMax"],
        ],
        "outputs": [
            ["outColorR", "outColorG", "outColorB"],
        ],
    },

    "remap_hsv": {
        "node": "remapHsv",
        "inputs": [
            ["colorR", "colorG", "colorB"],
            ["outputMin"],
            ["outputMax"],
            ["inputMin"],
            ["inputMax"],
        ],
        "outputs": [
            ["outColorR", "outColorG", "outColorB"],
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

    "reverse": {
        "node": "reverse",
        "inputs": [
            ["inputX", "inputY", "inputZ"],
        ],
        "outputs": [
            ["outputX", "outputY", "outputZ"],
        ]
    },

    "rgb_to_hsv": {
        "node": "rgbToHsv",
        "inputs": [
            ["inRgbR", "inRgbG", "inRgbB"],
        ],
        "outputs": [
            ["outHsvH", "outHsvS", "outHsvV"],
        ],
        "output_is_predetermined": True,
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

    "sum": {
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
        "operation": 1,
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

    "weighted_add_matrix": {
        "node": "wtAddMatrix",
        "inputs": [
            ["wtMatrix[{array}].matrixIn", "wtMatrix[{array}].weightIn"],
        ],
        "outputs": [
            ["matrixSum"],
        ],
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
            consider for angle between.
        vector_b (NcNode or NcAttrs or int or float or list or tuple): Vector
            to consider for angle between. Defaults to (1, 0, 0).

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
        attrs (NcNode or NcAttrs or NcList or string or list or tuple):
            Inputs to be averaged.

    Returns:
        NcNode: Instance with plusMinusAverage-node and output-attribute(s)

    Example:
        ::

            Op.average(Node("pCube.t"), [1, 2, 3])
    """
    if len(attrs) == 1:
        attrs = attrs[0]

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
            blend-amount. Defaults to 0.5.

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
        inputs (NcList or NcAttrs or list): Any number of input values or plugs
        selector (NcNode or NcAttrs or int): Selector-attr on choice node
            to select one of the inputs based on their index. Defaults to 0.

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
    if not isinstance(inputs, (list, tuple)):
        inputs = [inputs]

    choice_node_obj = _create_operation_node("choice", inputs, selector)

    return choice_node_obj


@noca_op
def clamp(attr_a, min_value=0, max_value=1):
    """Create clamp-node.

    Args:
        attr_a (NcNode or NcAttrs or str or int or float): Input value
        min_value (NcNode or NcAttrs or int or float or list): min-value
            for clamp-operation. Defaults to 0.
        max_value (NcNode or NcAttrs or int or float or list): max-value
            for clamp-operation. Defaults to 1.

    Returns:
        NcNode: Instance with clamp-node and output-attribute(s)

    Example:
        ::

            Op.clamp(Node("pCube.t"), [1, 2, 3], 5)
    """
    return _create_operation_node("clamp", attr_a, min_value, max_value)


@noca_op
def closest_point_on_mesh(mesh, position=(0, 0, 0), return_all_outputs=False):
    """Get the closest point on a mesh, from the given position.

    Args:
        mesh (NcNode or NcAttrs or str): Mesh node.
        position (NcNode or NcAttrs or int or float or list): Find closest
            point on mesh to this position. Defaults to (0, 0, 0).
        return_all_outputs (bool): Return all outputs as an NcList.
            Defaults to False.

    Returns:
        NcNode or NcList: If return_all_outputs is set to True, an NcList is
            returned with all outputs. Otherwise only the first output
            (position) is returned as an NcNode instance.

    Example:
        ::

            cube = Node("pCube1")
            Op.closest_point_on_mesh(cube.outMesh, [1, 0, 0])
    """
    return_value = _create_operation_node(
        "closest_point_on_mesh",
        mesh,
        position,
    )

    if return_all_outputs:
        return return_value

    return return_value[0]


@noca_op
def closest_point_on_surface(
        surface,
        position=(0, 0, 0),
        return_all_outputs=False):
    """Get the closest point on a surface, from the given position.

    Args:
        surface (NcNode or NcAttrs or str): NURBS surface node.
        position (NcNode or NcAttrs or int or float or list): Find closest
            point on surface to this position. Defaults to (0, 0, 0).
        return_all_outputs (bool): Return all outputs as an NcList.
            Defaults to False.

    Returns:
        NcNode or NcList: If return_all_outputs is set to True, an NcList is
            returned with all outputs. Otherwise only the first output
            (position) is returned as an NcNode instance.

    Example:
        ::

            sphere = Node("nurbsSphere1")
            Op.closest_point_on_surface(sphere.local, [1, 0, 0])
    """
    return_value = _create_operation_node(
        "closest_point_on_surface",
        surface,
        position,
    )

    if return_all_outputs:
        return return_value

    return return_value[0]


@noca_op
def compose_matrix(
        translate=None,
        rotate=None,
        scale=None,
        shear=None,
        rotate_order=None,
        euler_rotation=None,
        **kwargs):
    """Create composeMatrix-node to assemble matrix from transforms.

    Args:
        translate (NcNode or NcAttrs or str or int or float): translate [t]
            Defaults to None, which corresponds to value 0.
        rotate (NcNode or NcAttrs or str or int or float): rotate [r]
            Defaults to None, which corresponds to value 0.
        scale (NcNode or NcAttrs or str or int or float): scale [s]
            Defaults to None, which corresponds to value 1.
        shear (NcNode or NcAttrs or str or int or float): shear [sh]
            Defaults to None, which corresponds to value 0.
        rotate_order (NcNode or NcAttrs or str or int): rot-order [ro]
            Defaults to None, which corresponds to value 0.
        euler_rotation (NcNode or NcAttrs or bool): Euler or quaternion [uer]
            Defaults to None, which corresponds to True.
        kwargs (dict): Short flags, see in [brackets] for each arg above.
            Long names take precedence!

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
    translate = translate or kwargs.get("t", 0)
    rotate = rotate or kwargs.get("r", 0)
    scale = scale or kwargs.get("s", 1)
    shear = shear or kwargs.get("sh", 0)
    rotate_order = rotate_order or kwargs.get("ro", 0)
    euler_rotation = euler_rotation or kwargs.get("uer", True)

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
    # Catch case where condition_node is a static bool/int/... value
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
        attr_a (NcNode or NcAttrs or str or int or float or list): Vector A.
        attr_b (NcNode or NcAttrs or str or int or float or list): Vector B.
            Defaults to 0.
        normalize (NcNode or NcAttrs or bool): Whether resulting vector
            should be normalized. Defaults to False.

    Returns:
        NcNode: Instance with vectorProduct-node and output-attribute(s)

    Example:
        ::

            Op.cross(Node("pCube.t"), [1, 2, 3], True)
    """
    return _create_operation_node("cross", attr_a, attr_b, normalize)


@noca_op
def curve_info(curve):
    """Measure the length of a curve.

    Args:
        curve (NcNode, NcAttrs or string): The curve to be measured.

    Returns:
        NcNode: Instance with vectorProduct-node and output-attribute(s)

    Example:
        ::

            Op.curve_info(Node("nurbsCurve.local"))
    """
    return _create_operation_node("curve_info", curve)


@noca_op
def decompose_matrix(in_matrix, return_all_outputs=False):
    """Create decomposeMatrix-node to disassemble matrix into transforms.

    Args:
        in_matrix (NcNode or NcAttrs or string): matrix attr to decompose
        return_all_outputs (bool): Return all outputs, as an NcList.
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
        attr_a (NcNode or NcAttrs or str or int or float or list): Vector A.
        attr_b (NcNode or NcAttrs or str or int or float or list): Vector B.
            Defaults to 0.
        normalize (NcNode or NcAttrs or bool): Whether resulting vector
            should be normalized. Defaults to False.

    Returns:
        NcNode: Instance with vectorProduct-node and output-attribute(s)

    Example:
        ::

            Op.dot(Node("pCube.t"), [1, 2, 3], True)
    """
    return _create_operation_node("dot", attr_a, attr_b, normalize)


@noca_op
def euler_to_quat(angle, rotate_order=0):
    """Create eulerToQuat-node to add two quaternions together.

    Args:
        angle (NcNode or NcAttrs or str or list or tuple): Euler angles to
            convert into a quaternion.
        rotate_order (NcNode or NcAttrs or or int): Order of rotation.
            Defaults to 0, which represents rotate order "xyz".

    Returns:
        NcNode: Instance with eulerToQuat-node and output-attribute(s)

    Example:
        ::

            Op.euler_to_quat(Node("pCube").rotate, 2)
    """
    created_node = _create_operation_node("euler_to_quat", angle, rotate_order)

    return created_node


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
def four_by_four_matrix(
        vector_a=None,
        vector_b=None,
        vector_c=None,
        translate=None):
    """Create a four by four matrix out of its components.

    Args:
        vector_a (NcNode or NcAttrs or str or list or tuple or int or float):
            First vector of the matrix; the "x-axis". Or can contain all 16
            elements that make up the 4x4 matrix. Defaults to None, which
            means the identity matrix will be used.
        vector_b (NcNode or NcAttrs or str or list or tuple or int or float):
            Second vector of the matrix; the "y-axis". Defaults to None, which
            means the vector (0, 1, 0) will be used, if matrix is not defined
            solely by vector_a.
        vector_c (NcNode or NcAttrs or str or list or tuple or int or float):
            Third vector of the matrix; the "z-axis". Defaults to None, which
            means the vector (0, 0, 1) will be used, if matrix is not defined
            solely by vector_a.
        translate (NcNode or NcAttrs or str or list or tuple or int or float):
            Translate-elements of the matrix. Defaults to None, which means
            the vector (0, 0, 0) will be used, if matrix is not defined
            solely by vector_a.

    Returns:
        NcNode: Instance with fourByFourMatrix-node and output-attr(s)

    Example:
        ::

            cube = Node("pCube1")
            vec_a = Op.point_matrix_mult(
                [1, 0, 0],
                cube.worldMatrix,
                vector_multiply=True
            )
            vec_b = Op.point_matrix_mult(
                [0, 1, 0],
                cube.worldMatrix,
                vector_multiply=True
            )
            vec_c = Op.point_matrix_mult(
                [0, 0, 1],
                cube.worldMatrix,
                vector_multiply=True
            )
            out = Op.four_by_four_matrix(
                vector_a=vec_a,
                vector_b=vec_b,
                vector_c=vec_c,
                translate=[cube.tx, cube.ty, cube.tz]
            )
    """
    # If any vector is not None: The operator won't return the identity matrix.
    vectors = [vector_a, vector_b, vector_c, translate]
    if any([vector is not None for vector in vectors]):

        # If a vector other than vector_a is not None: Assume the matrix
        # should be created from multiple vectors.
        if any([vector is not None for vector in vectors[1:]]):

            # Start with the identity matrix and set/connect any given vector.
            created_node = _create_operation_node(
                "four_by_four_matrix",
                [1, 0, 0, 0, 0, 1, 0, 0, 0, 0, 1, 0, 0, 0, 0, 1]
            )

            if vector_a:
                _unravel_and_set_or_connect_a_to_b(
                    [created_node.in00, created_node.in01, created_node.in02],
                    vector_a,
                )
            if vector_b:
                _unravel_and_set_or_connect_a_to_b(
                    [created_node.in10, created_node.in11, created_node.in12],
                    vector_b,
                )
            if vector_c:
                _unravel_and_set_or_connect_a_to_b(
                    [created_node.in20, created_node.in21, created_node.in22],
                    vector_c,
                )
            if translate:
                _unravel_and_set_or_connect_a_to_b(
                    [created_node.in30, created_node.in31, created_node.in32],
                    translate,
                )

        # If only vector_a was given: Assume it contains all elements that
        # should make up the matrix.
        else:
            created_node = _create_operation_node(
                "four_by_four_matrix",
                vector_a
            )

    else:
        # Default to identity matrix
        created_node = _create_operation_node(
            "four_by_four_matrix",
            [1, 0, 0, 0, 0, 1, 0, 0, 0, 0, 1, 0, 0, 0, 0, 1]
        )

    return created_node


@noca_op
def hold_matrix(matrix):
    """Create holdMatrix-node for storing a matrix.

    Args:
        matrix (NcNode or NcAttrs or string or list): Matrix to store.

    Returns:
        NcNode: Instance with holdMatrix-node and output-attribute(s)

    Example:
        ::

            Op.hold_matrix(Node("pCube1.worldMatrix"))
    """
    return _create_operation_node("hold_matrix", matrix)


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
        attr_a (NcNode or NcAttrs or str or int or float): Start point.
        attr_b (NcNode or NcAttrs or str or int or float): End point.
            Defaults to 0.

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
            Defaults to None, which gives the length between the origin and
            the point described by matrix_a.

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
        attrs (NcNode or NcAttrs or NcList or string or list or tuple):
            Matrices to multiply together.

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
    if len(attrs) == 1:
        attrs = attrs[0]

    return _create_operation_node("mult_matrix", attrs)


@noca_op
def nearest_point_on_curve(
        curve,
        position=(0, 0, 0),
        return_all_outputs=False):
    """Get curve data from a particular point on a curve.

    Args:
        curve (NcNode or NcAttrs or str): Curve node.
        position (NcNode or NcAttrs or int or float or list): Find closest
            point on curve to this position. Defaults to (0, 0, 0).
        return_all_outputs (bool): Return all outputs as an NcList.
            Defaults to False.

    Returns:
        NcNode or NcList: If return_all_outputs is set to True, an NcList is
            returned with all outputs. Otherwise only the first output
            (position) is returned as an NcNode instance.

    Example:
        ::

            curve = Node("curve1")
            Op.nearest_point_on_curve(curve.local, [1, 0, 0])
    """
    return_value = _create_operation_node(
        "nearest_point_on_curve",
        curve,
        position,
    )

    if return_all_outputs:
        return return_value

    return return_value[0]


@noca_op
def normalize_vector(in_vector, normalize=True):
    """Create vectorProduct-node to normalize the given vector.

    Args:
        in_vector (NcNode or NcAttrs or str or int or float or list): Vect.
        normalize (NcNode or NcAttrs or bool): Turn normalize on/off.
            Defaults to True.

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
            Defaults to 0.
        rotate_a (NcNode or NcAttrs or str or int or float or list):
            Rotate value of first transform.
            Defaults to 0.
        translate_b (NcNode or NcAttrs or str or int or float or list):
            Translate value of second transform.
            Defaults to 0.
        rotate_b (NcNode or NcAttrs or str or int or float or list):
            Rotate value of second transform.
            Defaults to 0.
        weight (NcNode or NcAttrs or str or int or float or list):
            Bias towards first or second transform.
            Defaults to 1.
        quat_interpolation (NcNode or NcAttrs or bool):
            Use euler (False) or quaternions (True) to interpolate rotation
            Defaults to False.
        return_all_outputs (bool): Return all outputs, as an NcList.
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
def pass_matrix(matrix, scale=1):
    """Create passMatrix-node for passing and optionally scaling a matrix.

    Args:
        matrix (NcNode or NcAttrs or string or list): Matrix to store.
        scale (NcNode or NcAttrs or int or float): Scale to be applied to
            matrix. Defaults to 1.

    Returns:
        NcNode: Instance with passMatrix-node and output-attribute(s)

    Example:
        ::

            Op.pass_matrix(Node("pCube1.worldMatrix"))
    """
    return _create_operation_node("pass_matrix", matrix, scale)


@noca_op
def point_matrix_mult(in_vector, in_matrix, vector_multiply=False):
    """Create pointMatrixMult-node to transpose the given matrix.

    Args:
        in_vector (NcNode or NcAttrs or str or int or float or list): Vect.
        in_matrix (NcNode or NcAttrs or str): Matrix
        vector_multiply (NcNode or NcAttrs or str or int or bool): Whether
            vector multiplication should be performed. Defaults to False.

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
def quat_add(quat_a, quat_b=(0, 0, 0, 1)):
    """Create quatAdd-node to add two quaternions together.

    Args:
        quat_a (NcNode or NcAttrs or str or list or tuple): First quaternion.
        quat_b (NcNode or NcAttrs or str or list or tuple): Second quaternion.
            Defaults to (0, 0, 0, 1).

    Returns:
        NcNode: Instance with quatAdd-node and output-attribute(s)

    Example:
        ::

            Op.quat_add(
                create_node("decomposeMatrix").outputQuat,
                create_node("decomposeMatrix").outputQuat,
            )
    """
    created_node = _create_operation_node("quat_add", quat_a, quat_b)

    return created_node


@noca_op
def quat_conjugate(quat_a):
    """Create quatConjugate-node to conjugate a quaternion.

    Args:
        quat_a (NcNode or NcAttrs or str or list or tuple): Quaternion to
            conjugate.

    Returns:
        NcNode: Instance with quatConjugate-node and output-attribute(s)

    Example:
        ::

            Op.quat_conjugate(create_node("decomposeMatrix").outputQuat)
    """
    created_node = _create_operation_node("quat_conjugate", quat_a)

    return created_node


@noca_op
def quat_invert(quat_a):
    """Create quatInvert-node to invert a quaternion.

    Args:
        quat_a (NcNode or NcAttrs or str or list or tuple): Quaternion to
            invert.

    Returns:
        NcNode: Instance with quatInvert-node and output-attribute(s)

    Example:
        ::

            Op.quat_invert(create_node("decomposeMatrix").outputQuat)
    """
    created_node = _create_operation_node("quat_invert", quat_a)

    return created_node


@noca_op
def quat_negate(quat_a):
    """Create quatNegate-node to negate a quaternion.

    Args:
        quat_a (NcNode or NcAttrs or str or list or tuple): Quaternion to
            negate.

    Returns:
        NcNode: Instance with quatNegate-node and output-attribute(s)

    Example:
        ::

            Op.quat_negate(create_node("decomposeMatrix").outputQuat)
    """
    created_node = _create_operation_node("quat_negate", quat_a)

    return created_node


@noca_op
def quat_normalize(quat_a):
    """Create quatNormalize-node to normalize a quaternion.

    Args:
        quat_a (NcNode or NcAttrs or str or list or tuple): Quaternion to
            normalize.

    Returns:
        NcNode: Instance with quatNormalize-node and output-attribute(s)

    Example:
        ::

            Op.quat_normalize(create_node("decomposeMatrix").outputQuat)
    """
    created_node = _create_operation_node("quat_normalize", quat_a)

    return created_node


@noca_op
def quat_mul(quat_a, quat_b=(0, 0, 0, 1)):
    """Create quatProd-node to multiply two quaternions together.

    Args:
        quat_a (NcNode or NcAttrs or str or list or tuple): First quaternion.
        quat_b (NcNode or NcAttrs or str or list or tuple): Second quaternion.
            Defaults to (0, 0, 0, 1).

    Returns:
        NcNode: Instance with quatProd-node and output-attribute(s)

    Example:
        ::

            Op.quat_mul(
                create_node("decomposeMatrix").outputQuat,
                create_node("decomposeMatrix").outputQuat,
            )
    """
    created_node = _create_operation_node("quat_mul", quat_a, quat_b)

    return created_node


@noca_op
def quat_sub(quat_a, quat_b=(0, 0, 0, 1)):
    """Create quatSub-node to subtract two quaternions from each other.

    Args:
        quat_a (NcNode or NcAttrs or str or list or tuple): First quaternion.
        quat_b (NcNode or NcAttrs or str or list or tuple): Second quaternion
            that will be subtracted from the first. Defaults to (0, 0, 0, 1).

    Returns:
        NcNode: Instance with quatSub-node and output-attribute(s)

    Example:
        ::

            Op.quat_sub(
                create_node("decomposeMatrix").outputQuat,
                create_node("decomposeMatrix").outputQuat,
            )
    """
    created_node = _create_operation_node("quat_sub", quat_a, quat_b)

    return created_node


@noca_op
def quat_to_euler(quat_a, rotate_order=0):
    """Create quatToEuler-node to convert a quaternion into an euler angle.

    Args:
        quat_a (NcNode or NcAttrs or str or list or tuple): Quaternion to
            convert into Euler angles.
        rotate_order (NcNode or NcAttrs or or int): Order of rotation.
            Defaults to 0, which represents rotate order "xyz".

    Returns:
        NcNode: Instance with quatToEuler-node and output-attribute(s)

    Example:
        ::

            Op.quat_to_euler(create_node("decomposeMatrix").outputQuat, 2)
    """
    created_node = _create_operation_node(
        "quat_to_euler",
        quat_a,
        rotate_order
    )

    return created_node


@noca_op
def point_on_curve_info(
        curve,
        parameter=0,
        as_percentage=False,
        return_all_outputs=False):
    """Get curve data from a particular point on a curve.

    Args:
        curve (NcNode or NcAttrs or str): Curve node.
        parameter (NcNode or NcAttrs or int or float or list): Get curve data
            at the position on the curve specified by this parameter.
            Defaults to 0.
        as_percentage (NcNode or NcAttrs or int or float or bool): Use 0-1
            values for parameter. Defaults to False.
        return_all_outputs (bool): Return all outputs as an NcList.
            Defaults to False.

    Returns:
        NcNode or NcList: If return_all_outputs is set to True, an NcList is
            returned with all outputs. Otherwise only the first output
            (position) is returned as an NcNode instance.

    Example:
        ::

            curve = Node("curve1")
            Op.point_on_curve_info(curve.local, 0.5)
    """
    return_value = _create_operation_node(
        "point_on_curve_info",
        curve,
        parameter,
        as_percentage,
    )

    if return_all_outputs:
        return return_value

    return return_value[0]


@noca_op
def point_on_surface_info(
        surface,
        parameter=(0, 0),
        as_percentage=False,
        return_all_outputs=False):
    """Get surface data from a particular point on a NURBS surface.

    Args:
        surface (NcNode or NcAttrs or str): NURBS surface node.
        parameter (NcNode or NcAttrs or int or float or list): UV values that
            define point on NURBS surface. Defaults to (0, 0).
        as_percentage (NcNode or NcAttrs or int or float or bool): Use
            0-1 values for parameters. Defaults to False.
        return_all_outputs (bool): Return all outputs as an NcList.
            Defaults to False.

    Returns:
        NcNode or NcList: If return_all_outputs is set to True, an NcList is
            returned with all outputs. Otherwise only the first output
            (position) is returned as an NcNode instance.

    Example:
        ::

            sphere = Node("nurbsSphere1")
            Op.point_on_surface_info(sphere.local, [0.5, 0.5])
    """
    return_value = _create_operation_node(
        "point_on_surface_info",
        surface,
        parameter,
        as_percentage,
    )

    if return_all_outputs:
        return return_value

    return return_value[0]


@noca_op
def pow(attr_a, attr_b=2):
    """Raise attr_a to the power of attr_b.

    Args:
        attr_a (NcNode or NcAttrs or str or int or float): Value or attr.
        attr_b (NcNode or NcAttrs or str or int or float): Value or attr.
            Defaults to 2.

    Returns:
        NcNode: Instance with multiplyDivide-node and output-attr(s)

    Example:
        ::

            Op.pow(Node("pCube.t"), 2.5)
    """
    return attr_a ** attr_b


@noca_op
def remap_color(
        attr_a,
        output_min=0,
        output_max=1,
        input_min=0,
        input_max=1,
        values_red=None,
        values_green=None,
        values_blue=None):
    """Create remapColor-node to remap the given input.

    Args:
        attr_a (NcNode or NcAttrs or str or int or float): Input color.
        output_min (NcNode or NcAttrs or int or float or list): minValue.
            Defaults to 0.
        output_max (NcNode or NcAttrs or int or float or list): maxValue.
            Defaults to 1.
        input_min (NcNode or NcAttrs or int or float or list): old minValue.
            Defaults to 0.
        input_max (NcNode or NcAttrs or int or float or list): old maxValue.
            Defaults to 1.
        values_red (list): List of tuples for red-graph in the form;
            (value_Position, value_FloatValue, value_Interp)
            The value interpolation element is optional (default: linear)
            Defaults to None.
        values_green (list): List of tuples for green-graph in the form;
            (value_Position, value_FloatValue, value_Interp)
            The value interpolation element is optional (default: linear)
            Defaults to None.
        values_blue (list): List of tuples for blue-graph in the form;
            (value_Position, value_FloatValue, value_Interp)
            The value interpolation element is optional (default: linear)
            Defaults to None.

    Returns:
        NcNode: Instance with remapColor-node and output-attribute(s)

    Raises:
        TypeError: If given values isn't a list of either lists or tuples.
        RuntimeError: If given values isn't a list of lists/tuples of
            length 2 or 3.

    Example:
        ::

            Op.remap_color(
                Node("blinn1.outColor"),
                values_red=[(0.1, .2, 0), (0.4, 0.3)]
            )
    """
    created_node = _create_operation_node(
        "remap_color", attr_a, output_min, output_max, input_min, input_max
    )

    value_lists = [values_red, values_green, values_blue]
    for values, color in zip(value_lists, ["red", "green", "blue"]):
        for index, value_data in enumerate(values or []):
            # value_Position, value_FloatValue, value_Interp
            # "x-axis", "y-axis", interpolation

            if not isinstance(value_data, (list, tuple)):
                msg = (
                    "The values-flag for remap_color requires a list of "
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
                    "The values-flag for remap_color requires a list of "
                    "tuples of length 2 or 3! Got {0} instead.".format(values)
                )
                raise RuntimeError(msg)

            # Set these attributes directly to avoid unnecessary unravelling.
            _traced_set_attr(
                "{0}.{1}[{2}]".format(created_node.node, color, index),
                (pos, val, interp)
            )

    return created_node


@noca_op
def remap_hsv(
        attr_a,
        output_min=0,
        output_max=1,
        input_min=0,
        input_max=1,
        values_hue=None,
        values_saturation=None,
        values_value=None):
    """Create remapHsv-node to remap the given input.

    Args:
        attr_a (NcNode or NcAttrs or str or int or float): Input color.
        output_min (NcNode or NcAttrs or int or float or list): minValue.
            Defaults to 0.
        output_max (NcNode or NcAttrs or int or float or list): maxValue.
            Defaults to 1.
        input_min (NcNode or NcAttrs or int or float or list): old minValue.
            Defaults to 0.
        input_max (NcNode or NcAttrs or int or float or list): old maxValue.
            Defaults to 1.
        values_hue (list): List of tuples for hue-graph in the form;
            (value_Position, value_FloatValue, value_Interp)
            The value interpolation element is optional (default: linear)
            Defaults to None.
        values_saturation (list): List of tuples for saturation-graph in form;
            (value_Position, value_FloatValue, value_Interp)
            The value interpolation element is optional (default: linear)
            Defaults to None.
        values_value (list): List of tuples for value-graph in the form;
            (value_Position, value_FloatValue, value_Interp)
            The value interpolation element is optional (default: linear)
            Defaults to None.

    Returns:
        NcNode: Instance with remapHsv-node and output-attribute(s)

    Raises:
        TypeError: If given values isn't a list of either lists or tuples.
        RuntimeError: If given values isn't a list of lists/tuples of
            length 2 or 3.

    Example:
        ::

            Op.remap_hsv(
                Node("blinn1.outColor"),
                values_saturation=[(0.1, .2, 0), (0.4, 0.3)]
            )
    """
    created_node = _create_operation_node(
        "remap_hsv", attr_a, output_min, output_max, input_min, input_max
    )

    value_lists = [values_hue, values_saturation, values_value]
    for values, setting in zip(value_lists, ["hue", "saturation", "value"]):
        for index, value_data in enumerate(values or []):
            # value_Position, value_FloatValue, value_Interp
            # "x-axis", "y-axis", interpolation

            if not isinstance(value_data, (list, tuple)):
                msg = (
                    "The values-flag for remap_hsv requires a list of "
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
                    "The values-flag for remap_hsv requires a list of "
                    "tuples of length 2 or 3! Got {0} instead.".format(values)
                )
                raise RuntimeError(msg)

            # Set these attributes directly to avoid unnecessary unravelling.
            _traced_set_attr(
                "{0}.{1}[{2}]".format(created_node.node, setting, index),
                (pos, val, interp)
            )

    return created_node


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
        output_min (NcNode or NcAttrs or int or float or list): minValue.
            Defaults to 0.
        output_max (NcNode or NcAttrs or int or float or list): maxValue.
            Defaults to 1.
        input_min (NcNode or NcAttrs or int or float or list): old minValue.
            Defaults to 0.
        input_max (NcNode or NcAttrs or int or float or list): old maxValue.
            Defaults to 1.
        values (list): List of tuples in the following form;
            (value_Position, value_FloatValue, value_Interp)
            The value interpolation element is optional (default: linear)
            Defaults to None.

    Returns:
        NcNode: Instance with remapValue-node and output-attribute(s)

    Raises:
        TypeError: If given values isn't a list of either lists or tuples.
        RuntimeError: If given values isn't a list of lists/tuples of
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
def reverse(attr_a):
    """Create reverse-node to get 1 minus the input.

    Args:
        attr_a (NcNode or NcAttrs or str or int or float): Input value

    Returns:
        NcNode: Instance with reverse-node and output-attribute(s)

    Example:
        ::

            Op.reverse(Node("pCube.visibility"))
    """
    return _create_operation_node("reverse", attr_a)


@noca_op
def rgb_to_hsv(rgb_color):
    """Create rgbToHsv-node to get RGB color in HSV representation.

    Args:
        rgb_color (NcNode or NcAttrs or str or int or float): Input RGB color.

    Returns:
        NcNode: Instance with rgbToHsv-node and output-attribute(s)

    Example:
        ::

            Op.rgb_to_hsv(Node("blinn1.outColor"))
    """
    return _create_operation_node("rgb_to_hsv", rgb_color)


@noca_op
def set_range(
        attr_a,
        min_value=0,
        max_value=1,
        old_min_value=0,
        old_max_value=1):
    """Create setRange-node to remap the given input attr to a new min/max.

    Args:
        attr_a (NcNode or NcAttrs or str or int or float): Input value.
        min_value (NcNode or NcAttrs or int or float or list): New min.
            Defaults to 0.
        max_value (NcNode or NcAttrs or int or float or list): New max.
            Defaults to 1.
        old_min_value (NcNode or NcAttrs or int or float or list): Old min.
            Defaults to 0.
        old_max_value (NcNode or NcAttrs or int or float or list): Old max.
            Defaults to 1.

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
def sum(*attrs):
    """Create plusMinusAverage-node for averaging input attrs.

    Args:
        attrs (NcNode or NcAttrs or NcList or string or list or tuple):
            Inputs to be added up.

    Returns:
        NcNode: Instance with plusMinusAverage-node and output-attribute(s)

    Example:
        ::

            Op.average(Node("pCube.t"), [1, 2, 3])
    """
    if len(attrs) == 1:
        attrs = attrs[0]

    return _create_operation_node("sum", attrs)


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


@noca_op
def weighted_add_matrix(*matrices):
    """Add matrices with a weight-bias.

    Args:
        matrices (NcNode or NcAttrs or list or tuple): Any number of matrices.
            Can be a list of tuples; (matrix, weight) or simply a list of
            matrices. In that case the weight will be evenly distributed
            between all given matrices.

    Returns:
        NcNode: Instance with wtAddMatrix-node and output-attribute(s)

    Example:
        ::
            cube_a = Node("pCube1.worldMatrix")
            cube_b = Node("pCube2.worldMatrix")
            Op.weighted_add_matrix(cube_a, cube_b)
    """
    weighted_matrices = []
    num_matrices = len(matrices)
    for matrix in matrices:
        if isinstance(matrix, tuple) and len(matrix) == 2:
            weighted_matrices.append(matrix)
        else:
            weighted_matrices.append((matrix, 1.0/num_matrices))

    return _create_operation_node("weighted_add_matrix", weighted_matrices)
