"""
Unit tests for overall noca functionality:
- Plug unravelling
- Set or connect







a = noca.Node("A.ty", auto_consolidate=False)
b = noca.Node("B", auto_consolidate=False)
c = noca.Node("C", auto_consolidate=False)

multi-"layer" attributes!
e = noca.Node("blendShape1.inputTarget[0].inputTargetGroup[0].targetWeights[0]")

b.v = e
"""


# ERROR EXPECTED, IF noca.link IS NOT PRESENT!
# c.t = noca.link([a.ty, a.tx, 2]) - 5
# c.t = noca.link([a.ty, a.tx, 2]) * [1, 4, b.tx]

# Make example networks for all types!


# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# IMPORTS
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Python imports
import unittest

# Local imports
from cmt.test import TestCase
import node_calculator.core as noca


# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# TESTS
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~


class TestNodeCalculatorCore(TestCase):

    @unittest.skip("Not implemented yet")
    def test_xyz(self):
        """ Test XYZ """
        pass
