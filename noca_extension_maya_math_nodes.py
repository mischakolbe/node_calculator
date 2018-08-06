"""Additional Ops for NodeCalculator, based on Serguei Kalentchouk's math nodes.

Note:
    This NodeCalculator extension requires the built mayaMathNodes plugin
    (v1.3.0) from:
    https://github.com/serguei-k/maya-math-nodes

    This is a functioning example for what a possible NodeCalculator extension
    could look like, using proprietary/custom nodes.

    The following nodes are currently not implemented! They have a multi-index
    output, which is currently not supported. (You can still manually
    create and connect them though)
    - NormalizeArray
    - NormalizeWeightsArray
    - SelectArray
    - SelectIntArray
    - SelectAngleArray
    - SelectVectorArray
    - SelectMatrixArray

:author: Mischa Kolbe <mischakolbe@gmail.com>
"""

from maya import cmds

from node_calculator.core import noca_op
from node_calculator.core import _create_and_connect_node, _unravel_item_as_list


REQUIRED_EXTENSION_PLUGINS = ["mayaMathNodes"]


EXTENSION_OPERATORS = {
    # Absolute.h
    "absolute": {
        "node": "math_Absolute",
        "inputs": [
            ["input"],
        ],
        "outputs": [
            ["output"],
        ],
    },
    "absolute_int": {
        "node": "math_AbsoluteInt",
        "inputs": [
            ["input"],
        ],
        "outputs": [
            ["output"],
        ],
    },
    "absolute_angle": {
        "node": "math_AbsoluteAngle",
        "inputs": [
            ["input"],
        ],
        "outputs": [
            ["output"],
        ],
    },


    # Add.h
    "add": {
        "node": "math_Add",
        "inputs": [
            ["input1"],
            ["input2"],
        ],
        "outputs": [
            ["output"],
        ],
    },
    "add_int": {
        "node": "math_AddInt",
        "inputs": [
            ["input1"],
            ["input2"],
        ],
        "outputs": [
            ["output"],
        ],
    },
    "add_angle": {
        "node": "math_AddAngle",
        "inputs": [
            ["input1"],
            ["input2"],
        ],
        "outputs": [
            ["output"],
        ],
    },
    "add_vector": {
        "node": "math_AddVector",
        "inputs": [
            ["input1X", "input1Y", "input1Z"],
            ["input2X", "input2Y", "input2Z"],
        ],
        "outputs": [
            ["outputX", "outputY", "outputZ"],
        ],
    },


    # Array.h
    # Average
    "average": {
        "node": "math_Average",
        "inputs": [
            ["input[{multi_index}]"],
        ],
        "outputs": [
            ["output"],
        ],
        "is_multi_index": True,
    },
    "average_int": {
        "node": "math_AverageInt",
        "inputs": [
            ["input[{multi_index}]"],
        ],
        "outputs": [
            ["output"],
        ],
        "is_multi_index": True,
    },
    "average_angle": {
        "node": "math_AverageAngle",
        "inputs": [
            ["input[{multi_index}]"],
        ],
        "outputs": [
            ["output"],
        ],
        "is_multi_index": True,
    },
    "average_rotation": {
        "node": "math_AverageRotation",
        "inputs": [
            [
                "input[{multi_index}].inputX",
                "input[{multi_index}].inputY",
                "input[{multi_index}].inputZ",
            ],
        ],
        "outputs": [
            ["outputX", "outputY", "outputZ"],
        ],
        "is_multi_index": True,
    },
    "average_vector": {
        "node": "math_AverageVector",
        "inputs": [
            [
                "input[{multi_index}].inputX",
                "input[{multi_index}].inputY",
                "input[{multi_index}].inputZ",
            ],
        ],
        "outputs": [
            ["outputX", "outputY", "outputZ"],
        ],
        "is_multi_index": True,
    },
    "average_matrix": {
        "node": "math_AverageMatrix",
        "inputs": [
            ["input[{multi_index}]"],
        ],
        "outputs": [
            ["output"],
        ],
        "is_multi_index": True,
    },
    "average_quaternion": {
        "node": "math_AverageQuaternion",
        "inputs": [
            [
                "input[{multi_index}].inputX",
                "input[{multi_index}].inputY",
                "input[{multi_index}].inputZ",
                "input[{multi_index}].inputW",
            ],
        ],
        "outputs": [
            ["outputX", "outputY", "outputZ", "outputW"],
        ],
        "is_multi_index": True,
    },
    # Sum
    "sum": {
        "node": "math_Sum",
        "inputs": [
            ["input[{multi_index}]"],
        ],
        "outputs": [
            ["output"],
        ],
        "is_multi_index": True,
    },
    "sum_int": {
        "node": "math_SumInt",
        "inputs": [
            ["input[{multi_index}]"],
        ],
        "outputs": [
            ["output"],
        ],
        "is_multi_index": True,
    },
    "sum_angle": {
        "node": "math_SumAngle",
        "inputs": [
            ["input[{multi_index}]"],
        ],
        "outputs": [
            ["output"],
        ],
        "is_multi_index": True,
    },
    "sum_vector": {
        "node": "math_SumVector",
        "inputs": [
            [
                "input[{multi_index}].inputX",
                "input[{multi_index}].inputY",
                "input[{multi_index}].inputZ",
            ],
        ],
        "outputs": [
            ["outputX", "outputY", "outputZ"],
        ],
        "is_multi_index": True,
    },
    # Min/Max Element
    "min_element": {
        "node": "math_MinElement",
        "inputs": [
            ["input[{multi_index}]"],
        ],
        "outputs": [
            ["output"],
        ],
        "is_multi_index": True,
    },
    "min_int_element": {
        "node": "math_MinIntElement",
        "inputs": [
            ["input[{multi_index}]"],
        ],
        "outputs": [
            ["output"],
        ],
        "is_multi_index": True,
    },
    "min_angle_element": {
        "node": "math_MinAngleElement",
        "inputs": [
            ["input[{multi_index}]"],
        ],
        "outputs": [
            ["output"],
        ],
        "is_multi_index": True,
    },
    "max_element": {
        "node": "math_MaxElement",
        "inputs": [
            ["input[{multi_index}]"],
        ],
        "outputs": [
            ["output"],
        ],
        "is_multi_index": True,
    },
    "max_int_element": {
        "node": "math_MaxIntElement",
        "inputs": [
            ["input[{multi_index}]"],
        ],
        "outputs": [
            ["output"],
        ],
        "is_multi_index": True,
    },
    "max_angle_element": {
        "node": "math_MaxAngleElement",
        "inputs": [
            ["input[{multi_index}]"],
        ],
        "outputs": [
            ["output"],
        ],
        "is_multi_index": True,
    },
    # WeightedAverage
    "weighted_average": {
        "node": "math_WeightedAverage",
        "inputs": [
            [
                "input[{multi_index}].value",
                "input[{multi_index}].weight",
            ],
        ],
        "outputs": [
            ["output"],
        ],
        "is_multi_index": True,
    },
    "weighted_average_int": {
        "node": "math_WeightedAverageInt",
        "inputs": [
            [
                "input[{multi_index}].value",
                "input[{multi_index}].weight",
            ],
        ],
        "outputs": [
            ["output"],
        ],
        "is_multi_index": True,
    },
    "weighted_average_angle": {
        "node": "math_WeightedAverageAngle",
        "inputs": [
            [
                "input[{multi_index}].value",
                "input[{multi_index}].weight",
            ],
        ],
        "outputs": [
            ["output"],
        ],
        "is_multi_index": True,
    },
    "weighted_average_rotation": {
        "node": "math_WeightedAverageRotation",
        "inputs": [
            [
                "input[{multi_index}].value.valueX",
                "input[{multi_index}].value.valueY",
                "input[{multi_index}].value.valueZ",
                "input[{multi_index}].weight",
            ],
        ],
        "outputs": [
            ["outputX", "outputY", "outputZ"],
        ],
        "is_multi_index": True,
    },
    "weighted_average_vector": {
        "node": "math_WeightedAverageVector",
        "inputs": [
            [
                "input[{multi_index}].value.valueX",
                "input[{multi_index}].value.valueY",
                "input[{multi_index}].value.valueZ",
                "input[{multi_index}].weight",
            ],
        ],
        "outputs": [
            ["outputX", "outputY", "outputZ"],
        ],
        "is_multi_index": True,
    },
    "weighted_average_matrix": {
        "node": "math_WeightedAverageMatrix",
        "inputs": [
            [
                "input[{multi_index}].value",
                "input[{multi_index}].weight",
            ],
        ],
        "outputs": [
            ["output"],
        ],
        "is_multi_index": True,
    },
    "weighted_average_quaternion": {
        "node": "math_WeightedAverageQuaternion",
        "inputs": [
            [
                "input[{multi_index}].value.valueX",
                "input[{multi_index}].value.valueY",
                "input[{multi_index}].value.valueZ",
                "input[{multi_index}].value.valueW",
                "input[{multi_index}].weight",
            ],
        ],
        "outputs": [
            ["outputX", "outputY", "outputZ", "outputW"],
        ],
        "is_multi_index": True,
    },


    # Clamp.h
    "clamp": {
        "node": "math_Clamp",
        "inputs": [
            ["input"],
            ["inputMin"],
            ["inputMax"],
        ],
        "outputs": [
            ["output"],
        ],
    },
    "clamp_int": {
        "node": "math_ClampInt",
        "inputs": [
            ["input"],
            ["inputMin"],
            ["inputMax"],
        ],
        "outputs": [
            ["output"],
        ],
    },
    "clamp_angle": {
        "node": "math_ClampAngle",
        "inputs": [
            ["input"],
            ["inputMin"],
            ["inputMax"],
        ],
        "outputs": [
            ["output"],
        ],
    },


    # Condition.h
    # Compare
    "compare": {
        "node": "math_Compare",
        "inputs": [
            ["input1"],
            ["input2"],
            ["operation"],
        ],
        "outputs": [
            ["output"],
        ],
    },
    "compare_angle": {
        "node": "math_CompareAngle",
        "inputs": [
            ["input1"],
            ["input2"],
            ["operation"],
        ],
        "outputs": [
            ["output"],
        ],
    },
    # Select
    "select": {
        "node": "math_Select",
        "inputs": [
            ["input1"],
            ["input2"],
            ["condition"],
        ],
        "outputs": [
            ["output"],
        ],
    },
    "select_int": {
        "node": "math_SelectInt",
        "inputs": [
            ["input1"],
            ["input2"],
            ["condition"],
        ],
        "outputs": [
            ["output"],
        ],
    },
    "select_angle": {
        "node": "math_SelectAngle",
        "inputs": [
            ["input1"],
            ["input2"],
            ["condition"],
        ],
        "outputs": [
            ["output"],
        ],
    },
    "select_rotation": {
        "node": "math_SelectRotation",
        "inputs": [
            ["input1X", "input1Y", "input1Z"],
            ["input2X", "input2Y", "input2Z"],
            ["condition"],
        ],
        "outputs": [
            ["outputX", "outputY", "outputZ"],
        ],
    },
    "select_vector": {
        "node": "math_SelectVector",
        "inputs": [
            ["input1X", "input1Y", "input1Z"],
            ["input2X", "input2Y", "input2Z"],
            ["condition"],
        ],
        "outputs": [
            ["outputX", "outputY", "outputZ"],
        ],
    },
    "select_matrix": {
        "node": "math_SelectMatrix",
        "inputs": [
            ["input1"],
            ["input2"],
            ["condition"],
        ],
        "outputs": [
            ["output"],
        ],
    },
    "select_quaternion": {
        "node": "math_SelectQuaternion",
        "inputs": [
            ["input1X", "input1Y", "input1Z", "input1W"],
            ["input2X", "input2Y", "input2Z", "input2W"],
            ["condition"],
        ],
        "outputs": [
            ["outputX", "outputY", "outputZ", "outputW"],
        ],
        "output_is_predetermined": True,
    },
    # Logical
    "and_bool": {
        "node": "math_AndBool",
        "inputs": [
            ["input1"],
            ["input2"],
        ],
        "outputs": [
            ["output"],
        ],
    },
    "or_bool": {
        "node": "math_OrBool",
        "inputs": [
            ["input1"],
            ["input2"],
        ],
        "outputs": [
            ["output"],
        ],
    },
    "xor_bool": {
        "node": "math_XorBool",
        "inputs": [
            ["input1"],
            ["input2"],
        ],
        "outputs": [
            ["output"],
        ],
    },
    "and_int": {
        "node": "math_AndInt",
        "inputs": [
            ["input1"],
            ["input2"],
        ],
        "outputs": [
            ["output"],
        ],
    },
    "or_int": {
        "node": "math_OrInt",
        "inputs": [
            ["input1"],
            ["input2"],
        ],
        "outputs": [
            ["output"],
        ],
    },
    "xor_int": {
        "node": "math_XorInt",
        "inputs": [
            ["input1"],
            ["input2"],
        ],
        "outputs": [
            ["output"],
        ],
    },


    # Convert.h
    "rotation_from_matrix": {
        "node": "math_RotationFromMatrix",
        "inputs": [
            ["input"],
            ["rotationOrder"],
        ],
        "outputs": [
            ["outputX", "outputY", "outputZ"],
        ],
        "output_is_predetermined": True,
    },
    "rotation_from_quaternion": {
        "node": "math_RotationFromQuaternion",
        "inputs": [
            ["inputX", "inputY", "inputZ", "inputW"],
            ["rotationOrder"],
        ],
        "outputs": [
            ["outputX", "outputY", "outputZ"],
        ],
        "output_is_predetermined": True,
    },
    "quaternion_from_matrix": {
        "node": "math_QuaternionFromMatrix",
        "inputs": [
            ["input"],
            ["rotationOrder"],
        ],
        "outputs": [
            ["outputX", "outputY", "outputZ", "outputW"],
        ],
        "output_is_predetermined": True,
    },
    "quaternion_from_rotation": {
        "node": "math_QuaternionFromRotation",
        "inputs": [
            ["inputX", "inputY", "inputZ"],
            ["rotationOrder"],
        ],
        "outputs": [
            ["outputX", "outputY", "outputZ", "outputW"],
        ],
        "output_is_predetermined": True,
    },
    "translation_from_matrix": {
        "node": "math_TranslationFromMatrix",
        "inputs": [
            ["input"],
        ],
        "outputs": [
            ["outputX", "outputY", "outputZ"],
        ],
        "output_is_predetermined": True,
    },
    "scale_from_matrix": {
        "node": "math_ScaleFromMatrix",
        "inputs": [
            ["input"],
        ],
        "outputs": [
            ["outputX", "outputY", "outputZ"],
        ],
        "output_is_predetermined": True,
    },
    "matrix_from_trs": {
        "node": "math_MatrixFromTRS",
        "inputs": [
            ["translationX", "translationY", "translationZ"],
            ["rotationX", "rotationY", "rotationZ"],
            ["scaleX", "scaleY", "scaleZ"],
            ["rotationOrder"],
        ],
        "outputs": [
            ["output"],
        ],
        "output_is_predetermined": True,
    },
    "axis_from_matrix": {
        "node": "math_AxisFromMatrix",
        "inputs": [
            ["input"],
            ["axis"],
        ],
        "outputs": [
            ["outputX", "outputY", "outputZ"],
        ],
        "output_is_predetermined": True,
    },


    # Distance.h
    "distance_points": {
        "node": "math_DistancePoints",
        "inputs": [
            ["input1X", "input1Y", "input1Z"],
            ["input2X", "input2Y", "input2Z"],
        ],
        "outputs": [
            ["output"],
        ],
    },
    "distance_transforms": {
        "node": "math_DistanceTransforms",
        "inputs": [
            ["input1"],
            ["input2"],
        ],
        "outputs": [
            ["output"],
        ],
    },


    # Divide.h
    "divide": {
        "node": "math_Divide",
        "inputs": [
            ["input1"],
            ["input2"],
        ],
        "outputs": [
            ["output"],
        ],
    },
    "divide_by_int": {
        "node": "math_DivideByInt",
        "inputs": [
            ["input1"],
            ["input2"],
        ],
        "outputs": [
            ["output"],
        ],
    },
    "divide_by_angle": {
        "node": "math_DivideAngle",
        "inputs": [
            ["input1"],
            ["input2"],
        ],
        "outputs": [
            ["output"],
        ],
    },
    "divide_angle_by_int": {
        "node": "math_DivideAngleByInt",
        "inputs": [
            ["input1"],
            ["input2"],
        ],
        "outputs": [
            ["output"],
        ],
    },
    "modulus_int": {
        "node": "math_ModulusInt",
        "inputs": [
            ["input1"],
            ["input2"],
        ],
        "outputs": [
            ["output"],
        ],
    },


    # Interpolate.h
    "lerp": {
        "node": "math_Lerp",
        "inputs": [
            ["input1"],
            ["input2"],
            ["alpha"],
        ],
        "outputs": [
            ["output"],
        ],
    },
    "lerp_angle": {
        "node": "math_LerpAngle",
        "inputs": [
            ["input1"],
            ["input2"],
            ["alpha"],
        ],
        "outputs": [
            ["output"],
        ],
    },
    "lerp_vector": {
        "node": "math_LerpVector",
        "inputs": [
            ["input1X", "input1Y", "input1Z"],
            ["input2X", "input2Y", "input2Z"],
            ["alpha"],
        ],
        "outputs": [
            ["outputX", "outputY", "outputZ"],
        ],
    },
    "lerp_matrix": {
        "node": "math_LerpMatrix",
        "inputs": [
            ["input1"],
            ["input2"],
            ["alpha"],
        ],
        "outputs": [
            ["output"],
        ],
    },
    "slerp_quaternion": {
        "node": "math_SlerpQuaternion",
        "inputs": [
            ["input1X", "input1Y", "input1Z", "input1W"],
            ["input2X", "input2Y", "input2Z", "input2W"],
            ["alpha"],
            ["interpolationType"],
        ],
        "outputs": [
            ["outputX", "outputY", "outputZ", "outputW"],
        ],
        "output_is_predetermined": True,
    },


    # Inverse.h
    "inverse_rotation": {
        "node": "math_InverseRotation",
        "inputs": [
            ["inputX", "inputY", "inputZ"],
        ],
        "outputs": [
            ["outputX", "outputY", "outputZ"],
        ],
    },
    "inverse_matrix": {
        "node": "math_InverseMatrix",
        "inputs": [
            ["input"],
        ],
        "outputs": [
            ["output"],
        ],
    },
    "inverse_quaternion": {
        "node": "math_InverseQuaternion",
        "inputs": [
            ["inputX", "inputY", "inputZ", "inputW"],
        ],
        "outputs": [
            ["outputX", "outputY", "outputZ", "outputW"],
        ],
        "output_is_predetermined": True,
    },


    # MinMax.h
    "min": {
        "node": "math_Min",
        "inputs": [
            ["input1"],
            ["input2"],
        ],
        "outputs": [
            ["output"],
        ],
    },
    "max": {
        "node": "math_Max",
        "inputs": [
            ["input1"],
            ["input2"],
        ],
        "outputs": [
            ["output"],
        ],
    },
    "min_int": {
        "node": "math_MinInt",
        "inputs": [
            ["input1"],
            ["input2"],
        ],
        "outputs": [
            ["output"],
        ],
    },
    "max_int": {
        "node": "math_MaxInt",
        "inputs": [
            ["input1"],
            ["input2"],
        ],
        "outputs": [
            ["output"],
        ],
    },
    "min_angle": {
        "node": "math_MinAngle",
        "inputs": [
            ["input1"],
            ["input2"],
        ],
        "outputs": [
            ["output"],
        ],
    },
    "max_angle": {
        "node": "math_MaxAngle",
        "inputs": [
            ["input1"],
            ["input2"],
        ],
        "outputs": [
            ["output"],
        ],
    },


    # Multiply.h
    "multiply": {
        "node": "math_Multiply",
        "inputs": [
            ["input1"],
            ["input2"],
        ],
        "outputs": [
            ["output"],
        ],
    },
    "multiply_by_int": {
        "node": "math_MultiplyByInt",
        "inputs": [
            ["input1"],
            ["input2"],
        ],
        "outputs": [
            ["output"],
        ],
    },
    "multiply_int": {
        "node": "math_MultiplyInt",
        "inputs": [
            ["input1"],
            ["input2"],
        ],
        "outputs": [
            ["output"],
        ],
    },
    "multiply_angle": {
        "node": "math_MultiplyAngle",
        "inputs": [
            ["input1"],
            ["input2"],
        ],
        "outputs": [
            ["output"],
        ],
    },
    "multiply_angle_by_int": {
        "node": "math_MultiplyAngleByInt",
        "inputs": [
            ["input1"],
            ["input2"],
        ],
        "outputs": [
            ["output"],
        ],
    },
    "multiply_rotation": {
        "node": "math_MultiplyRotation",
        "inputs": [
            ["input1X", "input1Y", "input1Z"],
            ["input2"],
        ],
        "outputs": [
            ["outputX", "outputY", "outputZ"],
        ],
    },
    "multiply_vector": {
        "node": "math_MultiplyVector",
        "inputs": [
            ["input1X", "input1Y", "input1Z"],
            ["input2"],
        ],
        "outputs": [
            ["outputX", "outputY", "outputZ"],
        ],
    },
    "multiply_vector_by_matrix": {
        "node": "math_MultiplyVectorByMatrix",
        "inputs": [
            ["input1X", "input1Y", "input1Z"],
            ["input2"],
        ],
        "outputs": [
            ["outputX", "outputY", "outputZ"],
        ],
    },
    "multiply_matrix": {
        "node": "math_MultiplyMatrix",
        "inputs": [
            ["input1"],
            ["input2"],
        ],
        "outputs": [
            ["output"],
        ],
    },
    "multiply_quaternion": {
        "node": "math_MultiplyQuaternion",
        "inputs": [
            ["input1X", "input1Y", "input1Z", "input1W"],
            ["input2X", "input2Y", "input2Z", "input2W"],
        ],
        "outputs": [
            ["outputX", "outputY", "outputZ", "outputW"],
        ],
        "output_is_predetermined": True,
    },


    # Negate.h
    "negate": {
        "node": "math_Negate",
        "inputs": [
            ["input"],
        ],
        "outputs": [
            ["output"],
        ],
    },
    "negate_int": {
        "node": "math_NegateInt",
        "inputs": [
            ["input"],
        ],
        "outputs": [
            ["output"],
        ],
    },
    "negate_angle": {
        "node": "math_NegateAngle",
        "inputs": [
            ["input"],
        ],
        "outputs": [
            ["output"],
        ],
    },
    "negate_vector": {
        "node": "math_NegateVector",
        "inputs": [
            ["inputX", "inputY", "inputZ"],
        ],
        "outputs": [
            ["outputX", "outputY", "outputZ"],
        ],
    },


    # Power.h
    "power": {
        "node": "math_Power",
        "inputs": [
            ["input"],
            ["exponent"],
        ],
        "outputs": [
            ["output"],
        ],
    },
    "square_root": {
        "node": "math_SquareRoot",
        "inputs": [
            ["input"],
        ],
        "outputs": [
            ["output"],
        ],
    },


    # Round.h
    "ceil": {
        "node": "math_Ceil",
        "inputs": [
            ["input"],
        ],
        "outputs": [
            ["output"],
        ],
    },
    "ceil_angle": {
        "node": "math_CeilAngle",
        "inputs": [
            ["input"],
        ],
        "outputs": [
            ["output"],
        ],
    },
    "floor": {
        "node": "math_Floor",
        "inputs": [
            ["input"],
        ],
        "outputs": [
            ["output"],
        ],
    },
    "floor_angle": {
        "node": "math_FloorAngle",
        "inputs": [
            ["input"],
        ],
        "outputs": [
            ["output"],
        ],
    },
    "round": {
        "node": "math_Round",
        "inputs": [
            ["input"],
        ],
        "outputs": [
            ["output"],
        ],
    },
    "round_angle": {
        "node": "math_RoundAngle",
        "inputs": [
            ["input"],
        ],
        "outputs": [
            ["output"],
        ],
    },


    # Subtract.h
    "subtract": {
        "node": "math_Subtract",
        "inputs": [
            ["input1"],
            ["input2"],
        ],
        "outputs": [
            ["output"],
        ],
    },
    "subtract_int": {
        "node": "math_SubtractInt",
        "inputs": [
            ["input1"],
            ["input2"],
        ],
        "outputs": [
            ["output"],
        ],
    },
    "subtract_angle": {
        "node": "math_SubtractAngle",
        "inputs": [
            ["input1"],
            ["input2"],
        ],
        "outputs": [
            ["output"],
        ],
    },
    "subtract_vector": {
        "node": "math_SubtractVector",
        "inputs": [
            ["input1X", "input1Y", "input1Z"],
            ["input2X", "input2Y", "input2Z"],
        ],
        "outputs": [
            ["outputX", "outputY", "outputZ"],
        ],
    },


    # Trig.h
    "sin": {
        "node": "math_SinAngle",
        "inputs": [
            ["input"],
        ],
        "outputs": [
            ["output"],
        ],
    },
    "asin": {
        "node": "math_Asin",
        "inputs": [
            ["input"],
        ],
        "outputs": [
            ["output"],
        ],
    },
    "cos": {
        "node": "math_CosAngle",
        "inputs": [
            ["input"],
        ],
        "outputs": [
            ["output"],
        ],
    },
    "acos": {
        "node": "math_Acos",
        "inputs": [
            ["input"],
        ],
        "outputs": [
            ["output"],
        ],
    },
    "tan": {
        "node": "math_TanAngle",
        "inputs": [
            ["input"],
        ],
        "outputs": [
            ["output"],
        ],
    },
    "atan": {
        "node": "math_Atan",
        "inputs": [
            ["input"],
        ],
        "outputs": [
            ["output"],
        ],
    },
    "atan2": {
        "node": "math_Atan2",
        "inputs": [
            ["input1"],
            ["input2"],
        ],
        "outputs": [
            ["output"],
        ],
    },


    # Twist.h
    "twist_from_rotation": {
        "node": "math_TwistFromRotation",
        "inputs": [
            ["inputX", "inputY", "inputZ"],
            ["axis"],
            ["rotationOrder"],
        ],
        "outputs": [
            ["output"],
        ],
    },
    "twist_from_matrix": {
        "node": "math_TwistFromMatrix",
        "inputs": [
            ["input"],
            ["axis"],
            ["rotationOrder"],
        ],
        "outputs": [
            ["output"],
        ],
    },


    # VectorOps.h
    "vector_length": {
        "node": "math_VectorLength",
        "inputs": [
            ["inputX", "inputY", "inputZ"],
        ],
        "outputs": [
            ["output"],
        ],
    },
    "vector_length_squared": {
        "node": "math_VectorLengthSquared",
        "inputs": [
            ["inputX", "inputY", "inputZ"],
        ],
        "outputs": [
            ["output"],
        ],
    },
    "normalize_vector": {
        "node": "math_NormalizeVector",
        "inputs": [
            ["inputX", "inputY", "inputZ"],
        ],
        "outputs": [
            ["outputX", "outputY", "outputZ"],
        ],
    },
    "dot_product": {
        "node": "math_DotProduct",
        "inputs": [
            ["input1X", "input1Y", "input1Z"],
            ["input2X", "input2Y", "input2Z"],
        ],
        "outputs": [
            ["output"],
        ],
    },
    "angle_between_vectors": {
        "node": "math_AngleBetweenVectors",
        "inputs": [
            ["input1X", "input1Y", "input1Z"],
            ["input2X", "input2Y", "input2Z"],
        ],
        "outputs": [
            ["output"],
        ],
    },
    "cross_product": {
        "node": "math_CrossProduct",
        "inputs": [
            ["input1X", "input1Y", "input1Z"],
            ["input2X", "input2Y", "input2Z"],
        ],
        "outputs": [
            ["outputX", "outputY", "outputZ"],
        ],
    },

}


