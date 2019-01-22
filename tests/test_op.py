"""
Unit tests for noca.Op
"""

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# IMPORTS
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Python imports

# Third party imports
from maya import cmds

# Local imports
from base import BaseTestCase
import node_calculator.core as noca
from node_calculator import om_util


# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# GLOBALS
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~


IRREGULAR_OPERATORS = [
]


TEST_DATA_ASSOCIATION = {
    "add": {
        "input_plugs": ['tf_out_a.translate', 'tf_out_b.translate'],
        "output_plugs": ['tf_in_a.translate'],
    },
    "angle_between": {
        "input_plugs": ['tf_out_a.translate', 'tf_out_b.translate'],
        "output_plugs": ['tf_in_a.translateX'],
    },
    "average": {
        "input_plugs": ['tf_out_a.translate', 'tf_out_a.rotate', 'tf_out_b.translate', 'tf_out_b.rotate'],
        "output_plugs": ['tf_in_a.translate'],
    },
    "blend": {
        "input_plugs": ['tf_out_a.translate', 'tf_out_b.translate'],
        "output_plugs": ['tf_in_a.translate'],
    },
    "choice": {
        "input_plugs": [['tf_out_a.translateX', 'tf_out_b.translateX'], 'tf_out_b.translateY'],
        "output_plugs": ['tf_in_a.translateX'],
    },
    "clamp": {
        "input_plugs": ['tf_out_a.translate', 'tf_out_b.translate'],
        "output_plugs": ['tf_in_a.translate'],
    },
    "closest_point_on_mesh": {
        "input_plugs": ['mesh_shape_out_a.outMesh', 'tf_out_a.translate'],
        "output_plugs": ['tf_in_a.translate'],
    },
    "closest_point_on_surface": {
        "input_plugs": ['surface_shape_out_a.local', 'tf_out_a.translate'],
        "output_plugs": ['tf_in_a.translate'],
    },
    "compose_matrix": {
        "input_plugs": ['tf_out_a.translate', 'tf_out_a.rotate', 'tf_out_a.scale', 'tf_out_a.translate'],
        "output_plugs": ['mat_in_a.inMatrix'],
    },
    "cross": {
        "input_plugs": ['tf_out_a.translate', 'tf_out_b.translate'],
        "output_plugs": ['tf_in_a.translate'],
    },
    "curve_info": {
        "input_plugs": ['curve_out_a.local'],
        "output_plugs": ['tf_in_a.translateX'],
    },
    "decompose_matrix": {
        "input_plugs": ['mat_out_a.outMatrix'],
        "output_plugs": ['tf_in_a.translate', 'tf_in_a.rotate', 'tf_in_a.scale', 'tf_in_b.translate'],
    },
    "div": {
        "input_plugs": ['tf_out_a.translate', 'tf_out_b.translate'],
        "output_plugs": ['tf_in_a.translate'],
    },
    "dot": {
        "input_plugs": ['tf_out_a.translate', 'tf_out_b.translate'],
        "output_plugs": ['tf_in_a.translateX'],
    },
    "euler_to_quat": {
        "input_plugs": ['tf_out_a.rotate'],
        "output_plugs": ['quat_in_a.inputQuat'],
    },
    "four_by_four_matrix": {
        "input_plugs": ['tf_out_a.translateX'],
        "output_plugs": ['mat_in_a.inMatrix'],
    },
    "hold_matrix": {
        "input_plugs": ['mat_out_a.outMatrix'],
        "output_plugs": ['mat_in_a.inMatrix'],
    },
    "inverse_matrix": {
        "input_plugs": ['mat_out_a.outMatrix'],
        "output_plugs": ['mat_in_a.inMatrix'],
    },
    "length": {
        "input_plugs": ['tf_out_a.translate', 'tf_out_b.translate'],
        "output_plugs": ['tf_in_a.translateX'],
    },
    "matrix_distance": {
        "input_plugs": ['mat_out_a.outMatrix', 'mat_out_b.outMatrix'],
        "output_plugs": ['tf_in_a.translateX'],
    },
    "mul": {
        "input_plugs": ['tf_out_a.translate', 'tf_out_b.translate'],
        "output_plugs": ['tf_in_a.translate'],
    },
    "mult_matrix": {
        "input_plugs": ['mat_out_a.outMatrix', 'mat_out_b.outMatrix'],
        "output_plugs": ['mat_in_a.inMatrix'],
    },
    "nearest_point_on_curve": {
        "input_plugs": ['curve_shape_out_a.local', 'tf_out_a.translate'],
        "output_plugs": ['tf_in_a.translate'],
    },
    "normalize_vector": {
        "input_plugs": ['tf_out_a.translate'],
        "output_plugs": ['tf_in_a.translate'],
    },
    "pair_blend": {
        "input_plugs": ['tf_out_a.translate', 'tf_out_a.rotate', 'tf_out_b.translate', 'tf_out_b.rotate'],
        "output_plugs": ['tf_in_a.translate', 'tf_in_a.rotate'],
    },
    "pass_matrix": {
        "input_plugs": ['mat_out_a.outMatrix'],
        "output_plugs": ['mat_in_a.inMatrix'],
    },
    "point_matrix_mult": {
        "input_plugs": ['tf_out_a.translate', 'mat_out_a.outMatrix'],
        "output_plugs": ['tf_in_a.translate'],
    },
    "point_on_curve_info": {
        "input_plugs": ['curve_shape_out_a.local', 'tf_out_a.translateX'],
        "output_plugs": ['tf_in_a.translate'],
    },
    "point_on_surface_info": {
        "input_plugs": ['surface_shape_out_a.local', 'tf_out_a.translateX'],
        "output_plugs": ['tf_in_a.translate'],
    },
    "pow": {
        "input_plugs": ['tf_out_a.translate', 'tf_out_b.translate'],
        "output_plugs": ['tf_in_a.translate'],
    },
    "quat_add": {
        "input_plugs": ['quat_out_a.outputQuat', 'quat_out_b.outputQuat'],
        "output_plugs": ['quat_in_a.inputQuat'],
    },
    "quat_conjugate": {
        "input_plugs": ['quat_out_a.outputQuat'],
        "output_plugs": ['quat_in_a.inputQuat'],
    },
    "quat_invert": {
        "input_plugs": ['quat_out_a.outputQuat'],
        "output_plugs": ['quat_in_a.inputQuat'],
    },
    "quat_mul": {
        "input_plugs": ['quat_out_a.outputQuat', 'quat_out_b.outputQuat'],
        "output_plugs": ['quat_in_a.inputQuat'],
    },
    "quat_negate": {
        "input_plugs": ['quat_out_a.outputQuat'],
        "output_plugs": ['quat_in_a.inputQuat'],
    },
    "quat_normalize": {
        "input_plugs": ['quat_out_a.outputQuat'],
        "output_plugs": ['quat_in_a.inputQuat'],
    },
    "quat_sub": {
        "input_plugs": ['quat_out_a.outputQuat', 'quat_out_b.outputQuat'],
        "output_plugs": ['quat_in_a.inputQuat'],
    },
    "quat_to_euler": {
        "input_plugs": ['quat_out_a.outputQuat'],
        "output_plugs": ['tf_in_a.rotate'],
    },
    "remap_color": {
        "input_plugs": ['tf_out_a.translate'],
        "output_plugs": ['tf_in_a.translate'],
    },
    "remap_hsv": {
        "input_plugs": ['tf_out_a.translate'],
        "output_plugs": ['tf_in_a.translate'],
    },
    "remap_value": {
        "input_plugs": ['tf_out_a.translateX'],
        "output_plugs": ['tf_in_a.translateX'],
    },
    "reverse": {
        "input_plugs": ['tf_out_a.translate'],
        "output_plugs": ['tf_in_a.translate'],
    },
    "rgb_to_hsv": {
        "input_plugs": ['tf_out_a.translate'],
        "output_plugs": ['tf_in_a.translate'],
    },
    "set_range": {
        "input_plugs": ['tf_out_a.translate', 'tf_out_b.translate'],
        "output_plugs": ['tf_in_a.translate'],
    },
    "sub": {
        "input_plugs": ['tf_out_a.translate', 'tf_out_b.translate'],
        "output_plugs": ['tf_in_a.translate'],
    },
    "sum": {
        "input_plugs": ['tf_out_a.translate', 'tf_out_a.rotate', 'tf_out_b.translate', 'tf_out_b.rotate'],
        "output_plugs": ['tf_in_a.translate'],
    },
    "transpose_matrix": {
        "input_plugs": ['mat_out_a.outMatrix'],
        "output_plugs": ['mat_in_a.inMatrix'],
    },
    "weighted_add_matrix": {
        "input_plugs": ['mat_out_a.outMatrix', 'mat_out_b.outMatrix'],
        "output_plugs": ['mat_in_a.inMatrix'],
        "seek_input_parent": False,
    },
}


# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# HELPER FUNCTIONS
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~


def expand_array_attributes(node_inputs, input_plugs):
    """Expand a nodes inputs for array-inputs.

    Args:
        node_inputs (list): Node input-plugs specified in the OPERATORS-dict.
        input_plugs (list): The plugs that will be connected to the node.

    Returns:
        list: Adjusted node_inputs, where {array} plugs are correctly expanded.

    Example:
        ::

            node_inputs = [["matrixIn[{array}]"]]
            input_plugs = ["bogusMatrixA", "bogusMatrixB", "bogusMatrixC"]

            expand_array_attributes(node_inputs, input_plugs)
            >>> [['matrixIn[0]'], ['matrixIn[1]'], ['matrixIn[2]']]
    """
    adjusted_inputs = []
    for _input in node_inputs:
        if any(["{array}" in element for element in _input]):
            for index in range(len(input_plugs)):
                indexed_input = [element.format(array=index) for element in _input]
                adjusted_inputs.append(indexed_input)
        else:
            adjusted_inputs.append(_input)

    return adjusted_inputs


def convert_literal_to_object(class_instance, literal):
    """Get the actual class objects from the given string-literals.

    Args:
        class_instance (class): Class in which the objects should be found.
        literal (str or list or tuple): Name of the class object or a list of
            such objects.

    Returns:
        list or object: If literal is a list, then a list of objects will be
            returned. If literal was a string corresponding to an object, only
            the object will be returned.

    Example:
        ::

            objects = convert_literal_to_object(
                self,
                [["tf_in_a.tx", "tf_in_b.tx"], "tf_in_b.ty"]
            )
            >>> [[self.tf_in_a.tx, self.tf_in_b.tx], self.tf_in_b.ty]
    """
    input_plugs = []
    if isinstance(literal, (list, tuple)):
        for literal_element in literal:
            literal_element_as_object = convert_literal_to_object(class_instance, literal_element)
            input_plugs.append(literal_element_as_object)

    else:
        input_plugs = class_instance
        for literal_part in literal.split("."):
            input_plugs = getattr(input_plugs, literal_part)

    return input_plugs


