"""
Unit tests that must apply for NcNode AND NcAttrs class!
"""

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# IMPORTS
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Python imports
import unittest

# Third party imports
from maya import cmds
import pymel.core as pm

# Local imports
from cmt.test import TestCase
import node_calculator.core as noca


# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# GLOBALS
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
TEST_MESH = "A"
TEST_TRANSFORM = "B"

TEST_ATTRIBUTE_SINGLE = ["translateX"]

TEST_ATTRIBUTE_PARENT = ["translate"]

TEST_ATTRIBUTE_MULTI = ["translateX", "translateY", "translateZ"]

TEST_POSITION_A = [1.0, 2.5, 3.0]

TEST_POSITION_B = [8.0, 9.0, 10.2]


# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# TESTS
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
class TestNcBaseNodeClass(TestCase):

    def setUp(self):
        # Create regular polyCube transform & shape node
        self.test_mesh = cmds.polyCube(name=TEST_MESH, constructionHistory=False)[0]

        # Add a second shape under the same transform node
        shape_duplicate = cmds.duplicate(self.test_mesh)[0]
        cmds.parent(
            cmds.listRelatives(shape_duplicate, shapes=True)[0],
            self.test_mesh,
            relative=True,
            shape=True,
        )
        cmds.delete(shape_duplicate)
        self.test_shapes = cmds.listRelatives(self.test_mesh, shapes=True)
        self.node_mesh = noca.NcNode(self.test_mesh)

        self.test_transform = cmds.createNode("transform", name=TEST_TRANSFORM)
        self.node_single_attr = noca.NcNode(self.test_transform, TEST_ATTRIBUTE_SINGLE)
        self.node_parent_attr = noca.NcNode(self.test_transform, TEST_ATTRIBUTE_PARENT)
        self.node_multi_attr = noca.NcNode(self.test_transform, TEST_ATTRIBUTE_MULTI)

        self.attrs_single_attr = noca.NcAttrs(self.node_single_attr, TEST_ATTRIBUTE_SINGLE)
        self.attrs_parent_attr = noca.NcAttrs(self.node_single_attr, TEST_ATTRIBUTE_PARENT)
        self.attrs_multi_attr = noca.NcAttrs(self.node_multi_attr, TEST_ATTRIBUTE_MULTI)

        self.test_items = [
            self.node_single_attr,
            self.node_parent_attr,
            self.node_multi_attr,
            self.attrs_single_attr,
            self.attrs_parent_attr,
            self.attrs_multi_attr,
        ]

        # The desired attrs and values must match the order of the test_items!
        self.desired_attrs = [
            TEST_ATTRIBUTE_SINGLE,
            TEST_ATTRIBUTE_PARENT,
            TEST_ATTRIBUTE_MULTI,
            TEST_ATTRIBUTE_SINGLE,
            TEST_ATTRIBUTE_PARENT,
            TEST_ATTRIBUTE_MULTI,
        ]
        self.desired_values_a = [
            TEST_POSITION_A[0],
            TEST_POSITION_A,
            TEST_POSITION_A,
            TEST_POSITION_A[0],
            TEST_POSITION_A,
            TEST_POSITION_A,
        ]
        self.desired_values_b = [
            TEST_POSITION_B[0],
            TEST_POSITION_B,
            TEST_POSITION_B,
            TEST_POSITION_B[0],
            TEST_POSITION_B,
            TEST_POSITION_B,
        ]

    def tearDown(self):
        # Remove test nodes
        cmds.delete(TEST_MESH, TEST_TRANSFORM)

    def test_basic_methods(self):
        for i, noca_instance in enumerate(self.test_items):
            desired_attrs = self.desired_attrs[i]
            desired_value_a = self.desired_values_a[i]
            desired_value_b = self.desired_values_b[i]

            # Test node property
            self.assertEqual(noca_instance.node, TEST_TRANSFORM)
            self.assertEqual(noca_instance.nodes, [TEST_TRANSFORM])

            # Test attrs property
            self.assertIsInstance(noca_instance.attrs, noca.NcAttrs)
            # If current noca_instance is NcAttrs, its .attrs should be itself!
            if isinstance(noca_instance, noca.NcAttrs):
                self.assertIs(noca_instance.attrs, noca_instance)

            # Test attrs_list property
            self.assertListEqual(noca_instance.attrs_list, desired_attrs)

            # Move TEST_NODE back to same place every time loop comes around!
            cmds.setAttr(
                "{}.translate".format(TEST_TRANSFORM),
                *TEST_POSITION_A,
                type="double3"
            )

            # Test len method
            self.assertEqual(len(noca_instance), len(desired_attrs))

            # Test iter method
            for item, desired_attr in zip(noca_instance, desired_attrs):
                plug = "{}.{}".format(TEST_TRANSFORM, desired_attr)
                self.assertEqual(item.plugs[0], plug)

            # Test get method (use Tracer to get NcValues back!)
            with noca.Tracer():
                queried_value = noca_instance.get()
                self.assertEqual(queried_value, desired_value_a)
                if not isinstance(desired_value_a, list):
                    self.assertIsInstance(queried_value, noca.nc_value.NcValue)

            # Test set method
            noca_instance.set(desired_value_b)
            self.assertEqual(noca_instance.get(), desired_value_b)

    def test_convenience_methods(self):
        """Test various NcBaseNode methods that are purely there for convenience"""

        # Test get_shapes method to retrieve all shapes of the given node
        self.assertEqual(self.node_mesh.get_shapes(), self.test_shapes)
        self.assertEqual(self.node_single_attr.get_shapes(), [])

        # Test plugs method to retrieve plugs stored on a Node
        # No plugs
        self.assertEqual(self.node_mesh.plugs, [])
        # Single plug
        single_plug = ["{}.{}".format(TEST_TRANSFORM, TEST_ATTRIBUTE_SINGLE[0])]
        self.assertEqual(self.node_single_attr.plugs, single_plug)
        # Parent plug
        parent_plug = ["{}.{}".format(TEST_TRANSFORM, TEST_ATTRIBUTE_PARENT[0])]
        self.assertEqual(self.node_parent_attr.plugs, parent_plug)
        # List of plugs
        multi_plug = [
            "{}.{}".format(TEST_TRANSFORM, attr) for attr in TEST_ATTRIBUTE_MULTI
        ]
        self.assertEqual(self.attrs_multi_attr.plugs, multi_plug)

        # Test info method to print auto_consolidate and auto_unravel state exists
        self.node_mesh.auto_state()
        self.attrs_multi_attr.auto_state()

        # Test to_py_node method to easily retrieve a PyNode instance
        self.assertIsInstance(self.node_mesh.to_py_node(), pm.nodetypes.Transform)
        self.assertIsInstance(self.attrs_parent_attr.to_py_node(), pm.general.Attribute)
        with self.assertRaises(RuntimeError):
            self.attrs_multi_attr.to_py_node()

    def test_attribute_adding(self):
        """Test convenience methods to add attributes to Maya nodes"""

        # Test most basic attribute adding
        int_attr_name = "intTestAttr"
        int_plug = "{}.{}".format(TEST_MESH, int_attr_name)
        int_attr = self.node_mesh.add_float(int_attr_name)
        # Test whether returned value is a NcNode instance with the added attr
        self.assertIsInstance(int_attr, noca.NcNode)
        self.assertEqual(int_attr.plugs[0], int_plug)
        # Test whether added attribute actually exists
        self.assertTrue(cmds.objExists(int_plug))
        # Test whether attribute was set up correctly
        self.assertEqual(cmds.addAttr(int_plug, query=True, keyable=True), True)

        # Test attribute adding with kwargs
        kwargs = {
            "attributeType": "nonsenseType",
            "min": -1,
            "keyable": False,
            "hidden": True,
        }
        float_attr_name = "floatTestAttr"
        float_plug = "{}.{}".format(TEST_MESH, float_attr_name)
        self.node_mesh.add_float(float_attr_name, **kwargs)
        # Test whether added attribute actually exists
        self.assertTrue(cmds.objExists(float_plug))
        # Test whether attribute was set up correctly
        self.assertEqual(cmds.addAttr(float_plug, query=True, attributeType=True), "float")
        self.assertTrue(cmds.addAttr(float_plug, query=True, hasMinValue=True))
        self.assertEqual(cmds.addAttr(float_plug, query=True, minValue=True), -1)
        self.assertEqual(cmds.addAttr(float_plug, query=True, keyable=True), False)
        self.assertEqual(cmds.addAttr(float_plug, query=True, hidden=True), True)

        # Test enum attribute adding
        enum_attr_name = "enumTestAttr"
        enum_plug = "{}.{}".format(TEST_MESH, enum_attr_name)
        enum_cases = ["caseA", "caseB"]
        self.node_mesh.add_enum(enum_attr_name, cases=enum_cases)
        # Test whether added attribute actually exists
        self.assertTrue(cmds.objExists(enum_plug))
        # Test whether attribute was set up correctly
        self.assertEqual(
            cmds.attributeQuery(enum_attr_name, node=TEST_MESH, listEnum=True),
            [":".join(enum_cases)]
        )

        # Test separator adding
        separator_attr = self.node_mesh.add_separator()
        # Test whether added attribute actually exists
        self.assertTrue(cmds.objExists(separator_attr.plugs[0]))
        # Test whether attribute was set up correctly
        self.assertEqual(
            cmds.attributeQuery(separator_attr.attrs_list[0], node=TEST_MESH, niceName=True),
            noca.DEFAULT_SEPARATOR_NAME
        )
        self.assertEqual(
            cmds.attributeQuery(separator_attr.attrs_list[0], node=TEST_MESH, listEnum=True),
            ["{}".format(noca.DEFAULT_SEPARATOR_VALUE)]
        )