# Absolute.h
@noca_op
def absolute(attr_a):
    return _create_and_connect_node('absolute', attr_a)


@noca_op
def absolute_int(attr_a):
    return _create_and_connect_node('absolute_int', attr_a)


@noca_op
def absolute_angle(attr_a):
    return _create_and_connect_node('absolute_angle', attr_a)


# Add.h
@noca_op
def add(attr_a, attr_b=0):
    return _create_and_connect_node('add', attr_a, attr_b)


@noca_op
def add_int(attr_a, attr_b=0):
    return _create_and_connect_node('add_int', attr_a, attr_b)


@noca_op
def add_angle(attr_a, attr_b=0):
    return _create_and_connect_node('add_angle', attr_a, attr_b)


@noca_op
def add_vector(vector_a, vector_b=(0, 0, 0)):
    return _create_and_connect_node('add_vector', vector_a, vector_b)


# Array.h
# Average
@noca_op
def average(*attrs):
    return _create_and_connect_node('average', *attrs)


@noca_op
def average_int(*attrs):
    return _create_and_connect_node('average_int', *attrs)


@noca_op
def average_angle(*attrs):
    return _create_and_connect_node('average_angle', *attrs)


@noca_op
def average_rotation(*attrs):
    return _create_and_connect_node('average_rotation', *attrs)


