"""
Unit tests for noca convenience functions
"""

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# IMPORTS
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Python imports

# Third party imports
from maya import cmds

# Local imports
from cmt.test import TestCase
import node_calculator.core as noca


# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# GLOBALS
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~


class TestLink(TestCase):

    def test_node_creation(self):
        """ Test node creation via noca-convenience function """
        transform = cmds.group(empty=True, name="testGroup")
        node = noca.link(transform)

        # Make sure instance of correct type was created
        self.assertIsInstance(node, noca.Node)

        # Make sure no attributes were added to this node instance
        self.assertEqual(len(node.attrs), 0)

    def test_node_with_attrs_creation(self):
        """ Test node creation via noca-convenience function """
        transform = cmds.group(empty=True, name="testGroup")
        attributes = ["tx", "tz"]
        node = noca.link(transform, attributes)

        # Make sure instance of correct type was created
        self.assertIsInstance(node.attrs, noca.Attrs)

        # Make sure attributes were added to this node instance
        self.assertEqual(len(node.attrs), len(attributes))

    def test_metadata_variable_creation(self):
        """ Test metadata variable creation via noca-convenience function """
        value = 1.1
        node = noca.link(value)

        # Make sure instance of correct type was created
        self.assertIsInstance(node, noca.metadata_value.FloatMetadataValue)

        # Make sure MetadataValue holds correct value
        self.assertEqual(node, value)

    def test_collection_creation(self):
        """ Test collection creation via noca-convenience function """
        transform_a = cmds.group(empty=True, name="testGroupA")
        attributes = ["tx", "tz"]
        transform_b = cmds.group(empty=True, name="testGroupB")
        value_a = 1.1
        value_b = 5

        node = noca.link(
            [
                noca.link(transform_a, attributes),
                transform_b,
                noca.link(value_a),
                value_b
            ]
        )

        # Make sure instance of correct type was created
        self.assertIsInstance(node, noca.Collection)

        # Make sure Collection with right amount of elements was created
        self.assertEqual(len(node), 4)

        # Make sure elements of Collection are of correct type
        self.assertIsInstance(node[0], noca.Node)
        self.assertIsInstance(node[1], noca.Node)
        self.assertIsInstance(node[2], noca.metadata_value.FloatMetadataValue)
        self.assertIsInstance(node[3], int)


class TestLocator(TestCase):

    def test_creation(self):
        """ Test locator creation via noca-convenience function """
        name = "test"
        node = noca.locator(name)

        # Make sure noca-node refers to the correct Maya-node
        self.assertEqual(node.node, name)

        # Make sure transform was correctly created
        transform_exists = cmds.objExists(name)
        self.assertTrue(transform_exists)
        transform_type = cmds.objectType(name)
        self.assertEqual(transform_type, "transform")

        # Make sure transform has exactly one child (locator-shape)
        transform_children = cmds.listRelatives(name)
        num_transform_children = len(transform_children)
        self.assertEqual(num_transform_children, 1)

        # Make sure transform child is a locator node
        transform_child_type = cmds.objectType(transform_children[0])
        self.assertEqual(transform_child_type, "locator")


class TestTransform(TestCase):

    def test_creation(self):
        """ Test transform creation via noca-convenience function """
        name = "test"
        node = noca.transform(name)

        # Make sure noca-node refers to the correct Maya-node
        self.assertEqual(node.node, name)

        # Make sure transform was correctly created
        transform_exists = cmds.objExists(name)
        self.assertTrue(transform_exists)
        transform_type = cmds.objectType(name)
        self.assertEqual(transform_type, "transform")

        # Make sure transform has no children
        transform_children = cmds.listRelatives(name)
        self.assertIsNone(transform_children)


class TestCreateNode(TestCase):

    def test_creation(self):
        """ Test node creation via noca-convenience function """
        name = "test"
        node = noca.create_node("polySphere", name=name)

        # Make sure noca-node refers to the correct Maya-node
        self.assertEqual(node.node, name)

        # Make sure polySphere was correctly created
        transform_exists = cmds.objExists(name)
        self.assertTrue(transform_exists)
        transform_type = cmds.objectType(name)
        self.assertEqual(transform_type, "polySphere")
