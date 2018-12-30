"""
Unit tests for overall NodeCalculator functionality.
"""

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# IMPORTS
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Python imports

# Third party imports
from maya import cmds

# Local imports
from base import BaseTestCase
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

TEST_VALUES = [
    True,
    3,
    7.3,
]


# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# TESTS
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
class TestNodeCalculatorCore(BaseTestCase):

    def setUp(self):
        super(TestNodeCalculatorCore, self).setUp()

        self.node_a = noca.Node(cmds.createNode("transform", name=TEST_NODES[0]))
        self.node_b = noca.Node(cmds.createNode("transform", name=TEST_NODES[1]))
        self.node_c = noca.Node(cmds.createNode("transform", name=TEST_NODES[2]))
        self.desired_node_list = [self.node_a, self.node_b, self.node_c]

        self.attr_a = noca.Node(self.node_a, TEST_ATTR)
        self.attr_b = noca.Node(self.node_a, TEST_ATTR)
        self.attr_c = noca.Node(self.node_a, TEST_ATTR)
        self.desired_attr_list = [self.attr_a, self.attr_b, self.attr_c]

        self.value_a = noca.Node(TEST_VALUES[0])
        self.value_b = noca.Node(TEST_VALUES[1])
        self.value_c = noca.Node(TEST_VALUES[2])
        self.desired_value_list = [self.value_a, self.value_b, self.value_c]

        self.node_list = noca.NcList(self.desired_node_list)
        self.attr_list = noca.NcList(self.desired_attr_list)
        self.value_list = noca.NcList(self.desired_value_list)

    def tearDown(self):
        super(TestNodeCalculatorCore, self).tearDown()

        # Make sure the global auto unravel/consolidate is turned on again!
        noca.set_global_auto_unravel(True)
        noca.set_global_auto_consolidate(True)

    def test_auto_unravel(self):
        """ Test automatic attribute unravelling: .t -> .tx, .ty, .tz """

        # Test that by default unravelling takes place
        self.node_a.t = 1

        # Test individual auto unravel setting
        # Setattr that requires unravelling should NOT work
        node_a_no_auto_unravel = noca.Node(self.node_a, auto_unravel=False)
        # Setattr that doesn't require unravelling should work
        node_a_no_auto_unravel.tx = 1
        with self.assertRaises(RuntimeError):
            node_a_no_auto_unravel.t = [1, 2, 3]
        with self.assertRaises(RuntimeError):
            node_a_no_auto_unravel.t = 1

        # Test global auto unravel setting
        noca.set_global_auto_unravel(False)
        # Setattr that doesn't require unravelling should work
        self.node_a.tx = 1
        with self.assertRaises(RuntimeError):
            self.node_a.t = [1, 2, 3]
        # Setattr that requires unravelling should NOT work
        with self.assertRaises(RuntimeError):
            self.node_a.t = 1

    def test_auto_consolidate(self):
        """ Test automatic attribute consolidating: .tx, .ty, .tz -> .t """

        # Test that by default consolidating takes place
        self.node_a.s = self.node_a.t
        child_connections = [
            cmds.listConnections(
                "{}.sx".format(TEST_NODES[0]), connections=True, plugs=True
            ),
            cmds.listConnections(
                "{}.sy".format(TEST_NODES[0]), connections=True, plugs=True
            ),
            cmds.listConnections(
                "{}.sz".format(TEST_NODES[0]), connections=True, plugs=True
            ),
        ]
        parent_connections = cmds.listConnections(
            "{}.s".format(TEST_NODES[0]), connections=True, plugs=True
        )[1]
        self.assertEqual(child_connections, [None, None, None])
        self.assertEqual(parent_connections, "A.translate")

        # Test individual auto consolidate setting
        node_b_no_auto_consolidate = noca.Node(TEST_NODES[1], auto_consolidate=False)
        node_b_no_auto_consolidate.s = self.node_a.t
        child_connections = [
            cmds.listConnections(
                "{}.sx".format(TEST_NODES[1]), connections=True, plugs=True
            )[1],
            cmds.listConnections(
                "{}.sy".format(TEST_NODES[1]), connections=True, plugs=True
            )[1],
            cmds.listConnections(
                "{}.sz".format(TEST_NODES[1]), connections=True, plugs=True
            )[1],
        ]
        parent_connections = cmds.listConnections(
            "{}.s".format(TEST_NODES[1]), connections=True, plugs=True
        )
        self.assertEqual(child_connections, ["A.translateX", "A.translateY", "A.translateZ"])
        self.assertEqual(parent_connections, None)

        # Test global auto consolidate setting
        noca.set_global_auto_consolidate(False)
        self.node_c.s = self.node_a.t
        child_connections = [
            cmds.listConnections(
                "{}.sx".format(TEST_NODES[2]), connections=True, plugs=True
            )[1],
            cmds.listConnections(
                "{}.sy".format(TEST_NODES[2]), connections=True, plugs=True
            )[1],
            cmds.listConnections(
                "{}.sz".format(TEST_NODES[2]), connections=True, plugs=True
            )[1],
        ]
        parent_connections = cmds.listConnections(
            "{}.s".format(TEST_NODES[2]), connections=True, plugs=True
        )
        self.assertEqual(child_connections, ["A.translateX", "A.translateY", "A.translateZ"])
        self.assertEqual(parent_connections, None)

    def test_attributes(self):
        """Test child and indexed attribute handling"""
        blendshape_name = "test_blendshape"
        blendshape_attr = "inputTarget[0].inputTargetGroup[0].targetWeights[0]"
        blendshape_node = noca.Node(
            cmds.createNode("blendShape", name=blendshape_name),
            blendshape_attr
        )

        blendshape_node.attrs = self.attr_a

        blendshape_connections = cmds.listConnections(
            "{}.{}".format(blendshape_name, blendshape_attr),
            connections=True,
            plugs=True,
        )
        desired_connections = [
            "{}.{}".format(blendshape_name, blendshape_attr),
            "{}.{}".format(TEST_NODES[0], TEST_ATTR),
        ]
        self.assertEqual(blendshape_connections, desired_connections)

    def test_non_unique_node_names(self):
        """This test requires a specific set of nodes, different from the generic setUp."""

        node_x = cmds.createNode("transform", name="X")
        group = cmds.createNode("transform", name="grp")
        node_x_grouped = cmds.createNode("transform")
        cmds.parent(node_x_grouped, group)
        cmds.rename(node_x_grouped, "X")

        node_x = "|X"
        node_x_grouped = "grp|X"

        nc_x = noca.Node(node_x)
        nc_x_grouped = noca.Node(node_x_grouped)

        nc_x.tx = self.node_a.tx
        nc_x.ty = 1

        nc_x_grouped.tx = self.node_a.ty
        nc_x_grouped.ty = 2

        node_x_connection = cmds.listConnections(node_x + ".tx", plugs=True)
        self.assertEqual(node_x_connection, [self.node_a.node + '.translateX'])
        self.assertEqual(cmds.getAttr(node_x + ".ty"), 1)

        node_x_grouped_connection = cmds.listConnections(node_x_grouped + ".tx", plugs=True)
        self.assertEqual(node_x_grouped_connection, [self.node_a.node + '.translateY'])
        self.assertEqual(cmds.getAttr(node_x_grouped + ".ty"), 2)

    def test_shape_attribute_access(self):
        """Test whether attrs of a transforms shape are directly accessible"""

        mesh_a = cmds.polyCube(name="testMeshA", constructionHistory=False)[0]
        mesh_b = cmds.polyCube(name="testMeshB", constructionHistory=False)[0]

        nc_mesh_a = noca.Node(mesh_a)
        nc_mesh_b = noca.Node(mesh_b)

        # Make sure the NodeCalculator nodes directly refer to the transforms, not the shapes!
        self.assertEqual(cmds.objectType(nc_mesh_a.node), "transform")
        self.assertEqual(cmds.objectType(nc_mesh_b.node), "transform")

        # Check whether the shapes get connected correctly, without accessing them explicitly.
        nc_mesh_a.inMesh = nc_mesh_b.outMesh
        mesh_a_connections = cmds.listConnections(mesh_a + ".inMesh", plugs=True)
        self.assertEqual(mesh_a_connections, [mesh_b + 'Shape.outMesh'])