@noca_op
def average_vector(*attrs):
    return _create_and_connect_node('average_vector', *attrs)


@noca_op
def average_matrix(*attrs):
    return _create_and_connect_node('average_matrix', *attrs)


@noca_op
def average_quaternion(*attrs):
    return _create_and_connect_node('average_quaternion', *attrs)


# Sum
@noca_op
def sum(*attrs):
    return _create_and_connect_node('sum', *attrs)


@noca_op
def sum_int(*attrs):
    return _create_and_connect_node('sum_int', *attrs)


@noca_op
def sum_angle(*attrs):
    return _create_and_connect_node('sum_angle', *attrs)


@noca_op
def sum_vector(*attrs):
    return _create_and_connect_node('sum_vector', *attrs)


# Min/Max Element
@noca_op
def min_element(*attrs):
    return _create_and_connect_node('min_element', *attrs)


@noca_op
def min_int_element(*attrs):
    return _create_and_connect_node('min_int_element', *attrs)


@noca_op
def min_angle_element(*attrs):
    return _create_and_connect_node('min_angle_element', *attrs)


@noca_op
def max_element(*attrs):
    return _create_and_connect_node('max_element', *attrs)


@noca_op
def max_int_element(*attrs):
    return _create_and_connect_node('max_int_element', *attrs)


