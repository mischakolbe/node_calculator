"""
Unit tests for noca.NcList
"""

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# IMPORTS
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Python imports
import unittest
import copy

# Third party imports
from maya import cmds

# Local imports
from cmt.test import TestCase
import node_calculator.core as noca

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# GLOBALS
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
TEST_NODES = [
    "A",
    "B",
    "C",
]

TEST_ATTR = "translateX"

TEST_VALUE = 7.3


# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# TESTS
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
class TestNcListClass(TestCase):

    def setUp(self):
        self.a = noca.Node(cmds.createNode("transform", name=TEST_NODES[0]), TEST_ATTR)
        self.b = noca.Node(cmds.createNode("transform", name=TEST_NODES[1]), TEST_ATTR)
        self.c = noca.Node(cmds.createNode("transform", name=TEST_NODES[2]), TEST_ATTR)

        self.val = noca.Node(TEST_VALUE)

        self.desired_list = [self.a, self.val, self.b]

        self.nc_list = noca.NcList(self.desired_list)

    def test_list_functionality(self):

        # Check whether list elements were initialized correctly
        self.assertListEqual(list(self.nc_list), list(self.desired_list))

        # Test len-method
        self.assertEqual(len(self.nc_list), len(self.desired_list))

        # Test reversed-method
        self.assertListEqual(
            list(reversed(self.desired_list)),
            list(reversed(self.nc_list))
        )

        # Test getitem method
        self.assertEqual(self.nc_list[0], self.desired_list[0])
        self.assertEqual(self.nc_list[1], self.desired_list[1])
        self.assertEqual(self.nc_list[2], self.desired_list[2])

        # Test setitem method
        # Test setAttr
        val_before = cmds.getAttr("{}.{}".format(TEST_NODES[0], TEST_ATTR))
        self.assertEqual(val_before, 0)
        self.nc_list[0].attrs = self.val
        val_after = cmds.getAttr("{}.{}".format(TEST_NODES[0], TEST_ATTR))
        self.assertEqual(val_after, TEST_VALUE)
        # Test connectAttr
        connections_before = cmds.listConnections("{}.{}".format(TEST_NODES[2], TEST_ATTR))
        self.assertIsNone(connections_before)
        self.nc_list[2].attrs = self.c.attrs
        connections_after = cmds.listConnections(
            "{}.{}".format(TEST_NODES[2], TEST_ATTR),
            connections=True,
            plugs=True,
        )[0]
        self.assertEqual(connections_after, "{}.{}".format(TEST_NODES[2], TEST_ATTR))

        # Test copy method
        nc_list_copy = copy.copy(self.nc_list)
        self.assertListEqual(list(self.desired_list), list(nc_list_copy))

        # Test append method
        nc_list_copy.append(self.c)
        self.assertEqual(len(nc_list_copy), len(self.desired_list) + 1)
        self.assertEqual(nc_list_copy[-1], self.c)

        # Test insert method
        nc_list_copy = copy.copy(self.nc_list)
        nc_list_copy.insert(1, self.c)
        self.assertEqual(len(nc_list_copy), len(self.desired_list) + 1)
        self.assertEqual(nc_list_copy[1], self.c)

        # Test delitem method (Back to what it was before insert method!)
        del nc_list_copy[1]
        self.assertEqual(len(nc_list_copy), len(self.desired_list))
        self.assertEqual(nc_list_copy[1], self.val)

        # Test extend method
        nc_list_copy = copy.copy(self.nc_list)
        nc_list_copy.extend(self.nc_list)
        self.assertEqual(len(nc_list_copy), len(self.desired_list)*2)
        self.assertListEqual(
            list(nc_list_copy),
            list(self.desired_list*2)
        )

    def test_noca_methods(self):

        # Test nodes property
        self.assertEqual(self.nc_list.node, None)
        self.assertListEqual(self.nc_list.nodes, TEST_NODES[:2])

        # Test get method to retrieve values
        self.assertListEqual(self.nc_list.get(), [0, TEST_VALUE, 0])
