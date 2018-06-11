"""
Unit tests for noca.om_util
"""

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# IMPORTS
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Python imports
import unittest

# Third party imports

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
        ('', '', 'node', 'parent_attr', None, ''),
    "name_space:node.parent_attr":
        ('name_space', '', 'node', 'parent_attr', None, ''),
    "|dag|path|node.parent_attr":
        ('', 'dag|path|', 'node', 'parent_attr', None, ''),
    "node.parent_attr[1]":
        ('', '', 'node', 'parent_attr', 1, ''),
    "node.parent_attr.child_attr":
        ('', '', 'node', 'parent_attr', None, 'child_attr'),
    "name_space:|dag|path|node.parent_attr[1].child_attr":
        ('name_space', 'dag|path|', 'node', 'parent_attr', 1, 'child_attr'),
}


# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# TESTS
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~


class TestTracerClass(TestCase):

    def test_split_plug_string(self):
        """ Test plug strings are correctly split into their components """

        for test_plug_string, desired_components in test_plug_strings.iteritems():
            components = om_util.split_plug_string(test_plug_string)
            self.assertEqual(components, desired_components)

            node_string, attr_string = test_plug_string.split(".", 1)
            node_components = om_util.split_node_string(node_string)
            self.assertEqual(node_components, desired_components[:3])
            attr_components = om_util.split_attr_string(attr_string)
            self.assertEqual(attr_components, desired_components[3:])

    # def test_mobj(self):
    #     """ Test mobj creation & retrieving """
    #     om_util.get_name_of_mobj(mobj)
    #     om_util.get_mobj(node)
    #     om_util.get_long_name_of_mobj(mobj, full=True/False)
    #     om_util.rename_mobj(mobj, name)
    #     om_util.selected_nodes_in_scene_as_mobjs()
    #     om_util.select_mobjs(mobjs)

    # def test_mdag_path(self):
    #     """ """
    #     om_util.get_mdag_path(mobj)

    # def test_shape(self):
    #     """ """
    #     om_util.get_shape_mobjs(mobj)

    # def test_node(self):
    #     """ """
    #     om_util.is_instanced(node)
    #     om_util.get_node_type(node, api_type=False)
    #     om_util.get_all_mobjs_of_type(dependency_node_type)
    #     om_util.get_mfn_dag_node(node)
    #     om_util.get_parents(node)
    #     om_util.get_parent(node)

    # def test_plug(self):
    #     """ """
    #     om_util.set_mobj_attribute(mobj, attr, value)
    #     om_util.get_attr_of_mobj(mobj, attr)

    #     om_util.get_mplug_of_mobj(mobj, attr)
    #     om_util.is_valid_mplug(mplug)
    #     om_util.get_parent_plug(mplug)
    #     om_util.get_child_mplug(mplug, child)
    #     om_util.get_child_mplugs(mplug)
    #     om_util.get_array_plug_elements(mplug)

    #     om_util.get_array_plug_by_physical_index(mplug, index)
    #     om_util.get_array_plug_by_logical_index(mplug, index)
    #     om_util.get_mplug_of_node_and_attr(node, attr)
    #     om_util.get_mplug_of_plug(plug)