@noca_op
def max_angle_element(*attrs):
    return _create_and_connect_node('max_angle_element', *attrs)


# WeightedAverage
@noca_op
def weighted_average(*attrs):
    return _create_and_connect_node('weighted_average', *attrs)


@noca_op
def weighted_average_int(*attrs):
    return _create_and_connect_node('weighted_average_int', *attrs)


@noca_op
def weighted_average_angle(*attrs):
    return _create_and_connect_node('weighted_average_angle', *attrs)


@noca_op
def weighted_average_rotation(*attrs):
    flattened_attrs = []
    for attr, weight in attrs:
        unravelled_items = _unravel_item_as_list(attr)
        unravelled_items.append(weight)
        if len(unravelled_items) != 4:
            cmds.error(
                "Expected list of [3D rotation, weight], got {0}".format(attrs)
            )
        flattened_attrs.append(unravelled_items)

    return _create_and_connect_node('weighted_average_rotation', *flattened_attrs)


@noca_op
def weighted_average_vector(*attrs):
    flattened_attrs = []
    for attr, weight in attrs:
        unravelled_items = _unravel_item_as_list(attr)
        unravelled_items.append(weight)
        if len(unravelled_items) != 4:
            cmds.error(
                "Expected list of [3D vector, weight], got {0}".format(attrs)
            )
        flattened_attrs.append(unravelled_items)

    return _create_and_connect_node('weighted_average_vector', *flattened_attrs)


