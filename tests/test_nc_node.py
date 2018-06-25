"""
Unit tests for noca.NcNode
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


# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# GLOBALS
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
TEST_TRANSFORM = "A"

TEST_VALUE = 5.5


# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# TESTS
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
class TestNodeClass(TestCase):

    def setUp(self):
        self.test_transform = cmds.createNode("transform", name=TEST_TRANSFORM)

    def tearDown(self):
        # Remove test nodes
        cmds.delete(TEST_TRANSFORM)

    def test_initialization(self):
        """Test the instantiation of the NcNode class"""

        # Test various ways a NcNode class can be instantiated
        nc_node_as_argument = noca.NcNode(TEST_TRANSFORM, "tx")
        nc_attrs_as_argument = noca.NcAttrs(nc_node_as_argument, "tx")
        args_options = [
            ["A", None],
            ["A.t", None],
            ["A.tx", None],
            ["A", ["tx"]],
            ["A", ["tx", "ty"]],
            [nc_node_as_argument, None],
            [nc_attrs_as_argument, None],
        ]
        for node_arg, attrs_arg in args_options:
            expected_node_arg = node_arg
            expected_attrs_arg = attrs_arg

            if isinstance(node_arg, noca.NcBaseNode):
                expected_node_arg = node_arg.node
                expected_attrs_arg = node_arg.attrs_list

            elif "." in node_arg:
                expected_node_arg, expected_attrs_arg = node_arg.split(".", 1)

            elif attrs_arg is None:
                expected_attrs_arg = []

            if not isinstance(expected_attrs_arg, list):
                expected_attrs_arg = [expected_attrs_arg]

            node_instance = noca.NcNode(node_arg, attrs_arg)
            self.assertEqual(node_instance.node, expected_node_arg)
            self.assertEqual(node_instance.attrs_list, expected_attrs_arg)

        # Test auto_unravel & auto_consolidate setting at NcNode initialization
        for state in [True, False]:
            node_instance = noca.NcNode(TEST_TRANSFORM, auto_unravel=state)
            self.assertEqual(node_instance._auto_unravel, state)

            node_instance = noca.NcNode(TEST_TRANSFORM, auto_consolidate=state)
            self.assertEqual(node_instance._auto_consolidate, state)

        # Test auto_unravel & auto_consolidate setting when initialized with NcNode
        for state in [True, False]:
            node_instance = noca.NcNode(TEST_TRANSFORM, auto_unravel=state)
            # First; initialize NcNode without specifying auto_unravel-state:
            # auto_unravel behaviour should mimic the state of the given NcNode
            node_offspring = noca.NcNode(node_instance)
            self.assertEqual(node_offspring._auto_unravel, state)
            # Second; A given auto_unravel state precedes the inherited state
            node_offspring = noca.NcNode(node_instance, auto_unravel=not state)
            self.assertEqual(node_offspring._auto_unravel, not state)

            # auto_consolidate testing similar to auto_unravel tests above
            node_instance = noca.NcNode(TEST_TRANSFORM, auto_consolidate=state)
            node_offspring = noca.NcNode(node_instance)
            self.assertEqual(node_offspring._auto_consolidate, state)
            node_offspring = noca.NcNode(node_instance, auto_consolidate=not state)
            self.assertEqual(node_offspring._auto_consolidate, not state)

    def test_methods(self):
        """Test basic methods of NcNodes"""
        base_attribute = "translateX"
        base_plug = "{}.{}".format(TEST_TRANSFORM, base_attribute)
        node_instance = noca.NcNode(base_plug)

        # Test getattr method
        attr_plug = "{}.translateY".format(TEST_TRANSFORM)
        result = node_instance.translateY
        self.assertIsInstance(result, noca.NcAttrs)
        self.assertEqual(result.plugs, [attr_plug])

        # Test setattr method by comparing values before and after setting
        self.assertEqual(cmds.getAttr(attr_plug), 0)
        node_instance.translateY = TEST_VALUE
        self.assertEqual(cmds.getAttr(attr_plug), TEST_VALUE)
        node_instance.translateY = node_instance
        connections = cmds.listConnections(attr_plug, connections=True, plugs=True)
        self.assertEqual(connections, [attr_plug, base_plug])

        # Test getitem method
        item_plug = "{}.translateZ".format(TEST_TRANSFORM)
        result = node_instance[0]
        self.assertIsInstance(result, noca.NcNode)
        self.assertEqual(result.plugs, [base_plug])

        # Test setitem method
        node_item_instance = noca.NcNode(item_plug)
        self.assertEqual(cmds.getAttr(item_plug), 0)
        node_item_instance[0] = TEST_VALUE
        self.assertEqual(cmds.getAttr(item_plug), TEST_VALUE)
        node_item_instance[0] = node_instance
        connections = cmds.listConnections(item_plug, connections=True, plugs=True)
        self.assertEqual(connections, [item_plug, base_plug])
