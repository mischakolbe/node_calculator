"""
Unit tests for metadata_values.py
"""

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# IMPORTS
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Python imports
import unittest

# Local imports
if __name__ == "__main__":
    # Make sure relative paths don't mess up the import procedure, if script is run directly
    import sys
    from os import path
    sys.path.append(path.dirname(path.dirname(path.abspath(__file__))))
    import attrs_class
else:
    from .. import attrs_class


# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# GLOBALS
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~


class TestAttrsClass(unittest.TestCase):

    def setUp(self):
        """
        Generic setup available to all tests
        """

        # noca_node_a is a generic, "standard" node_calculator node
        self.node_a_name = "pCube1"
        self.node_a_attrs = ["tx", "rx", "ty"]
        self.noca_node_a = attrs_class.NewNode(self.node_a_name, self.node_a_attrs)

        # noca_node_b is created out of a range of noca_node_a
        self.b_range_min = 1
        self.b_range_max = 3
        self.noca_node_b = self.noca_node_a[self.b_range_min:self.b_range_max]

    def test_node_instantiation(self):

        self.assertEqual(self.noca_node_a.node, self.node_a_name)
        self.assertListEqual(self.noca_node_a.attrs, self.node_a_attrs)

        self.assertIs(type(self.noca_node_a), attrs_class.NewNode)
        self.assertIs(type(self.noca_node_a.node), str)
        self.assertIs(type(self.noca_node_a.attrs), list)

    def test_node_attrs_index_lookup(self):
        for i, attr in enumerate(self.node_a_attrs):
            node_attrs_i = self.noca_node_a.attrs[i]
            self.assertEqual(node_attrs_i, attr)
            self.assertEqual(type(node_attrs_i), type(attr))

    def test_node_index_lookup(self):
        for i, noca_node_a_sub in enumerate(self.noca_node_a):
            self.assertEqual(noca_node_a_sub.attrs[0], self.node_a_attrs[i])
            self.assertEqual(type(noca_node_a_sub.attrs[0]), type(self.node_a_attrs[i]))

    def test_node_derivated_instantiation(self):
        self.assertEqual(self.noca_node_b.node, self.node_a_name)
        self.assertListEqual(self.noca_node_b.attrs, self.node_a_attrs[self.b_range_min:self.b_range_max])

        self.assertIs(type(self.noca_node_b), attrs_class.NewNode)
        self.assertIs(type(self.noca_node_b.node), str)
        self.assertIs(type(self.noca_node_b.attrs), list)


if __name__ == '__main__':
    unittest.main()