@noca_op
def weighted_average_matrix(*attrs):
    return _create_and_connect_node('weighted_average_matrix', *attrs)


@noca_op
def weighted_average_quaternion(*attrs):
    flattened_attrs = []
    for attr, weight in attrs:
        unravelled_items = _unravel_item_as_list(attr)
        unravelled_items.append(weight)
        if len(unravelled_items) != 4:
            cmds.error(
                "Expected list of [4D quaternion, weight], got {0}".format(attrs)
            )
        flattened_attrs.append(unravelled_items)

    return _create_and_connect_node('weighted_average_quaternion', *flattened_attrs)


# Clamp.h
@noca_op
def clamp(attr_a, input_min=0, input_max=1):
    return _create_and_connect_node('clamp', attr_a, input_min, input_max)


@noca_op
def clamp_int(attr_a, input_min=0, input_max=1):
    return _create_and_connect_node('clamp_int', attr_a, input_min, input_max)


@noca_op
def clamp_angle(attr_a, input_min=0, input_max=360):
    return _create_and_connect_node('clamp_angle', attr_a, input_min, input_max)


# Condition.h
# Compare
@noca_op
def compare(attr_a, attr_b=0, operation=0):
    return _create_and_connect_node('compare', attr_a, attr_b, operation)


@noca_op
def compare_angle(attr_a, attr_b=0, operation=0):
    return _create_and_connect_node('compare_angle', attr_a, attr_b, operation)


