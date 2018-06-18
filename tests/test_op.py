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
]
IRREGULAR_OPERATORS = [
    "matrix_distance",
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
        node_data = lookup_table.NODE_LOOKUP_TABLE[operator]
        condition_value = 1.1
        false_value = 2

        # Run noca operation
        bool_operator_func = getattr(noca.Atom, "__{}__".format(operator))
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

    def test(self):
        node_data = lookup_table.NODE_LOOKUP_TABLE[operator]

        node_type = node_data.get("node", None)
        node_inputs = node_data.get("inputs", None)
        node_output = node_data.get("output", None)
        node_is_multi_index = node_data.get("is_multi_index", False)
        node_operation = node_data.get("operation", None)
        node_output_is_predetermined = node_data.get("output_is_predetermined", False)

        if node_is_multi_index:
            new_node_inputs = []
            for i in range(2):
                input_item = [x.format(multi_index=i) for x in node_inputs[0]]
                new_node_inputs.append(input_item)

            node_inputs = new_node_inputs

        possible_inputs = [
            self.a.translateX,
            self.b.translateX,
            self.a.translateY,
            self.b.translateY,
            self.a.translateZ,
            self.b.translateZ,
        ]
        true_operator = operator
        # node_data = lookup_table.NODE_LOOKUP_TABLE[true_operator]

        actual_inputs = possible_inputs[0:len(node_inputs)]

        try:
            noca_operator_func = getattr(noca.Atom, "__{}__".format(true_operator))
        except AttributeError:
            noca_operator_func = getattr(noca.Op, true_operator)

        # Run noca operation
        result = noca_operator_func(*actual_inputs)
        self.c.t = result

        # Assertions
        self.assertEqual(cmds.nodeType(result.node), node_type)

        for node_input, desired_input in zip(node_inputs, actual_inputs):
            if isinstance(node_input, (tuple, list)):
                node_input = node_input[0]
            input_plug = noca.Node(result, node_input).plugs[0]

            input_plugs = cmds.listConnections(input_plug, plugs=True)

            print(">>>>", desired_input.plugs, input_plugs)
            self.assertEqual(
                input_plugs,
                desired_input.plugs
            )

        # self.assertEqual(result.operation.get(), 2)
        # self.assertEqual(result.secondTerm.get(), 1)
        # self.assertEqual(result.colorIfFalseR.get(), 2)

        # self.assertEqual(
        #     cmds.listConnections(result.firstTerm.plugs[0], plugs=True),
        #     ['A.translateX']
        # )
        # self.assertEqual(
        #     cmds.listConnections(result.colorIfTrueR.plugs[0], plugs=True),
        #     ['B.translateX']
        # )

        # self.assertEqual(
        #     sorted(cmds.listConnections(result.outColorR.plugs[0], plugs=True)),
        #     ['C.translateX', 'C.translateY', 'C.translateZ']
        # )

    return test


class TestOperatorsMeta(type):

    def __new__(_mcs, _name, _bases, _dict):
        """
        Overriding the class creation method allows to create unittests for various
        types on the fly; without specifying the same test for each type specifically
        """

        # Add tests for each operator
        for operator, data in lookup_table.NODE_LOOKUP_TABLE.iteritems():

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

    def tearDown(self):
        cmds.delete(TEST_NODES)
