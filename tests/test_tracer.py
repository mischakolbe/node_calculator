"""
Unit tests for noca.Tracer
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
# GLOBALS
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
TEST_NODES = {
    "A": "transform",
    "B": "transform",
    "C": "transform",
}


# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# TESTS
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~


class TestTracerClass(TestCase):

    def setUp(self):
        for node, node_type in TEST_NODES.iteritems():
            cmds.createNode(node_type, name=node)

    def tearDown(self):
        cmds.delete(TEST_NODES.keys())

    def test_standard_trace(self):
        """ Test regular tracing """

        expected_trace = [
            "cmds.setAttr('A.translateY', 1.1)",
            "val1 = cmds.getAttr('A.ty')",
            "var1 = cmds.createNode('multiplyDivide', name='nc_MUL_translateX_1f_multiplyDivide')",
            "cmds.setAttr(var1 + '.operation', 1)",
            "cmds.connectAttr('A.translateX', var1 + '.input1X', force=True)",
            "cmds.setAttr(var1 + '.input2X', (val1 + 2) / 2)",
            "var2 = cmds.createNode('plusMinusAverage', name='nc_SUB_list_plusMinusAverage')",
            "cmds.setAttr(var2 + '.operation', 2)",
            "cmds.connectAttr('B.scale', var2 + '.input3D[0]', force=True)",
            "cmds.connectAttr(var1 + '.outputX', var2 + '.input3D[1].input3Dx', force=True)",
            "cmds.connectAttr(var1 + '.outputX', var2 + '.input3D[1].input3Dy', force=True)",
            "cmds.connectAttr(var1 + '.outputX', var2 + '.input3D[1].input3Dz', force=True)",
            "cmds.connectAttr(var2 + '.output3D', 'C.translate', force=True)"
        ]

        with noca.Tracer() as trace:
            a = noca.Node("A")
            b = noca.Node("B")
            c = noca.Node("C")
            a.ty = 1.1
            num = a.ty.get()
            c.t = b.s - a.tx * ((num + 2) / 2)

        self.assertEqual(trace, expected_trace)