# Select
@noca_op
def select(attr_a, attr_b=0, condition=False):
    return _create_and_connect_node('select', attr_a, attr_b, condition)


@noca_op
def select_int(attr_a, attr_b=0, condition=False):
    return _create_and_connect_node('select_int', attr_a, attr_b, condition)


@noca_op
def select_angle(attr_a, attr_b=0, condition=False):
    return _create_and_connect_node('select_angle', attr_a, attr_b, condition)


@noca_op
def select_rotation(vector_a, vector_b=(0, 0, 0), condition=False):
    return _create_and_connect_node('select_rotation', vector_a, vector_b, condition)


@noca_op
def select_vector(vector_a, vector_b=(0, 0, 0), condition=False):
    return _create_and_connect_node('select_vector', vector_a, vector_b, condition)


@noca_op
def select_matrix(matrix_a, matrix_b, condition=False):
    return _create_and_connect_node('select_matrix', matrix_a, matrix_b, condition)


@noca_op
def select_quaternion(attr_a, attr_b=(0, 0, 0, 1), condition=False):
    return _create_and_connect_node('select_quaternion', attr_a, attr_b, condition)


# Logical
@noca_op
def and_bool(attr_a, attr_b=False):
    return _create_and_connect_node('and_bool', attr_a, attr_b)


