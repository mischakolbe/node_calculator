"""
Unit tests for noca.Op
"""

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# IMPORTS
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Python imports
import unittest

# Third party imports
from maya import cmds

# Local imports
from cmt.test import TestCase
import node_calculator.core as noca
from node_calculator import lookup_table


# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# GLOBALS
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Value of all the types that should be tested
TEST_NODES = [
    "A",
    "B",
    "C",
    "M",
]

MATRIX_OPERATORS = [
    "decompose_matrix",
    "inverse_matrix",
    "mult_matrix",
    "transpose_matrix",
]

IRREGULAR_OPERATORS = [
    "matrix_distance",
    "compose_matrix",
    "point_matrix_mult",
]


# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# TESTS
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
def _test_condition_op(operator):
    """
    Basic tests for condition operators

    Args:
        operator (string): Boolean operator: >, <, =, >=, <=

    Returns:
        test function for the given operator
    """

    def test(self):
        node_data = lookup_table.OPERATOR_LOOKUP_TABLE[operator]
        condition_value = 1.1
        false_value = 2

        # Run noca operation
        bool_operator_func = getattr(noca.NcAtom, "__{}__".format(operator))
        condition_node = bool_operator_func(self.a.tx, condition_value)
        result = noca.Op.condition(condition_node, self.b.tx, false_value)
        self.c.t = result

        # Assertions
        self.assertEqual(cmds.nodeType(result.node), node_data.get("node", None))

        self.assertEqual(result.operation.get(), node_data.get("operation", None))

        self.assertEqual(
            cmds.listConnections(result.firstTerm.plugs[0], plugs=True),
            ['A.translateX']
        )
        self.assertAlmostEqual(result.secondTerm.get(), condition_value, places=7)

        self.assertEqual(result.colorIfFalseR.get(), false_value)
        self.assertEqual(
            cmds.listConnections(result.colorIfTrueR.plugs[0], plugs=True),
            ['B.translateX']
        )

        self.assertEqual(
            sorted(cmds.listConnections(result.outColorR.plugs[0], plugs=True)),
            ['C.translateX', 'C.translateY', 'C.translateZ']
        )

    return test


def _test_regular_op(operator):
    """
    Basic tests that a given value is correctly set up; correct value, type, metadata, ...

    Args:
        value (bool, int, float, list, dict, ...): Value of any data type

    Returns:
        test function for the given value & its type
    """

    matrix_operator = False
    if operator in MATRIX_OPERATORS:
        matrix_operator = True

    def test(self):
        node_data = lookup_table.OPERATOR_LOOKUP_TABLE[operator]

        node_type = node_data.get("node", None)
        node_inputs = node_data.get("inputs", None)
        node_outputs = node_data.get("output", None)
        node_is_multi_index = node_data.get("is_multi_index", False)
        node_operation = node_data.get("operation", None)
        node_output_is_predetermined = node_data.get("output_is_predetermined", False)

        if node_is_multi_index:
            new_node_inputs = []
            for i in range(2):
                input_item = [x.format(multi_index=i) for x in node_inputs[0]]
                new_node_inputs.append(input_item)

            node_inputs = new_node_inputs

        # If this is a matrix operator: Use matrix plugs.
        if matrix_operator:
            possible_inputs = [
                self.a.worldMatrix,
                self.b.worldMatrix,
            ]

            result_plug = self.m.inMatrix
        # If this is NOT a matrix operator: Use transform plugs.
        else:
            possible_inputs = [
                self.a.translateX,
                self.b.translateX,
                self.a.translateY,
                self.b.translateY,
                self.a.translateZ,
                self.b.translateZ,
            ]

            result_plug = self.c.t
        actual_inputs = possible_inputs[0:len(node_inputs)]

        # This assignment is necessary because closure argument can't be used directly.
        true_operator = operator
        try:
            noca_operator_func = getattr(noca.NcAtom, "__{}__".format(true_operator))
        except AttributeError:
            noca_operator_func = getattr(noca.Op, true_operator)

        # Run noca operation
        result = noca_operator_func(*actual_inputs)
        result_plug.attrs = result

        result_node_name = result.node

        # Test that the created node is of the correct type
        self.assertEqual(cmds.nodeType(result_node_name), node_type)

        # Test that the inputs are correct
        for node_input, desired_input in zip(node_inputs, actual_inputs):
            if isinstance(node_input, (tuple, list)):
                node_input = node_input[0]
            input_plug = "{}.{}".format(result_node_name, node_input)

            # Check the input plug actually exists
            input_exists = cmds.objExists(input_plug)
            self.assertTrue(input_exists)

            # Check the correct plug is connected into the input-plug
            input_connections = cmds.listConnections(input_plug, plugs=True)
            self.assertEqual(input_connections, desired_input.plugs)

        # Test that the outputs are correct
        for node_output, desired_output in zip(result, node_outputs):
            self.assertEqual(node_output.attrs_list[0], desired_output)

            output_exists = cmds.objExists(node_output.plugs[0])
            self.assertTrue(output_exists)

        # Test if the operation of the created node is correctly set
        if node_operation:
            operation_attr_value = cmds.getAttr("{}.operation".format(result_node_name))
            self.assertEqual(operation_attr_value, node_operation)

    return test