def flatten(in_list):
    """Flatten a given list recursively.

    Args:
        in_list (list or tuple): Can contain scalars, lists or lists of lists.

    Returns:
        list: List of depth 1; no inner lists, only strings, ints, floats, etc.

    Example:
        ::

            flatten([1, [2, [3], 4, 5], 6])
            >>> [1, 2, 3, 4, 5, 6]
    """
    flattened_list = []
    for item in in_list:
        if isinstance(item, (list, tuple)):
            flattened_list.extend(flatten(item))
        else:
            flattened_list.append(item)
    return flattened_list


# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# TESTS
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
def _test_condition_op(operator):
    """Basic tests for condition operators

    Args:
        operator (string): Boolean operator: >, <, =, >=, <=

    Returns:
        object: Test function for the given operator
    """

    def test(self):
        node_data = noca.OPERATORS[operator]
        condition_value = 1.1
        false_value = 2

        # Run noca operation
        bool_operator_func = getattr(noca.NcBaseClass, "__{}__".format(operator))
        condition_node = bool_operator_func(self.tf_out_a.translateX, condition_value)
        result = noca.Op.condition(condition_node, self.tf_out_b.translateX, false_value)
        self.tf_in_a.t = result

        # Assertions
        self.assertEqual(cmds.nodeType(result.node), node_data.get("node", None))

        self.assertEqual(result.operation.get(), node_data.get("operation", None))

        self.assertEqual(
            cmds.listConnections(result.firstTerm.plugs[0], plugs=True),
            self.tf_out_a.translateX.plugs
        )
        self.assertAlmostEqual(result.secondTerm.get(), condition_value, places=7)

        self.assertEqual(result.colorIfFalseR.get(), false_value)
        self.assertEqual(
            cmds.listConnections(result.colorIfTrueR.plugs[0], plugs=True),
            self.tf_out_b.translateX.plugs
        )

        self.assertEqual(
            sorted(cmds.listConnections(result.outColorR.plugs[0], plugs=True)),
            [self.tf_in_a.translateX.plugs[0], self.tf_in_a.translateY.plugs[0], self.tf_in_a.translateZ.plugs[0]]
        )

    return test