@noca_op
def or_bool(attr_a, attr_b=False):
    return _create_and_connect_node('or_bool', attr_a, attr_b)


@noca_op
def xor_bool(attr_a, attr_b=False):
    return _create_and_connect_node('xor_bool', attr_a, attr_b)


@noca_op
def and_int(attr_a, attr_b=0):
    return _create_and_connect_node('and_int', attr_a, attr_b)


@noca_op
def or_int(attr_a, attr_b=0):
    return _create_and_connect_node('or_int', attr_a, attr_b)


@noca_op
def xor_int(attr_a, attr_b=0):
    return _create_and_connect_node('xor_int', attr_a, attr_b)


# Convert.h
@noca_op
def rotation_from_matrix(attr_a, rotation_order=0):
    return _create_and_connect_node('rotation_from_matrix', attr_a, rotation_order)


@noca_op
def rotation_from_quaternion(attr_a, rotation_order=0):
    return _create_and_connect_node('rotation_from_quaternion', attr_a, rotation_order)


@noca_op
def quaternion_from_matrix(attr_a, rotation_order=0):
    return _create_and_connect_node('quaternion_from_matrix', attr_a, rotation_order)


@noca_op
def quaternion_from_rotation(attr_a, rotation_order=0):
    return _create_and_connect_node('quaternion_from_rotation', attr_a, rotation_order)


@noca_op
def translation_from_matrix(attr_a):
    return _create_and_connect_node('translation_from_matrix', attr_a)


@noca_op
def scale_from_matrix(attr_a):
    return _create_and_connect_node('scale_from_matrix', attr_a)


@noca_op
def matrix_from_trs(
        translation=(0, 0, 0),
        rotation=(0, 0, 0),
        scale=(1, 1, 1),
        rotation_order=0):
    created_node = _create_and_connect_node(
        'matrix_from_trs',
        translation,
        rotation,
        scale,
        rotation_order
    )
    return created_node


@noca_op
def axis_from_matrix(attr_a, axis=0):
    return _create_and_connect_node('axis_from_matrix', attr_a, axis)


# Distance.h
@noca_op
def distance_points(vector_a, vector_b=(0, 0, 0)):
    return _create_and_connect_node('distance_points', vector_a, vector_b)


@noca_op
def distance_transforms(matrix_a, matrix_b=None):
    if matrix_b is None:
        return _create_and_connect_node('distance_transforms', matrix_a)
    return _create_and_connect_node('distance_transforms', matrix_a, matrix_b)


# Divide.h
@noca_op
def divide(attr_a, attr_b=1):
    return _create_and_connect_node('divide', attr_a, attr_b)


@noca_op
def divide_by_int(attr_a, attr_b=1):
    return _create_and_connect_node('divide_by_int', attr_a, attr_b)


@noca_op
def divide_by_angle(attr_a, attr_b=1):
    return _create_and_connect_node('divide_by_angle', attr_a, attr_b)


@noca_op
def divide_angle_by_int(attr_a, attr_b=1):
    return _create_and_connect_node('divide_angle_by_int', attr_a, attr_b)


@noca_op
def modulus_int(attr_a, attr_b=1):
    return _create_and_connect_node('modulus_int', attr_a, attr_b)


# Interpolate.h
@noca_op
def lerp(attr_a, attr_b=0, alpha=0.5):
    return _create_and_connect_node('lerp', attr_a, attr_b, alpha)


@noca_op
def lerp_angle(attr_a, attr_b=0, alpha=0.5):
    return _create_and_connect_node('lerp_angle', attr_a, attr_b, alpha)


@noca_op
def lerp_vector(vector_a, vector_b=(0, 0, 0), alpha=0.5):
    return _create_and_connect_node('lerp_vector', vector_a, vector_b, alpha)


@noca_op
def lerp_matrix(matrix_a, matrix_b, alpha=0.5):
    return _create_and_connect_node('lerp_matrix', matrix_a, matrix_b, alpha)


@noca_op
def slerp_quaternion(attr_a, attr_b=(0, 0, 0, 0), alpha=0.5, interpolation_type=0):
    return _create_and_connect_node('slerp_quaternion', attr_a, attr_b, alpha, interpolation_type)


# Inverse.h
@noca_op
def inverse_rotation(attr_a):
    return _create_and_connect_node('inverse_rotation', attr_a)


@noca_op
def inverse_matrix(matrix_a):
    return _create_and_connect_node('inverse_matrix', matrix_a)


@noca_op
def inverse_quaternion(attr_a):
    return _create_and_connect_node('inverse_quaternion', attr_a)


# MinMax.h
@noca_op
def min(attr_a, attr_b=1):
    return _create_and_connect_node('min', attr_a, attr_b)


@noca_op
def max(attr_a, attr_b=0):
    return _create_and_connect_node('max', attr_a, attr_b)


@noca_op
def min_int(attr_a, attr_b=1):
    return _create_and_connect_node('min_int', attr_a, attr_b)


@noca_op
def max_int(attr_a, attr_b=0):
    return _create_and_connect_node('max_int', attr_a, attr_b)


