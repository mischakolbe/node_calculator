"""
Unit tests for noca.NcBaseNode: Must apply for NcNode AND NcAttrs class!
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
# TESTS
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~


class TestNodeClass(TestCase):
    def setUp(self):
        self.node_name = "testNode"
        self.node_alt_name = "testAltName"
        self.group_name = "testGrp"
        self.instance_name = "testInstance"
        self.operator_name = "testPlusMinusAverage"

        # Create regular polyCube transform & shape node
        self.test_node = cmds.polyCube(name=self.node_name, constructionHistory=False)[0]

        # Add a second shape under the same transform node
        shape_duplicate = cmds.duplicate(self.test_node)[0]
        cmds.parent(
            cmds.listRelatives(shape_duplicate, shapes=True)[0],
            self.test_node,
            relative=True,
            shape=True,
        )
        cmds.delete(shape_duplicate)
        self.test_shapes = cmds.listRelatives(self.test_node, shapes=True)

        # Parent the polyCube node under a group
        self.test_group = cmds.group(empty=True, name=self.group_name)
        cmds.parent(self.test_node, self.test_group)

        # Instantiate the polyCube
        self.test_instance = cmds.instance(self.test_node, name=self.instance_name)[0]

        # Create an operator node used for calculations
        self.test_operator = cmds.createNode("plusMinusAverage", name=self.operator_name)
        cmds.connectAttr(
            "{}.t".format(self.node_name),
            "{}.input3D[0]".format(self.operator_name)
        )
        cmds.connectAttr(
            "{}.s".format(self.node_name),
            "{}.input3D[3]".format(self.operator_name)
        )

    @unittest.skip("Not implemented yet")
    def test_some_test(self):
        """ Test XYZ """
        for nc_type in [self.test_node, self.test_attrs]:
            do_whatever_test_you_want
