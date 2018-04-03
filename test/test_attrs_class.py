"""
Unit tests for attrs_class.py
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
        self.b_attrs_slice = slice(1, 3)
        self.noca_node_b = self.noca_node_a[self.b_attrs_slice]

    def test_node_instantiation(self):
        """ Test normal instantiation of a noca-node """

        self.assertEqual(self.noca_node_a.node, self.node_a_name)
        self.assertListEqual(self.noca_node_a.attrs, self.node_a_attrs)

        self.assertIs(type(self.noca_node_a), attrs_class.NewNode)
        self.assertIs(type(self.noca_node_a.node), str)
        self.assertIs(type(self.noca_node_a.attrs), list)

    def test_node_attrs_index_lookup(self):
        """
        Test indexed lookup of noca-node attributes
        (as in: the list of attributes)
        """

        for i, attr in enumerate(self.node_a_attrs):
            node_attrs_i = self.noca_node_a.attrs[i]
            self.assertEqual(node_attrs_i, attr)
            self.assertEqual(type(node_attrs_i), type(attr))

    def test_node_index_lookup(self):
        """
        Test indexed lookup of noca-nodes
        (as in: use parts of a noca-node to get a new noca-node object)
        """

        for i, noca_node_a_sub in enumerate(self.noca_node_a):
            self.assertEqual(noca_node_a_sub.attrs[0], self.node_a_attrs[i])
            self.assertEqual(type(noca_node_a_sub.attrs[0]), type(self.node_a_attrs[i]))

    def test_node_derivated_instantiation(self):
        """ Test instantiation of noca-nodes from an existing noca-node """

        self.assertEqual(self.noca_node_b.node, self.node_a_name)
        self.assertListEqual(self.noca_node_b.attrs, self.node_a_attrs[self.b_attrs_slice])

        self.assertIs(type(self.noca_node_b), attrs_class.NewNode)
        self.assertIs(type(self.noca_node_b.node), str)
        self.assertIs(type(self.noca_node_b.attrs), list)

    def __test_node_attrs_assignment(self):
        self.noca_node_a.tx = 3
        # Should assign a value to pCube1.tx
        self.noca_node_a.attrs = [self.noca_node_a[2], 7, attrs_class.NewNode("pSphere1.sz")]
        # Should assign given list to attributes of node noca_node_a.node

    def test_node_attrs_redefinition(self):
        """ Test redefining node-attrs """

        replace_one_attr = "replace_one"
        replace_one_attr_list = self.node_a_attrs[:]
        replace_one_attr_list[1] = "replace_one"
        replace_all_attrs_list = ["replace_all"]*3

        self.noca_node_a.attrs[1] = replace_one_attr
        self.assertListEqual(self.noca_node_a.attrs, replace_one_attr_list)

        self.noca_node_a.attrs[:] = replace_all_attrs_list
        self.assertListEqual(self.noca_node_a.attrs, replace_all_attrs_list)


if __name__ == '__main__':
    unittest.main()