@noca_op
def min_angle(attr_a, attr_b=360):
    return _create_and_connect_node('min_angle', attr_a, attr_b)


@noca_op
def max_angle(attr_a, attr_b=0):
    return _create_and_connect_node('max_angle', attr_a, attr_b)


# Multiply.h
@noca_op
def multiply(attr_a, attr_b=1):
    return _create_and_connect_node('multiply', attr_a, attr_b)


@noca_op
def multiply_by_int(attr_a, attr_b=1):
    return _create_and_connect_node('multiply_by_int', attr_a, attr_b)


@noca_op
def multiply_int(attr_a, attr_b=1):
    return _create_and_connect_node('multiply_int', attr_a, attr_b)


@noca_op
def multiply_angle(attr_a, attr_b=1):
    return _create_and_connect_node('multiply_angle', attr_a, attr_b)


@noca_op
def multiply_angle_by_int(attr_a, attr_b=1):
    return _create_and_connect_node('multiply_angle_by_int', attr_a, attr_b)


@noca_op
def multiply_rotation(attr_a, attr_b=1):
    return _create_and_connect_node('multiply_rotation', attr_a, attr_b)


@noca_op
def multiply_vector(attr_a, attr_b=1):
    return _create_and_connect_node('multiply_vector', attr_a, attr_b)


@noca_op
def multiply_vector_by_matrix(attr_a, attr_b=None):
    if attr_b is None:
        return _create_and_connect_node('multiply_vector_by_matrix', attr_a)
    return _create_and_connect_node('multiply_vector_by_matrix', attr_a, attr_b)


@noca_op
def multiply_matrix(matrix_a, matrix_b=None):
    if matrix_b is None:
        return _create_and_connect_node('multiply_matrix', matrix_a)
    return _create_and_connect_node('multiply_matrix', matrix_a, matrix_b)


@noca_op
def multiply_quaternion(attr_a, attr_b=(0, 0, 0, 1)):
    return _create_and_connect_node('multiply_quaternion', attr_a, attr_b)


# Negate.h
@noca_op
def negate(attr_a):
    return _create_and_connect_node('negate', attr_a)


@noca_op
def negate_int(attr_a):
    return _create_and_connect_node('negate_int', attr_a)


@noca_op
def negate_angle(attr_a):
    return _create_and_connect_node('negate_angle', attr_a)


@noca_op
def negate_vector(attr_a):
    return _create_and_connect_node('negate_vector', attr_a)


# Power.h
@noca_op
def power(attr_a, exponent=2):
    return _create_and_connect_node('power', attr_a, exponent)


@noca_op
def square_root(attr_a):
    return _create_and_connect_node('square_root', attr_a)


# Round.h
@noca_op
def ceil(attr_a):
    return _create_and_connect_node('ceil', attr_a)


@noca_op
def ceil_angle(attr_a):
    return _create_and_connect_node('ceil_angle', attr_a)


@noca_op
def floor(attr_a):
    return _create_and_connect_node('floor', attr_a)


@noca_op
def floor_angle(attr_a):
    return _create_and_connect_node('floor_angle', attr_a)


@noca_op
def round(attr_a):
    return _create_and_connect_node('round', attr_a)


@noca_op
def round_angle(attr_a):
    return _create_and_connect_node('round_angle', attr_a)


# Subtract.h
@noca_op
def subtract(attr_a, attr_b=0):
    return _create_and_connect_node('subtract', attr_a, attr_b)


@noca_op
def subtract_int(attr_a, attr_b=0):
    return _create_and_connect_node('subtract_int', attr_a, attr_b)


@noca_op
def subtract_angle(attr_a, attr_b=0):
    return _create_and_connect_node('subtract_angle', attr_a, attr_b)


@noca_op
def subtract_vector(attr_a, attr_b=(0, 0, 0)):
    return _create_and_connect_node('subtract_vector', attr_a, attr_b)


# Trig.h
@noca_op
def sin(attr_a):
    return _create_and_connect_node('sin', attr_a)


@noca_op
def asin(attr_a):
    return _create_and_connect_node('asin', attr_a)


@noca_op
def cos(attr_a):
    return _create_and_connect_node('cos', attr_a)


@noca_op
def acos(attr_a):
    return _create_and_connect_node('acos', attr_a)


@noca_op
def tan(attr_a):
    return _create_and_connect_node('tan', attr_a)


@noca_op
def atan(attr_a):
    return _create_and_connect_node('atan', attr_a)


@noca_op
def atan2(attr_a, attr_b=1):
    return _create_and_connect_node('atan2', attr_a, attr_b)


# Twist.h
@noca_op
def twist_from_rotation(attr_a, axis=0, rotation_order=0):
    return _create_and_connect_node('twist_from_rotation', attr_a, axis, rotation_order)


@noca_op
def twist_from_matrix(matrix_a, axis=0, rotation_order=0):
    return _create_and_connect_node('twist_from_matrix', matrix_a, axis, rotation_order)


# VectorOps.h
@noca_op
def vector_length(vector_a):
    return _create_and_connect_node('vector_length', vector_a)


@noca_op
def vector_length_squared(vector_a):
    return _create_and_connect_node('vector_length_squared', vector_a)


@noca_op
def normalize_vector(vector_a):
    return _create_and_connect_node('normalize_vector', vector_a)


@noca_op
def dot_product(vector_a, vector_b=(1, 0, 0)):
    return _create_and_connect_node('dot_product', vector_a, vector_b)


@noca_op
def angle_between_vectors(vector_a, vector_b=(1, 0, 0)):
    return _create_and_connect_node('angle_between_vectors', vector_a, vector_b)


@noca_op
def cross_product(vector_a, vector_b=(1, 0, 0)):
    return _create_and_connect_node('cross_product', vector_a, vector_b)
