"""Additional Ops for NodeCalculator, based on Serguei Kalentchouk's math nodes.

Note:
    This NodeCalculator extension requires the built mayaMathNodes plugin
    (v1.3.0) from:
    https://github.com/serguei-k/maya-math-nodes

    This is a functioning example for what a possible NodeCalculator extension
    could look like, using proprietary/custom nodes.

:author: Mischa Kolbe <mischakolbe@gmail.com>
"""

from maya import cmds

from node_calculator.core import noca_op
from node_calculator.core import _create_operation_node, _unravel_item_as_list


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
    "add_float": {
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
            ["input[{array}]"],
        ],
        "outputs": [
            ["output"],
        ],
    },
    "average_int": {
        "node": "math_AverageInt",
        "inputs": [
            ["input[{array}]"],
        ],
        "outputs": [
            ["output"],
        ],
    },
    "average_angle": {
        "node": "math_AverageAngle",
        "inputs": [
            ["input[{array}]"],
        ],
        "outputs": [
            ["output"],
        ],
    },
    "average_rotation": {
        "node": "math_AverageRotation",
        "inputs": [
            [
                "input[{array}].inputX",
                "input[{array}].inputY",
                "input[{array}].inputZ",
            ],
        ],
        "outputs": [
            ["outputX", "outputY", "outputZ"],
        ],
    },
    "average_vector": {
        "node": "math_AverageVector",
        "inputs": [
            [
                "input[{array}].inputX",
                "input[{array}].inputY",
                "input[{array}].inputZ",
            ],
        ],
        "outputs": [
            ["outputX", "outputY", "outputZ"],
        ],
    },
    "average_matrix": {
        "node": "math_AverageMatrix",
        "inputs": [
            ["input[{array}]"],
        ],
        "outputs": [
            ["output"],
        ],
    },
    "average_quaternion": {
        "node": "math_AverageQuaternion",
        "inputs": [
            [
                "input[{array}].inputX",
                "input[{array}].inputY",
                "input[{array}].inputZ",
                "input[{array}].inputW",
            ],
        ],
        "outputs": [
            ["outputX", "outputY", "outputZ", "outputW"],
        ],
    },
    # Sum
    "sum": {
        "node": "math_Sum",
        "inputs": [
            ["input[{array}]"],
        ],
        "outputs": [
            ["output"],
        ],
    },
    "sum_int": {
        "node": "math_SumInt",
        "inputs": [
            ["input[{array}]"],
        ],
        "outputs": [
            ["output"],
        ],
    },
    "sum_angle": {
        "node": "math_SumAngle",
        "inputs": [
            ["input[{array}]"],
        ],
        "outputs": [
            ["output"],
        ],
    },
    "sum_vector": {
        "node": "math_SumVector",
        "inputs": [
            [
                "input[{array}].inputX",
                "input[{array}].inputY",
                "input[{array}].inputZ",
            ],
        ],
        "outputs": [
            ["outputX", "outputY", "outputZ"],
        ],
    },
    # Min/Max Element
    "min_element": {
        "node": "math_MinElement",
        "inputs": [
            ["input[{array}]"],
        ],
        "outputs": [
            ["output"],
        ],
    },
    "min_int_element": {
        "node": "math_MinIntElement",
        "inputs": [
            ["input[{array}]"],
        ],
        "outputs": [
            ["output"],
        ],
    },
    "min_angle_element": {
        "node": "math_MinAngleElement",
        "inputs": [
            ["input[{array}]"],
        ],
        "outputs": [
            ["output"],
        ],
    },
    "max_element": {
        "node": "math_MaxElement",
        "inputs": [
            ["input[{array}]"],
        ],
        "outputs": [
            ["output"],
        ],
    },
    "max_int_element": {
        "node": "math_MaxIntElement",
        "inputs": [
            ["input[{array}]"],
        ],
        "outputs": [
            ["output"],
        ],
    },
    "max_angle_element": {
        "node": "math_MaxAngleElement",
        "inputs": [
            ["input[{array}]"],
        ],
        "outputs": [
            ["output"],
        ],
    },
    # WeightedAverage
    "weighted_average": {
        "node": "math_WeightedAverage",
        "inputs": [
            ["input[{array}].value", "input[{array}].weight"],
        ],
        "outputs": [
            ["output"],
        ],
    },
    "weighted_average_int": {
        "node": "math_WeightedAverageInt",
        "inputs": [
            ["input[{array}].value", "input[{array}].weight"],
        ],
        "outputs": [
            ["output"],
        ],
    },
    "weighted_average_angle": {
        "node": "math_WeightedAverageAngle",
        "inputs": [
            ["input[{array}].value", "input[{array}].weight"],
        ],
        "outputs": [
            ["output"],
        ],
    },
    "weighted_average_rotation": {
        "node": "math_WeightedAverageRotation",
        "inputs": [
            [
                "input[{array}].value.valueX",
                "input[{array}].value.valueY",
                "input[{array}].value.valueZ",
                "input[{array}].weight",
            ],
        ],
        "outputs": [
            ["outputX", "outputY", "outputZ"],
        ],
    },
    "weighted_average_vector": {
        "node": "math_WeightedAverageVector",
        "inputs": [
            [
                "input[{array}].value.valueX",
                "input[{array}].value.valueY",
                "input[{array}].value.valueZ",
                "input[{array}].weight",
            ],
        ],
        "outputs": [
            ["outputX", "outputY", "outputZ"],
        ],
    },
    "weighted_average_matrix": {
        "node": "math_WeightedAverageMatrix",
        "inputs": [
            ["input[{array}].value", "input[{array}].weight"],
        ],
        "outputs": [
            ["output"],
        ],
    },
    "weighted_average_quaternion": {
        "node": "math_WeightedAverageQuaternion",
        "inputs": [
            [
                "input[{array}].value.valueX",
                "input[{array}].value.valueY",
                "input[{array}].value.valueZ",
                "input[{array}].value.valueW",
                "input[{array}].weight",
            ],
        ],
        "outputs": [
            ["outputX", "outputY", "outputZ", "outputW"],
        ],
    },
    # Normalize
    "normalize_array": {
        "node": "math_NormalizeArray",
        "inputs": [
            ["input[{array}]"],
        ],
        "outputs": [
            ["output[{array}]"],
        ],
    },
    "normalize_weights_array": {
        "node": "math_NormalizeWeightsArray",
        "inputs": [
            ["input[{array}]"],
        ],
        "outputs": [
            ["output[{array}]"],
        ],
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
    # Select Array
    "select_array": {
        "node": "math_SelectArray",
        "inputs": [
            ["input1[{array}]"],
            ["input2[{array}]"],
            ["condition"],
        ],
        "outputs": [
            ["output[{array}]"],
        ],
    },
    "select_int_array": {
        "node": "math_SelectIntArray",
        "inputs": [
            ["input1[{array}]"],
            ["input2[{array}]"],
            ["condition"],
        ],
        "outputs": [
            ["output[{array}]"],
        ],
    },
    "select_angle_array": {
        "node": "math_SelectAngleArray",
        "inputs": [
            ["input1[{array}]"],
            ["input2[{array}]"],
            ["condition"],
        ],
        "outputs": [
            ["output[{array}]"],
        ],
    },
    "select_vector_array": {
        "node": "math_SelectVectorArray",
        "inputs": [
            ["input1[{array}].input1X", "input1[{array}].input1Y", "input1[{array}].input1Z"],
            ["input2[{array}].input2X", "input2[{array}].input2Y", "input2[{array}].input2Z"],
            ["condition"],
        ],
        "outputs": [
            ["output[{array}].outputX", "output[{array}].outputY", "output[{array}].outputZ"],
        ],
    },
    "select_matrix_array": {
        "node": "math_SelectMatrixArray",
        "inputs": [
            ["input1[{array}]"],
            ["input2[{array}]"],
            ["condition"],
        ],
        "outputs": [
            ["output[{array}]"],
        ],
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
    "divide_angle": {
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
    "min_float": {
        "node": "math_Min",
        "inputs": [
            ["input1"],
            ["input2"],
        ],
        "outputs": [
            ["output"],
        ],
    },
    "max_float": {
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
    "round_float": {
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
    """Create math_Absolute-node to get absolute value of given attr.

    Args:
        attr_a (NcNode or NcAttrs or string): Maya node attribute.

    Returns:
        NcNode: Instance with node and output-attribute(s)
    """
    return _create_operation_node('absolute', attr_a)


@noca_op
def absolute_int(attr_a):
    """Create math_AbsoluteInt-node to get absolute value of given attr as int.

    Args:
        attr_a (NcNode or NcAttrs or string): Maya node attribute.

    Returns:
        NcNode: Instance with node and output-attribute(s)
    """
    return _create_operation_node('absolute_int', attr_a)


@noca_op
def absolute_angle(attr_a):
    """Create math_AbsoluteAngle-node to get absolute value of given angle attr.

    Args:
        attr_a (NcNode or NcAttrs or string): Maya node attribute.

    Returns:
        NcNode: Instance with node and output-attribute(s)
    """
    return _create_operation_node('absolute_angle', attr_a)


# Add.h
@noca_op
def add_float(attr_a, attr_b=0):
    """Create math_Add-node to add attributes together.

    Note:
        Called "add_float" instead of "add" to prevent naming collision with
        default NodeCalculator operator!

    Args:
        attr_a (NcNode or NcAttrs or string): Maya node attribute.
        attr_b (NcNode or NcAttrs or string): Maya node attribute.

    Returns:
        NcNode: Instance with node and output-attribute(s)
    """
    return _create_operation_node('add_float', attr_a, attr_b)


@noca_op
def add_int(attr_a, attr_b=0):
    """Create math_AddInt-node to add attributes together as integers.

    Args:
        attr_a (NcNode or NcAttrs or string): Maya node attribute.
        attr_b (NcNode or NcAttrs or string): Maya node attribute.

    Returns:
        NcNode: Instance with node and output-attribute(s)
    """
    return _create_operation_node('add_int', attr_a, attr_b)


@noca_op
def add_angle(attr_a, attr_b=0):
    """Create math_AddAngle-node to add angle attributes together.

    Args:
        attr_a (NcNode or NcAttrs or string): Maya node attribute.
        attr_b (NcNode or NcAttrs or string): Maya node attribute.

    Returns:
        NcNode: Instance with node and output-attribute(s)
    """
    return _create_operation_node('add_angle', attr_a, attr_b)


@noca_op
def add_vector(vector_a, vector_b=(0, 0, 0)):
    """Create math_AddVector-node to add vector attributes together.

    Args:
        vector_a (NcNode or NcAttrs or string): Maya node attribute.
        vector_b (NcNode or NcAttrs or string): Maya node attribute.

    Returns:
        NcNode: Instance with node and output-attribute(s)
    """
    return _create_operation_node('add_vector', vector_a, vector_b)


# Array.h
# Average
@noca_op
def average(*attrs):
    """Create math_Average-node to average all given attributes.

    Args:
        attrs (NcNode or NcAttrs or string): Any number of Maya node attrs.

    Returns:
        NcNode: Instance with node and output-attribute(s)
    """
    return _create_operation_node('average', attrs)


@noca_op
def average_int(*attrs):
    """Create math_AverageInt-node to average all given attributes as integers.

    Args:
        attrs (NcNode or NcAttrs or string): Any number of Maya node attrs.

    Returns:
        NcNode: Instance with node and output-attribute(s)
    """
    return _create_operation_node('average_int', attrs)


@noca_op
def average_angle(*attrs):
    """Create math_AverageAngle-node to average all given angle attributes.

    Args:
        attrs (NcNode or NcAttrs or string): Any number of Maya node attrs.

    Returns:
        NcNode: Instance with node and output-attribute(s)
    """
    return _create_operation_node('average_angle', attrs)


@noca_op
def average_rotation(*attrs):
    """Create math_AverageRotation-node to average all given rotation attrs.

    Args:
        attrs (NcNode or NcAttrs or string): Any number of Maya node attrs.

    Returns:
        NcNode: Instance with node and output-attribute(s)
    """
    return _create_operation_node('average_rotation', attrs)


@noca_op
def average_vector(*attrs):
    """Create math_AverageVector-node to average all given vector attributes.

    Args:
        attrs (NcNode or NcAttrs or string): Any number of Maya node attrs.

    Returns:
        NcNode: Instance with node and output-attribute(s)
    """
    return _create_operation_node('average_vector', attrs)


@noca_op
def average_matrix(*attrs):
    """Create math_AverageMatrix-node to average all given matrix attributes.

    Args:
        attrs (NcNode or NcAttrs or string): Any number of Maya node attrs.

    Returns:
        NcNode: Instance with node and output-attribute(s)
    """
    return _create_operation_node('average_matrix', attrs)


@noca_op
def average_quaternion(*attrs):
    """Create math_AverageQuaternion-node to average all given quaternion attrs.

    Args:
        attrs (NcNode or NcAttrs or string): Any number of Maya node attrs.

    Returns:
        NcNode: Instance with node and output-attribute(s)
    """
    return _create_operation_node('average_quaternion', attrs)


# Sum
@noca_op
def sum(*attrs):
    """Create math_Sum-node to sum up all given attributes.

    Args:
        attrs (NcNode or NcAttrs or string): Any number of Maya node attrs.

    Returns:
        NcNode: Instance with node and output-attribute(s)
    """
    return _create_operation_node('sum', attrs)


@noca_op
def sum_int(*attrs):
    """Create math_SumInt-node to sum up all given attributes as integers.

    Args:
        attrs (NcNode or NcAttrs or string): Any number of Maya node attrs.

    Returns:
        NcNode: Instance with node and output-attribute(s)
    """
    return _create_operation_node('sum_int', attrs)


@noca_op
def sum_angle(*attrs):
    """Create math_SumAngle-node to sum up all given angle attributes.

    Args:
        attrs (NcNode or NcAttrs or string): Any number of Maya node attrs.

    Returns:
        NcNode: Instance with node and output-attribute(s)
    """
    return _create_operation_node('sum_angle', attrs)


@noca_op
def sum_vector(*attrs):
    """Create math_SumVector-node to sum up all given vector attributes.

    Args:
        attrs (NcNode or NcAttrs or string): Any number of Maya node attrs.

    Returns:
        NcNode: Instance with node and output-attribute(s)
    """
    return _create_operation_node('sum_vector', attrs)


# Min/Max Element
@noca_op
def min_element(*attrs):
    """Create math_MinElement-node to find smallest of all given attributes.

    Args:
        attrs (NcNode or NcAttrs or string): Any number of Maya node attrs.

    Returns:
        NcNode: Instance with node and output-attribute(s)
    """
    return _create_operation_node('min_element', attrs)


@noca_op
def min_int_element(*attrs):
    """Create math_MinIntElement-node to find smallest of all given attrs as int.

    Args:
        attrs (NcNode or NcAttrs or string): Any number of Maya node attrs.

    Returns:
        NcNode: Instance with node and output-attribute(s)
    """
    return _create_operation_node('min_int_element', attrs)


@noca_op
def min_angle_element(*attrs):
    """Create math_MinAngleElement-node to find smallest of all given angle attrs.

    Args:
        attrs (NcNode or NcAttrs or string): Any number of Maya node attrs.

    Returns:
        NcNode: Instance with node and output-attribute(s)
    """
    return _create_operation_node('min_angle_element', attrs)


@noca_op
def max_element(*attrs):
    """Create math_MaxElement-node to find biggest of all given attributes.

    Args:
        attrs (NcNode or NcAttrs or string): Any number of Maya node attrs.

    Returns:
        NcNode: Instance with node and output-attribute(s)
    """
    return _create_operation_node('max_element', attrs)


@noca_op
def max_int_element(*attrs):
    """Create math_MaxIntElement-node to find biggest of all given attrs as int.

    Args:
        attrs (NcNode or NcAttrs or string): Any number of Maya node attrs.

    Returns:
        NcNode: Instance with node and output-attribute(s)
    """
    return _create_operation_node('max_int_element', attrs)


@noca_op
def max_angle_element(*attrs):
    """Create math_MaxAngleElement-node to find biggest of all given angle attrs.

    Args:
        attrs (NcNode or NcAttrs or string): Any number of Maya node attrs.

    Returns:
        NcNode: Instance with node and output-attribute(s)
    """
    return _create_operation_node('max_angle_element', attrs)


# WeightedAverage
@noca_op
def weighted_average(*attrs):
    """Create math_WeightedAverage-node to get weighted average of given attrs.

    Args:
        attrs (NcNode or NcAttrs or string): Any number of Maya node attrs.

    Returns:
        NcNode: Instance with node and output-attribute(s)
    """
    return _create_operation_node('weighted_average', attrs)


@noca_op
def weighted_average_int(*attrs):
    """Create math_WeightedAverageInt-node to get weighted average of given attrs as int.

    Args:
        attrs (NcNode or NcAttrs or string): Any number of Maya node attrs.

    Returns:
        NcNode: Instance with node and output-attribute(s)
    """
    return _create_operation_node('weighted_average_int', attrs)


@noca_op
def weighted_average_angle(*attrs):
    """Create math_WeightedAverageAngle-node to get weighted average of given angle attrs.

    Args:
        attrs (NcNode or NcAttrs or string): Any number of Maya node attrs.

    Returns:
        NcNode: Instance with node and output-attribute(s)
    """
    return _create_operation_node('weighted_average_angle', attrs)


@noca_op
def weighted_average_rotation(*attrs):
    """Create math_WeightedAverageRotation-node to get weighted average of given rotation attrs.

    Args:
        attrs (NcNode or NcAttrs or string): Any number of Maya node attrs.

    Returns:
        NcNode: Instance with node and output-attribute(s)
    """
    flattened_attrs = []
    for attr, weight in attrs:
        unravelled_items = _unravel_item_as_list(attr)
        unravelled_items.append(weight)
        if len(unravelled_items) != 4:
            cmds.error(
                "Expected list of [3D rotation, weight], got {0}".format(attrs)
            )
        flattened_attrs.append(unravelled_items)

    return _create_operation_node('weighted_average_rotation', flattened_attrs)


@noca_op
def weighted_average_vector(*attrs):
    """Create math_WeightedAverageVector-node to get weighted average of given vector attrs.

    Args:
        attrs (NcNode or NcAttrs or string): Any number of Maya node attrs.

    Returns:
        NcNode: Instance with node and output-attribute(s)
    """
    flattened_attrs = []
    for attr, weight in attrs:
        unravelled_items = _unravel_item_as_list(attr)
        unravelled_items.append(weight)
        if len(unravelled_items) != 4:
            cmds.error(
                "Expected list of [3D vector, weight], got {0}".format(attrs)
            )
        flattened_attrs.append(unravelled_items)

    return _create_operation_node('weighted_average_vector', flattened_attrs)


@noca_op
def weighted_average_matrix(*attrs):
    """Create math_WeightedAverageMatrix-node to get weighted average of given matrix attrs.

    Args:
        attrs (NcNode or NcAttrs or string): Any number of Maya node attrs.

    Returns:
        NcNode: Instance with node and output-attribute(s)
    """
    return _create_operation_node('weighted_average_matrix', attrs)


@noca_op
def weighted_average_quaternion(*attrs):
    """Create math_WeightedAverageQuaternion-node to get weighted average of given quaternion attrs.

    Args:
        attrs (NcNode or NcAttrs or string): Any number of Maya node attrs.

    Returns:
        NcNode: Instance with node and output-attribute(s)
    """
    flattened_attrs = []
    for attr, weight in attrs:
        unravelled_items = _unravel_item_as_list(attr)
        unravelled_items.append(weight)
        if len(unravelled_items) != 4:
            cmds.error(
                "Expected list of [4D quaternion, weight], got {0}".format(attrs)
            )
        flattened_attrs.append(unravelled_items)

    return _create_operation_node('weighted_average_quaternion', flattened_attrs)


# Normalize Array
@noca_op
def normalize_array(*attrs):
    """Create math_NormalizeArray-node to get normalized values of given attrs.

    Args:
        attrs (NcNode or NcAttrs or string): Any number of Maya node attrs.

    Returns:
        NcList: Instance with node and output-attribute(s)
    """
    return _create_operation_node('normalize_array', attrs)


@noca_op
def normalize_weights_array(*attrs):
    """Create math_NormalizeWeightsArray-node to get normalized values of given weights.

    Args:
        attrs (NcNode or NcAttrs or string): Any number of Maya node attrs.

    Returns:
        NcList: Instance with node and output-attribute(s)
    """
    return _create_operation_node('normalize_weights_array', attrs)


# Clamp.h
@noca_op
def clamp(attr_a, input_min=0, input_max=1):
    """Create math_Clamp-node to get clamped value of given attr.

    Args:
        attr_a (NcNode or NcAttrs or string): Maya node attribute.
        input_min (NcNode or NcAttrs or float): Min possible value.
        input_max (NcNode or NcAttrs or float): Max possible value.

    Returns:
        NcNode: Instance with node and output-attribute(s)
    """
    return _create_operation_node('clamp', attr_a, input_min, input_max)


@noca_op
def clamp_int(attr_a, input_min=0, input_max=1):
    """Create math_ClampInt-node to get clamped value of given attr as integer.

    Args:
        attr_a (NcNode or NcAttrs or string): Maya node attribute.
        input_min (NcNode or NcAttrs or float): Min possible value.
        input_max (NcNode or NcAttrs or float): Max possible value.

    Returns:
        NcNode: Instance with node and output-attribute(s)
    """
    return _create_operation_node('clamp_int', attr_a, input_min, input_max)


@noca_op
def clamp_angle(attr_a, input_min=0, input_max=360):
    """Create math_ClampAngle-node to get clamped value of given angle attr.

    Args:
        attr_a (NcNode or NcAttrs or string): Maya node attribute.
        input_min (NcNode or NcAttrs or float): Min possible angle.
        input_max (NcNode or NcAttrs or float): Max possible angle.

    Returns:
        NcNode: Instance with node and output-attribute(s)
    """
    return _create_operation_node('clamp_angle', attr_a, input_min, input_max)


# Condition.h
# Compare
@noca_op
def compare(attr_a, attr_b=0, operation=0):
    """Create math_Compare-node to get boolean of logical comparison between given attrs.

    Args:
        attr_a (NcNode or NcAttrs or string): Maya node attribute.
        attr_b (NcNode or NcAttrs or float): Maya node attribute.
        operation (NcNode or NcAttrs or int): Comparison operation: <, >, =, ...

    Returns:
        NcNode: Instance with node and output-attribute(s)
    """
    return _create_operation_node('compare', attr_a, attr_b, operation)


@noca_op
def compare_angle(attr_a, attr_b=0, operation=0):
    """Create math_CompareAngle-node to get boolean of logical comparison between given attrs.

    Args:
        attr_a (NcNode or NcAttrs or string): Maya node attribute.
        attr_b (NcNode or NcAttrs or float): Maya node attribute.
        operation (NcNode or NcAttrs or int): Comparison operation: <, >, =, ...

    Returns:
        NcNode: Instance with node and output-attribute(s)
    """
    return _create_operation_node('compare_angle', attr_a, attr_b, operation)


# Select
@noca_op
def select(attr_a, attr_b=0, condition=False):
    """Create math_Select-node to get one of the given attrs, depending on condition-state.

    Args:
        attr_a (NcNode or NcAttrs or string): Maya node attribute.
        attr_b (NcNode or NcAttrs or float): Maya node attribute.
        condition (NcNode or NcAttrs or bool): False > attr_a, True > attr_b

    Returns:
        NcNode: Instance with node and output-attribute(s)
    """
    return _create_operation_node('select', attr_a, attr_b, condition)


@noca_op
def select_int(attr_a, attr_b=0, condition=False):
    """Create math_SelectInt-node to get one of the given attrs, depending on condition-state.

    Args:
        attr_a (NcNode or NcAttrs or string): Maya node attribute.
        attr_b (NcNode or NcAttrs or float): Maya node attribute.
        condition (NcNode or NcAttrs or bool): False > attr_a, True > attr_b

    Returns:
        NcNode: Instance with node and output-attribute(s)
    """
    return _create_operation_node('select_int', attr_a, attr_b, condition)


@noca_op
def select_angle(attr_a, attr_b=0, condition=False):
    """Create math_SelectAngle-node to get one of the given attrs, depending on condition-state.

    Args:
        attr_a (NcNode or NcAttrs or string): Maya node attribute.
        attr_b (NcNode or NcAttrs or float): Maya node attribute.
        condition (NcNode or NcAttrs or bool): False > attr_a, True > attr_b

    Returns:
        NcNode: Instance with node and output-attribute(s)
    """
    return _create_operation_node('select_angle', attr_a, attr_b, condition)


@noca_op
def select_rotation(vector_a, vector_b=(0, 0, 0), condition=False):
    """Create math_SelectRotation-node to get one of the given attrs, depending on condition-state.

    Args:
        attr_a (NcNode or NcAttrs or string): Maya node attribute.
        attr_b (NcNode or NcAttrs or float): Maya node attribute.
        condition (NcNode or NcAttrs or bool): False > attr_a, True > attr_b

    Returns:
        NcNode: Instance with node and output-attribute(s)
    """
    return _create_operation_node('select_rotation', vector_a, vector_b, condition)


@noca_op
def select_vector(vector_a, vector_b=(0, 0, 0), condition=False):
    """Create math_SelectVector-node to get one of the given attrs, depending on condition-state.

    Args:
        attr_a (NcNode or NcAttrs or string): Maya node attribute.
        attr_b (NcNode or NcAttrs or float): Maya node attribute.
        condition (NcNode or NcAttrs or bool): False > attr_a, True > attr_b

    Returns:
        NcNode: Instance with node and output-attribute(s)
    """
    return _create_operation_node('select_vector', vector_a, vector_b, condition)


@noca_op
def select_matrix(matrix_a, matrix_b, condition=False):
    """Create math_SelectMatrix-node to get one of the given attrs, depending on condition-state.

    Args:
        attr_a (NcNode or NcAttrs or string): Maya node attribute.
        attr_b (NcNode or NcAttrs or float): Maya node attribute.
        condition (NcNode or NcAttrs or bool): False > attr_a, True > attr_b

    Returns:
        NcNode: Instance with node and output-attribute(s)
    """
    return _create_operation_node('select_matrix', matrix_a, matrix_b, condition)


@noca_op
def select_quaternion(attr_a, attr_b=(0, 0, 0, 1), condition=False):
    """Create math_SelectQuaternion-node to get one of the given attrs, depending on condition-state.

    Args:
        attr_a (NcNode or NcAttrs or string): Maya node attribute.
        attr_b (NcNode or NcAttrs or float): Maya node attribute.
        condition (NcNode or NcAttrs or bool): False > attr_a, True > attr_b

    Returns:
        NcNode: Instance with node and output-attribute(s)
    """
    return _create_operation_node('select_quaternion', attr_a, attr_b, condition)


# Select Array
@noca_op
def select_array(array_a, array_b, condition=False):
    """Create math_SelectArray-node to select array_a/array_b based on condition.

    Args:
        attr_a (list): Array of inputs (NcNode, NcAttrs, float).
        attr_b (list): Array of inputs (NcNode, NcAttrs, float).
        condition (NcNode or NcAttrs or bool): If set to False the node output
            is attr_a, if set to True the node output is attr_b.

    Returns:
        NcNode: Instance with node and output-attribute(s)
    """
    return _create_operation_node('select_array', array_a, array_b, condition)


@noca_op
def select_int_array(array_a, array_b, condition=False):
    """Create math_SelectIntArray-node to select array_a/array_b based on condition.

    Args:
        attr_a (list): Array of inputs (NcNode, NcAttrs, int).
        attr_b (list): Array of inputs (NcNode, NcAttrs, int).
        condition (NcNode or NcAttrs or bool): If set to False the node output
            is attr_a, if set to True the node output is attr_b.

    Returns:
        NcNode: Instance with node and output-attribute(s)
    """
    return _create_operation_node('select_int_array', array_a, array_b, condition)


@noca_op
def select_angle_array(array_a, array_b, condition=False):
    """Create math_SelectAngleArray-node to select array_a/array_b based on condition.

    Args:
        attr_a (list): Array of inputs (NcNode, NcAttrs, angle).
        attr_b (list): Array of inputs (NcNode, NcAttrs, angle).
        condition (NcNode or NcAttrs or bool): If set to False the node output
            is attr_a, if set to True the node output is attr_b.

    Returns:
        NcNode: Instance with node and output-attribute(s)
    """
    return _create_operation_node('select_angle_array', array_a, array_b, condition)


@noca_op
def select_vector_array(array_a, array_b, condition=False):
    """Create math_SelectVectorArray-node to select array_a/array_b based on condition.

    Args:
        attr_a (list): Array of inputs (NcNode, NcAttrs, list).
        attr_b (list): Array of inputs (NcNode, NcAttrs, list).
        condition (NcNode or NcAttrs or bool): If set to False the node output
            is attr_a, if set to True the node output is attr_b.

    Returns:
        NcNode: Instance with node and output-attribute(s)
    """
    return _create_operation_node('select_vector_array', array_a, array_b, condition)


@noca_op
def select_matrix_array(array_a, array_b, condition=False):
    """Create math_SelectMatrixArray-node to select array_a/array_b based on condition.

    Args:
        attr_a (list): Array of inputs (NcNode, NcAttrs, matrix).
        attr_b (list): Array of inputs (NcNode, NcAttrs, matrix).
        condition (NcNode or NcAttrs or bool): If set to False the node output
            is attr_a, if set to True the node output is attr_b.

    Returns:
        NcNode: Instance with node and output-attribute(s)
    """
    return _create_operation_node('select_matrix_array', array_a, array_b, condition)


# Logical
@noca_op
def and_bool(attr_a, attr_b=False):
    """Create math_AndBool-node to get logical AND operation between attrs.

    Args:
        attr_a (NcNode or NcAttrs or bool): Maya node attribute.
        attr_b (NcNode or NcAttrs or bool): Maya node attribute.

    Returns:
        NcNode: Instance with node and output-attribute(s)
    """
    return _create_operation_node('and_bool', attr_a, attr_b)


@noca_op
def or_bool(attr_a, attr_b=False):
    """Create math_OrBool-node to get logical OR operation between attrs.

    Args:
        attr_a (NcNode or NcAttrs or bool): Maya node attribute.
        attr_b (NcNode or NcAttrs or bool): Maya node attribute.

    Returns:
        NcNode: Instance with node and output-attribute(s)
    """
    return _create_operation_node('or_bool', attr_a, attr_b)


@noca_op
def xor_bool(attr_a, attr_b=False):
    """Create math_XorBool-node to get logical XOR operation between attrs.

    Args:
        attr_a (NcNode or NcAttrs or bool): Maya node attribute.
        attr_b (NcNode or NcAttrs or bool): Maya node attribute.

    Returns:
        NcNode: Instance with node and output-attribute(s)
    """
    return _create_operation_node('xor_bool', attr_a, attr_b)


@noca_op
def and_int(attr_a, attr_b=0):
    """Create math_AndInt-node to get logical AND operation between attrs.

    Args:
        attr_a (NcNode or NcAttrs or int): Maya node attribute.
        attr_b (NcNode or NcAttrs or int): Maya node attribute.

    Returns:
        NcNode: Instance with node and output-attribute(s)
    """
    return _create_operation_node('and_int', attr_a, attr_b)


@noca_op
def or_int(attr_a, attr_b=0):
    """Create math_OrInt-node to get logical OR operation between attrs.

    Args:
        attr_a (NcNode or NcAttrs or int): Maya node attribute.
        attr_b (NcNode or NcAttrs or int): Maya node attribute.

    Returns:
        NcNode: Instance with node and output-attribute(s)
    """
    return _create_operation_node('or_int', attr_a, attr_b)


@noca_op
def xor_int(attr_a, attr_b=0):
    """Create math_XorInt-node to get logical XOR operation between attrs.

    Args:
        attr_a (NcNode or NcAttrs or int): Maya node attribute.
        attr_b (NcNode or NcAttrs or int): Maya node attribute.

    Returns:
        NcNode: Instance with node and output-attribute(s)
    """
    return _create_operation_node('xor_int', attr_a, attr_b)


# Convert.h
@noca_op
def rotation_from_matrix(attr_a, rotation_order=0):
    """Create math_RotationFromMatrix-node to get rotation from given matrix.

    Args:
        attr_a (NcNode or NcAttrs or string): Maya node matrix attribute.
        rotation_order (NcNode or NcAttrs or int): Order of rotation.

    Returns:
        NcNode: Instance with node and output-attribute(s)
    """
    return _create_operation_node('rotation_from_matrix', attr_a, rotation_order)


@noca_op
def rotation_from_quaternion(attr_a, rotation_order=0):
    """Create math_RotationFromQuaternion-node to get rotation from given quaternion.

    Args:
        attr_a (NcNode or NcAttrs or string): Maya node attribute.
        rotation_order (NcNode or NcAttrs or int): Order of rotation.

    Returns:
        NcNode: Instance with node and output-attribute(s)
    """
    return _create_operation_node('rotation_from_quaternion', attr_a, rotation_order)


@noca_op
def quaternion_from_matrix(attr_a, rotation_order=0):
    """Create math_QuaternionFromMatrix-node to get quaternion from given matrix.

    Args:
        attr_a (NcNode or NcAttrs or string): Maya node matrix attribute.
        rotation_order (NcNode or NcAttrs or int): Order of rotation.

    Returns:
        NcNode: Instance with node and output-attribute(s)
    """
    return _create_operation_node('quaternion_from_matrix', attr_a, rotation_order)


@noca_op
def quaternion_from_rotation(attr_a, rotation_order=0):
    """Create math_QuaternionFromRotation-node to get quaternion from given rotation.

    Args:
        attr_a (NcNode or NcAttrs or string): Maya node attribute.
        rotation_order (NcNode or NcAttrs or int): Order of rotation.

    Returns:
        NcNode: Instance with node and output-attribute(s)
    """
    return _create_operation_node('quaternion_from_rotation', attr_a, rotation_order)


@noca_op
def translation_from_matrix(attr_a):
    """Create math_TranslationFromMatrix-node to get translation from given matrix.

    Args:
        attr_a (NcNode or NcAttrs or string): Maya node matrix attribute.

    Returns:
        NcNode: Instance with node and output-attribute(s)
    """
    return _create_operation_node('translation_from_matrix', attr_a)


@noca_op
def scale_from_matrix(attr_a):
    """Create math_ScaleFromMatrix-node to get scale from given matrix.

    Args:
        attr_a (NcNode or NcAttrs or string): Maya node matrix attribute.

    Returns:
        NcNode: Instance with node and output-attribute(s)
    """
    return _create_operation_node('scale_from_matrix', attr_a)


@noca_op
def matrix_from_trs(
        translation=(0, 0, 0),
        rotation=(0, 0, 0),
        scale=(1, 1, 1),
        rotation_order=0):
    """Create math_MatrixFromTRS-node to get matrix from given transforms.

    Args:
        translation (NcNode or NcAttrs or list): Maya node matrix attribute.
        rotation (NcNode or NcAttrs or list): Maya node matrix attribute.
        scale (NcNode or NcAttrs or list): Maya node matrix attribute.
        rotation_order (NcNode or NcAttrs or int): Order of rotation.

    Returns:
        NcNode: Instance with node and output-attribute(s)
    """
    created_node = _create_operation_node(
        'matrix_from_trs',
        translation,
        rotation,
        scale,
        rotation_order
    )
    return created_node


@noca_op
def axis_from_matrix(attr_a, axis=0):
    """Create math_AxisFromMatrix-node to get axis-vector from given matrix.

    Args:
        attr_a (NcNode or NcAttrs or string): Maya node matrix attribute.
        axis (NcNode or NcAttrs or int): Desired axis from resulting coordinate system.

    Returns:
        NcNode: Instance with node and output-attribute(s)
    """
    return _create_operation_node('axis_from_matrix', attr_a, axis)


# Distance.h
@noca_op
def distance_points(vector_a, vector_b=(0, 0, 0)):
    """Create math_DistancePoints-node to get distance between given points.

    Args:
        vector_a (NcNode or NcAttrs or list): Maya node attribute.
        vector_b (NcNode or NcAttrs or list): Maya node attribute.

    Returns:
        NcNode: Instance with node and output-attribute(s)
    """
    return _create_operation_node('distance_points', vector_a, vector_b)


@noca_op
def distance_transforms(matrix_a, matrix_b=None):
    """Create math_DistanceTransforms-node to get distance between given matrices.

    Args:
        matrix_a (NcNode or NcAttrs or str): Maya node matrix attribute.
        matrix_b (NcNode or NcAttrs or str): Maya node matrix attribute.

    Returns:
        NcNode: Instance with node and output-attribute(s)
    """
    if matrix_b is None:
        return _create_operation_node('distance_transforms', matrix_a)
    return _create_operation_node('distance_transforms', matrix_a, matrix_b)


# Divide.h
@noca_op
def divide(attr_a, attr_b=1):
    """Create math_Divide-node to get division result of given attrs.

    Args:
        attr_a (NcNode or NcAttrs or float): Maya node attribute.
        attr_b (NcNode or NcAttrs or float): Maya node attribute.

    Returns:
        NcNode: Instance with node and output-attribute(s)
    """
    return _create_operation_node('divide', attr_a, attr_b)


@noca_op
def divide_by_int(attr_a, attr_b=1):
    """Create math_DivideByInt-node to get division result of given attrs as int.

    Args:
        attr_a (NcNode or NcAttrs or float): Maya node attribute.
        attr_b (NcNode or NcAttrs or int): Maya node attribute.

    Returns:
        NcNode: Instance with node and output-attribute(s)
    """
    return _create_operation_node('divide_by_int', attr_a, attr_b)


@noca_op
def divide_angle(attr_a, attr_b=1):
    """Create math_DivideAngle-node to get division result of given angle attr.

    Args:
        attr_a (NcNode or NcAttrs or float): Maya node angle attribute.
        attr_b (NcNode or NcAttrs or float): Maya node attribute.

    Returns:
        NcNode: Instance with node and output-attribute(s)
    """
    return _create_operation_node('divide_angle', attr_a, attr_b)


@noca_op
def divide_angle_by_int(attr_a, attr_b=1):
    """Create math_DivideAngleByInt-node to get division result of given angle attrs as int.

    Args:
        attr_a (NcNode or NcAttrs or int): Maya node attribute.
        attr_b (NcNode or NcAttrs or int): Maya node attribute.

    Returns:
        NcNode: Instance with node and output-attribute(s)
    """
    return _create_operation_node('divide_angle_by_int', attr_a, attr_b)


@noca_op
def modulus_int(attr_a, attr_b=1):
    """Create math_ModulusInt-node to get modulus result of given int attrs.

    Args:
        attr_a (NcNode or NcAttrs or int): Maya node attribute.
        attr_b (NcNode or NcAttrs or int): Maya node attribute.

    Returns:
        NcNode: Instance with node and output-attribute(s)
    """
    return _create_operation_node('modulus_int', attr_a, attr_b)


# Interpolate.h
@noca_op
def lerp(attr_a, attr_b=0, alpha=0.5):
    """Create math_Lerp-node to linearly interpolate between given attrs.

    Args:
        attr_a (NcNode or NcAttrs or float): Maya node attribute.
        attr_b (NcNode or NcAttrs or float): Maya node attribute.
        alpha (NcNode or NcAttrs or float): Interpolation bias.

    Returns:
        NcNode: Instance with node and output-attribute(s)
    """
    return _create_operation_node('lerp', attr_a, attr_b, alpha)


@noca_op
def lerp_angle(attr_a, attr_b=0, alpha=0.5):
    """Create math_LerpAngle-node to linearly interpolate between given angles.

    Args:
        attr_a (NcNode or NcAttrs or float): Maya node attribute.
        attr_b (NcNode or NcAttrs or float): Maya node attribute.
        alpha (NcNode or NcAttrs or float): Interpolation bias.

    Returns:
        NcNode: Instance with node and output-attribute(s)
    """
    return _create_operation_node('lerp_angle', attr_a, attr_b, alpha)


@noca_op
def lerp_vector(vector_a, vector_b=(0, 0, 0), alpha=0.5):
    """Create math_LerpVector-node to linearly interpolate between given vector attrs.

    Args:
        attr_a (NcNode or NcAttrs or list): Maya node attribute.
        attr_b (NcNode or NcAttrs or list): Maya node attribute.
        alpha (NcNode or NcAttrs or float): Interpolation bias.

    Returns:
        NcNode: Instance with node and output-attribute(s)
    """
    return _create_operation_node('lerp_vector', vector_a, vector_b, alpha)


@noca_op
def lerp_matrix(matrix_a, matrix_b, alpha=0.5):
    """Create math_LerpMatrix-node to linearly interpolate between given matrix attrs.

    Args:
        attr_a (NcNode or NcAttrs or str): Maya node attribute.
        attr_b (NcNode or NcAttrs or str): Maya node attribute.
        alpha (NcNode or NcAttrs or float): Interpolation bias.

    Returns:
        NcNode: Instance with node and output-attribute(s)
    """
    return _create_operation_node('lerp_matrix', matrix_a, matrix_b, alpha)


@noca_op
def slerp_quaternion(attr_a, attr_b=(0, 0, 0, 0), alpha=0.5, interpolation_type=0):
    """Create math_SlerpQuaternion-node to linearly interpolate between given quaternion attrs.

    Args:
        attr_a (NcNode or NcAttrs or list): Maya node attribute.
        attr_b (NcNode or NcAttrs or list): Maya node attribute.
        alpha (NcNode or NcAttrs or float): Interpolation bias.
        interpolation_type (NcNode or NcAttrs or int): Short or long interpolation.

    Returns:
        NcNode: Instance with node and output-attribute(s)
    """
    return _create_operation_node('slerp_quaternion', attr_a, attr_b, alpha, interpolation_type)


# Inverse.h
@noca_op
def inverse_rotation(attr_a):
    """Create math_InverseRotation-node to get inverted rotation value of given attr.

    Args:
        attr_a (NcNode or NcAttrs or float): Maya node attribute.

    Returns:
        NcNode: Instance with node and output-attribute(s)
    """
    return _create_operation_node('inverse_rotation', attr_a)


@noca_op
def inverse_matrix(matrix_a):
    """Create math_InverseMatrix-node to get inverted matrix of given attr.

    Args:
        attr_a (NcNode or NcAttrs or string): Maya node attribute.

    Returns:
        NcNode: Instance with node and output-attribute(s)
    """
    return _create_operation_node('inverse_matrix', matrix_a)


@noca_op
def inverse_quaternion(attr_a):
    """Create math_InverseQuaternion-node to get inverted quaternion value of given attr.

    Args:
        attr_a (NcNode or NcAttrs or string): Maya node attribute.

    Returns:
        NcNode: Instance with node and output-attribute(s)
    """
    return _create_operation_node('inverse_quaternion', attr_a)


# MinMax.h
@noca_op
def min_float(attr_a, attr_b=1):
    """Create math_Min-node to get smaller of the two given attrs.

    Args:
        attr_a (NcNode or NcAttrs or float): Maya node attribute.
        attr_b (NcNode or NcAttrs or float): Maya node attribute.

    Returns:
        NcNode: Instance with node and output-attribute(s)
    """
    return _create_operation_node('min_float', attr_a, attr_b)


@noca_op
def max_float(attr_a, attr_b=0):
    """Create math_Max-node to get bigger of the two given attrs.

    Args:
        attr_a (NcNode or NcAttrs or float): Maya node attribute.
        attr_b (NcNode or NcAttrs or float): Maya node attribute.

    Returns:
        NcNode: Instance with node and output-attribute(s)
    """
    return _create_operation_node('max_float', attr_a, attr_b)


@noca_op
def min_int(attr_a, attr_b=1):
    """Create math_MinInt-node to get smaller of the two given int attrs.

    Args:
        attr_a (NcNode or NcAttrs or float): Maya node attribute.
        attr_b (NcNode or NcAttrs or float): Maya node attribute.

    Returns:
        NcNode: Instance with node and output-attribute(s)
    """
    return _create_operation_node('min_int', attr_a, attr_b)


@noca_op
def max_int(attr_a, attr_b=0):
    """Create math_MaxInt-node to get bigger of the two given int attrs.

    Args:
        attr_a (NcNode or NcAttrs or float): Maya node attribute.
        attr_b (NcNode or NcAttrs or float): Maya node attribute.

    Returns:
        NcNode: Instance with node and output-attribute(s)
    """
    return _create_operation_node('max_int', attr_a, attr_b)


@noca_op
def min_angle(attr_a, attr_b=360):
    """Create math_MinAngle-node to get smaller of the two given angle attrs.

    Args:
        attr_a (NcNode or NcAttrs or float): Maya node attribute.
        attr_b (NcNode or NcAttrs or float): Maya node attribute.

    Returns:
        NcNode: Instance with node and output-attribute(s)
    """
    return _create_operation_node('min_angle', attr_a, attr_b)


@noca_op
def max_angle(attr_a, attr_b=0):
    """Create math_MaxAngle-node to get bigger of the two given angle attrs.

    Args:
        attr_a (NcNode or NcAttrs or float): Maya node attribute.
        attr_b (NcNode or NcAttrs or float): Maya node attribute.

    Returns:
        NcNode: Instance with node and output-attribute(s)
    """
    return _create_operation_node('max_angle', attr_a, attr_b)


# Multiply.h
@noca_op
def multiply(attr_a, attr_b=1.0):
    """Create math_Multiply-node to get result of multiplying given attrs.

    Args:
        attr_a (NcNode or NcAttrs or string): Maya node attribute.
        attr_b (NcNode or NcAttrs or string): Maya node attribute.

    Returns:
        NcNode: Instance with node and output-attribute(s)
    """
    return _create_operation_node('multiply', attr_a, attr_b)


@noca_op
def multiply_by_int(attr_a, attr_b=1):
    """Create math_MultiplyByInt-node to get result of multiplying given attrs.

    Args:
        attr_a (NcNode or NcAttrs or string): Maya node attribute.
        attr_b (NcNode or NcAttrs or string): Maya node attribute.

    Returns:
        NcNode: Instance with node and output-attribute(s)
    """
    return _create_operation_node('multiply_by_int', attr_a, attr_b)


@noca_op
def multiply_int(attr_a, attr_b=1):
    """Create math_MultiplyInt-node to get result of multiplying given int attrs.

    Args:
        attr_a (NcNode or NcAttrs or string): Maya node attribute.
        attr_b (NcNode or NcAttrs or string): Maya node attribute.

    Returns:
        NcNode: Instance with node and output-attribute(s)
    """
    return _create_operation_node('multiply_int', attr_a, attr_b)


@noca_op
def multiply_angle(attr_a, attr_b=1):
    """Create math_MultiplyAngle-node to get result of multiplying given angle attrs.

    Args:
        attr_a (NcNode or NcAttrs or string): Maya node attribute.
        attr_b (NcNode or NcAttrs or string): Maya node attribute.

    Returns:
        NcNode: Instance with node and output-attribute(s)
    """
    return _create_operation_node('multiply_angle', attr_a, attr_b)


@noca_op
def multiply_angle_by_int(attr_a, attr_b=1):
    """Create math_MultiplyAngleByInt-node to get result of multiplying given attrs.

    Args:
        attr_a (NcNode or NcAttrs or string): Maya node attribute.
        attr_b (NcNode or NcAttrs or string): Maya node attribute.

    Returns:
        NcNode: Instance with node and output-attribute(s)
    """
    return _create_operation_node('multiply_angle_by_int', attr_a, attr_b)


@noca_op
def multiply_rotation(attr_a, attr_b=1):
    """Create math_MultiplyRotation-node to get result of multiplying given rotation attr.

    Args:
        attr_a (NcNode or NcAttrs or string): Maya node attribute.
        attr_b (NcNode or NcAttrs or string): Maya node attribute.

    Returns:
        NcNode: Instance with node and output-attribute(s)
    """
    return _create_operation_node('multiply_rotation', attr_a, attr_b)


@noca_op
def multiply_vector(attr_a, attr_b=1):
    """Create math_MultiplyVector-node to get result of multiplying given vector attr.

    Args:
        attr_a (NcNode or NcAttrs or string): Maya node attribute.
        attr_b (NcNode or NcAttrs or string): Maya node attribute.

    Returns:
        NcNode: Instance with node and output-attribute(s)
    """
    return _create_operation_node('multiply_vector', attr_a, attr_b)


@noca_op
def multiply_vector_by_matrix(attr_a, attr_b=None):
    """Create math_MultiplyVectorByMatrix-node to get result of multiplying given attrs.

    Args:
        attr_a (NcNode or NcAttrs or list): Maya node vector attribute.
        attr_b (NcNode or NcAttrs or string): Maya node matrix attribute.

    Returns:
        NcNode: Instance with node and output-attribute(s)
    """
    if attr_b is None:
        return _create_operation_node('multiply_vector_by_matrix', attr_a)
    return _create_operation_node('multiply_vector_by_matrix', attr_a, attr_b)


@noca_op
def multiply_matrix(matrix_a, matrix_b=None):
    """Create math_MultiplyMatrix-node to get result of multiplying given matrix attrs.

    Args:
        attr_a (NcNode or NcAttrs or string): Maya node matrix attribute.
        attr_b (NcNode or NcAttrs or string): Maya node matrix attribute.

    Returns:
        NcNode: Instance with node and output-attribute(s)
    """
    if matrix_b is None:
        return _create_operation_node('multiply_matrix', matrix_a)
    return _create_operation_node('multiply_matrix', matrix_a, matrix_b)


@noca_op
def multiply_quaternion(attr_a, attr_b=(0, 0, 0, 1)):
    """Create math_MultiplyQuaternion-node to get result of multiplying given quaternion attrs.

    Args:
        attr_a (NcNode or NcAttrs or list): Maya node quaternion attribute.
        attr_b (NcNode or NcAttrs or list): Maya node quaternion attribute.

    Returns:
        NcNode: Instance with node and output-attribute(s)
    """
    return _create_operation_node('multiply_quaternion', attr_a, attr_b)


# Negate.h
@noca_op
def negate(attr_a):
    """Create math_Negate-node to get result of multiplying given attr by -1.

    Args:
        attr_a (NcNode or NcAttrs or string): Maya node attribute.

    Returns:
        NcNode: Instance with node and output-attribute(s)
    """
    return _create_operation_node('negate', attr_a)


@noca_op
def negate_int(attr_a):
    """Create math_NegateInt-node to get result of multiplying given int attr by -1.

    Args:
        attr_a (NcNode or NcAttrs or string): Maya node attribute.

    Returns:
        NcNode: Instance with node and output-attribute(s)
    """
    return _create_operation_node('negate_int', attr_a)


@noca_op
def negate_angle(attr_a):
    """Create math_NegateAngle-node to get result of multiplying given angle attr by -1.

    Args:
        attr_a (NcNode or NcAttrs or string): Maya node attribute.

    Returns:
        NcNode: Instance with node and output-attribute(s)
    """
    return _create_operation_node('negate_angle', attr_a)


@noca_op
def negate_vector(attr_a):
    """Create math_NegateVector-node to get result of multiplying given vector attr by -1.

    Args:
        attr_a (NcNode or NcAttrs or string): Maya node attribute.

    Returns:
        NcNode: Instance with node and output-attribute(s)
    """
    return _create_operation_node('negate_vector', attr_a)


# Power.h
@noca_op
def power(attr_a, exponent=2):
    """Create math_Power-node to get result of raising given attr to a power.

    Args:
        attr_a (NcNode or NcAttrs or string): Maya node attribute.
        exponent (NcNode or NcAttrs or float): Exponent of power-calculation.

    Returns:
        NcNode: Instance with node and output-attribute(s)
    """
    return _create_operation_node('power', attr_a, exponent)


@noca_op
def square_root(attr_a):
    """Create math_SquareRoot-node to get square root of given attr.

    Args:
        attr_a (NcNode or NcAttrs or string): Maya node attribute.

    Returns:
        NcNode: Instance with node and output-attribute(s)
    """
    return _create_operation_node('square_root', attr_a)


# Round.h
@noca_op
def ceil(attr_a):
    """Create math_Ceil-node to get rounded up value of given attr.

    Args:
        attr_a (NcNode or NcAttrs or string): Maya node attribute.

    Returns:
        NcNode: Instance with node and output-attribute(s)
    """
    return _create_operation_node('ceil', attr_a)


@noca_op
def ceil_angle(attr_a):
    """Create math_CeilAngle-node to get rounded up value of given angle attr.

    Args:
        attr_a (NcNode or NcAttrs or string): Maya node attribute.

    Returns:
        NcNode: Instance with node and output-attribute(s)
    """
    return _create_operation_node('ceil_angle', attr_a)


@noca_op
def floor(attr_a):
    """Create math_Floor-node to get rounded down value of given attr.

    Args:
        attr_a (NcNode or NcAttrs or string): Maya node attribute.

    Returns:
        NcNode: Instance with node and output-attribute(s)
    """
    return _create_operation_node('floor', attr_a)


@noca_op
def floor_angle(attr_a):
    """Create math_FloorAngle-node to get rounded down value of given angle attr.

    Args:
        attr_a (NcNode or NcAttrs or string): Maya node attribute.

    Returns:
        NcNode: Instance with node and output-attribute(s)
    """
    return _create_operation_node('floor_angle', attr_a)


@noca_op
def round_float(attr_a):
    """Create math_Round-node to get rounded (up or down) value of given attr.

    Args:
        attr_a (NcNode or NcAttrs or string): Maya node attribute.

    Returns:
        NcNode: Instance with node and output-attribute(s)
    """
    return _create_operation_node('round_float', attr_a)


@noca_op
def round_angle(attr_a):
    """Create math_RoundAngle-node to get rounded (up or down) value of given angle attr.

    Args:
        attr_a (NcNode or NcAttrs or string): Maya node attribute.

    Returns:
        NcNode: Instance with node and output-attribute(s)
    """
    return _create_operation_node('round_angle', attr_a)


# Subtract.h
@noca_op
def subtract(attr_a, attr_b=0):
    """Create math_Subtract-node to subtract given attrs.

    Args:
        attr_a (NcNode or NcAttrs or string): Maya node attribute.
        attr_b (NcNode or NcAttrs or string): Maya node attribute.

    Returns:
        NcNode: Instance with node and output-attribute(s)
    """
    return _create_operation_node('subtract', attr_a, attr_b)


@noca_op
def subtract_int(attr_a, attr_b=0):
    """Create math_SubtractInt-node to subtract given int attrs.

    Args:
        attr_a (NcNode or NcAttrs or int): Maya node attribute.
        attr_b (NcNode or NcAttrs or int): Maya node attribute.

    Returns:
        NcNode: Instance with node and output-attribute(s)
    """
    return _create_operation_node('subtract_int', attr_a, attr_b)


@noca_op
def subtract_angle(attr_a, attr_b=0):
    """Create math_SubtractAngle-node to subtract given angle attrs.

    Args:
        attr_a (NcNode or NcAttrs or float): Maya node attribute.
        attr_b (NcNode or NcAttrs or float): Maya node attribute.

    Returns:
        NcNode: Instance with node and output-attribute(s)
    """
    return _create_operation_node('subtract_angle', attr_a, attr_b)


@noca_op
def subtract_vector(attr_a, attr_b=(0, 0, 0)):
    """Create math_SubtractVector-node to subtract given vector attrs.

    Args:
        attr_a (NcNode or NcAttrs or list): Maya node attribute.
        attr_b (NcNode or NcAttrs or list): Maya node attribute.

    Returns:
        NcNode: Instance with node and output-attribute(s)
    """
    return _create_operation_node('subtract_vector', attr_a, attr_b)


# Trig.h
@noca_op
def sin(attr_a):
    """Create math_Sin-node to get sinus of given attr.

    Args:
        attr_a (NcNode or NcAttrs or string): Maya node attribute.

    Returns:
        NcNode: Instance with node and output-attribute(s)
    """
    return _create_operation_node('sin', attr_a)


@noca_op
def asin(attr_a):
    """Create math_Asin-node to get arcus sinus of given attr.

    Args:
        attr_a (NcNode or NcAttrs or string): Maya node attribute.

    Returns:
        NcNode: Instance with node and output-attribute(s)
    """
    return _create_operation_node('asin', attr_a)


@noca_op
def cos(attr_a):
    """Create math_Cos-node to get cosinus of given attr.

    Args:
        attr_a (NcNode or NcAttrs or string): Maya node attribute.

    Returns:
        NcNode: Instance with node and output-attribute(s)
    """
    return _create_operation_node('cos', attr_a)


@noca_op
def acos(attr_a):
    """Create math_Acos-node to get arcus cosinus of given attr.

    Args:
        attr_a (NcNode or NcAttrs or string): Maya node attribute.

    Returns:
        NcNode: Instance with node and output-attribute(s)
    """
    return _create_operation_node('acos', attr_a)


@noca_op
def tan(attr_a):
    """Create math_Tan-node to get tangens of given attr.

    Args:
        attr_a (NcNode or NcAttrs or string): Maya node attribute.

    Returns:
        NcNode: Instance with node and output-attribute(s)
    """
    return _create_operation_node('tan', attr_a)


@noca_op
def atan(attr_a):
    """Create math_Atan-node to get arcus tangens of given attr.

    Args:
        attr_a (NcNode or NcAttrs or string): Maya node attribute.

    Returns:
        NcNode: Instance with node and output-attribute(s)
    """
    return _create_operation_node('atan', attr_a)


@noca_op
def atan2(attr_a, attr_b=1):
    """Create math_Atan2-node to get arcus tangens 2 of given attr.

    Args:
        attr_a (NcNode or NcAttrs or string): Maya node attribute.
        attr_b (NcNode or NcAttrs or string): Maya node attribute.

    Returns:
        NcNode: Instance with node and output-attribute(s)
    """
    return _create_operation_node('atan2', attr_a, attr_b)


# Twist.h
@noca_op
def twist_from_rotation(attr_a, axis=0, rotation_order=0):
    """Create math_TwistFromRotation-node to get twist from given rotation attr.

    Args:
        attr_a (NcNode or NcAttrs or string): Maya node attribute.
        axis (NcNode or NcAttrs or int): Axis to consider for twist-extraction.
        rotation_order (NcNode or NcAttrs or int): Order of rotation.

    Returns:
        NcNode: Instance with node and output-attribute(s)
    """
    return _create_operation_node('twist_from_rotation', attr_a, axis, rotation_order)


@noca_op
def twist_from_matrix(matrix_a, axis=0, rotation_order=0):
    """Create math_TwistFromMatrix-node to get twist from given matrix attr.

    Args:
        matrix_a (NcNode or NcAttrs or string): Maya node matrix attribute.
        axis (NcNode or NcAttrs or int): Axis to consider for twist-extraction.
        rotation_order (NcNode or NcAttrs or int): Order of rotation.

    Returns:
        NcNode: Instance with node and output-attribute(s)
    """
    return _create_operation_node('twist_from_matrix', matrix_a, axis, rotation_order)


# VectorOps.h
@noca_op
def vector_length(vector_a):
    """Create math_VectorLength-node to get length of given vector attr.

    Args:
        vector_a (NcNode or NcAttrs or string): Maya node attribute.

    Returns:
        NcNode: Instance with node and output-attribute(s)
    """
    return _create_operation_node('vector_length', vector_a)


@noca_op
def vector_length_squared(vector_a):
    """Create math_VectorLengthSquared-node to get sum of squares of all vector components.

    Args:
        vector_a (NcNode or NcAttrs or string): Maya node attribute.

    Returns:
        NcNode: Instance with node and output-attribute(s)
    """
    return _create_operation_node('vector_length_squared', vector_a)


@noca_op
def normalize_vector(vector_a):
    """Create math_NormalizeVector-node to get normalized vector attr.

    Args:
        vector_a (NcNode or NcAttrs or string): Maya node attribute.

    Returns:
        NcNode: Instance with node and output-attribute(s)
    """
    return _create_operation_node('normalize_vector', vector_a)


@noca_op
def dot_product(vector_a, vector_b=(1, 0, 0)):
    """Create math_DotProduct-node to get dot product between given vector attrs.

    Args:
        vector_a (NcNode or NcAttrs or string): Maya node attribute.
        vector_b (NcNode or NcAttrs or string): Maya node attribute.

    Returns:
        NcNode: Instance with node and output-attribute(s)
    """
    return _create_operation_node('dot_product', vector_a, vector_b)


@noca_op
def angle_between_vectors(vector_a, vector_b=(1, 0, 0)):
    """Create math_AngleBetweenVectors-node to get vector between given vector attrs.

    Args:
        vector_a (NcNode or NcAttrs or string): Maya node attribute.
        vector_b (NcNode or NcAttrs or string): Maya node attribute.

    Returns:
        NcNode: Instance with node and output-attribute(s)
    """
    return _create_operation_node('angle_between_vectors', vector_a, vector_b)


@noca_op
def cross_product(vector_a, vector_b=(1, 0, 0)):
    """Create math_CrossProduct-node to get cross product between given vector attrs.

    Args:
        vector_a (NcNode or NcAttrs or string): Maya node attribute.
        vector_b (NcNode or NcAttrs or string): Maya node attribute.

    Returns:
        NcNode: Instance with node and output-attribute(s)
    """
    return _create_operation_node('cross_product', vector_a, vector_b)
