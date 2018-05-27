"""
Unit tests for noca.om_util
"""

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# IMPORTS
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Python imports
import unittest

# Local imports
from cmt.test import TestCase
from node_calculator import om_util


# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# GLOBALS
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

test_plug_strings = {
    # string of the made-up maya-plug
    "node.parent_attr":
        # The tuple that should be returned, consisting of:
        # namespace, dag_path, node, parent_attr, array_index, child_attr
        ('', '', 'node', 'parent_attr', '', ''),
    "name_space:node.parent_attr":
        ('name_space', '', 'node', 'parent_attr', '', ''),
    "|dag|path|node.parent_attr":
        ('', 'dag|path|', 'node', 'parent_attr', '', ''),
    "node.parent_attr[1]":
        ('', '', 'node', 'parent_attr', '1', ''),
    "node.parent_attr.child_attr":
        ('', '', 'node', 'parent_attr', '', 'child_attr'),
    "name_space:|dag|path|node.parent_attr[1].child_attr":
        ('name_space', 'dag|path|', 'node', 'parent_attr', '1', 'child_attr'),
}


class TestTracerClass(TestCase):

    def test_split_plug_string_into_components(self):
        """ Test plug strings are correctly split into their components """

        for test_plug_string, desired_components in test_plug_strings.iteritems():
            components = om_util.split_plug_string_into_components(test_plug_string)

            self.assertEqual(components, desired_components)
