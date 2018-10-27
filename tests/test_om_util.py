"""
Unit tests for noca.om_util
"""

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# IMPORTS
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Python imports
import unittest
import timeit

# Third party imports
from maya import cmds
from maya.api import OpenMaya

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
        (
            '', '', 'node',
            [('parent_attr', None)]
        ),
    "name_space:node.parent_attr":
        (
            'name_space', '', 'node',
            [('parent_attr', None)]
        ),
    "|dag|path|node.parent_attr":
        (
            '', 'dag|path|', 'node',
            [('parent_attr', None)]
        ),
    "node.parent_attr[1]":
        (
            '', '', 'node',
            [('parent_attr', 1)]
        ),
    "node.parent_attr.child_attr":
        (
            '', '', 'node',
            [('parent_attr', None), ('child_attr', None)]
        ),
    "node.parent_attr[1].child_attr[2].grand_child_attr":
        (
            '', '', 'node',
            [('parent_attr', 1), ('child_attr', 2), ('grand_child_attr', None)]
        ),
    "name_space:|dag|path|node.parent_attr[1].child_attr[2].grand_child_attr":
        (
            'name_space', 'dag|path|', 'node',
            [('parent_attr', 1), ('child_attr', 2), ('grand_child_attr', None)]
        )
}


# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# TESTS
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
class TestTracerClass(TestCase):

    def setUp(self):
        self.node_name = "testNode"
        self.node_alt_name = "testAltName"
        self.group_name = "testGrp"
        self.instance_name = "testInstance"
        self.operator_name = "testPlusMinusAverage"
        self.long_name_attr = "longName"
        self.aliased_attr_orig = "willBeAliased"
        self.aliased_attr = "aliased"

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

        # Add a normal attribute and an aliased attribute to the testNode
        cmds.addAttr(self.node_name, longName=self.long_name_attr, keyable=True)
        cmds.addAttr(self.node_name, longName=self.aliased_attr_orig, keyable=True)
        cmds.aliasAttr(self.aliased_attr, self.node_name + "." + self.aliased_attr_orig)

    def test_split_plug_string(self):
        """ Test plug strings are correctly split into their components """

        for test_plug_string, desired_components in test_plug_strings.iteritems():
            components = om_util.split_plug_string(test_plug_string)
            self.assertEqual(components, desired_components)

            node_string, attr_string = test_plug_string.split(".", 1)
            node_components = om_util.split_node_string(node_string)
            self.assertEqual(node_components, desired_components[:3])
            attr_components = om_util.split_attr_string(attr_string)
            self.assertEqual(attr_components, desired_components[-1])

    def test_mobj(self):
        """ Test mobj creation & retrieving """

        # Test MObject creation
        test_node_mobj = om_util.get_mobj(self.test_node)
        self.assertEqual(type(test_node_mobj), OpenMaya.MObject)
        self.assertEqual(type(om_util.get_mobj(test_node_mobj)), OpenMaya.MObject)

        # Test name retrieving of MObjects
        self.assertEqual(om_util.get_name_of_mobj(test_node_mobj), self.node_name)
        self.assertEqual(
            om_util.get_dag_path_of_mobj(test_node_mobj, full=False),
            self.node_name
        )
        self.assertEqual(
            om_util.get_dag_path_of_mobj(test_node_mobj, full=True),
            "|{}|{}".format(self.group_name, self.node_name)
        )

        # Test renaming of MObjects
        om_util.rename_mobj(test_node_mobj, self.node_alt_name)
        self.assertEqual(om_util.get_name_of_mobj(test_node_mobj), self.node_alt_name)
        om_util.rename_mobj(test_node_mobj, self.node_name)

        # Test MObject selection and retrieving of selection
        om_util.select_mobjs(test_node_mobj)
        self.assertEqual(cmds.ls(selection=True), [self.node_name])
        selected_mobjs = om_util.get_selected_nodes_as_mobjs()
        self.assertEqual(len(selected_mobjs), 1)
        self.assertEqual(om_util.get_name_of_mobj(selected_mobjs[0]), self.node_name)

    def test_mdag_path(self):
        """ Test mdag path creation & retrieving """

        test_node_mobj = om_util.get_mobj(self.test_node)
        mdag_path = om_util.get_mdag_path(test_node_mobj)
        self.assertEqual(type(mdag_path), OpenMaya.MDagPath)
        self.assertEqual(str(mdag_path), self.node_name)

    def test_shape(self):
        """ Test shape creation & retrieving """

        test_node_mobj = om_util.get_mobj(self.test_node)
        shape_mobjs = om_util.get_shape_mobjs(test_node_mobj)
        self.assertEqual(len(shape_mobjs), 2)
        shape_mobj_name = om_util.get_name_of_mobj(shape_mobjs[0])
        self.assertEqual(shape_mobj_name, "{}Shape".format(self.node_name))

    def test_node(self):
        """ Test node creation & retrieving """

        # Test check for instantiated nodes
        self.assertEqual(om_util.is_instanced(self.test_node), False)
        self.assertEqual(om_util.is_instanced(self.test_instance), False)
        self.assertEqual(
            om_util.is_instanced(self.test_shapes[0]),
            True
        )

        # Test type query
        self.assertEqual(om_util.get_node_type(self.test_node, api_type=False), "transform")
        self.assertEqual(om_util.get_node_type(self.test_node, api_type=True), "kTransform")

        # Test relatives query
        self.assertEqual(type(om_util.get_mfn_dag_node(self.test_node)), OpenMaya.MFnDagNode)
        self.assertEqual(om_util.get_parent(self.test_shapes[0]), self.test_node)
        _expected_parents = [self.test_node, self.test_group]
        self.assertEqual(om_util.get_parents(self.test_shapes[0]), _expected_parents)

    def test_aliased_attrs(self):
        """ """
        test_node_mobj = om_util.get_mobj(self.test_node)

        # Make sure regular (custom) attributes are accessible
        normal_plug = om_util.get_mplug_of_mobj(test_node_mobj, self.long_name_attr)
        self.assertEqual(type(normal_plug), OpenMaya.MPlug)
        self.assertEqual(str(normal_plug), "{}.{}".format(self.test_node, self.long_name_attr))

        # Check whether an aliased attribute is accessible
        aliased_plug = om_util.get_mplug_of_mobj(test_node_mobj, self.aliased_attr)
        self.assertEqual(type(aliased_plug), OpenMaya.MPlug)
        self.assertEqual(str(aliased_plug), "{}.{}".format(self.test_node, self.aliased_attr))

        # Check whether an aliased attribute can still be found via its actual name as well.
        aliased_orig_plug = om_util.get_mplug_of_mobj(test_node_mobj, self.aliased_attr_orig)
        self.assertEqual(type(aliased_orig_plug), OpenMaya.MPlug)
        self.assertEqual(str(aliased_orig_plug), "{}.{}".format(self.test_node, self.aliased_attr))

        # Check whether an attribute that doesn't exist returns None.
        bogus_plug = om_util.get_mplug_of_mobj(test_node_mobj, "someBogusName")
        self.assertIsNone(bogus_plug)

    def test_plug(self):
        """ """
        test_node_mobj = om_util.get_mobj(self.test_node)
        operator_mobj = om_util.get_mobj(self.test_operator)
        transform_attr = "translateX"
        parent_attr = "input3D"
        array_attr = "{}[0]".format(parent_attr)
        child_attr = "input3Dx"
        test_value = 7

        # Test getting an mplug from a plug
        mplug = om_util.get_mplug_of_plug("{}.{}".format(self.test_operator, array_attr))
        self.assertEqual(type(mplug), OpenMaya.MPlug)
        self.assertEqual(str(mplug), "{}.{}".format(self.test_operator, array_attr))
        mplug = om_util.get_mplug_of_node_and_attr(self.test_operator, array_attr)
        self.assertEqual(type(mplug), OpenMaya.MPlug)
        self.assertEqual(str(mplug), "{}.{}".format(self.test_operator, array_attr))

        self.assertEqual(om_util.is_valid_mplug(mplug), True)

        # Test attribute setting and getting
        om_util.set_mobj_attribute(test_node_mobj, transform_attr, test_value)
        queried_val = cmds.getAttr("{}.{}".format(self.test_node, transform_attr))
        self.assertEqual(queried_val, test_value)
        self.assertEqual(om_util.get_attr_of_mobj(test_node_mobj, transform_attr), queried_val)

        # Test mplug query
        parent_plug = om_util.get_mplug_of_mobj(operator_mobj, parent_attr)
        self.assertEqual(type(parent_plug), OpenMaya.MPlug)
        self.assertEqual(str(parent_plug), "{}.{}".format(self.test_operator, parent_attr))

        # Test array attribute access
        array_mplug_elements = om_util.get_array_mplug_elements(parent_plug)
        array_mplug_elements_as_str = [str(var) for var in array_mplug_elements]
        expected_array_plugs = [
            "{}.{}[{}]".format(self.test_operator, parent_attr, var) for var in [0, 3]
        ]
        self.assertEqual(array_mplug_elements_as_str, expected_array_plugs)

        # Test array mplug access via pysical index
        mplug_by_index = str(om_util.get_array_mplug_by_index(parent_plug, 0, physical=True))
        expected_plug = "{}.{}[0]".format(self.test_operator, parent_attr)
        self.assertEqual(mplug_by_index, expected_plug)
        mplug_by_index = str(om_util.get_array_mplug_by_index(parent_plug, 1, physical=True))
        expected_plug = "{}.{}[3]".format(self.test_operator, parent_attr)
        self.assertEqual(mplug_by_index, expected_plug)
        mplug_by_index = om_util.get_array_mplug_by_index(parent_plug, 2, physical=True)
        expected_plug = None
        self.assertEqual(mplug_by_index, expected_plug)

        # Test array mplug access via logical index
        mplug_by_index = str(om_util.get_array_mplug_by_index(parent_plug, 0, physical=False))
        expected_plug = "{}.{}[0]".format(self.test_operator, parent_attr)
        self.assertEqual(mplug_by_index, expected_plug)
        mplug_by_index = str(om_util.get_array_mplug_by_index(parent_plug, 1, physical=False))
        expected_plug = "{}.{}[1]".format(self.test_operator, parent_attr)
        self.assertEqual(mplug_by_index, expected_plug)
        mplug_by_index = str(om_util.get_array_mplug_by_index(parent_plug, 3, physical=False))
        expected_plug = "{}.{}[3]".format(self.test_operator, parent_attr)
        self.assertEqual(mplug_by_index, expected_plug)

        # Test child attribute access
        child_mplug = om_util.get_child_mplug(mplug, child_attr)
        expected_child_plug = "{}.{}.{}".format(self.test_operator, array_attr, child_attr)
        self.assertEqual(str(child_mplug), expected_child_plug)

        # Test parent attribute access
        parent_mplug = om_util.get_parent_mplug(child_mplug)
        self.assertEqual(str(parent_mplug), "{}.{}".format(self.test_operator, array_attr))

        # Test children attributes access
        child_mplugs = om_util.get_child_mplugs(parent_mplug)
        expected_child_plugs = [
            "{}.{}.input3D{}".format(self.test_operator, array_attr, var) for var in "xyz"
        ]
        self.assertEqual([str(var) for var in child_mplugs], expected_child_plugs)

    def test_speed(self):
        """Test speed advantage of om_util functions over cmds equivalent"""

        # TODO: Write speed tests

        num_iterations = 1000
        node = self.test_node
        mobj = om_util.get_mobj(self.test_node)

        # Test speed of get_parent
        def maya_get_parent():
            return cmds.listRelatives(node, parent=True)[0]

        def noca_get_parent():
            return om_util.get_parent(mobj)
        self.assertEqual(maya_get_parent(), noca_get_parent())
        maya_time = timeit.timeit(maya_get_parent, number=num_iterations)
        noca_time = timeit.timeit(noca_get_parent, number=num_iterations)
        self.assertLess(noca_time, maya_time)

        # Test speed of get_parents
        def maya_get_parents():
            return cmds.listRelatives(node, allParents=True)

        def noca_get_parents():
            return om_util.get_parents(mobj)
        self.assertEqual(maya_get_parents(), noca_get_parents())
        maya_time = timeit.timeit(maya_get_parents, number=num_iterations)
        noca_time = timeit.timeit(noca_get_parents, number=num_iterations)
        self.assertLess(noca_time, maya_time)

        # Test speed of get_dag_path_of_mobj
        def maya_get_dag_path():
            return cmds.ls(node, long=True)

        def noca_get_dag_path():
            return om_util.get_dag_path_of_mobj(mobj, full=True)
        self.assertEqual(maya_get_dag_path()[0], noca_get_dag_path())
        maya_time = timeit.timeit(maya_get_dag_path, number=num_iterations)
        noca_time = timeit.timeit(noca_get_dag_path, number=num_iterations)
        self.assertLess(noca_time, maya_time)

        # Test speed of get_node_type
        def maya_get_node_type():
            return cmds.objectType(node)

        def noca_get_node_type():
            return om_util.get_node_type(mobj, api_type=False)
        self.assertEqual(maya_get_node_type(), noca_get_node_type())
        maya_time = timeit.timeit(maya_get_node_type, number=num_iterations)
        noca_time = timeit.timeit(noca_get_node_type, number=num_iterations)
        self.assertLess(noca_time, maya_time)

        # # Test speed of rename_mobj
        # # THIS IS CURRENTLY SLOWER THAN CMDS!!
        # def maya_rename():
        #     return cmds.rename(node, node)

        # def noca_rename():
        #     return om_util.rename_mobj(mobj, node)
        # self.assertEqual(maya_rename(), noca_rename())
        # maya_time = timeit.timeit(maya_rename, number=num_iterations)
        # noca_time = timeit.timeit(noca_rename, number=num_iterations)
        # self.assertLess(noca_time, maya_time)

        # # Test speed of set_mobj_attribute
        # # THIS IS CURRENTLY SLOWER THAN CMDS!!
        # def maya_set_attr():
        #     return cmds.setAttr(node + ".tx", 1)

        # def noca_set_attr():
        #     return om_util.set_mobj_attribute(mobj, "tx", 1)
        # self.assertEqual(maya_set_attr(), noca_set_attr())
        # maya_time = timeit.timeit(maya_set_attr, number=num_iterations)
        # noca_time = timeit.timeit(noca_set_attr, number=num_iterations)
        # self.assertLess(noca_time, maya_time)

        # # Test speed of get_node_type
        # # THIS IS CURRENTLY SLOWER THAN CMDS!!
        # def maya_get_attr():
        #     return cmds.getAttr(node + ".tx")

        # def noca_get_attr():
        #     return om_util.get_attr_of_mobj(mobj, "tx")
        # self.assertEqual(maya_get_attr(), noca_get_attr())
        # maya_time = timeit.timeit(maya_get_attr, number=num_iterations)
        # noca_time = timeit.timeit(noca_get_attr, number=num_iterations)
        # self.assertLess(noca_time, maya_time)