def _test_regular_op(operator):
    """Basic tests whether an operator performs correctly.

    Args:
        operator (str): Name of the operator from the noca.Op-class.

    Returns:
        object: Test function for the given operator.
    """

    def test(self):

        # Get input plugs for this operator from dictionary
        literal_input_plugs = TEST_DATA_ASSOCIATION[operator]["input_plugs"]
        # Convert these input strings into actual objects of "self"
        input_plugs = convert_literal_to_object(self, literal_input_plugs)

        # Get output plugs for this operator from dictionary
        literal_output_plugs = TEST_DATA_ASSOCIATION[operator]["output_plugs"]
        # Convert these output strings into actual objects of "self"
        output_plugs = convert_literal_to_object(self, literal_output_plugs)

        # Get NodeCalculator data for this operator
        node_data = noca.OPERATORS[operator]
        node_type = node_data.get("node", None)
        node_inputs = expand_array_attributes(node_data.get("inputs", None), input_plugs)
        node_outputs = node_data.get("outputs", None)
        node_operation = node_data.get("operation", None)

        # This assignment is necessary because closure argument can't be used directly.
        true_operator = operator
        try:
            noca_operator_func = getattr(noca.NcBaseClass, "__{}__".format(true_operator))
        except AttributeError:
            noca_operator_func = getattr(noca.Op, true_operator)

        # Perform operation
        try:
            results = noca_operator_func(*input_plugs, return_all_outputs=True)
        except TypeError:
            results = noca_operator_func(*input_plugs)

        if not isinstance(results, (list, tuple)):
            results = [results]
        for output_plug, result in zip(output_plugs, results):
            output_plug.attrs = result

        # Check that result is an NcNode
        self.assertTrue(isinstance(result, noca.NcNode))

        # Test that the created node is of the correct type
        self.assertEqual(cmds.nodeType(result.node), node_type)

        # Some Operators require a list as input-parameter. These
        flattened_input_plugs = flatten(input_plugs)
        for node_input, desired_input in zip(node_inputs, flattened_input_plugs):
            if isinstance(node_input, (tuple, list)):
                node_input = node_input[0]

            plug = "{}.{}".format(result.node, node_input)

            # Check the input plug actually exists
            self.assertTrue(cmds.objExists(plug))

            # Usually the parent plug gets connected and should be compared.
            # However, some nodes have oddly parented attributes. In that case
            # don't get the parent attribute!
            if TEST_DATA_ASSOCIATION[operator].get("seek_input_parent", True):
                # Get a potential parent plug, which would have been connected instead.
                mplug = om_util.get_mplug_of_plug(plug)
                parent_plug = om_util.get_parent_mplug(mplug)
                if parent_plug:
                    plug = parent_plug

            # Check the correct plug is connected into the input-plug
            input_connections = cmds.listConnections(plug, plugs=True, skipConversionNodes=True)
            self.assertEqual(input_connections, desired_input.plugs)

        # Test that the outputs are correct
        for node_output, desired_output in zip(node_outputs, output_plugs):
            output_is_multidimensional = False
            if len(node_output) > 1:
                output_is_multidimensional = True

            node_output = node_output[0]
            plug = "{}.{}".format(result.node, node_output)

            # Check the output plug actually exists
            self.assertTrue(cmds.objExists(plug))

            if output_is_multidimensional:
                mplug = om_util.get_mplug_of_plug(plug)
                parent_plug = om_util.get_parent_mplug(mplug)
                if parent_plug:
                    plug = parent_plug

            output_connections = cmds.listConnections(plug, plugs=True, skipConversionNodes=True)
            self.assertEqual(output_connections, desired_output.plugs)

        # Test if the operation of the created node is correctly set
        if node_operation:
            operation_attr_value = cmds.getAttr("{}.operation".format(result.node))
            self.assertEqual(operation_attr_value, node_operation)

    return test