class TestOperatorsMeta(type):

    def __new__(_mcs, _name, _bases, _dict):
        """
        Overriding the class creation method allows to create unittests for various
        types on the fly; without specifying the same test for each type specifically
        """

        # Add tests for each operator
        for operator, data in lookup_table.OPERATOR_LOOKUP_TABLE.iteritems():

            # Skip operators that need an individual test
            if operator in IRREGULAR_OPERATORS:
                continue

            if data["node"] == "condition":
                op_test_name = "test_{}".format(operator)
                _dict[op_test_name] = _test_condition_op(operator)

            else:
                op_test_name = "test_{}".format(operator)
                _dict[op_test_name] = _test_regular_op(operator)

        return type.__new__(_mcs, _name, _bases, _dict)


class TestOperators(TestCase):
    """ Metaclass helps to instantiate the TestMetadataValueMeta with all tests """
    __metaclass__ = TestOperatorsMeta

    def setUp(self):
        self.a = noca.Node(cmds.createNode("transform", name=TEST_NODES[0]))
        self.b = noca.Node(cmds.createNode("transform", name=TEST_NODES[1]))
        self.c = noca.Node(cmds.createNode("transform", name=TEST_NODES[2]))
        self.m = noca.Node(cmds.createNode("holdMatrix", name=TEST_NODES[3]))

    def tearDown(self):
        cmds.delete(TEST_NODES)

    def test_matrix_distance(self):

        node_data = lookup_table.OPERATOR_LOOKUP_TABLE["matrix_distance"]
        node_type = node_data.get("node", None)
        node_inputs = node_data.get("inputs", None)

        input_plugs = [
            self.a.worldMatrix,
            self.b.worldMatrix,
        ]

        result = noca.Op.matrix_distance(*input_plugs)
        self.c.tx = result

        # Test that the created node is of the correct type
        self.assertEqual(cmds.nodeType(result.node), node_type)

        for node_input, desired_input in zip(node_inputs, input_plugs):
            if isinstance(node_input, (tuple, list)):
                node_input = node_input[0]
            # Check the correct plug is connected into the input-plug
            input_connections = cmds.listConnections(
                "{}.{}".format(result.node, node_input),
                plugs=True
            )
            self.assertEqual(input_connections, desired_input.plugs)

        # Test that the outputs are correct
        plug_connected_to_output = cmds.listConnections(result.plugs, plugs=True)[0]
        self.assertEqual(plug_connected_to_output, "{}.translateX".format(TEST_NODES[2]))

    def test_compose_matrix(self):
        node_data = lookup_table.OPERATOR_LOOKUP_TABLE["compose_matrix"]
        node_type = node_data.get("node", None)
        node_inputs = node_data.get("inputs", None)

        input_plugs = [
            self.a.translateX,
            self.b.rotateX,
            self.a.scaleX,
            self.b.translateX,
        ]

        result = noca.Op.compose_matrix(
            translate=input_plugs[0],
            rotate=input_plugs[1],
            scale=input_plugs[2],
            shear=input_plugs[3],
        )
        self.m.inMatrix = result

        # Test that the created node is of the correct type
        self.assertEqual(cmds.nodeType(result.node), node_type)

        for node_input, desired_input in zip(node_inputs, input_plugs):
            if isinstance(node_input, (tuple, list)):
                node_input = node_input[0]
            # Check the correct plug is connected into the input-plug
            input_connections = cmds.listConnections(
                "{}.{}".format(result.node, node_input),
                plugs=True
            )
            self.assertEqual(input_connections, desired_input.plugs)

        # Test that the outputs are correct
        plug_connected_to_output = cmds.listConnections(result.plugs, plugs=True)[0]
        self.assertEqual(plug_connected_to_output, "{}.inMatrix".format(TEST_NODES[3]))

    def test_point_matrix_mult(self):
        node_data = lookup_table.OPERATOR_LOOKUP_TABLE["point_matrix_mult"]
        node_type = node_data.get("node", None)
        node_inputs = node_data.get("inputs", None)

        input_plugs = [
            self.a.translateX,
            self.m.inMatrix,
        ]

        result = noca.Op.point_matrix_mult(*input_plugs)
        self.c.tx = result

        # Test that the created node is of the correct type
        self.assertEqual(cmds.nodeType(result.node), node_type)

        for node_input, desired_input in zip(node_inputs, input_plugs):
            if isinstance(node_input, (tuple, list)):
                node_input = node_input[0]
            # Check the correct plug is connected into the input-plug
            input_connections = cmds.listConnections(
                "{}.{}".format(result.node, node_input),
                plugs=True
            )
            self.assertEqual(input_connections, desired_input.plugs)

        # Test that the outputs are correct
        plug_connected_to_output = cmds.listConnections(result.plugs, plugs=True)[0]
        self.assertEqual(plug_connected_to_output, "{}.translateX".format(TEST_NODES[2]))

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
        all_operators = lookup_table.OPERATOR_LOOKUP_TABLE.keys()[:]
        self.assertEqual(sorted(all_operators), sorted(operator_tests))
