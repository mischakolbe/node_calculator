"""
Unit tests for noca.NcAttrs
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

TEST_BLENDSHAPE = "B"

TEST_VALUE = 5.5


# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# TESTS
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
class TestAttrsClass(TestCase):

    def setUp(self):
        self.test_transform = cmds.createNode("transform", name=TEST_TRANSFORM)
        self.node_instance = noca.NcNode(TEST_TRANSFORM)

    def tearDown(self):
        # Remove test nodes
        cmds.delete(TEST_TRANSFORM)

    def test_initialization(self):
        """Test the instantiation of the NcAttrs class"""

        # Test various ways a NcAttrs class can be instantiated
        nc_attrs_as_argument = noca.NcAttrs(self.node_instance, "tx")
        args_options = [
            None,
            "tx",
            ["tx"],
            ["tx", "ty"],
            nc_attrs_as_argument,
        ]
        for attrs_arg in args_options:
            expected_attrs_arg = attrs_arg

            if isinstance(attrs_arg, noca.NcAttrs):
                expected_attrs_arg = attrs_arg.attrs_list

            if attrs_arg is None:
                expected_attrs_arg = []

            if not isinstance(expected_attrs_arg, list):
                expected_attrs_arg = [expected_attrs_arg]

            attrs_instance = noca.NcAttrs(self.node_instance, attrs_arg)
            self.assertEqual(attrs_instance.node, TEST_TRANSFORM)
            self.assertEqual(attrs_instance.attrs_list, expected_attrs_arg)

        # Test auto_unravel & auto_consolidate of NcAttrs initialization
        for state in [True, False]:
            node_instance = noca.NcNode(TEST_TRANSFORM, auto_unravel=state)
            attrs_instance = node_instance.tx
            self.assertEqual(attrs_instance._auto_unravel, state)

            node_instance = noca.NcNode(TEST_TRANSFORM, auto_consolidate=state)
            attrs_instance = node_instance.tx
            self.assertEqual(attrs_instance._auto_consolidate, state)

    def test_methods(self):
        """Test basic methods of NcAttrs"""

        # A blendshape is used, because it has "sub-attributes": .attr_a.attr_b
        # This comes in handy to test the "concatenation" of _held_attrs_list,
        # when these NcAttrs methods are invoked.
        test_blendshape = cmds.createNode("blendShape", name=TEST_BLENDSHAPE)

        # Create NcNode instance that will be used as an inConnection
        in_connection_plug = "{}.translateX".format(TEST_TRANSFORM)
        in_connection_node = noca.NcNode(in_connection_plug)

        # Define general variables used later on
        base_attribute = "inputTarget[0]"
        full_attribute = "{}.sculptInbetweenWeight".format(base_attribute)
        full_plug = "{}.{}".format(TEST_BLENDSHAPE, full_attribute)

        # Create NcAttrs test instance (manually with NcNode instance!)
        node_instance = noca.NcNode(TEST_BLENDSHAPE)
        attrs_instance = noca.NcAttrs(node_instance, base_attribute)

        # Test getattr method
        result = attrs_instance.sculptInbetweenWeight
        self.assertIsInstance(result, noca.NcAttrs)
        self.assertEqual(result.plugs, [full_plug])

        # Test setattr method by comparing values before and after setting
        self.assertEqual(cmds.getAttr(full_plug), -1)
        attrs_instance.sculptInbetweenWeight = TEST_VALUE
        self.assertEqual(cmds.getAttr(full_plug), TEST_VALUE)
        attrs_instance.sculptInbetweenWeight = in_connection_node
        connections = cmds.listConnections(full_plug, connections=True, plugs=True)
        self.assertEqual(connections, [full_plug, in_connection_plug])

        # Delete and recreated blendshape to start fresh for getitem/setitem methods
        cmds.delete(test_blendshape)
        cmds.createNode("blendShape", name=TEST_BLENDSHAPE)

        # Test getitem method
        node_instance = noca.NcNode(TEST_BLENDSHAPE)
        attrs_instance = noca.NcAttrs(node_instance, full_attribute)
        result = attrs_instance[0]
        self.assertIsInstance(result, noca.NcAttrs)
        self.assertEqual(result.plugs, [full_plug])

        # Test setitem method
        self.assertEqual(cmds.getAttr(full_plug), -1)
        attrs_instance[0] = TEST_VALUE
        self.assertEqual(cmds.getAttr(full_plug), TEST_VALUE)
        attrs_instance[0] = in_connection_node
        connections = cmds.listConnections(full_plug, connections=True, plugs=True)
        self.assertEqual(connections, [full_plug, in_connection_plug])