class TestOperatorsMeta(type):

    def __new__(_mcs, _name, _bases, _dict):
        """Overriding the class creation method allows to create unittests for
        various types on the fly; without specifying the same test for each
        type specifically.
        """

        # Add tests for each operator
        for operator, data in noca.OPERATORS.iteritems():

            # Skip operators that need an individual test
            if operator in IRREGULAR_OPERATORS:
                continue

            # Skip all condition operators as well; they need a special test
            if data["node"] == "condition":
                op_test_name = "test_{}".format(operator)
                _dict[op_test_name] = _test_condition_op(operator)

            # Any other operator can be tested with the regular op-test
            else:
                op_test_name = "test_{}".format(operator)
                _dict[op_test_name] = _test_regular_op(operator)

        return type.__new__(_mcs, _name, _bases, _dict)


class TestOperators(BaseTestCase):
    """ Metaclass helps to instantiate the TestMetadataValueMeta with all tests """
    __metaclass__ = TestOperatorsMeta

    def setUp(self):
        super(TestOperators, self).setUp()

        # Create standard nodes on which to perform the operations on.
        # Transform test nodes
        self.tf_out_a = noca.create_node("transform", name="transform_out_A")
        self.tf_out_b = noca.create_node("transform", name="transform_out_B")
        self.tf_in_a = noca.create_node("transform", name="transform_in_A")
        self.tf_in_b = noca.create_node("transform", name="transform_in_B")

        # Matrix test nodes
        self.mat_out_a = noca.create_node("holdMatrix", name="matrix_out_A")
        self.mat_out_b = noca.create_node("holdMatrix", name="matrix_out_B")
        self.mat_in_a = noca.create_node("holdMatrix", name="matrix_in_A")

        # Quaternion test nodes
        self.quat_out_a = noca.create_node("eulerToQuat", name="quaternion_out_A")
        self.quat_out_b = noca.create_node("eulerToQuat", name="quaternion_out_B")
        self.quat_in_a = noca.create_node("quatNormalize", name="quaternion_in_A")

        # Mesh, curve and nurbsSurface test nodes
        self.mesh_out_a = noca.create_node("mesh", name="mesh_out_A")
        self.mesh_shape_out_a = noca.Node("mesh_out_AShape")
        self.curve_out_a = noca.create_node("nurbsCurve", name="curve_out_A")
        self.curve_shape_out_a = noca.Node("curve_out_AShape")
        self.surface_out_a = noca.create_node("nurbsSurface", name="surface_out_A")
        self.surface_shape_out_a = noca.Node("surface_out_AShape")

    def test_for_every_operator(self):
        """
        Make sure every operator has its individual test implemented.
        """
        # Get all operators with implemented tests
        operator_tests = []
        for method in TestOperators.__dict__:
            if method == "test_for_every_operator":
                continue

            if method.startswith("test_"):
                tested_operator = method.split("test_", 1)[-1]
                operator_tests.append(tested_operator)

        # Compare operators with implemented tests to all available operators
        all_operators = noca.OPERATORS.keys()[:]
        self.assertEqual(sorted(all_operators), sorted(operator_tests))
